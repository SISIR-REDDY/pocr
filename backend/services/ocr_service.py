"""
PaddleOCR multilingual OCR service.
Supports English, Hindi (Devanagari), Arabic, and mixed languages.
Handles both handwritten and printed text.
"""

from paddleocr import PaddleOCR
from PIL import Image
import numpy as np
import cv2
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import os
import sys

# Add parent directory to path for utils import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import setup_logger
from utils.language_detector import detect_language, get_paddleocr_lang_code
from services.preprocess import preprocess_image

logger = setup_logger("ocr_service")

# Global PaddleOCR instance cache (one per language)
_paddle_ocr_instances = {}
_initialized_languages = set()


def initialize_paddleocr(lang: str = 'en') -> Optional[PaddleOCR]:
    """
    Initialize PaddleOCR engine for specific language.
    
    Args:
        lang: Language code ('en', 'hi', 'ar', or 'ch' for multilingual)
        use_gpu: Whether to use GPU acceleration
        
    Returns:
        PaddleOCR instance or None if failed
    """
    global _paddle_ocr_instances, _initialized_languages
    
    # Check cache
    if lang in _paddle_ocr_instances:
        return _paddle_ocr_instances[lang]
    
    try:
        logger.info(f"Initializing PaddleOCR for language: {lang}")
        
        # Initialize PaddleOCR with minimal parameters - only lang is required
        # Newer PaddleOCR versions may not support use_gpu, show_log, use_angle_cls
        try:
            # Try with just language first (most compatible)
            ocr = PaddleOCR(lang=lang)
            logger.info(f"[OK] PaddleOCR initialized with lang={lang}")
        except Exception as e1:
            logger.warning(f"Initialization with lang failed: {e1}, trying alternative...")
            try:
                # Try with use_angle_cls if supported
                ocr = PaddleOCR(lang=lang, use_angle_cls=True)
                logger.info(f"[OK] PaddleOCR initialized with lang={lang}, use_angle_cls=True")
            except Exception as e2:
                logger.error(f"All PaddleOCR initialization attempts failed: {e2}")
                return None
        
        _paddle_ocr_instances[lang] = ocr
        _initialized_languages.add(lang)
        logger.info(f"[OK] PaddleOCR initialized successfully for {lang}")
        
        return ocr
        
    except Exception as e:
        logger.error(f"Failed to initialize PaddleOCR for {lang}: {e}", exc_info=True)
        return None


def detect_handwriting(image: Image.Image) -> bool:
    """
    Simple heuristic to detect if text is handwritten.
    This is a basic implementation - can be enhanced with ML models.
    
    Args:
        image: PIL Image
        
    Returns:
        True if likely handwritten, False if likely printed
    """
    try:
        # Convert to numpy array
        img_array = np.array(image)
        
        # Basic heuristic: handwritten text often has more variation
        # in stroke width and less uniform spacing
        # For now, return False (assume printed) - can be enhanced
        # In production, you might use a separate handwriting detection model
        
        return False  # Default to printed
    except Exception:
        return False


def extract_text_from_image(
    image: Image.Image,
    language: Optional[str] = None,
    return_detailed: bool = False
) -> Dict:
    """
    Extract text from image using PaddleOCR with multilingual support.
    
    Processing pipeline:
    1. Preprocess image
    2. Detect language (if not provided)
    3. Select appropriate PaddleOCR model
    4. Run OCR
    5. Extract and merge text
    
    Args:
        image: PIL Image
        language: Optional language code ('en', 'hi', 'ar', 'multi')
                  If None, will auto-detect from image
        return_detailed: Whether to return detailed box information
        
    Returns:
        Dict with keys:
        - raw_text: Combined text from all detections
        - avg_confidence: Average confidence score
        - line_count: Number of text lines detected
        - boxes: List of text boxes with coordinates (if return_detailed=True)
        - language_detected: Detected language code
        - error: Error message if any
    """
    try:
        # Step 1: Preprocess image (skip for now to test if preprocessing is the issue)
        logger.info("Skipping preprocessing for testing - using original image")
        logger.info(f"[DEBUG] Original image size: {image.size}, mode: {image.mode}")
        processed_image = image
        previews = {}
        
        # TODO: Re-enable preprocessing once OCR is working
        # try:
        #     processed_image, previews = preprocess_image(image)
        #     logger.info(f"[OK] Image preprocessed - new size: {processed_image.size}, mode: {processed_image.mode}")
        # except Exception as e:
        #     logger.warning(f"Preprocessing failed: {e}, using original image")
        #     processed_image = image
        #     previews = {}
        
        # Step 2: Detect language (if not provided)
        if language is None:
            # Run initial OCR with multilingual model to detect language
            logger.info("Detecting language...")
            ocr_multi = initialize_paddleocr('ch')  # 'ch' = multilingual
            if ocr_multi:
                img_array = np.array(processed_image)
                if processed_image.mode != "RGB":
                    processed_image = processed_image.convert("RGB")
                    img_array = np.array(processed_image)
                
                # Use RGB directly for PaddleOCR (no BGR conversion needed)
                img_array_rgb = img_array
                
                # Quick OCR to get sample text for language detection
                try:
                    try:
                        result = ocr_multi.ocr(img_array_rgb, cls=True)
                    except (TypeError, ValueError):
                        result = ocr_multi.ocr(img_array_rgb)
                    
                    sample_text = ""
                    if result and result[0]:
                        ocr_result = result[0]
                        logger.info(f"[DEBUG] Language detection - ocr_result type: {type(ocr_result)}")
                        
                        # Handle OCRResult object format (PaddleX/PaddleOCR newer version)
                        try:
                            # Try to access rec_texts attribute
                            if hasattr(ocr_result, 'rec_texts'):
                                rec_texts = ocr_result.rec_texts
                                logger.info(f"[DEBUG] Found rec_texts attribute with {len(rec_texts) if rec_texts else 0} items")
                                if rec_texts:
                                    # Get first 5 text items
                                    sample_list = rec_texts[:5] if len(rec_texts) > 5 else rec_texts
                                    sample_text = " ".join([str(t).strip() for t in sample_list if t and str(t).strip()])
                                    logger.info(f"[DEBUG] Extracted sample text for language detection: {sample_text[:100]}")
                            # Try dict-like access
                            elif isinstance(ocr_result, dict) and 'rec_texts' in ocr_result:
                                rec_texts = ocr_result['rec_texts']
                                if rec_texts:
                                    sample_list = rec_texts[:5] if len(rec_texts) > 5 else rec_texts
                                    sample_text = " ".join([str(t).strip() for t in sample_list if t and str(t).strip()])
                            # Try list format (standard PaddleOCR)
                            elif isinstance(ocr_result, list):
                                logger.info(f"[DEBUG] Using list format with {len(ocr_result)} items")
                                for line in ocr_result[:5]:  # Check first 5 lines
                                    if line and len(line) >= 2:
                                        text_info = line[1]
                                        if isinstance(text_info, (list, tuple)) and len(text_info) >= 1:
                                            sample_text += str(text_info[0]) + " "
                            else:
                                # Try to get text from string representation or other attributes
                                logger.warning(f"[DEBUG] Unknown OCRResult format, trying to extract text from: {type(ocr_result)}")
                                # Try common attribute names
                                for attr_name in ['text', 'texts', 'result', 'output']:
                                    if hasattr(ocr_result, attr_name):
                                        attr_value = getattr(ocr_result, attr_name)
                                        if isinstance(attr_value, list) and attr_value:
                                            sample_text = " ".join([str(t) for t in attr_value[:5] if t])
                                            break
                        except Exception as e:
                            logger.warning(f"Error extracting text for language detection: {e}, will default to English")
                            sample_text = ""
                    
                    if sample_text:
                        language = detect_language(sample_text)
                        logger.info(f"Language detected from sample: {language}")
                    else:
                        language = 'en'  # Default
                        logger.info("No text found for language detection, defaulting to English")
                except Exception as e:
                    logger.warning(f"Language detection failed: {e}, defaulting to English")
                    language = 'en'
            else:
                language = 'en'  # Default fallback
        else:
            logger.info(f"Using provided language: {language}")
        
        # Step 3: Get PaddleOCR language code
        paddle_lang = get_paddleocr_lang_code(language)
        logger.info(f"Using PaddleOCR language code: {paddle_lang}")
        
        # Step 4: Initialize appropriate OCR model
        ocr = initialize_paddleocr(paddle_lang)
        if ocr is None:
            return {
                "raw_text": "",
                "avg_confidence": 0.0,
                "line_count": 0,
                "language_detected": language or 'en',
                "error": "PaddleOCR initialization failed"
            }
        
        # Step 5: Ensure image is RGB
        if processed_image.mode != "RGB":
            processed_image = processed_image.convert("RGB")
        
        # Step 6: Convert PIL Image to numpy array
        # PaddleOCR expects numpy array in BGR format (OpenCV format)
        img_array = np.array(processed_image)
        logger.info(f"[DEBUG] Image array shape after conversion: {img_array.shape}")
        logger.info(f"[DEBUG] Image array dtype: {img_array.dtype}")
        
        # PaddleOCR can accept RGB directly (numpy array from PIL)
        # No need to convert to BGR - PaddleOCR handles RGB numpy arrays
        logger.info("[DEBUG] Using RGB format for PaddleOCR (no BGR conversion needed)")
        
        # Step 7: Run OCR
        logger.info(f"Running PaddleOCR text detection and recognition (lang={paddle_lang})...")
        logger.info(f"[DEBUG] Image array shape: {img_array.shape if hasattr(img_array, 'shape') else 'unknown'}")
        logger.info(f"[DEBUG] Image array dtype: {img_array.dtype if hasattr(img_array, 'dtype') else 'unknown'}")
        logger.info(f"[DEBUG] Image array min/max: {img_array.min()}/{img_array.max() if hasattr(img_array, 'min') else 'unknown'}")
        
        try:
            # Try with cls parameter first (angle classification)
            logger.info("[DEBUG] Attempting OCR with cls=True...")
            result = ocr.ocr(img_array, cls=True)
            logger.info(f"[DEBUG] OCR result type: {type(result)}")
            logger.info(f"[DEBUG] OCR result length: {len(result) if result else 0}")
            if result:
                logger.info(f"[DEBUG] OCR result[0] type: {type(result[0])}")
                logger.info(f"[DEBUG] OCR result[0] length: {len(result[0]) if result[0] else 0}")
        except (TypeError, ValueError) as e:
            # If cls parameter not supported, run without it
            logger.warning(f"cls parameter not supported: {e}, running OCR without angle classification")
            try:
                result = ocr.ocr(img_array)
                logger.info(f"[DEBUG] OCR result (no cls) type: {type(result)}")
                logger.info(f"[DEBUG] OCR result (no cls) length: {len(result) if result else 0}")
            except Exception as e2:
                logger.error(f"OCR call failed completely: {e2}", exc_info=True)
                return {
                    "raw_text": "",
                    "avg_confidence": 0.0,
                    "line_count": 0,
                    "language_detected": language or 'en',
                    "error": f"OCR execution failed: {str(e2)}"
                }
        except Exception as e:
            logger.error(f"Unexpected error during OCR: {e}", exc_info=True)
            return {
                "raw_text": "",
                "avg_confidence": 0.0,
                "line_count": 0,
                "language_detected": language or 'en',
                "error": f"OCR execution failed: {str(e)}"
            }
        
        if not result:
            logger.warning("OCR returned None")
            logger.warning(f"Image shape: {img_array.shape if hasattr(img_array, 'shape') else 'unknown'}")
            return {
                "raw_text": "",
                "avg_confidence": 0.0,
                "line_count": 0,
                "language_detected": language or 'en',
                "error": "OCR returned no result. Please check the image format and content."
            }
        
        # Log the actual result structure
        logger.info(f"[DEBUG] Full OCR result: {result}")
        logger.info(f"[DEBUG] result[0] type: {type(result[0])}")
        logger.info(f"[DEBUG] result[0] value: {result[0]}")
        logger.info(f"[DEBUG] result[0] length: {len(result[0]) if result[0] else 0}")
        
        if not result[0]:
            logger.warning("OCR returned empty result list")
            logger.warning(f"OCR result structure: {result}")
            logger.warning(f"Image shape: {img_array.shape if hasattr(img_array, 'shape') else 'unknown'}")
            return {
                "raw_text": "",
                "avg_confidence": 0.0,
                "line_count": 0,
                "language_detected": language or 'en',
                "error": "No text detected in image. Please ensure the image contains clear, readable text."
            }
        
        # Step 8: Parse results
        text_lines = []
        confidences = []
        boxes = []
        
        ocr_result = result[0]
        logger.info(f"[DEBUG] ocr_result type: {type(ocr_result)}")
        
        # Handle different PaddleOCR result formats
        # Format 1: OCRResult object (newer PaddleOCR/PaddleX)
        if hasattr(ocr_result, 'rec_texts') or (isinstance(ocr_result, dict) and 'rec_texts' in ocr_result):
            # It's an OCRResult object or dict-like
            try:
                if hasattr(ocr_result, 'rec_texts'):
                    rec_texts = ocr_result.rec_texts
                    rec_scores = getattr(ocr_result, 'rec_scores', None)
                    rec_boxes = getattr(ocr_result, 'rec_boxes', None)
                else:
                    rec_texts = ocr_result.get('rec_texts', [])
                    rec_scores = ocr_result.get('rec_scores', None)
                    rec_boxes = ocr_result.get('rec_boxes', None)
                
                logger.info(f"[DEBUG] Found OCRResult format with {len(rec_texts) if rec_texts else 0} text lines")
                
                if rec_texts:
                    for i, text in enumerate(rec_texts):
                        if text and str(text).strip():
                            text_lines.append(str(text).strip())
                            if rec_scores and i < len(rec_scores):
                                confidences.append(float(rec_scores[i]))
                            else:
                                confidences.append(0.8)  # Default confidence
                            
                            if return_detailed and rec_boxes and i < len(rec_boxes):
                                box = rec_boxes[i]
                                if hasattr(box, 'tolist'):
                                    box = box.tolist()
                                boxes.append({
                                    "text": str(text).strip(),
                                    "confidence": float(rec_scores[i]) if rec_scores and i < len(rec_scores) else 0.8,
                                    "bbox": box
                                })
            except Exception as e:
                logger.warning(f"Error parsing OCRResult format: {e}, trying list format")
                # Fall through to list format handling
        
        # Format 2: List format (standard PaddleOCR) [[[x1,y1],[x2,y2],[x3,y3],[x4,y4]], (text, confidence)]
        if not text_lines and isinstance(ocr_result, list):
            logger.info(f"[DEBUG] Using list format with {len(ocr_result)} items")
            for line in ocr_result:
                if line and len(line) >= 2:
                    box = line[0]  # Bounding box coordinates
                    text_info = line[1]  # (text, confidence)
                    
                    if isinstance(text_info, (list, tuple)) and len(text_info) >= 2:
                        text, confidence = str(text_info[0]), float(text_info[1])
                    else:
                        text = str(text_info)
                        confidence = 0.5
                    
                    if text and text.strip():
                        text_lines.append(text.strip())
                        confidences.append(confidence)
                        
                        if return_detailed:
                            boxes.append({
                                "text": text.strip(),
                                "confidence": confidence,
                                "bbox": box
                            })
        
        # Format 3: Try to access as dict if it has text-related keys
        if not text_lines and isinstance(ocr_result, dict):
            logger.info("[DEBUG] Trying dict format")
            # Try common keys
            for key in ['text', 'texts', 'rec_text', 'rec_texts', 'result']:
                if key in ocr_result:
                    value = ocr_result[key]
                    if isinstance(value, list):
                        text_lines.extend([str(t).strip() for t in value if t and str(t).strip()])
                    elif value:
                        text_lines.append(str(value).strip())
        
        # Step 9: Merge text into intelligent structured lines
        # Group nearby text boxes into lines
        merged_text = "\n".join(text_lines)
        avg_confidence = float(np.mean(confidences)) if confidences else 0.0
        
        logger.info(f"Extracted {len(text_lines)} text lines, {len(merged_text)} characters")
        logger.info(f"Average confidence: {avg_confidence:.2f}")
        logger.info(f"Language detected: {language or 'en'}")
        
        result_dict = {
            "raw_text": merged_text,
            "avg_confidence": avg_confidence,
            "line_count": len(text_lines),
            "language_detected": language or 'en',
            "error": None
        }
        
        if return_detailed:
            result_dict["boxes"] = boxes
        
        return result_dict
        
    except Exception as e:
        logger.error(f"OCR extraction failed: {e}", exc_info=True)
        return {
            "raw_text": "",
            "avg_confidence": 0.0,
            "line_count": 0,
            "language_detected": language or 'en',
            "error": f"OCR extraction failed: {str(e)}"
        }


def extract_text_from_pdf(
    pdf_path: str,
    language: Optional[str] = None
) -> Dict:
    """
    Extract text from PDF using PaddleOCR (multi-page).
    
    Args:
        pdf_path: Path to PDF file
        language: Optional language code
        
    Returns:
        Dict with extracted text from all pages
    """
    try:
        from pdf2image import convert_from_path
    except ImportError:
        return {
            "raw_text": "",
            "avg_confidence": 0.0,
            "page_count": 0,
            "line_count": 0,
            "language_detected": language or 'en',
            "error": "PDF support requires pdf2image and poppler"
        }
    
    try:
        logger.info(f"Converting PDF to images: {pdf_path}")
        pages = convert_from_path(pdf_path, dpi=300)
        
        all_text = []
        all_confidences = []
        total_lines = 0
        detected_language = language
        
        for page_num, page_image in enumerate(pages):
            logger.info(f"Processing page {page_num + 1}/{len(pages)}")
            result = extract_text_from_image(page_image, language=detected_language)
            
            if result.get("error"):
                logger.warning(f"Page {page_num + 1} extraction failed: {result['error']}")
                continue
            
            # Use detected language from first page for subsequent pages
            if page_num == 0 and not detected_language:
                detected_language = result.get("language_detected", 'en')
            
            all_text.append(result["raw_text"])
            all_confidences.append(result["avg_confidence"])
            total_lines += result["line_count"]
        
        combined_text = "\n\n".join(all_text)
        avg_confidence = float(np.mean(all_confidences)) if all_confidences else 0.0
        
        logger.info(f"PDF extraction complete: {len(pages)} pages, {total_lines} lines")
        
        return {
            "raw_text": combined_text,
            "avg_confidence": avg_confidence,
            "page_count": len(pages),
            "line_count": total_lines,
            "language_detected": detected_language or 'en',
            "error": None
        }
        
    except Exception as e:
        logger.error(f"PDF extraction failed: {e}", exc_info=True)
        return {
            "raw_text": "",
            "avg_confidence": 0.0,
            "page_count": 0,
            "line_count": 0,
            "language_detected": language or 'en',
            "error": f"PDF extraction failed: {str(e)}"
        }

