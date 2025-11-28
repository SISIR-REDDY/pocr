# Backend Deployment Script for Railway
# Run this script from the project root

Write-Host "🚀 Setting up Backend for Railway Deployment..." -ForegroundColor Green
Write-Host ""

# Check if Railway CLI is installed
if (-not (Get-Command railway -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Railway CLI..." -ForegroundColor Yellow
    Write-Host "Please visit: https://docs.railway.app/develop/cli#installation" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "For Windows, run:" -ForegroundColor Cyan
    Write-Host "  iwr https://railway.app/install.ps1 | iex" -ForegroundColor White
    Write-Host ""
    $install = Read-Host "Would you like to install Railway CLI now? (y/n)"
    if ($install -eq "y") {
        Invoke-WebRequest https://railway.app/install.ps1 | Invoke-Expression
    } else {
        Write-Host "Please install Railway CLI manually and run this script again" -ForegroundColor Yellow
        exit
    }
}

# Navigate to backend directory
Set-Location backend

Write-Host "Current directory: $(Get-Location)" -ForegroundColor Cyan
Write-Host ""

# Check if Railway project is initialized
if (-not (Test-Path railway.json) -and -not (Get-Command railway -ErrorAction SilentlyContinue)) {
    Write-Host "Initializing Railway project..." -ForegroundColor Cyan
    Write-Host "You will be prompted to login and create/link a project" -ForegroundColor Yellow
    railway login
    railway init
}

Write-Host ""
Write-Host "Deploying to Railway..." -ForegroundColor Cyan
railway up

Write-Host ""
Write-Host "✅ Backend deployment initiated!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Note your backend URL from Railway dashboard" -ForegroundColor White
Write-Host "  2. Update VITE_API_URL in Vercel dashboard with this URL" -ForegroundColor White
Write-Host "  3. Update CORS in backend/main.py with frontend URL" -ForegroundColor White

Set-Location ..

