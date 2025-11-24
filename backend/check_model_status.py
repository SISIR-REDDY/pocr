"""
Check status of TrOCR models.
"""

from pathlib import Path
import json

BACKEND_DIR = Path(__file__).parent
MODEL_HANDWRITTEN = BACKEND_DIR / "models" / "trocr-handwritten"
MODEL_PRINTED = BACKEND_DIR / "models" / "trocr-printed"

def get_model_size(model_path: Path) -> float:
    """Get total size of model directory in GB."""
    if not model_path.exists():
        return 0.0
    total = sum(f.stat().st_size for f in model_path.rglob('*') if f.is_file())
    return total / (1024 ** 3)

def check_model_type(model_path: Path) -> str:
    """Check if model is base or large."""
    if not model_path.exists():
        return "MISSING"
    
    config_file = model_path / "config.json"
    if not config_file.exists():
        return "INCOMPLETE"
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Check model file size - large models are > 500MB
        model_file = model_path / "pytorch_model.bin"
        if model_file.exists():
            size_mb = model_file.stat().st_size / (1024 ** 2)
            if size_mb > 500:
                return "LARGE"
            else:
                return "BASE"
        else:
            return "INCOMPLETE"
    except:
        return "UNKNOWN"

print("=" * 60)
print("TrOCR Model Status")
print("=" * 60)

# Check handwritten model
hw_status = check_model_type(MODEL_HANDWRITTEN)
hw_size = get_model_size(MODEL_HANDWRITTEN)
print(f"\nHandwritten Model: {hw_status}")
print(f"  Size: {hw_size:.2f} GB")
print(f"  Path: {MODEL_HANDWRITTEN}")

# Check printed model
pr_status = check_model_type(MODEL_PRINTED)
pr_size = get_model_size(MODEL_PRINTED)
print(f"\nPrinted Model: {pr_status}")
print(f"  Size: {pr_size:.2f} GB")
print(f"  Path: {MODEL_PRINTED}")

print("\n" + "=" * 60)
if hw_status == "LARGE" and pr_status == "LARGE":
    print("[OK] Both large models are ready!")
elif hw_status == "LARGE" and pr_status in ["BASE", "INCOMPLETE"]:
    print("[INFO] Handwritten model is large, printed model is still downloading/upgrading")
elif pr_size > 0.5:  # If printed model is > 500MB, it's likely downloading
    print("[INFO] Printed model download in progress...")
else:
    print("[INFO] Models status checked")
print("=" * 60)

