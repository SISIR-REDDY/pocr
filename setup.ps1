# Complete setup script for MOSIP OCR Web Prototype (Windows PowerShell)

Write-Host "🚀 Setting up MOSIP OCR Web Prototype..." -ForegroundColor Cyan
Write-Host ""

# Backend Setup
Write-Host "📦 Setting up backend..." -ForegroundColor Yellow
Set-Location backend

# Create virtual environment
if (-not (Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Green
    python -m venv venv
}

# Activate virtual environment
& .\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Green
python -m pip install --upgrade pip

# Install dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Green
pip install -r requirements.txt

Write-Host "✅ Backend setup complete!" -ForegroundColor Green
Write-Host ""

# Frontend Setup
Set-Location ..\frontend
Write-Host "📦 Setting up frontend..." -ForegroundColor Yellow
npm install

Write-Host "✅ Frontend setup complete!" -ForegroundColor Green
Write-Host ""

Write-Host "🎉 Setup complete!" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start the application:" -ForegroundColor Yellow
Write-Host "  1. Backend: cd backend && .\venv\Scripts\Activate.ps1 && python main.py"
Write-Host "  2. Frontend: cd frontend && npm run dev"
Write-Host ""


