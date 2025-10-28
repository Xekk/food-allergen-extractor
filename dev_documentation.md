# 🧩 Developer Documentation

## 📘 Project Overview
This project extracts **allergen** and **nutrition information** from PDF documents using **FastAPI (backend)**, **Next.js (frontend)**, and **OpenAI GPT models** for data interpretation.  
It supports both text-based and scanned PDFs and returns structured **JSON output**.

---

## 🏗️ Tech Stack

| Layer | Technology |
|--------|-------------|
| **Frontend** | Next.js (React) |
| **Backend** | FastAPI |
| **OCR (optional)** | PyTesseract |
| **AI Model** | OpenAI GPT-4o-mini |
| **Containerization** | Docker |
| **Deployment** | Render Web Services | Vercel

---



## ⚙️ Backend Setup

### 1️⃣ Environment Variables

Create a '.env' file in the 'backend/' directory:

```env
OPENAI_API_KEY=your_openai_api_key_here

OPENAI_MODEL=gpt-4o-mini
```
### 2️⃣ Install Dependencies

```cd backend

pip install -r requirements.txt
```

### 3️⃣ Run Locally
```uvicorn main:app --host 0.0.0.0 --port 8000 --reload```

The backend will start at: http://localhost:8000

## 💻 Frontend Setup

### 1️⃣ Dependencies
From the /frontend folder:
```npm install```

### 2️⃣ Environment Variables

Create a .env file inside /frontend:
```NEXT_PUBLIC_API_URL=http://localhost:8000```

### 3️⃣ Run Locally
```npm run dev```
Frontend runs at:
http://localhost:3000

---

## 🚀 Deployment Guide (Render)

This project is deployed using **Render**, which supports both **FastAPI** and **Next.js** web services.  
Follow the steps below carefully.

---

### 🧠 Backend (FastAPI)

1. **Create a New Web Service**
   - Go to [https://render.com](https://render.com)
   - Click **"New +" → "Web Service"**
   - Connect your GitHub repository
   - Select the `/backend` directory as the root


2. **Environment Variables**
   Add the following under **Environment → Add Environment Variable**:
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_MODEL=gpt-4o-mini

3. **Deploy**

  ```Click "Deploy Web Service"
  
  After deployment, note your backend URL — e.g.:
  https://food-allergen-extractor-backend.onrender.com
  ```

## 💻 Frontend Deployment (Next.js on Vercel)

This project’s frontend is deployed using **Vercel**, which natively supports Next.js apps.

---

### 1. Connect Your GitHub Repository

1. Go to [https://vercel.com](https://vercel.com).
2. Log in with your GitHub account.
3. Click **“Add New Project”**.
4. Import your GitHub repository that contains this project.
5. When prompted, select the **`/frontend`** folder as the root directory.

---

### 2. Configure Build Settings

Vercel will automatically detect it’s a **Next.js** project.

You can keep the defaults:

- **Framework Preset:** Next.js  
- **Build Command:** `npm run build`  
- **Output Directory:** `.next`  
- **Install Command:** `npm install`

> ⚙️ If you’re using Yarn or pnpm, Vercel will detect that automatically.

---

### 3. Add Environment Variables

Go to the **“Environment Variables”** section in Vercel’s project settings and add:

```bash
NEXT_PUBLIC_API_URL=https://food-allergen-extractor-backend.onrender.com
```
Make sure this points exactly to your deployed backend URL.

### 4. Deploy

Click “Deploy” and wait for the build process to finish.
Once done, Vercel will give you a live link such as:
```
https://food-allergen-extractor.vercel.app
```
### 5. Test the live app

1.  Visit your Vercel deployment URL.

2.  Upload a sample PDF.

3.  Confirm that the backend receives the file and the extracted allergen/nutrition data appears.





