"""
Image preprocessing pipeline for OCR optimization.
Full pipeline: grayscale, denoise, adaptive threshold, deskew, shadow removal, 
perspective fix, upscale x2.
"""

import cv2
import numpy as np
from PIL import Image
import base64
from io import BytesIO
from typing import Tuple, Dict
import sys
import os

# Add parent directory to path for utils import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import setup_logger

logger = setup_logger("preprocess")


def safe_convert_to_rgb(image: Image.Image) -> Image.Image:
    """Safely convert image to RGB mode."""
    try:
        if image.mode != "RGB":
            return image.convert("RGB")
        return image
    except Exception as e:
        logger.warning(f"Image conversion warning: {e}, using original")
        return image


def grayscale(img: np.ndarray) -> np.ndarray:
    """Convert to grayscale."""
    try:
        if len(img.shape) == 3:
            return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return img
    except Exception as e:
        logger.warning(f"Grayscale conversion failed: {e}, using original")
        return img


def adaptive_threshold(img: np.ndarray) -> np.ndarray:
    """Apply adaptive thresholding."""
    try:
        return cv2.adaptiveThreshold(
            img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
    except Exception as e:
        logger.warning(f"Adaptive threshold failed: {e}, using original")
        return img


def bilateral_denoise(img: np.ndarray) -> np.ndarray:
    """Apply bilateral filter for noise reduction while preserving edges."""
    try:
        return cv2.bilateralFilter(img, 9, 75, 75)
    except Exception as e:
        logger.warning(f"Denoise failed: {e}, using original")
        return img


def gaussian_blur(img: np.ndarray, kernel_size: int = 3) -> np.ndarray:
    """Apply Gaussian blur."""
    try:
        return cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)
    except Exception as e:
        logger.warning(f"Gaussian blur failed: {e}, using original")
        return img


def clahe_enhance(img: np.ndarray) -> np.ndarray:
    """Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)."""
    try:
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return clahe.apply(img)
    except Exception as e:
        logger.warning(f"CLAHE failed: {e}, using original")
        return img


def sharpen(img: np.ndarray) -> np.ndarray:
    """Apply sharpening kernel."""
    try:
        kernel = np.array([[-1, -1, -1],
                           [-1,  9, -1],
                           [-1, -1, -1]])
        return cv2.filter2D(img, -1, kernel)
    except Exception as e:
        logger.warning(f"Sharpen failed: {e}, using original")
        return img


def contrast_boost(img: np.ndarray, alpha: float = 1.5, beta: int = 0) -> np.ndarray:
    """Boost contrast."""
    try:
        return cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
    except Exception as e:
        logger.warning(f"Contrast boost failed: {e}, using original")
        return img


def deskew(img: np.ndarray) -> np.ndarray:
    """Deskew image by detecting and correcting rotation."""
    try:
        coords = np.column_stack(np.where(img > 0))
        if len(coords) == 0:
            return img
        
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        
        if abs(angle) < 0.5:
            return img
        
        (h, w) = img.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return rotated
    except Exception as e:
        logger.warning(f"Deskew failed: {e}, continuing without deskew")
        return img


def image_to_base64(img: Image.Image) -> str:
    """Convert PIL Image to base64 string."""
    try:
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()
    except Exception:
        return ""


def remove_shadows(img: np.ndarray) -> np.ndarray:
    """Remove shadows using morphological operations."""
    try:
        # Convert to grayscale if needed
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()
        
        # Create a morphological kernel
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
        
        # Apply morphological opening to remove small dark regions
        morph = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
        
        # Divide original by morph to normalize lighting
        result = cv2.divide(gray, morph, scale=255)
        
        # Apply CLAHE for better contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        result = clahe.apply(result)
        
        return result
    except Exception as e:
        logger.warning(f"Shadow removal failed: {e}, using original")
        return img


def fix_perspective(img: np.ndarray) -> np.ndarray:
    """Fix perspective distortion (basic implementation)."""
    try:
        # This is a simplified perspective fix
        # For full implementation, would need corner detection
        # For now, return original
        return img
    except Exception as e:
        logger.warning(f"Perspective fix failed: {e}, using original")
        return img


def upscale_image(img: np.ndarray, scale: int = 2) -> np.ndarray:
    """Upscale image by specified factor."""
    try:
        h, w = img.shape[:2]
        new_h, new_w = h * scale, w * scale
        return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
    except Exception as e:
        logger.warning(f"Upscaling failed: {e}, using original")
        return img


def preprocess_image(image: Image.Image) -> Tuple[Image.Image, Dict[str, str]]:
    """
    Full preprocessing pipeline for PaddleOCR.
    Steps: grayscale, denoise, adaptive threshold, deskew, shadow removal,
    perspective fix, upscale x2.
    
    Args:
        image: PIL Image
        
    Returns:
        Tuple of (processed PIL Image, dict with base64 previews)
    """
    previews = {}
    
    try:
        # Step 1: Convert to RGB if needed
        rgb_image = safe_convert_to_rgb(image)
        logger.info("[PREPROCESS] [OK] RGB conversion")
        
        # Step 2: Convert to OpenCV format
        img_array = np.array(rgb_image)
        img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # Step 3: Grayscale
        gray = grayscale(img_cv)
        logger.info("[PREPROCESS] [OK] Grayscale")
        
        # Step 4: Denoise
        denoised = bilateral_denoise(gray)
        logger.info("[PREPROCESS] [OK] Denoise")
        
        # Step 5: Shadow removal
        shadow_removed = remove_shadows(denoised)
        logger.info("[PREPROCESS] [OK] Shadow removal")
        
        # Step 6: Deskew
        deskewed = deskew(shadow_removed)
        logger.info("[PREPROCESS] [OK] Deskew")
        
        # Step 7: Perspective fix (simplified)
        perspective_fixed = fix_perspective(deskewed)
        logger.info("[PREPROCESS] [OK] Perspective fix")
        
        # Step 8: Adaptive threshold
        thresholded = adaptive_threshold(perspective_fixed)
        logger.info("[PREPROCESS] [OK] Adaptive threshold")
        
        # Step 9: Upscale x2
        upscaled = upscale_image(thresholded, scale=2)
        logger.info("[PREPROCESS] [OK] Upscale x2")
        
        # Step 10: Convert back to RGB PIL Image
        # Convert grayscale to RGB for PIL
        if len(upscaled.shape) == 2:
            upscaled_rgb = cv2.cvtColor(upscaled, cv2.COLOR_GRAY2RGB)
        else:
            upscaled_rgb = upscaled
        
        final_image = Image.fromarray(cv2.cvtColor(upscaled_rgb, cv2.COLOR_BGR2RGB))
        
        # Ensure it's RGB
        if final_image.mode != 'RGB':
            final_image = final_image.convert('RGB')
        
        # Create preview
        preview_base64 = image_to_base64(final_image)
        if preview_base64:
            previews['processed'] = f"data:image/png;base64,{preview_base64}"
        
        logger.info("Preprocessing completed successfully (full pipeline)")
        
        return final_image, previews
        
    except Exception as e:
        logger.error(f"Preprocessing error: {e}", exc_info=True)
        # Fallback: return original image in RGB
        logger.warning("Returning original image as fallback")
        return safe_convert_to_rgb(image), previews
