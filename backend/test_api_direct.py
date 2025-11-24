"""
Test API extraction endpoint directly
"""
import requests
from PIL import Image, ImageDraw
import io

# Create test image
print("Creating test image...")
img = Image.new('RGB', (800, 400), 'white')
draw = ImageDraw.Draw(img)

# Add multiple lines of text
y = 20
for line in ["Name: John Doe", "Age: 30 years", "Gender: Male", "Phone: +1234567890", "Email: john@example.com", "Address: 123 Main St"]:
    draw.text((20, y), line, fill='black')
    y += 50

# Save to bytes
img_bytes = io.BytesIO()
img.save(img_bytes, format='PNG')
img_bytes.seek(0)

# Send to API
print("Sending to API...")
try:
    response = requests.post(
        'http://localhost:8000/api/extract',
        files={'file': ('test.png', img_bytes, 'image/png')}
    )
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    result = response.json()
    if result.get('success'):
        print(f"\n✅ SUCCESS!")
        print(f"Text extracted: {len(result.get('raw_text', ''))} chars")
        print(f"Fields: {result.get('fields', {})}")
        print(f"Raw text:\n{result.get('raw_text', '')}")
    else:
        print(f"\n❌ FAILED: {result.get('error', 'Unknown error')}")
        
except Exception as e:
    print(f"\n❌ EXCEPTION: {e}")
    import traceback
    traceback.print_exc()
