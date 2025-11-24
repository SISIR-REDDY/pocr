"""
Model selector for TrOCR: chooses between handwritten and printed models.
Uses edge variance and text density for detection.
"""

import cv2
import numpy as np
from PIL import Image
from typing import Literal
import sys
import os

# Add parent directory to path for utils import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import setup_logger

logger = setup_logger("model_selector")


def detect_handwriting_vs_printed(image: Image.Image) -> Literal["handwritten", "printed"]:
    """
    Detect if image contains handwriting or printed text.
    
    Uses heuristics:
    - Handwriting: more irregular edges, variable stroke widths, higher edge variance
    - Printed: more uniform, straight lines, lower edge variance
    
    Args:
        image: PIL Image
        
    Returns:
        "handwritten" or "printed" (defaults to handwritten if unsure)
    """
    try:
        # Convert to numpy array (grayscale)
        img_array = np.array(image.convert('L'))
        
        # Apply edge detection
        edges = cv2.Canny(img_array, 50, 150)
        
        # Calculate edge density
        edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
        
        # Calculate variance in stroke width using horizontal projection
        horizontal_proj = np.sum(img_array < 128, axis=1)
        proj_variance = np.var(horizontal_proj) if len(horizontal_proj) > 0 else 0
        
        # Calculate edge variance (irregularity measure)
        edge_variance = np.var(edges)
        
        # Calculate text density (percentage of dark pixels)
        text_density = np.sum(img_array < 128) / (img_array.shape[0] * img_array.shape[1])
        
        logger.info(f"Detection metrics - Edge density: {edge_density:.3f}, "
                   f"Proj variance: {proj_variance:.1f}, "
                   f"Edge variance: {edge_variance:.1f}, "
                   f"Text density: {text_density:.3f}")
        
        # Heuristics:
        # - High edge density + high variance = likely handwriting
        # - High edge variance = irregular strokes (handwriting)
        # - Low edge density + low variance = likely printed
        
        # Thresholds (tunable)
        if edge_density > 0.15 and proj_variance > 1000:
            logger.info("Detected: handwritten (high edge density + variance)")
            return "handwritten"
        
        if edge_variance > 5000:
            logger.info("Detected: handwritten (high edge variance)")
            return "handwritten"
        
        if edge_density < 0.05 and proj_variance < 500:
            logger.info("Detected: printed (low edge density + variance)")
            return "printed"
        
        # Default to handwritten if unsure (safer for forms)
        logger.info("Uncertain, defaulting to: handwritten")
        return "handwritten"
        
    except Exception as e:
        logger.warning(f"Detection failed: {e}, defaulting to handwritten")
        return "handwritten"


def get_model_type(image: Image.Image) -> Literal["handwritten", "printed"]:
    """
    Get the appropriate TrOCR model type for the image.
    
    Args:
        image: PIL Image
        
    Returns:
        "handwritten" or "printed"
    """
    return detect_handwriting_vs_printed(image)
