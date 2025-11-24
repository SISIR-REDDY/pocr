"""
Test API extraction - simple version
"""
import requests
from PIL import Image, ImageDraw
import io
import json

# Create test image
img = Image.new('RGB', (800, 400), 'white')
draw = ImageDraw.Draw(img)
y = 20
for line in ["Name: John Doe", "Age: 30", "Phone: 123456"]:
    draw.text((20, y), line, fill='black')
    y += 50

# Save to bytes
img_bytes = io.BytesIO()
img.save(img_bytes, format='PNG')
img_bytes.seek(0)

# Send to API
response = requests.post(
    'http://localhost:8001/api/extract',
    files={'file': ('test.png', img_bytes, 'image/png')}
)

print("Status:", response.status_code)
result = response.json()
print("\nFull response:")
print(json.dumps(result, indent=2))

if result.get('error'):
    print("\n>>> ERROR:", result['error'])
