# Quick Start Guide

Get the MOSIP OCR Web Prototype running in 5 minutes!

## 🚀 Automatic Setup (Recommended)

### Windows (PowerShell)

```powershell
.\setup.ps1
```

### Linux/Mac

```bash
chmod +x setup.sh
./setup.sh
```

## 📝 Manual Setup

### Step 1: Backend Setup

```bash
cd backend
python3 -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

### Step 2: Frontend Setup

```bash
cd frontend
npm install
```

### Step 3: Start Backend

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python main.py
```

Backend runs on: `http://localhost:8000`

### Step 4: Start Frontend

```bash
cd frontend
npm run dev
```

Frontend runs on: `http://localhost:3000`

## 🎯 Test It!

1. Open `http://localhost:3000` in your browser
2. Click **"Use Demo PDF"** button
3. Wait for extraction (first time may take longer - models are downloading)
4. Review extracted fields
5. Click **"Verify Information"**

## 📄 Sample PDF

For demo mode, place a PDF at:
- `backend/sample_inputs/sample.pdf`

Or the system will try:
- `/mnt/data/690e263ff3503_Optical_Character_Recognition__OCR__for_Text_Extraction_and_Verification.pdf`

## ⚠️ First Run Notes

- **First extraction takes longer** (~2-5 minutes) - TrOCR models are downloading (~1-2GB)
- Models are cached after first download
- GPU acceleration is automatic if available
- CPU works fine, just slower

## 🐛 Troubleshooting

**Backend won't start?**
- Check Python version: `python --version` (need 3.10+)
- Ensure virtual environment is activated
- Check if port 8000 is available

**Frontend won't start?**
- Check Node.js version: `node --version` (need 18+)
- Try: `npm cache clean --force` then `npm install`

**Models not downloading?**
- Check internet connection
- Models download from HuggingFace (first time only)

**PDF processing fails?**
- Install poppler-utils:
  - Ubuntu: `sudo apt-get install poppler-utils`
  - Mac: `brew install poppler`
  - Windows: Download from poppler website

## ✅ Success!

If you see the beautiful UI with glassmorphism effects and smooth animations, you're all set! 🎉


