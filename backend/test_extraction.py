"""
Direct test of PaddleOCR extraction with a real image.
"""

import sys
import os
from PIL import Image, ImageDraw, ImageFont

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.paddleocr_service import extract_text_from_image

print("\n" + "="*60)
print("Testing PaddleOCR Direct Extraction")
print("="*60 + "\n")

# Create a test image with multiple lines
print("[1/2] Creating test document...")
test_image = Image.new('RGB', (600, 300), color='white')
draw = ImageDraw.Draw(test_image)

# Draw multiple lines of text
test_lines = [
    "Name: John Doe",
    "Age: 30 years",
    "Gender: Male",
    "Phone: +1234567890",
    "Email: john.doe@example.com",
    "Address: 123 Main Street"
]

y_pos = 20
for line in test_lines:
    draw.text((20, y_pos), line, fill='black')
    y_pos += 40

print(f"✅ Created test image with {len(test_lines)} lines of text\n")

# Extract text
print("[2/2] Extracting text with PaddleOCR...")
result = extract_text_from_image(test_image)

if result.get("error"):
    print(f"❌ FAILED: {result['error']}\n")
else:
    raw_text = result.get("raw_text", "")
    confidence = result.get("avg_confidence", 0.0)
    line_count = result.get("line_count", 0)
    
    print(f"✅ SUCCESS!")
    print(f"   Lines detected: {line_count}")
    print(f"   Characters extracted: {len(raw_text)}")
    print(f"   Average confidence: {confidence:.2%}\n")
    
    if raw_text:
        print("   Extracted text:")
        print("   " + "-"*50)
        for line in raw_text.split('\n'):
            print(f"   {line}")
        print("   " + "-"*50)

print("\n" + "="*60)
print("Test Complete")
print("="*60 + "\n")
