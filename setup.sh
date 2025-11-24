#!/bin/bash

# Complete setup script for MOSIP OCR Web Prototype

echo "🚀 Setting up MOSIP OCR Web Prototype..."
echo ""

# Backend Setup
echo "📦 Setting up backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "✅ Backend setup complete!"
echo ""

# Frontend Setup
cd ../frontend
echo "📦 Setting up frontend..."
npm install

echo "✅ Frontend setup complete!"
echo ""

echo "🎉 Setup complete!"
echo ""
echo "To start the application:"
echo "  1. Backend: cd backend && source venv/bin/activate && python main.py"
echo "  2. Frontend: cd frontend && npm run dev"
echo ""
echo "Or use the start scripts in each directory."


