from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import io
from pdf2image import convert_from_bytes
import pytesseract
import pdfplumber
from langchain_community.llms import Ollama
from prompt_templates import build_llm_prompt
import json
import re
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Ollama (make sure the model name matches what you pulled)
# llm = Ollama(model="llama3.1")
llm = Ollama(
    model=os.getenv("OLLAMA_MODEL", "deepseek-v3.1:671b-cloud"),
    base_url="https://api.ollama.com"  # cloud endpoint
)

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    text_chunks = []
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                text_chunks.append(page.extract_text() or "")
    except Exception:
        text_chunks = []

    text = "\n".join(filter(None, text_chunks)).strip()

    # OCR fallback if text too short
    if len(text) < 100:
        print("No text detected, running OCR...")
        images = convert_from_bytes(pdf_bytes, dpi=200)
        config = (
            "-c tessedit_char_whitelist="
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
            "0123456789☑☒☐✔✖[]- "
            "--psm 6"
        )
        ocr_text = []
        for img in images:
            page_text = pytesseract.image_to_string(img, lang="hun+eng", config=config)
            ocr_text.append(page_text)
        text = "\n".join(ocr_text)
    return text

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    print("Received file, processing: ", file.filename)

    contents = await file.read()
    raw_text = extract_text_from_pdf(contents)
    if not raw_text.strip():
        raise HTTPException(status_code=500, detail="No text found in PDF")

    prompt = build_llm_prompt(raw_text)
    result = llm.invoke(prompt)

    try:
        json_match = re.search(r'\{.*\}', result, re.DOTALL)
        if json_match:
            result_json = json.loads(json_match.group(0))
        else:
            raise ValueError("No JSON found in response")
    except Exception as e:
        print("Error parsing JSON:", e)
        result_json = {"error": "Failed to parse model output", "raw": result}

    return {"extracted": result_json, "preview": raw_text[:200]}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
