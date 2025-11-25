"""
Extraction route: handles OCR extraction requests.
Returns stable JSON responses even on partial failure.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import sys
import tempfile
from PIL import Image
from utils.logger import setup_logger, log_ocr_result, log_field_extraction, log_error_with_traceback

# Add parent directory to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from services.preprocess import preprocess_image
from services.ocr_service import extract_text_from_image, extract_text_from_pdf
from services.field_mapper import extract_all_fields, normalize_text

logger = setup_logger("extract_route")

router = APIRouter(prefix="/api/extract", tags=["extract"])


def create_error_response(error_message: str, debug_info: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Create a stable error response.
    
    Args:
        error_message: Error message
        debug_info: Optional debug information
        
    Returns:
        Error response dict
    """
    response = {
        "success": False,
        "fields": {},
        "error": error_message,
        "confidence": 0.0,
        "raw_text": "",
        "debug": debug_info or {}
    }
    return response


# Removed create_success_response - now handled inline in extract_fields


@router.post("")
async def extract_fields(
    file: Optional[UploadFile] = File(None)
):
    """
    Extract fields from uploaded image/PDF.
    
    Supports:
    - Image uploads (PNG, JPG, JPEG)
    - PDF uploads
    
    Returns stable JSON even on partial failure.
    """
    debug_info = {}
    
    try:
        # Initialize variables
        image = None
        raw_text = ""
        ocr_confidence = 0.0
        language_detected = "en"
        ocr_error = None
        
        # Handle file upload - file is required
        if not file:
            return create_error_response(
                "No file provided. Please upload an image or PDF file.",
                {"file_provided": False}
            )
        
        logger.info(f"Processing file: {file.filename}")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
            content = await file.read()
            
            # DEBUG: Check file upload
            logger.info(f"[DEBUG] Received file: {file.filename}")
            logger.info(f"[DEBUG] File size: {len(content)} bytes")
            logger.info(f"[DEBUG] Content type: {file.content_type}")
            
            if len(content) == 0:
                logger.error("[ERROR] File content is empty!")
                return create_error_response(
                    "File upload failed: file is empty",
                    {"file_provided": True, "file_size": 0}
                )
            
            tmp_file.write(content)
            tmp_path = tmp_file.name
            logger.info(f"[DEBUG] Saved temp file to: {tmp_path}")
        
        try:
            # Determine file type
            file_ext = os.path.splitext(file.filename)[1].lower()
            
            if file_ext == ".pdf":
                # Handle PDF
                logger.info("Processing PDF file")
                ocr_result = extract_text_from_pdf(tmp_path)
                raw_text = ocr_result.get("raw_text", "")
                ocr_confidence = ocr_result.get("avg_confidence", 0.0)
                language_detected = ocr_result.get("language_detected", "en")
                ocr_error = ocr_result.get("error")
                
                if ocr_error:
                    logger.warning(f"PDF extraction error: {ocr_error}")
                    return create_error_response(
                        f"Text could not be extracted from PDF: {ocr_error}",
                        {"file_type": "pdf", "ocr_error": ocr_error}
                    )
                
            else:
                # Handle image
                logger.info("Processing image file")
                try:
                    image = Image.open(tmp_path)
                    if image.mode != "RGB":
                        image = image.convert("RGB")
                except Exception as e:
                    log_error_with_traceback(logger, e, "Image opening")
                    return create_error_response(
                        f"Failed to open image: {str(e)}",
                        {"file_type": "image", "error": str(e)}
                    )
                
                # Extract text using PaddleOCR (preprocessing is handled inside OCR service)
                logger.info(f"[DEBUG] Original image size: {image.size}, mode: {image.mode}")
                logger.info("[DEBUG] Calling PaddleOCR multilingual OCR")
                # Pass original image - preprocessing will be done inside OCR service
                ocr_result = extract_text_from_image(image)
                raw_text = ocr_result.get("raw_text", "")
                ocr_confidence = ocr_result.get("avg_confidence", 0.0)
                language_detected = ocr_result.get("language_detected", "en")
                ocr_error = ocr_result.get("error")
                
                # DEBUG: Print raw OCR text
                logger.info("=" * 60)
                logger.info("=== OCR RAW TEXT START ===")
                logger.info(f"Raw OCR Text: {repr(raw_text)}")
                logger.info(f"Text Length: {len(raw_text)}")
                logger.info(f"Language Detected: {language_detected}")
                logger.info(f"Text Preview: {raw_text[:200] if raw_text else '(empty)'}")
                logger.info("=== OCR RAW TEXT END ===")
                logger.info("=" * 60)
                
                if ocr_error:
                    logger.warning(f"OCR extraction error: {ocr_error}")
                    return create_error_response(
                        f"Text could not be extracted: {ocr_error}",
                        {"file_type": "image", "ocr_error": ocr_error, **debug_info}
                    )
                
                log_ocr_result(logger, len(raw_text), ocr_confidence, language_detected)
                
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass
        
        # Normalize raw text
        logger.info(f"[DEBUG] Raw text before normalization: {repr(raw_text[:100])}")
        if raw_text:
            raw_text = normalize_text(raw_text)
            logger.info(f"[DEBUG] Raw text after normalization: {repr(raw_text[:100])}")
        
        # Extract fields with multilingual support
        logger.info(f"[DEBUG] Extracting fields from text (length: {len(raw_text)}, language: {language_detected})")
        try:
            field_result = extract_all_fields(raw_text, language=language_detected)
            # Handle both old format (dict) and new format (dict with "fields" key)
            if isinstance(field_result, dict) and "fields" in field_result:
                fields = field_result.get("fields", {})
                field_confidences = field_result.get("confidence_scores", {})
            else:
                # Old format - field_result is the fields dict directly
                fields = field_result
                field_confidences = {}
            
            # Filter out None/null values - only keep extracted fields
            fields = {k: v for k, v in fields.items() if v is not None and v != ""}
            
            logger.info(f"[DEBUG] Extracted fields (after filtering): {fields}")
            logger.info(f"[DEBUG] Number of fields extracted: {len(fields)}")
            log_field_extraction(logger, fields, field_confidences)
        except Exception as e:
            log_error_with_traceback(logger, e, "Field extraction")
            fields = {}  # Empty dict - no fields extracted
            field_confidences = {}
        
        # Create response
        if not raw_text:
            error_msg = "Text could not be extracted from the document"
            if ocr_error:
                error_msg = f"OCR extraction failed: {ocr_error}"
            elif ocr_confidence == 0.0:
                error_msg = "No text detected in the image. Please ensure the image contains clear, readable text."
            else:
                error_msg = "Text extraction returned empty result. The image may not contain readable text."
            
            logger.warning(f"Extraction failed: {error_msg}")
            logger.warning(f"OCR confidence: {ocr_confidence}, Language: {language_detected}")
            return create_error_response(
                error_msg,
                {
                    "ocr_confidence": ocr_confidence, 
                    "language_detected": language_detected,
                    "ocr_error": ocr_error,
                    **debug_info
                }
            )
        
        # Calculate overall confidence
        overall_confidence = ocr_confidence
        if field_confidences:
            avg_field_confidence = sum(field_confidences.values()) / len(field_confidences) if field_confidences else 0.0
            overall_confidence = (ocr_confidence + avg_field_confidence) / 2.0
        
        response = {
            "success": True,
            "fields": fields,
            "confidence": overall_confidence,
            "raw_text": raw_text,
            "language_detected": language_detected,
            "field_confidences": field_confidences,
            "debug": debug_info or {}
        }
        
        return response
        
    except Exception as e:
        log_error_with_traceback(logger, e, "Extraction route")
        return create_error_response(
            f"Extraction failed: {str(e)}",
            {"exception_type": type(e).__name__, **debug_info}
        )
