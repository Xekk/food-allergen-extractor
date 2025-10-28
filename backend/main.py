from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import io
import pdfplumber
from pdf2image import convert_from_bytes
import pytesseract
from prompt_templates import build_llm_prompt
from openai import AsyncOpenAI
import json
import re
import os
from dotenv import load_dotenv
import asyncio

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
def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract text from PDF; fallback to OCR if text is too short."""
    text_chunks = []
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                text_chunks.append(page.extract_text() or "")
    except Exception:
        text_chunks = []

    text = "\n".join(filter(None, text_chunks)).strip()

    # OCR fallback
    if len(text) < 100:
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
            timeout=120,  # allow longer for big PDFs
        )
        return response.choices[0].message.content.strip()
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="OpenAI request timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI error: {e}")

# --- Routes ---
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    print(f"📄 Received file {file.filename}", flush=True)
    contents = await file.read()

    # Extract text (OCR included)
    raw_text = extract_text_from_pdf(contents)
    print(f"✅ Text extracted ({len(raw_text)} chars)", flush=True)

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
