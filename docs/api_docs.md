# API Documentation

## Base URL

```
http://localhost:8000
```

## Endpoints

### 1. Health Check

**GET** `/`

**GET** `/health`

**Response:** 
```json
{
  "status": "ok",
  "service": "MOSIP OCR API (PaddleOCR Multilingual)",
  "version": "3.0.0",
  "models": {
    "languages": ["en", "hi", "ar", "ch"],
    "status": "ready"
  },
  "offline": true,
  "supported_languages": ["en", "hi", "ar", "multi"]
}
```

---

### 2. Extract Fields

**POST** `/api/extract`

Extract structured fields from uploaded image or PDF.

**Request:**
- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `file` (file, optional): Image or PDF file
  - `demo_mode` (boolean, default: false): Use sample PDF (mosip_sample.pdf or sample.pdf)

**Example (cURL):**
```bash
curl -X POST http://localhost:8000/api/extract \
  -F "file=@document.pdf" \
  -F "demo_mode=false"
```

**Example (Demo Mode):**
```bash
curl -X POST http://localhost:8000/api/extract \
  -F "demo_mode=true"
```

**Response (Success):**
```json
{
  "success": true,
  "fields": {
    "name": "John Doe",
    "age": "30",
    "gender": "Male",
    "phone": "+1234567890",
    "email": "john@example.com",
    "address": "123 Main St\nCity, State 12345",
    "address_line1": "123 Main St",
    "address_line2": null,
    "city": "City",
    "state": "State",
    "country": null
  },
  "field_confidences": {
    "name": 0.8,
    "age": 0.8,
    "gender": 0.8,
    "phone": 0.8,
    "email": 0.8,
    "address": 0.8
  },
  "confidence": 0.85,
  "raw_text": "Full extracted text...",
  "language_detected": "en",
  "previews": {
    "grayscale": "base64...",
    "denoised": "base64...",
    ...
  }
}
```

**Response (Error):**
```json
{
  "detail": "Error message here"
}
```

**Status Codes:**
- `200`: Success
- `400`: Bad request (missing file, invalid format)
- `404`: Sample PDF not found (demo mode)
- `500`: Server error

---

### 3. Verify Fields

**POST** `/api/verify`

Verify submitted fields against extracted fields using fuzzy matching.

**Request:**
```json
{
  "submitted_fields": {
    "name": "John Doe",
    "age": "30",
    "gender": "Male",
    "phone": "+1234567890",
    "email": "john@example.com",
    "address": "123 Main St, City, State 12345"
  },
  "extracted_fields": {
    "name": "John Doe",
    "age": "30",
    "gender": "Male",
    "phone": "+1234567890",
    "email": "john@example.com",
    "address": "123 Main St\nCity, State 12345"
  }
}
```

**Example (cURL):**
```bash
curl -X POST http://localhost:8000/api/verify \
  -H "Content-Type: application/json" \
  -d '{
    "submitted_fields": {
      "name": "John Doe",
      "age": "30"
    },
    "extracted_fields": {
      "name": "John Doe",
      "age": "30"
    }
  }'
```

**Response (Success):**
```json
{
  "success": true,
  "matches": {
    "name": 1.0,
    "age": 1.0,
    "gender": 0.95,
    "phone": 0.98,
    "email": 1.0,
    "address": 0.92
  },
  "mismatches": [
    {
      "field": "address",
      "submitted": "123 Main St, City, State 12345",
      "extracted": "123 Main St\nCity, State 12345",
      "match_score": 0.92
    }
  ],
  "overall_score": 0.97,
  "verification_passed": true
}
```

**Response Fields:**
- `matches`: Dictionary of field → match score (0.0 to 1.0)
- `mismatches`: Array of fields with match_score < 0.8
- `overall_score`: Average of all match scores
- `verification_passed`: true if overall_score >= 0.85 and no mismatches

**Status Codes:**
- `200`: Success
- `400`: Bad request (missing fields)
- `500`: Server error

---

## Field Definitions

### Extracted Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `name` | string | Full name | "John Doe" |
| `age` | string | Age in years | "30" |
| `gender` | string | Gender | "Male", "Female", "Other" |
| `phone` | string | Phone number | "+1234567890" |
| `email` | string | Email address | "john@example.com" |
| `address` | string | Multi-line address | "123 Main St\nCity, State" |

### Confidence Scores

- Range: `0.0` to `1.0`
- `>= 0.8`: High confidence (green)
- `>= 0.6`: Medium confidence (yellow)
- `< 0.6`: Low confidence (red)

---

## Error Handling

All errors follow this format:

```json
{
  "detail": "Error message"
}
```

Common errors:
- `"No file provided"`: Missing file in upload
- `"Sample PDF not found"`: Demo mode but sample PDF missing
- `"Extraction failed: ..."`: OCR processing error
- `"Verification failed: ..."`: Verification processing error

---

## Rate Limiting

Currently no rate limiting. For production, implement:
- Per-IP rate limiting
- Request size limits
- Timeout handling

---

## CORS

CORS is enabled for all origins in development. For production:
- Set specific allowed origins
- Configure credentials if needed

---

## Authentication

Currently no authentication. For production:
- Add API key authentication
- Implement JWT tokens
- Add user sessions


