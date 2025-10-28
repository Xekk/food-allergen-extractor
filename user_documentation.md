# 🧾 User Documentation

## 📘 Overview
The **Allergen & Nutrition Extractor** is a web-based AI tool that automatically extracts **allergen** and **nutritional** data from food product PDFs.  
It supports both **text-based** and **scanned PDFs** (with OCR fallback).  


---

## 🚀 Features
- ✅ Upload food label PDFs directly from the browser  
- ✅ Automatic extraction of:
  - Allergen presence (e.g., Gluten, Egg, Milk, etc.)
  - Nutritional values per 100g
- ✅ JSON output (structured and machine-readable)
- ✅ Text preview of extracted document
- ✅ Works with multilingual content (Hungarian / English)
- ✅ OCR fallback for scanned PDFs (Tesseract-based)
- ✅ Clean, responsive web interface (Next.js + FastAPI backend)

---

## 🧑‍💻 How to Use

1. **Open the web app**  
   Visit https://food-allergen-extractor.vercel.app/.

2. **Upload a PDF file**  
   Click **Choose File** → select your PDF → press **Upload & Extract**.

3. **Wait for processing**  
   The system reads the text (and performs OCR if needed).  
   Then it sends the extracted content to OpenAI for structured data extraction.

4. **View Results**  
   - The app displays a table of allergens and nutritional values.  
   - You’ll also see a short preview of the PDF’s extracted text.  

5. **Download JSON**  
   Click **💾 Download JSON** to save the extracted results.

---

## 📂 Supported Files
- PDF format only (one at a time)
- Both text-based and scanned PDFs are supported

---

## 🧠 Example Output

```json
{
  "allergens": {
    "Gluten": "absent",
    "Egg": "absent",
    "Milk": "present",
    "Soy": "no_data"
  },
  "nutrition_per_100g": {
    "Energy": "120 kcal",
    "Protein": "8.5 g",
    "Fat": "4.2 g",
    "Sugar": "1.1 g",
    "Sodium": "0.12 g"
  }
}
