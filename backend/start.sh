#!/bin/bash

# Start script for MOSIP OCR Backend
# Automatically sets up environment and downloads models if needed

set -e  # Exit on error

echo "=========================================="
echo "MOSIP OCR Backend Setup & Start"
echo "=========================================="

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Step 1: Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Step 2: Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Step 3: Install/upgrade requirements
echo ""
echo "Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Requirements installed"

# Step 4: Note about PaddleOCR models
echo ""
echo "Note: PaddleOCR models will be downloaded automatically on first use."
echo "Supported languages: English (en), Hindi (hi), Arabic (ar), Multilingual (ch)"
echo "✓ PaddleOCR ready"

# Step 5: Create logs directory
mkdir -p logs
echo "✓ Logs directory ready"

# Step 6: Load environment variables
if [ -f ".env" ]; then
    echo ""
    echo "Loading environment variables..."
    export $(cat .env | grep -v '^#' | xargs)
    echo "✓ Environment variables loaded"
fi

# Step 7: Start uvicorn server
echo ""
echo "=========================================="
echo "Starting server..."
echo "=========================================="
echo ""
python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --reload
