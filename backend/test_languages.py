"""Test PaddleOCR language support"""
from paddleocr import PaddleOCR

print("Testing PaddleOCR language support...")
print("=" * 50)

languages_to_test = [
    ('en', 'English'),
    ('hi', 'Hindi'),
    ('ar', 'Arabic'),
    ('ch', 'Multilingual (Chinese-based, supports multiple)')
]

for lang_code, lang_name in languages_to_test:
    try:
        print(f"\nTesting {lang_name} ({lang_code})...")
        ocr = PaddleOCR(lang=lang_code)
        print(f"✓ {lang_name} ({lang_code}) - SUPPORTED")
    except Exception as e:
        print(f"✗ {lang_name} ({lang_code}) - ERROR: {str(e)[:100]}")

print("\n" + "=" * 50)
print("Note: PaddleOCR will download models on first use.")
print("The 'ch' (multilingual) model supports many languages including English, Hindi, Arabic.")

