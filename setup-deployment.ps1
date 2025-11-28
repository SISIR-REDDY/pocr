# Complete Deployment Setup Script
# This script helps you deploy both frontend and backend

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Optical Recognition Deployment Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Git status
Write-Host "Checking Git status..." -ForegroundColor Yellow
$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Host "⚠️  You have uncommitted changes!" -ForegroundColor Yellow
    Write-Host "Changes:" -ForegroundColor Yellow
    git status --short
    Write-Host ""
    $commit = Read-Host "Would you like to commit and push changes? (y/n)"
    if ($commit -eq "y") {
        git add .
        $message = Read-Host "Enter commit message (or press Enter for default)"
        if (-not $message) {
            $message = "Prepare for deployment"
        }
        git commit -m $message
        git push origin main
        Write-Host "✅ Changes committed and pushed!" -ForegroundColor Green
    }
} else {
    Write-Host "✅ Git repository is clean" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Deployment Options" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Deploy Frontend to Vercel (Recommended)" -ForegroundColor White
Write-Host "2. Deploy Backend to Railway (Recommended for large models)" -ForegroundColor White
Write-Host "3. Deploy Backend to Render" -ForegroundColor White
Write-Host "4. Deploy Both (Frontend + Backend)" -ForegroundColor White
Write-Host "5. Exit" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Select an option (1-5)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Deploying Frontend to Vercel..." -ForegroundColor Green
        & .\deploy-frontend.ps1
    }
    "2" {
        Write-Host ""
        Write-Host "Deploying Backend to Railway..." -ForegroundColor Green
        & .\deploy-backend-railway.ps1
    }
    "3" {
        Write-Host ""
        Write-Host "For Render deployment:" -ForegroundColor Yellow
        Write-Host "1. Go to https://render.com" -ForegroundColor White
        Write-Host "2. Create new Web Service" -ForegroundColor White
        Write-Host "3. Connect GitHub repository" -ForegroundColor White
        Write-Host "4. Set Root Directory: backend" -ForegroundColor White
        Write-Host "5. Build Command: pip install -r requirements.txt" -ForegroundColor White
        Write-Host "6. Start Command: python main.py" -ForegroundColor White
        Write-Host "7. Deploy" -ForegroundColor White
    }
    "4" {
        Write-Host ""
        Write-Host "Deploying Frontend..." -ForegroundColor Green
        & .\deploy-frontend.ps1
        Write-Host ""
        Write-Host "Deploying Backend..." -ForegroundColor Green
        & .\deploy-backend-railway.ps1
    }
    "5" {
        Write-Host "Exiting..." -ForegroundColor Yellow
        exit
    }
    default {
        Write-Host "Invalid option!" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Post-Deployment Checklist" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "After deployment, make sure to:" -ForegroundColor Yellow
Write-Host "  [ ] Note your frontend URL" -ForegroundColor White
Write-Host "  [ ] Note your backend URL" -ForegroundColor White
Write-Host "  [ ] Set VITE_API_URL in Vercel dashboard" -ForegroundColor White
Write-Host "  [ ] Update CORS in backend/main.py" -ForegroundColor White
Write-Host "  [ ] Test the deployment" -ForegroundColor White
Write-Host ""

