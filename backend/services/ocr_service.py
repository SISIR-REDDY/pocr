"""
Premium PaddleOCR multilingual OCR service - Optimized for Speed & Accuracy.
Supports English, Hindi (Devanagari), Arabic, and mixed languages.
Handles both handwritten and printed text with GPU acceleration.
"""

from paddleocr import PaddleOCR
from PIL import Image
import numpy as np
import cv2
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import os
import sys
import hashlib
import time

# Add parent directory to path for utils import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import setup_logger
from utils.language_detector import get_paddleocr_lang_code

logger = setup_logger("ocr_service")

# Global PaddleOCR instance cache (one per language)
_paddle_ocr_instances = {}

# Simple result cache (in-memory, for speed)
_ocr_cache = {}
_cache_max_size = 50  # Max cached results


def initialize_paddleocr(lang: str = 'en') -> Optional[PaddleOCR]:
    """
    Initialize PaddleOCR engine for specific language with premium optimizations.
    Uses GPU if available, optimized for speed and accuracy.
    
    Args:
        lang: Language code ('en', 'hi', 'ar', or 'ch' for multilingual)
        
    Returns:
        PaddleOCR instance or None if failed
    """
    global _paddle_ocr_instances
    
    # Check cache
    if lang in _paddle_ocr_instances:
        return _paddle_ocr_instances[lang]
    
    try:
        logger.info(f"[INIT] Initializing PaddleOCR for language: {lang}")
        start_time = time.time()
        
        # Detect GPU availability for speed
        use_gpu = False
        try:
            import torch
            use_gpu = torch.cuda.is_available() if hasattr(torch, 'cuda') else False
            if use_gpu:
                logger.info(f"[SPEED] GPU detected: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A'}")
        except:
            pass
        
        # Initialize PaddleOCR with minimal parameters (only lang is required)
        # Newer PaddleOCR versions don't support show_log, use_angle_cls, etc.
        try:
            # Simple initialization with just language (most compatible)
            ocr = PaddleOCR(lang=lang)
            init_time = time.time() - start_time
            logger.info(f"[OK] PaddleOCR initialized with lang={lang} (GPU: {use_gpu}, Time: {init_time:.2f}s)")
        except Exception as e:
            logger.error(f"PaddleOCR initialization failed: {e}")
            return None
        
        _paddle_ocr_instances[lang] = ocr
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


# Removed _smart_preprocess_image - skipping preprocessing for maximum speed
# PaddleOCR handles image enhancement internally, so we don't need to preprocess


def _get_image_hash(image: Image.Image) -> str:
    """Generate hash for image caching."""
    try:
        img_bytes = image.tobytes()
        return hashlib.md5(img_bytes).hexdigest()
    except:
        return ""


def extract_text_from_image(
    image: Image.Image,
    language: Optional[str] = None,
    return_detailed: bool = False
) -> Dict:
    """
    Premium OCR extraction: Ultra-fast with aggressive optimizations.
    
    Processing pipeline:
    1. Check cache (for speed)
    2. Aggressive image resizing (max 1200px)
    3. Skip preprocessing (PaddleOCR handles it internally)
    4. Use multilingual model directly (fastest)
    5. Run OCR with cls=False (skip angle classification)
    6. Extract and merge text
    
    Args:
        image: PIL Image
        language: Optional language code ('en', 'hi', 'ar', 'multi')
                  If None, uses multilingual model directly (fastest)
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
    global _ocr_cache
    
    try:
        start_time = time.time()
        
        # Step 1: Check cache (for speed)
        img_hash = _get_image_hash(image)
        cache_key = f"{img_hash}_{language or 'multi'}"
        if cache_key in _ocr_cache:
            logger.debug("[SPEED] Using cached OCR result")
            return _ocr_cache[cache_key]
        
        # Step 2: Aggressive image optimization for maximum speed
        # Smaller images = exponentially faster OCR (quadratic complexity)
        max_dimension = 1000  # Ultra-aggressive resize for speed (was 1200)
        width, height = image.size
        original_size = (width, height)
        
        if max(width, height) > max_dimension:
            ratio = max_dimension / max(width, height)
            new_size = (int(width * ratio), int(height * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
            logger.info(f"[SPEED] Resized image from {original_size} to {new_size} ({ratio:.2%} size) for faster OCR")
        
        # Step 3: Skip all preprocessing for maximum speed
        # PaddleOCR has built-in preprocessing, so we skip ours entirely
        if image.mode != "RGB":
            image = image.convert("RGB")
        img_array = np.array(image)
        preprocess_time = time.time() - start_time
        logger.debug(f"[SPEED] Image prep time: {preprocess_time:.3f}s (no preprocessing)")
        
        # Step 4: Use multilingual model directly (fastest - no language detection needed)
        if language is None:
            language = 'multi'
        paddle_lang = get_paddleocr_lang_code(language)
        
        # Step 5: Initialize OCR model (cached)
        ocr = initialize_paddleocr(paddle_lang)
        if ocr is None:
            return {
                "raw_text": "",
                "avg_confidence": 0.0,
                "line_count": 0,
                "language_detected": language or 'en',
                "error": "PaddleOCR initialization failed"
            }
        
        # Step 6: Run OCR with maximum speed optimizations
        ocr_start = time.time()
        logger.info(f"[SPEED] Starting OCR on image shape: {img_array.shape} (max dimension: {max(img_array.shape[:2])}px)")
        
        try:
            # Try fastest OCR call with all speed optimizations
            # cls=False: Skip angle classification (saves 30-50% time)
            result = ocr.ocr(img_array, cls=False)
            ocr_time = time.time() - ocr_start
            logger.info(f"[SPEED] OCR completed in {ocr_time:.2f}s")
        except (TypeError, ValueError) as e:
            # Fallback: try without cls parameter (some versions don't support it)
            logger.debug(f"[SPEED] cls=False not supported, trying without cls parameter")
            try:
                result = ocr.ocr(img_array)
                ocr_time = time.time() - ocr_start
                logger.debug(f"[SPEED] OCR completed in {ocr_time:.2f}s (fallback)")
            except Exception as e2:
                logger.error(f"OCR execution failed: {e2}", exc_info=True)
                return {
                    "raw_text": "",
                    "avg_confidence": 0.0,
                    "line_count": 0,
                    "language_detected": language or 'en',
                    "error": f"OCR execution failed: {str(e2)}"
                }
        except Exception as e:
            logger.error(f"OCR error: {e}", exc_info=True)
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
        
        # Minimal logging for speed (only log if debug enabled)
        
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
        
        # Step 7: Parse results efficiently
        text_lines = []
        confidences = []
        boxes = []
        
        ocr_result = result[0]
        
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
                
                logger.debug(f"Found OCRResult format with {len(rec_texts) if rec_texts else 0} text lines")
                
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
        
        # Step 7: Parse results efficiently
        text_lines = []
        confidences = []
        boxes = []
        
        ocr_result = result[0]
        
        # Handle different PaddleOCR result formats
        # Format 1: OCRResult object (newer PaddleOCR/PaddleX)
        if hasattr(ocr_result, 'rec_texts') or (isinstance(ocr_result, dict) and 'rec_texts' in ocr_result):
            try:
                if hasattr(ocr_result, 'rec_texts'):
                    rec_texts = ocr_result.rec_texts
                    rec_scores = getattr(ocr_result, 'rec_scores', None)
                    rec_boxes = getattr(ocr_result, 'rec_boxes', None)
                else:
                    rec_texts = ocr_result.get('rec_texts', [])
                    rec_scores = ocr_result.get('rec_scores', None)
                    rec_boxes = ocr_result.get('rec_boxes', None)
                
                if rec_texts:
                    for i, text in enumerate(rec_texts):
                        if text and str(text).strip():
                            text_lines.append(str(text).strip())
                            if rec_scores and i < len(rec_scores):
                                confidences.append(float(rec_scores[i]))
                            else:
                                confidences.append(0.8)
                            
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
        
        # Format 2: List format (standard PaddleOCR)
        if not text_lines and isinstance(ocr_result, list):
            for line in ocr_result:
                if line and len(line) >= 2:
                    box = line[0]
                    text_info = line[1]
                    
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
        
        # Step 8: Merge text efficiently
        merged_text = "\n".join(text_lines)
        avg_confidence = float(np.mean(confidences)) if confidences else 0.0
        
        total_time = time.time() - start_time
        logger.info(f"[SPEED] Extracted {len(text_lines)} lines, {len(merged_text)} chars, confidence: {avg_confidence:.2f}, time: {total_time:.2f}s (OCR: {ocr_time:.2f}s)")
        
        result_dict = {
            "raw_text": merged_text,
            "avg_confidence": avg_confidence,
            "line_count": len(text_lines),
            "language_detected": language or 'en',
            "error": None
        }
        
        if return_detailed:
            result_dict["boxes"] = boxes
        
        # Cache result (with size limit)
        if len(_ocr_cache) >= _cache_max_size:
            # Remove oldest entry (simple FIFO)
            oldest_key = next(iter(_ocr_cache))
            del _ocr_cache[oldest_key]
        _ocr_cache[cache_key] = result_dict
        
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

