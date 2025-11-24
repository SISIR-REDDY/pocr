import logging
import sys
import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("test_minimal")

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    logger.info("Importing TrOCR service...")
    from services.trocr_service import extract_text_from_image, initialize_models
    
    # Initialize models first
    logger.info("Initializing models...")
    initialize_models()
    
    logger.info("Creating test image...")
    # Create a simple image with text
    img = Image.new('RGB', (400, 100), color='white')
    d = ImageDraw.Draw(img)
    # Use default font
    d.text((10, 10), "Name: John Doe", fill='black')
    d.text((10, 50), "Age: 30", fill='black')
    
    logger.info("Extracting text...")
    result = extract_text_from_image(img)
    
    print(f"\nResult: {result}")
    
    if result.get("raw_text"):
        print(f"SUCCESS: Extracted {len(result['raw_text'])} characters")
        print(f"Text: {result['raw_text']}")
    else:
        print(f"FAILURE: {result.get('error')}")

except Exception as e:
    logger.error(f"Test failed: {e}", exc_info=True)
