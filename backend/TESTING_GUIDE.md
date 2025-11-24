# Testing Guide - Real File Uploads

## System Status
- ✅ Demo mode: REMOVED
- ✅ Real file uploads: REQUIRED
- ✅ Field extraction: Optimized for real OCR data

## How to Test

1. **Start the servers:**
   - Backend: `python backend/main.py` (port 8000)
   - Frontend: `npm run dev` in frontend folder (port 3000)

2. **Upload a document:**
   - Open http://localhost:3000
   - Drag & drop or click to upload an image (PNG, JPG, JPEG) or PDF
   - Click "Extract Information"

3. **Expected behavior:**
   - System processes the file with PaddleOCR
   - Extracts text in English, Hindi, or Arabic
   - Automatically fills form fields:
     - Name
     - Age
     - Gender
     - Phone
     - Email
     - Address
     - City
     - State
     - Country

## Field Extraction Patterns

The system uses intelligent regex patterns to extract fields from OCR text:

- **Name**: Looks for "Name:", "Full Name:", capitalized words
- **Age**: Looks for "Age:", numbers 1-150
- **Gender**: Looks for "Gender:", "Male", "Female", etc.
- **Phone**: Looks for phone number patterns (10-15 digits)
- **Email**: Looks for email patterns
- **Address**: Looks for "Address:", street names, numbers
- **City/State/Country**: Looks for labeled fields

## Supported Languages
- English (en)
- Hindi/Devanagari (hi)
- Arabic (ar)
- Mixed languages

## Troubleshooting

If fields are not extracting:
1. Check backend logs: `backend/logs/app.log`
2. Verify OCR extracted text in the response
3. Ensure document has clear, readable text
4. Check language detection is working

