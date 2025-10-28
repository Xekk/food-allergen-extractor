from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import io
import asyncio
import pdfplumber
from pdf2image import convert_from_bytes
import pytesseract
from prompt_templates import build_llm_prompt
from openai import AsyncOpenAI
import json
import re
import os
from dotenv import load_dotenv
import tempfile

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI async client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# --- Utilities ---

def extract_text_from_pdf(pdf_bytes: bytes, run_ocr_if_needed: bool = True) -> str:
    """Extract text from PDF; fallback to OCR if text is too short."""
    text_chunks = []
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                text_chunks.append(page.extract_text() or "")
    except Exception:
        text_chunks = []

    text = "\n".join(filter(None, text_chunks)).strip()

    # Optional OCR fallback
    if run_ocr_if_needed and len(text) < 100:
        print("No text detected, running OCR...", flush=True)
        images = convert_from_bytes(pdf_bytes, dpi=200)
        config = "-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789☑☒☐✔✖[]- --psm 6"
        ocr_text = [pytesseract.image_to_string(img, lang="hun+eng", config=config) for img in images]
        text = "\n".join(ocr_text)
    return text

async def call_openai(prompt: str) -> str:
    """Send prompt to OpenAI asynchronously with timeout."""
    try:
        response = await asyncio.wait_for(
            client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a JSON-only data extraction assistant. Return only valid JSON with no extra text."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0,
                max_tokens=3000,
            ),
            timeout=90,  # prevent hanging
        )
        return response.choices[0].message.content.strip()
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="OpenAI request timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI error: {e}")

# --- Background OCR (temporary file, auto-cleanup) ---
def background_ocr_task(pdf_bytes: bytes):
    """Run OCR in background and save to a temp file (deleted automatically)."""
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", delete=True) as tmp:
        text = extract_text_from_pdf(pdf_bytes, run_ocr_if_needed=True)
        tmp.write(text)
        tmp.flush()
        print(f"OCR result processed in background (temp file: {tmp.name})", flush=True)
        # file is deleted automatically after leaving this block

# --- Routes ---
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    print(f"📄 Received file {file.filename}", flush=True)
    contents = await file.read()

    # Extract text (skip OCR for speed; optional to run in background)
    raw_text = extract_text_from_pdf(contents, run_ocr_if_needed=False)
    print(f"✅ Text extracted ({len(raw_text)} chars)", flush=True)

    # Optional background OCR for long-term use
    if background_tasks is not None and len(raw_text) < 100:
        background_tasks.add_task(background_ocr_task, contents)
        print("🔄 OCR scheduled in background", flush=True)

    if not raw_text.strip():
        raise HTTPException(status_code=500, detail="No text found in PDF")

    prompt = build_llm_prompt(raw_text)
    print("🚀 Sending to OpenAI...", flush=True)
    result = await call_openai(prompt)

    # Parse JSON
    try:
        json_match = re.search(r'\{.*\}', result, re.DOTALL)
        if json_match:
            result_json = json.loads(json_match.group(0))
        else:
            raise ValueError("No JSON found in response")
    except Exception as e:
        print("❌ Error parsing JSON:", e, flush=True)
        result_json = {"error": "Failed to parse model output", "raw": result}

    return {"extracted": result_json, "preview": raw_text[:200]}

# --- Run server ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
