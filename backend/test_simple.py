"""
Simple test to verify PaddleOCR loads and runs.
"""

print("\n" + "="*60)
print("Testing PaddleOCR Installation")
print("="*60 + "\n")

try:
    print("[1/2] Importing PaddleOCR...")
    from paddleocr import PaddleOCR
    print("✅ SUCCESS: PaddleOCR imported")
    
    print("\n[2/2] Initializing PaddleOCR with minimal params...")
    # Use only essential parameters
    ocr = PaddleOCR(lang='en')
    print("✅ SUCCESS: PaddleOCR initialized")
    
    print("\n" + "="*60)
    print("🎉 PaddleOCR is ready to use!")
    print("="*60 + "\n")
    
except Exception as e:
    print(f"\n❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    print("\n")
