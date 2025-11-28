"""
PaddleOCR service for full document OCR.
Handles text detection + recognition for complete documents.
"""

from paddleocr import PaddleOCR
from PIL import Image
import numpy as np
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import os
import sys

# Add parent directory to path for utils import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import setup_logger

logger = setup_logger("paddleocr_service")


# Global PaddleOCR instance cache
_paddle_ocr_instance = None
_initialized = False
_initialization_error = None


def initialize_paddleocr(use_gpu: bool = False) -> Optional[PaddleOCR]:
    """
    Initialize PaddleOCR engine.
    
    Args:
        use_gpu: Whether to use GPU acceleration
        
    Returns:
        PaddleOCR instance or None if failed
    """
    global _paddle_ocr_instance, _initialized, _initialization_error
    
    if _initialized and _paddle_ocr_instance is not None:
        return _paddle_ocr_instance
    
    try:
        logger.info("Initializing PaddleOCR...")
        logger.info(f"GPU enabled: {use_gpu}")
        
        # Initialize PaddleOCR with minimal settings for compatibility
        # Using only core parameters that are universally supported
        init_params = {
            'lang': 'en'  # English language only
        }
        
        # Only add use_gpu if False (default behavior)
        # Some versions may not support this parameter
        if not use_gpu:
            try:
                ocr = PaddleOCR(**init_params, use_gpu=False)
            except (TypeError, ValueError):
                # Fall back to initialization without use_gpu parameter
                logger.warning("use_gpu parameter not supported, using default")
                ocr = PaddleOCR(**init_params)
        else:
            ocr = PaddleOCR(**init_params, use_gpu=True)
        
        _paddle_ocr_instance = ocr
        _initialized = True
        _initialization_error = None
        logger.info("[OK] PaddleOCR initialized successfully")
        
        return ocr
        
    except Exception as e:
        _initialization_error = str(e)
        logger.error(f"Failed to initialize PaddleOCR: {e}", exc_info=True)
        return None


def extract_text_from_image(
    image: Image.Image,
    return_detailed: bool = False
) -> Dict:
    """
    Extract text from image using PaddleOCR.
    
    Args:
        image: PIL Image
        return_detailed: Whether to return detailed box information
        
    Returns:
        Dict with keys:
        - raw_text: Combined text from all detections
        - avg_confidence: Average confidence score
        - line_count: Number of text lines detected
        - boxes: List of text boxes with coordinates (if return_detailed=True)
        - error: Error message if any
    """
    try:
        # Initialize PaddleOCR if needed
        ocr = initialize_paddleocr(use_gpu=False)
        if ocr is None:
            return {
                "raw_text": "",
                "avg_confidence": 0.0,
                "line_count": 0,
                "error": "PaddleOCR initialization failed"
            }
        
        # Ensure image is RGB
        if image.mode != "RGB":
            image = image.convert("RGB")
        
        # Convert PIL Image to numpy array
        img_array = np.array(image)
        
        # Run OCR
        logger.info("Running PaddleOCR text detection and recognition...")
        result = ocr.ocr(img_array)
        logger.info(f"Raw PaddleOCR result type: {type(result)}")
        if result:
            logger.info(f"Raw PaddleOCR result length: {len(result)}")
            if len(result) > 0:
                logger.info(f"First item type: {type(result[0])}")
                logger.info(f"First item content: {result[0]}")
        
        if not result or not result[0]:
            logger.warning("No text detected in image")
            return {
                "raw_text": "",
                "avg_confidence": 0.0,
                "line_count": 0,
                "error": None
            }
        
        # Parse results
        text_lines = []
        confidences = []
        boxes = []
        
        # Handle different result formats
        # Format 1: List of lists (standard PaddleOCR)
        # Format 2: OCRResult object (PaddleX/Newer PaddleOCR)
        
        ocr_result = result[0]
        
        # Check if it's the new OCRResult format (dict-like)
        if isinstance(ocr_result, dict) or hasattr(ocr_result, 'get'):
            # It's likely an OCRResult object or dict
            # Try to get rec_texts and rec_scores
            rec_texts = ocr_result.get('rec_texts', [])
            rec_scores = ocr_result.get('rec_scores', [])
            rec_boxes = ocr_result.get('rec_boxes', [])
            
            if rec_texts:
                logger.info(f"Found rec_texts in result: {len(rec_texts)} lines")
                text_lines = rec_texts
                confidences = rec_scores if rec_scores else [0.0] * len(text_lines)
                
                if return_detailed and len(rec_boxes) == len(text_lines):
                    for i, text in enumerate(text_lines):
                        boxes.append({
                            "text": text,
                            "confidence": float(confidences[i]) if i < len(confidences) else 0.0,
                            "bbox": rec_boxes[i].tolist() if hasattr(rec_boxes[i], 'tolist') else rec_boxes[i]
                        })
            else:
                # Fallback: iterate if it behaves like a list but is not a dict
                # This handles the case where it might be a list but passed the dict check?
                # Unlikely for OCRResult, but let's be safe
                pass
        
        # If text_lines is still empty, try the standard list format
        if not text_lines and isinstance(ocr_result, list):
            for line in ocr_result:
                if line and len(line) >= 2:
                    # PaddleOCR returns: [[[x1,y1],[x2,y2],[x3,y3],[x4,y4]], (text, confidence)]
                    box = line[0]
                    text_info = line[1]
                    
                    if isinstance(text_info, (list, tuple)) and len(text_info) >= 2:
                        text, confidence = text_info[0], text_info[1]
                    else:
                        # Fallback if format is different
                        text = str(text_info)
                        confidence = 0.5
                    
                    text_lines.append(text)
                    confidences.append(float(confidence))
                    
                    if return_detailed:
                        boxes.append({
                            "text": text,
                            "confidence": float(confidence),
                            "bbox": box
                        })
        
        # Combine text lines
        combined_text = "\n".join(text_lines)
        avg_confidence = float(np.mean(confidences)) if confidences else 0.0
        
        logger.info(f"Extracted {len(text_lines)} text lines, {len(combined_text)} characters")
        logger.info(f"Average confidence: {avg_confidence:.2f}")
        
        result_dict = {
            "raw_text": combined_text,
            "avg_confidence": avg_confidence,
            "line_count": len(text_lines),
            "error": None
        }
        
        if return_detailed:
            result_dict["boxes"] = boxes
        
        return result_dict
        
    except Exception as e:
        logger.error(f"PaddleOCR extraction failed: {e}", exc_info=True)
        return {
            "raw_text": "",
            "avg_confidence": 0.0,
            "line_count": 0,
            "error": f"OCR extraction failed: {str(e)}"
        }


def extract_text_from_pdf(
    pdf_path: str
) -> Dict:
    """
    Extract text from PDF using PaddleOCR (multi-page).
    
    Args:
        pdf_path: Path to PDF file
        
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
            "error": "PDF support requires pdf2image and poppler"
        }
    
    try:
        logger.info(f"Converting PDF to images: {pdf_path}")
        pages = convert_from_path(pdf_path, dpi=300)
        
        all_text = []
        all_confidences = []
        total_lines = 0
        
        for page_num, page_image in enumerate(pages):
            logger.info(f"Processing page {page_num + 1}/{len(pages)}")
            result = extract_text_from_image(page_image)
            
            if result.get("error"):
                logger.warning(f"Page {page_num + 1} extraction failed: {result['error']}")
                continue
            
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
            "error": None
        }
        
    except Exception as e:
        logger.error(f"PDF extraction failed: {e}", exc_info=True)
        return {
            "raw_text": "",
            "avg_confidence": 0.0,
            "page_count": 0,
            "line_count": 0,
            "error": f"PDF extraction failed: {str(e)}"
        }
