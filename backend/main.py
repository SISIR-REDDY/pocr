"""
MOSIP OCR Web Prototype - FastAPI Backend
Main application entry point.
100% offline TrOCR OCR with local model loading.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from routes import extract, verify
from utils.logger import setup_logger, log_error_with_traceback
from services.ocr_service import initialize_paddleocr

# Configure logging
logger = setup_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown."""
    # Startup
    logger.info("=" * 60)
    logger.info("Starting MOSIP OCR Backend (PaddleOCR Multilingual)")
    logger.info("=" * 60)
    
    # Initialize PaddleOCR for multiple languages
    logger.info("Initializing PaddleOCR models...")
    languages = ['en', 'hi', 'ar', 'ch']  # English, Hindi, Arabic, Multilingual
    
    initialized_count = 0
    for lang in languages:
        try:
            ocr = initialize_paddleocr(lang)
            if ocr:
                initialized_count += 1
                logger.info(f"[OK] PaddleOCR initialized for {lang}")
            else:
                logger.warning(f"[WARN] PaddleOCR initialization failed for {lang}")
        except Exception as e:
            logger.warning(f"[WARN] PaddleOCR initialization error for {lang}: {e}")
    
    if initialized_count > 0:
        logger.info(f"[OK] {initialized_count}/{len(languages)} PaddleOCR models initialized")
    else:
        logger.error("[FAIL] No PaddleOCR models initialized")
        logger.warning("Server will start but OCR may fail")
    
    logger.info("=" * 60)
    
    yield  # Application runs here
    
    # Shutdown (if needed)
    logger.info("Shutting down MOSIP OCR Backend")


# Create FastAPI app with lifespan
app = FastAPI(
    title="MOSIP OCR API",
    description="Offline PaddleOCR multilingual OCR service (English, Hindi, Arabic) with field extraction",
    version="3.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    log_error_with_traceback(logger, exc, f"Unhandled exception in {request.url.path}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "details": str(exc) if os.getenv("DEBUG", "false").lower() == "true" else "An error occurred"
        }
    )


# Include routers
app.include_router(extract.router)
app.include_router(verify.router)


@app.get("/")
async def root():
    """Health check endpoint."""
    from services.ocr_service import _initialized_languages
    
    return {
        "status": "ok",
        "service": "MOSIP OCR API (PaddleOCR Multilingual)",
        "version": "3.0.0",
        "models": {
            "languages": list(_initialized_languages) if _initialized_languages else [],
            "status": "ready" if _initialized_languages else "initializing"
        },
        "offline": True,
        "supported_languages": ["en", "hi", "ar", "multi"]
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    from services.ocr_service import _initialized_languages
    
    if not _initialized_languages:
        return JSONResponse(
            status_code=503,
            content={
                "status": "degraded",
                "message": "PaddleOCR models not initialized",
                "models": {
                    "initialized": list(_initialized_languages),
                    "status": "initializing"
                }
            }
        )
    
    return {
        "status": "healthy",
        "models": {
            "initialized": list(_initialized_languages),
            "status": "ready"
        }
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
