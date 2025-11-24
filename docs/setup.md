# Setup Guide

## Prerequisites

### System Requirements

- **Python**: 3.10 or higher
- **Node.js**: 18.0 or higher
- **npm**: 9.0 or higher (comes with Node.js)
- **RAM**: Minimum 4GB (8GB+ recommended for PaddleOCR models)
- **Disk Space**: ~2-3GB for PaddleOCR models and dependencies

### Optional

- **CUDA-capable GPU**: For faster OCR processing (optional, CPU works fine)
- **poppler-utils**: For PDF processing (installed automatically in Docker)

## Installation Steps

### 1. Clone/Download Project

Ensure you have the complete project structure.

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

**Note**: PaddleOCR models will be downloaded automatically on first use. Models are cached after first download. Supported languages: English (en), Hindi (hi), Arabic (ar), Multilingual (ch).

### 3. Backend Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env (optional)
# OPENROUTER_API_KEY=your_key_here
# FALLBACK_ALLOW=false
# PORT=8000
```

### 4. Sample PDF Setup (for Demo Mode)

Place your sample PDF at:
```
backend/sample_inputs/mosip_sample.pdf
```

Or alternatively:
```
backend/sample_inputs/sample.pdf
```

### 5. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

### 6. Start Backend

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python main.py
```

Backend will start on `http://localhost:8000`

### 7. Start Frontend

```bash
cd frontend
npm run dev
```

Frontend will start on `http://localhost:3000`

## Verification

1. Open browser to `http://localhost:3000`
2. Click "Use Demo PDF" or upload a file
3. Wait for extraction
4. Review extracted fields
5. Submit for verification

## Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError`
- **Solution**: Ensure virtual environment is activated and dependencies are installed

**Problem**: `CUDA out of memory`
- **Solution**: Models will fall back to CPU automatically

**Problem**: `PDF processing fails`
- **Solution**: Install poppler-utils:
  - Ubuntu/Debian: `sudo apt-get install poppler-utils`
  - Mac: `brew install poppler`
  - Windows: Download from poppler website

**Problem**: Models download slowly
- **Solution**: PaddleOCR models download automatically on first use. First download may take time. Models are cached after first download.

### Frontend Issues

**Problem**: `Cannot connect to backend`
- **Solution**: Ensure backend is running on port 8000

**Problem**: `npm install fails`
- **Solution**: Clear cache: `npm cache clean --force` and try again

**Problem**: Port 3000 already in use
- **Solution**: Change port in `vite.config.js` or kill process using port 3000

## Docker Setup (Alternative)

### Build Backend Image

```bash
cd backend
docker build -t mosip-ocr-backend .
```

### Run Backend Container

```bash
docker run -p 8000:8000 mosip-ocr-backend
```

## Production Deployment

### Backend

1. Set `FALLBACK_ALLOW=false` in production (unless needed)
2. Use production WSGI server (gunicorn, uvicorn workers)
3. Set up reverse proxy (nginx)
4. Configure CORS for specific frontend domain

### Frontend

1. Build production bundle:
   ```bash
   npm run build
   ```
2. Serve `dist/` folder with nginx or similar
3. Update API URLs in production

## Environment Variables

### Backend (.env)

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PORT` | Backend server port | `8000` | No |
| `USE_GPU` | Enable GPU acceleration for PaddleOCR | `false` | No |

## Next Steps

After setup:
1. Test with demo PDF
2. Try uploading your own images/PDFs
3. Review confidence scores
4. Test verification flow
5. Customize field extraction patterns if needed


