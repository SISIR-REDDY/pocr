# Architecture Documentation

## System Overview

The MOSIP OCR Web Prototype is a full-stack application consisting of:

1. **Backend**: FastAPI-based Python service with PaddleOCR multilingual OCR engine
2. **Frontend**: React + Vite application with modern glassmorphism UI

## Backend Architecture

### Core Services

#### 1. Preprocessing Pipeline (`preprocess.py`)
- **Purpose**: Optimize images for OCR
- **Full Pipeline Steps**:
  1. RGB conversion
  2. Grayscale conversion
  3. Bilateral denoising
  4. Shadow removal (morphological operations)
  5. Deskewing (rotation correction)
  6. Perspective fix (basic)
  7. Adaptive thresholding
  8. Upscaling (2x) for better OCR accuracy

#### 2. Language Detector (`utils/language_detector.py`)
- **Purpose**: Detect script/language from text
- **Supported Languages**: English, Hindi (Devanagari), Arabic
- **Method**: Unicode range detection
- **Returns**: 'en', 'hi', 'ar', or 'multi' for mixed languages

#### 3. OCR Service (`ocr_service.py`)
- **Purpose**: Multilingual OCR processing using PaddleOCR
- **Features**:
  - Automatic language detection
  - Model caching per language
  - GPU acceleration support (optional)
  - Multi-page PDF support
  - Confidence scoring
  - Handwritten and printed text support
- **Languages**: English (en), Hindi (hi), Arabic (ar), Multilingual (ch)

#### 4. Field Mapper (`field_mapper.py`)
- **Purpose**: Extract structured fields from raw OCR text with multilingual support
- **Fields**: name, age, gender, phone, email, address, address_line1, address_line2, city, state, country
- **Method**: Multilingual regex patterns + keyword matching
- **Supported Keywords**: English, Hindi (Devanagari), Arabic

#### 5. Verifier Service (`verifier.py`)
- **Purpose**: Verify submitted fields against extracted fields
- **Method**: rapidfuzz fuzzy matching
- **Features**:
  - Field-by-field comparison
  - Overall verification score
  - Mismatch detection

#### 6. (Removed) Fallback Service
- **Status**: Removed - system is fully offline
  - `allow_fallback = true`
  - `FALLBACK_ALLOW = true`
  - Document confidence < 0.70 OR field confidence < 0.65

#### 7. Merge Service (`merge_service.py`)
- **Purpose**: Combine TrOCR and fallback results
- **Rules**:
  - TrOCR confidence >= 0.75 → use TrOCR
  - Else if fallback exists → use fallback
  - Else → normalize TrOCR

#### 8. Verifier (`verifier.py`)
- **Purpose**: Verify submitted fields against extracted fields
- **Method**: Fuzzy string matching (SequenceMatcher)

### API Routes

#### `/api/extract`
- Handles file uploads (images/PDFs)
- Supports demo mode
- Returns extracted fields with confidence scores

#### `/api/verify`
- Compares submitted vs extracted fields
- Returns match scores and mismatches

## Frontend Architecture

### Component Structure

```
App.jsx (Main State Management)
├── Navbar.jsx
├── UploadBox.jsx
├── ExtractedForm.jsx
│   ├── FieldConfidenceBar.jsx
│   └── AnimatedCard.jsx
├── VerificationPanel.jsx
└── LoaderSpinner.jsx
```

### State Flow

1. **Upload** → User uploads file or uses demo mode
2. **Extraction** → Backend processes document
3. **Form** → Auto-filled form with confidence scores
4. **Verification** → User submits → backend verifies
5. **Results** → Display verification results

### UI Libraries

- **Framer Motion**: Animations and transitions
- **TailwindCSS**: Styling
- **Lucide React**: Icons
- **Axios**: HTTP client

## Data Flow

```
User Upload
    ↓
Preprocessing
    ↓
Model Selection
    ↓
TrOCR OCR
    ↓
Field Extraction
    ↓
Confidence Calculation
    ↓
[Optional] Fallback Cleanup
    ↓
Result Merging
    ↓
Return to Frontend
    ↓
User Edits Form
    ↓
Verification
    ↓
Results Display
```

## Security Considerations

- CORS enabled for development (restrict in production)
- File uploads validated
- No sensitive data stored
- Local processing (no data sent to cloud unless fallback enabled)

## Performance Optimizations

- Model caching (TrOCR models loaded once)
- GPU acceleration when available
- Image preprocessing reduces OCR time
- Frontend code splitting (Vite)

## Scalability

- Stateless backend (can scale horizontally)
- Model loading can be optimized with model serving
- Frontend can be CDN-hosted
- Database can be added for result storage (future)


