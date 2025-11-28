# Automated Backend Deployment Script
# This script helps deploy your backend to Render (most reliable for Python)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Automated Backend Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "I cannot directly deploy to external services without your authentication." -ForegroundColor Yellow
Write-Host "However, I'll guide you through the EASIEST method (Render - 5 minutes)" -ForegroundColor Green
Write-Host ""

Write-Host "Option 1: Render (Recommended - Most Reliable)" -ForegroundColor Cyan
Write-Host "----------------------------------------" -ForegroundColor Cyan
Write-Host ""
Write-Host "Steps (5 minutes):" -ForegroundColor White
Write-Host "1. Go to: https://render.com" -ForegroundColor Yellow
Write-Host "2. Sign up with GitHub (free)" -ForegroundColor Yellow
Write-Host "3. Click 'New +' → 'Web Service'" -ForegroundColor Yellow
Write-Host "4. Connect GitHub → Select 'pocr' repository" -ForegroundColor Yellow
Write-Host "5. Configure:" -ForegroundColor Yellow
Write-Host "   - Name: optical-recognition-backend" -ForegroundColor White
Write-Host "   - Root Directory: backend" -ForegroundColor White
Write-Host "   - Environment: Python 3" -ForegroundColor White
Write-Host "   - Build Command: pip install -r requirements.txt" -ForegroundColor White
Write-Host "   - Start Command: python main.py" -ForegroundColor White
Write-Host "6. Click 'Create Web Service'" -ForegroundColor Yellow
Write-Host "7. Wait 15-20 minutes (first deployment)" -ForegroundColor Yellow
Write-Host "8. Copy your backend URL from Render dashboard" -ForegroundColor Yellow
Write-Host ""

$continue = Read-Host "Would you like me to open Render in your browser? (y/n)"
if ($continue -eq "y") {
    Start-Process "https://render.com"
    Write-Host ""
    Write-Host "Render opened! Follow the steps above." -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  After Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Once deployed, you'll get a URL like:" -ForegroundColor White
Write-Host "  https://your-app.onrender.com" -ForegroundColor Yellow
Write-Host ""
Write-Host "Then:" -ForegroundColor White
Write-Host "1. Update Vercel frontend environment variable:" -ForegroundColor Yellow
Write-Host "   VITE_API_URL = your-render-url" -ForegroundColor White
Write-Host "2. Update CORS in backend/main.py with frontend URL" -ForegroundColor Yellow
Write-Host "3. Commit and push CORS changes" -ForegroundColor Yellow
Write-Host ""

Write-Host "Your backend will be live! 🚀" -ForegroundColor Green

