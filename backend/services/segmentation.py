import cv2
import numpy as np
from PIL import Image
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

def segment_text_lines(pil_image: Image.Image) -> List[Tuple[Image.Image, Tuple[int, int, int, int]]]:
    """
    Segment text lines from a document image using OpenCV.
    
    Args:
        pil_image: Input PIL Image
        
    Returns:
        List of tuples: (cropped_line_image, (x, y, w, h))
        Sorted top-to-bottom.
    """
    try:
        # Convert PIL to OpenCV format (RGB -> BGR)
        img = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply adaptive thresholding to get binary image
        # Invert so text is white on black background
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Dilate horizontally to connect characters into words/lines
        # Kernel width > height to connect horizontally
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 3))
        dilated = cv2.dilate(binary, kernel, iterations=1)
        
        # Find contours
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter small contours (noise)
        min_area = 100
        valid_contours = [c for c in contours if cv2.contourArea(c) > min_area]
        
        # Get bounding boxes
        boxes = [cv2.boundingRect(c) for c in valid_contours]
        
        # Sort boxes top-to-bottom
        # Add a small tolerance for y-coordinate to group lines roughly on same level if needed
        # But simple y-sort is usually enough for documents
        boxes.sort(key=lambda b: b[1])
        
        # Crop images
        segments = []
        for (x, y, w, h) in boxes:
            # Add a small padding
            pad = 2
            x = max(0, x - pad)
            y = max(0, y - pad)
            w = min(img.shape[1] - x, w + 2*pad)
            h = min(img.shape[0] - y, h + 2*pad)
            
            # Crop from original PIL image
            cropped = pil_image.crop((x, y, x + w, y + h))
            segments.append((cropped, (x, y, w, h)))
            
        logger.info(f"Segmented {len(segments)} text lines")
        return segments
        
    except Exception as e:
        logger.error(f"Segmentation failed: {e}")
        # Return the whole image as a single segment if segmentation fails
        return [(pil_image, (0, 0, pil_image.width, pil_image.height))]
