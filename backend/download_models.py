"""
Model download script for TrOCR models.
Downloads models locally for offline use.
"""

import os
import sys
from pathlib import Path
from huggingface_hub import snapshot_download
import torch
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Model configurations
MODELS = {
    "handwritten": {
        "hf_name": "microsoft/trocr-large-handwritten",  # Upgraded to large for better accuracy
        "local_path": "backend/models/trocr-handwritten"
    },
    "printed": {
        "hf_name": "microsoft/trocr-large-printed",  # Upgraded to large for better accuracy
        "local_path": "backend/models/trocr-printed"
    }
}


def detect_device():
    """Detect if GPU is available."""
    if torch.cuda.is_available():
        logger.info(f"[OK] GPU detected: {torch.cuda.get_device_name(0)}")
        return "cuda"
    else:
        logger.info("[OK] Using CPU (no GPU detected)")
        return "cpu"


def download_model(hf_name: str, local_path: str):
    """
    Download a model from HuggingFace and save locally.
    
    Args:
        hf_name: HuggingFace model name
        local_path: Local path to save the model
    """
    local_path_abs = Path(local_path).resolve()
    
    # Check if model already exists
    if local_path_abs.exists() and any(local_path_abs.iterdir()):
        logger.info(f"[OK] Model already exists at {local_path_abs}, skipping download")
        return True
    
    logger.info(f"📥 Downloading {hf_name}...")
    logger.info(f"   Saving to: {local_path_abs}")
    
    try:
        # Create directory if it doesn't exist
        local_path_abs.parent.mkdir(parents=True, exist_ok=True)
        
        # Download model
        snapshot_download(
            repo_id=hf_name,
            local_dir=str(local_path_abs),
            local_dir_use_symlinks=False
        )
        
        logger.info(f"[OK] Successfully downloaded {hf_name}")
        return True
        
    except Exception as e:
        logger.error(f"[FAIL] Failed to download {hf_name}: {e}")
        return False


def main():
    """Main function to download all models."""
    logger.info("=" * 60)
    logger.info("TrOCR Model Download Script")
    logger.info("=" * 60)
    
    # Detect device
    device = detect_device()
    logger.info("")
    
    # Get base directory (project root)
    script_dir = Path(__file__).parent.resolve()
    # If script is in backend/, go up one level to project root
    if script_dir.name == "backend":
        base_dir = script_dir.parent
    else:
        base_dir = script_dir
    
    # Download all models
    success_count = 0
    for model_type, config in MODELS.items():
        logger.info(f"\n[{model_type.upper()} MODEL]")
        logger.info("-" * 60)
        
        # Resolve local path relative to project root
        local_path = base_dir / config["local_path"]
        
        if download_model(config["hf_name"], str(local_path)):
            success_count += 1
        logger.info("")
    
    # Summary
    logger.info("=" * 60)
    if success_count == len(MODELS):
        logger.info("[OK] All models downloaded successfully!")
        logger.info(f"[OK] Models are ready for offline use")
        logger.info("=" * 60)
        return 0
    else:
        logger.error(f"[FAIL] Only {success_count}/{len(MODELS)} models downloaded successfully")
        logger.error("Please check your internet connection and try again")
        logger.info("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())

