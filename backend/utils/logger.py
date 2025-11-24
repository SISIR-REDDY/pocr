"""
Deep logging utility for the OCR backend.
Logs to both console and file.
"""

import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime

# Get backend directory
BACKEND_DIR = Path(__file__).parent.parent
LOGS_DIR = BACKEND_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

LOG_FILE = LOGS_DIR / "app.log"


def setup_logger(name: str = "ocr_backend", level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger with file and console handlers.
    
    Args:
        name: Logger name
        level: Logging level
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler with UTF-8 encoding support for Windows
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    # Set encoding to UTF-8 to handle Unicode characters
    if hasattr(console_handler.stream, 'reconfigure'):
        try:
            console_handler.stream.reconfigure(encoding='utf-8', errors='replace')
        except:
            pass
    logger.addHandler(console_handler)
    
    # File handler with rotation and UTF-8 encoding
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


def log_preprocessing_step(logger: logging.Logger, step: str, success: bool, details: str = ""):
    """Log a preprocessing step."""
    status = "[OK]" if success else "[FAIL]"
    logger.info(f"[PREPROCESS] {status} {step} {details}")


def log_model_selection(logger: logging.Logger, model_type: str, confidence: float, reason: str = ""):
    """Log model selection."""
    logger.info(f"[MODEL_SELECT] Selected: {model_type} (confidence: {confidence:.2f}) {reason}")


def log_ocr_result(logger: logging.Logger, text_length: int, confidence: float, model_used: str):
    """Log OCR extraction result."""
    logger.info(f"[OCR] Extracted {text_length} chars, confidence: {confidence:.2f}, model: {model_used}")


def log_field_extraction(logger: logging.Logger, fields: dict, confidences: dict):
    """Log field extraction results."""
    extracted = [k for k, v in fields.items() if v is not None]
    logger.info(f"[FIELDS] Extracted: {', '.join(extracted)}")
    if confidences:
        avg_conf = sum(confidences.values()) / len(confidences) if confidences else 0.0
        logger.info(f"[FIELDS] Average confidence: {avg_conf:.2f}")


def log_error_with_traceback(logger: logging.Logger, error: Exception, context: str = ""):
    """Log error with full traceback."""
    logger.error(f"[ERROR] {context}: {str(error)}", exc_info=True)

