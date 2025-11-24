# MOSIP OCR Web Prototype - PaddleOCR Multilingual

A complete, production-ready, multilingual OCR + auto-form-mapping web application for MOSIP. Fully offline, supports **English, Hindi (Devanagari), and Arabic**, with both handwritten and printed text recognition.

## ✨ Features

- ✅ **100% Offline OCR** using PaddleOCR (supports 80+ languages)
- ✅ **Multilingual Support**: English, Hindi (Devanagari), Arabic, and mixed languages
- ✅ **Handwritten & Printed Text** recognition
- ✅ **Automatic Field Extraction** (name, age, gender, phone, email, address, city, state, country)
- ✅ **Language Auto-Detection** from document content
- ✅ **Beautiful Modern UI** with premium glassmorphism and animations
- ✅ **Auto-filled Digital Form** with confidence scores
- ✅ **Verification API** with rapidfuzz fuzzy matching
- ✅ **Full Preprocessing Pipeline**: grayscale, denoise, adaptive threshold, deskew, shadow removal, upscale
- ✅ **Demo Mode** with sample PDF
- ✅ **PDF Support** (multi-page)
- ✅ **Runs out-of-the-box** with single command

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm or yarn

### Automatic Setup & Run

#### Backend

```bash
cd backend
python3 -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

# Copy sample PDF (if available)
# Place your sample PDF at: backend/sample_inputs/sample.pdf

# Start server
python main.py
```

The backend will start on `http://localhost:8000`

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend will start on `http://localhost:3000`

## 📁 Project Structure

```
mosip-ocr-web/
├── backend/
│   ├── main.py                 # FastAPI app entry point
│   ├── routes/
│   │   ├── extract.py          # Extraction endpoint
│   │   └── verify.py           # Verification endpoint
│   ├── services/
│   │   ├── preprocess.py       # Image preprocessing
│   │   ├── model_selector.py   # Handwritten vs printed detection
│   │   ├── trocr_service.py    # TrOCR OCR engine
│   │   ├── field_mapper.py     # Field extraction
│   │   ├── confidence.py       # Confidence calculation
│   │   ├── fallback_openrouter.py  # Optional AI fallback
│   │   ├── merge_service.py    # Result merging
│   │   └── verifier.py         # Field verification
│   ├── sample_inputs/
│   │   └── sample.pdf          # Demo PDF (copy your PDF here)
│   ├── requirements.txt
│   ├── .env.example
│   └── start.sh
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── styles.css
│   │   └── components/
│   │       ├── Navbar.jsx
│   │       ├── UploadBox.jsx
│   │       ├── ExtractedForm.jsx
│   │       ├── VerificationPanel.jsx
│   │       ├── LoaderSpinner.jsx
│   │       ├── AnimatedCard.jsx
│   │       └── FieldConfidenceBar.jsx
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## 🔧 Configuration

### Backend Environment Variables

Create `backend/.env` from `backend/.env.example`:

```env
OPENROUTER_API_KEY=your_key_here  # Optional, for fallback
FALLBACK_ALLOW=false              # Enable/disable fallback
PORT=8000                         # Server port
```

### Demo Mode

To use demo mode, ensure `backend/sample_inputs/sample.pdf` exists, or the system will try to use:
`/mnt/data/690e263ff3503_Optical_Character_Recognition__OCR__for_Text_Extraction_and_Verification.pdf`

## 📡 API Endpoints

### POST `/api/extract`

Extract fields from uploaded image/PDF.

**Request:**
- `file`: Image or PDF file (multipart/form-data)
- `demo_mode`: boolean (use sample PDF)
- `allow_fallback`: boolean (enable OpenRouter fallback)

**Response:**
```json
{
  "success": true,
  "fields": {
    "name": "...",
    "age": "...",
    "gender": "...",
    "phone": "...",
    "email": "...",
    "address": "..."
  },
  "field_confidences": {...},
  "document_confidence": 0.85,
  "ocr_confidence": 0.90,
  "model_used": "microsoft/trocr-large-printed",
  "fallback_used": false
}
```

### POST `/api/verify`

Verify submitted fields against extracted fields.

**Request:**
```json
{
  "submitted_fields": {...},
  "extracted_fields": {...}
}
```

**Response:**
```json
{
  "success": true,
  "matches": {...},
  "mismatches": [...],
  "overall_score": 0.92,
  "verification_passed": true
}
```

## 🎨 UI Features

- **Glassmorphism Design** - Modern glass-effect panels
- **Smooth Animations** - Framer Motion powered transitions
- **Confidence Visualization** - Animated progress bars
- **Real-time Feedback** - Loading states and progress indicators
- **Responsive Design** - Works on all screen sizes

## 🔒 MOSIP Compliance

- ✅ Primary OCR is **100% local offline** (TrOCR)
- ✅ No cloud OCR dependencies
- ✅ Fallback AI is **optional** and only used when:
  - `allow_fallback = true`
  - `FALLBACK_ALLOW = true` in .env
  - Document confidence < 0.70 OR field confidence < 0.65

## 🛠️ Development

### Backend Development

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python main.py
```

### Frontend Development

```bash
cd frontend
npm run dev
```

## 📝 Notes

- First run will download TrOCR models (~1-2GB) - this is a one-time download
- GPU acceleration is automatically used if available
- PDF processing requires `poppler-utils` (installed via Docker or system package manager)

## 🐳 Docker Support

A Dockerfile is provided for containerized deployment:

```bash
cd backend
docker build -t mosip-ocr-backend .
docker run -p 8000:8000 mosip-ocr-backend
```

## 📄 License

MIT License

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a PR.


