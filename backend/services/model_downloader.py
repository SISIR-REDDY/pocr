"""
On-demand model downloader for deployment.
Downloads models from Hugging Face Hub on first request if not present locally.
"""

import os
import sys
from pathlib import Path
from typing import Optional
import logging
from huggingface_hub import snapshot_download
import torch

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import setup_logger

logger = setup_logger("model_downloader")

# Model configurations
MODELS = {
    "trocr-handwritten": {
        "hf_name": "microsoft/trocr-large-handwritten",
        "local_path": "models/trocr-handwritten"
    },
    "trocr-printed": {
        "hf_name": "microsoft/trocr-large-printed",
        "local_path": "models/trocr-printed"
    }
}

BACKEND_DIR = Path(__file__).parent.parent.resolve()


def check_model_exists(model_path: Path) -> bool:
    """Check if model exists locally."""
    if not model_path.exists():
        return False
    # Check for required files
    required_files = ["config.json"]
    return all((model_path / f).exists() for f in required_files)


def download_model_from_hf(hf_name: str, local_path: Path, model_key: str) -> bool:
    """
    Download model from Hugging Face Hub.
    
    Args:
        hf_name: Hugging Face model name
        local_path: Local path to save model
        model_key: Model identifier for logging
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"[DOWNLOAD] Starting download of {model_key} from Hugging Face...")
        logger.info(f"[DOWNLOAD] Model: {hf_name}")
        logger.info(f"[DOWNLOAD] Destination: {local_path}")
        
        # Create directory if it doesn't exist
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Download from Hugging Face
        snapshot_download(
            repo_id=hf_name,
            local_dir=str(local_path),
            local_dir_use_symlinks=False,
            resume_download=True  # Resume if interrupted
        )
        
        logger.info(f"[DOWNLOAD] ✅ Successfully downloaded {model_key}")
        return True
        
    except Exception as e:
        logger.error(f"[DOWNLOAD] ❌ Failed to download {model_key}: {e}")
        return False


def ensure_model_available(model_key: str) -> bool:
    """
    Ensure model is available locally, download if not.
    
    Args:
        model_key: Key from MODELS dict (e.g., "trocr-handwritten")
        
    Returns:
        True if model is available, False otherwise
    """
    if model_key not in MODELS:
        logger.error(f"Unknown model key: {model_key}")
        return False
    
    model_config = MODELS[model_key]
    local_path = BACKEND_DIR / model_config["local_path"]
    
    # Check if model exists
    if check_model_exists(local_path):
        logger.info(f"[MODEL] {model_key} already exists locally")
        return True
    
    # Download model
    logger.warning(f"[MODEL] {model_key} not found locally, downloading...")
    return download_model_from_hf(
        model_config["hf_name"],
        local_path,
        model_key
    )


def ensure_all_models_available() -> dict:
    """
    Ensure all models are available, download missing ones.
    
    Returns:
        Dict with model keys and availability status
    """
    results = {}
    
    for model_key in MODELS.keys():
        results[model_key] = ensure_model_available(model_key)
    
    return results


def get_model_size_mb(model_path: Path) -> float:
    """Get model size in MB."""
    if not model_path.exists():
        return 0.0
    
    total_size = 0
    for file_path in model_path.rglob("*"):
        if file_path.is_file():
            total_size += file_path.stat().st_size
    
    return total_size / (1024 * 1024)


if __name__ == "__main__":
    """Test model downloader."""
    print("Testing model downloader...")
    results = ensure_all_models_available()
    
    for model_key, available in results.items():
        status = "✅ Available" if available else "❌ Failed"
        print(f"{model_key}: {status}")
        
        if available:
            model_path = BACKEND_DIR / MODELS[model_key]["local_path"]
            size_mb = get_model_size_mb(model_path)
            print(f"  Size: {size_mb:.2f} MB")

