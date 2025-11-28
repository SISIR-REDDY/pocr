"""
Vercel serverless function entry point for FastAPI backend.
This file is used when deploying to Vercel.
"""

import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Import the FastAPI app
from main import app

# Export the app for Vercel
# Vercel will use this as the handler
handler = app

