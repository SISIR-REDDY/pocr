"""
Language detector for OCR text.
Detects script based on Unicode ranges for English, Hindi (Devanagari), and Arabic.
"""

import re
from typing import Literal
import sys
import os

# Add parent directory to path for utils import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import setup_logger

logger = setup_logger("language_detector")

# Unicode ranges
ARABIC_RANGE = (0x0600, 0x06FF)  # Arabic script
DEVANAGARI_RANGE = (0x0900, 0x097F)  # Devanagari (Hindi) script
ENGLISH_PATTERN = re.compile(r'[a-zA-Z]')


def detect_language(text: str) -> Literal['en', 'hi', 'ar', 'multi']:
    """
    Detect language/script from text based on Unicode ranges.
    
    Args:
        text: Input text to analyze
        
    Returns:
        Language code: 'en' (English), 'hi' (Hindi), 'ar' (Arabic), or 'multi' (mixed)
    """
    if not text or not text.strip():
        return 'en'  # Default to English
    
    try:
        has_english = bool(ENGLISH_PATTERN.search(text))
        has_arabic = False
        has_devanagari = False
        
        # Check for Arabic characters
        for char in text:
            code_point = ord(char)
            if ARABIC_RANGE[0] <= code_point <= ARABIC_RANGE[1]:
                has_arabic = True
                break
        
        # Check for Devanagari (Hindi) characters
        for char in text:
            code_point = ord(char)
            if DEVANAGARI_RANGE[0] <= code_point <= DEVANAGARI_RANGE[1]:
                has_devanagari = True
                break
        
        # Count languages detected
        languages_detected = sum([has_english, has_arabic, has_devanagari])
        
        if languages_detected > 1:
            logger.info(f"Detected multiple languages: EN={has_english}, HI={has_devanagari}, AR={has_arabic}")
            return 'multi'
        elif has_arabic:
            logger.info("Detected Arabic script")
            return 'ar'
        elif has_devanagari:
            logger.info("Detected Hindi (Devanagari) script")
            return 'hi'
        else:
            logger.info("Detected English (default)")
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

