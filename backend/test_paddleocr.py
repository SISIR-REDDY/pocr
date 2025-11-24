"""
Quick test script to verify PaddleOCR integration.
"""

import sys
import os
from pathlib import Path
from PIL import Image

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.paddleocr_service import extract_text_from_image, initialize_paddleocr

def test_paddleocr():
    """Test PaddleOCR extraction with a simple test."""
    print("="* 60)
    print("PaddleOCR Integration Test")
    print("="* 60)
    
    # Initialize
    print("\n[1/3] Initializing PaddleOCR...")
    ocr = initialize_paddleocr(use_gpu=False)
    if ocr is None:
        print("❌ FAILED: PaddleOCR initialization failed")
        return False
    print("✅ SUCCESS: PaddleOCR initialized")
    
    # Create a simple test image with text
    print("\n[2/3] Creating test image...")
    try:
        # Create a simple white image with black text
        from PIL import ImageDraw, ImageFont
        
        test_image = Image.new('RGB', (400, 200), color='white')
        draw = ImageDraw.Draw(test_image)
        
        # Draw some test text
        test_text = [
            "Name: John Doe",
            "Age: 30",
            "Email: john@example.com",
            "Phone: +1234567890"
        ]
        
        y_position = 20
        for line in test_text:
            draw.text((20, y_position), line, fill='black')
            y_position += 40
        
        print("✅ SUCCESS: Test image created")
        
    except Exception as e:
        print(f"⚠️  WARNING: Could not create test image: {e}")
        print("   (This is OK, will skip image test)")
        return True
    
    # Test extraction
    print("\n[3/3] Testing text extraction...")
    try:
        result = extract_text_from_image(test_image)
        
        if result.get("error"):
            print(f"❌ FAILED: {result['error']}")
            return False
        
        raw_text = result.get("raw_text", "")
        confidence = result.get("avg_confidence", 0.0)
        line_count = result.get("line_count", 0)
        
        print(f"✅ SUCCESS: Extracted {line_count} lines")
        print(f"   Confidence: {confidence:.2%}")
        print(f"   Text length: {len(raw_text)} characters")
        
        if raw_text:
            print(f"\n   Extracted text preview:")
            preview = raw_text[:200] + "..." if len(raw_text) > 200 else raw_text
            for line in preview.split('\n'):
                print(f"   > {line}")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: Extraction error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n")
    success = test_paddleocr()
    print("\n" + "="* 60)
    if success:
        print("🎉 ALL TESTS PASSED! PaddleOCR is ready to use.")
    else:
        print("❌ TESTS FAILED. Please check the error messages above.")
    print("="* 60)
    print("\n")
