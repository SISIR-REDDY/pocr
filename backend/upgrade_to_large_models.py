"""
Upgrade to TrOCR large models for better accuracy.
"""

from huggingface_hub import snapshot_download
from pathlib import Path
import shutil
import sys
import time
import os

BACKEND_DIR = Path(__file__).parent
MODEL_HANDWRITTEN = BACKEND_DIR / "models" / "trocr-handwritten"
MODEL_PRINTED = BACKEND_DIR / "models" / "trocr-printed"

def remove_model_safely(model_path: Path, max_retries: int = 3):
    """Safely remove model directory, handling locked files."""
    if not model_path.exists():
        return True
    
    for attempt in range(max_retries):
        try:
            # Try to remove .cache directory first if it exists
            cache_dir = model_path / ".cache"
            if cache_dir.exists():
                try:
                    shutil.rmtree(cache_dir)
                except:
                    pass
            
            # Wait a bit before trying again
            if attempt > 0:
                time.sleep(2)
            
            shutil.rmtree(model_path)
            return True
        except PermissionError as e:
            if attempt < max_retries - 1:
                print(f"[WARN] Model in use, retrying in 2 seconds... (attempt {attempt + 1}/{max_retries})")
                continue
            else:
                print(f"[WARN] Could not remove {model_path}: {e}")
                print("[INFO] Trying to download over existing model...")
                return False
        except Exception as e:
            print(f"[WARN] Error removing model: {e}")
            return False
    
    return False

print("=" * 60)
print("Upgrading to TrOCR Large Models")
print("=" * 60)

# Check if handwritten model already exists and is large
handwritten_exists = MODEL_HANDWRITTEN.exists() and any(MODEL_HANDWRITTEN.iterdir())
if handwritten_exists:
    # Check if it's already the large model by checking config
    config_file = MODEL_HANDWRITTEN / "config.json"
    if config_file.exists():
        try:
            import json
            with open(config_file, 'r') as f:
                config = json.load(f)
                if config.get('model_type') == 'vision-encoder-decoder':
                    # Check model size - large models have more parameters
                    model_file = MODEL_HANDWRITTEN / "pytorch_model.bin"
                    if model_file.exists() and model_file.stat().st_size > 500_000_000:  # > 500MB
                        print("[OK] Large handwritten model already exists, skipping...")
                        handwritten_done = True
                    else:
                        handwritten_done = False
                else:
                    handwritten_done = False
        except:
            handwritten_done = False
    else:
        handwritten_done = False
else:
    handwritten_done = False

if not handwritten_done:
    if MODEL_HANDWRITTEN.exists():
        print(f"\nRemoving existing handwritten model at {MODEL_HANDWRITTEN}")
        remove_model_safely(MODEL_HANDWRITTEN)
    
    print("\n[1/2] Downloading microsoft/trocr-large-handwritten...")
    snapshot_download(
        repo_id="microsoft/trocr-large-handwritten",
        local_dir=str(MODEL_HANDWRITTEN),
        local_dir_use_symlinks=False
    )
    print("[OK] Handwritten model downloaded")
else:
    print("\n[1/2] Handwritten model already up to date")

# Download large printed model
printed_exists = MODEL_PRINTED.exists() and any(MODEL_PRINTED.iterdir())
if printed_exists:
    config_file = MODEL_PRINTED / "config.json"
    if config_file.exists():
        try:
            import json
            with open(config_file, 'r') as f:
                config = json.load(f)
                if config.get('model_type') == 'vision-encoder-decoder':
                    model_file = MODEL_PRINTED / "pytorch_model.bin"
                    if model_file.exists() and model_file.stat().st_size > 500_000_000:  # > 500MB
                        print("[OK] Large printed model already exists, skipping...")
                        printed_done = True
                    else:
                        printed_done = False
                else:
                    printed_done = False
        except:
            printed_done = False
    else:
        printed_done = False
else:
    printed_done = False

if not printed_done:
    if MODEL_PRINTED.exists():
        print(f"\nRemoving existing printed model at {MODEL_PRINTED}")
        removed = remove_model_safely(MODEL_PRINTED)
        if not removed:
            print("[INFO] Some files locked, will download over existing...")
    
    print("\n[2/2] Downloading microsoft/trocr-large-printed...")
    print("[INFO] This is a large model (~2.4GB), please be patient...")
    max_retries = 3
    for attempt in range(max_retries):
        try:
            snapshot_download(
                repo_id="microsoft/trocr-large-printed",
                local_dir=str(MODEL_PRINTED)
            )
            print("[OK] Printed model downloaded")
            break
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"[WARN] Download failed (attempt {attempt + 1}/{max_retries}): {e}")
                print("[INFO] Retrying in 5 seconds...")
                time.sleep(5)
            else:
                print(f"[ERROR] Failed to download printed model after {max_retries} attempts: {e}")
                print("[INFO] You can retry later by running this script again")
                sys.exit(1)
else:
    print("\n[2/2] Printed model already up to date")

print("\n" + "=" * 60)
print("[OK] All large models ready!")
print("=" * 60)

