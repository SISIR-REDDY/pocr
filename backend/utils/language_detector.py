"""
Language detector for OCR text.
Detects script based on Unicode ranges for English, Hindi (Devanagari), and Arabic.
Optimized for speed using regex and text sampling.
"""

import re
from typing import Literal
import sys
import os

# Add parent directory to path for utils import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import setup_logger

logger = setup_logger("language_detector")

# Unicode ranges (using regex patterns for speed)
ARABIC_PATTERN = re.compile(r'[\u0600-\u06FF]')  # Arabic script
DEVANAGARI_PATTERN = re.compile(r'[\u0900-\u097F]')  # Devanagari (Hindi) script
ENGLISH_PATTERN = re.compile(r'[a-zA-Z]')


def detect_language(text: str, sample_size: int = 500) -> Literal['en', 'hi', 'ar', 'multi']:
    """
    Fast language/script detection from text based on Unicode ranges.
    Uses a sample of text for speed (default 500 chars).
    
    Args:
        text: Input text to analyze
        sample_size: Maximum characters to analyze (for performance)
        
    Returns:
        Language code: 'en' (English), 'hi' (Hindi), 'ar' (Arabic), or 'multi' (mixed)
    """
    if not text or not text.strip():
        return 'en'  # Default to English
    
    try:
        # Use only a sample of text for faster detection
        sample_text = text[:sample_size] if len(text) > sample_size else text
        
        # Use pre-compiled regex patterns for fastest detection (single pass)
        has_english = bool(ENGLISH_PATTERN.search(sample_text))
        has_arabic = bool(ARABIC_PATTERN.search(sample_text))
        has_devanagari = bool(DEVANAGARI_PATTERN.search(sample_text))
        
        # Count languages detected
        languages_detected = sum([has_english, has_arabic, has_devanagari])
        
        if languages_detected > 1:
            logger.debug(f"Detected multiple languages: EN={has_english}, HI={has_devanagari}, AR={has_arabic}")
            return 'multi'
        elif has_arabic:
            logger.debug("Detected Arabic script")
            return 'ar'
        elif has_devanagari:
            logger.debug("Detected Hindi (Devanagari) script")
            return 'hi'
        else:
            logger.debug("Detected English (default)")
            return 'en'
            
    except Exception as e:
        logger.warning(f"Language detection failed: {e}, defaulting to English")
        return 'en'


def get_paddleocr_lang_code(detected_lang: str) -> str:
    """
    Map detected language to PaddleOCR language code.
    
    Args:
        detected_lang: Language code from detect_language()
        
    Returns:
        PaddleOCR language code
    """
    mapping = {
        'en': 'en',  # English
        'hi': 'hi',  # Hindi
        'ar': 'ar',  # Arabic
        'multi': 'ch'  # PaddleOCR multilingual model (ch = Chinese, but supports multiple languages)
    }
    
    return mapping.get(detected_lang, 'en')

