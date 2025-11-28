# Frontend Deployment Script for Vercel
# Run this script from the project root

Write-Host "🚀 Deploying Frontend to Vercel..." -ForegroundColor Green
Write-Host ""

# Check if Vercel CLI is installed
if (-not (Get-Command vercel -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Vercel CLI..." -ForegroundColor Yellow
    npm install -g vercel
}

# Navigate to frontend directory
Set-Location frontend

Write-Host "Current directory: $(Get-Location)" -ForegroundColor Cyan
Write-Host ""

# Check if already linked to a Vercel project
if (Test-Path .vercel) {
    Write-Host "Project already linked to Vercel" -ForegroundColor Yellow
    Write-Host "Deploying..." -ForegroundColor Cyan
    vercel --prod
} else {
    Write-Host "Linking project to Vercel..." -ForegroundColor Cyan
    Write-Host "You will be prompted to:" -ForegroundColor Yellow
    Write-Host "  1. Login to Vercel (if not already logged in)" -ForegroundColor Yellow
    Write-Host "  2. Link to existing project or create new one" -ForegroundColor Yellow
    Write-Host "  3. Set root directory (should be: frontend)" -ForegroundColor Yellow
    Write-Host ""
    
    vercel link
    
    Write-Host ""
    Write-Host "Setting environment variable placeholder..." -ForegroundColor Cyan
    Write-Host "⚠️  IMPORTANT: After backend deployment, update VITE_API_URL in Vercel dashboard" -ForegroundColor Yellow
    Write-Host ""
    
    # Deploy
    Write-Host "Deploying to production..." -ForegroundColor Cyan
    vercel --prod
}

Write-Host ""
Write-Host "✅ Frontend deployment initiated!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Note your frontend URL from the output above" -ForegroundColor White
Write-Host "  2. Deploy backend (see deploy-backend.ps1 or use Railway/Render)" -ForegroundColor White
Write-Host "  3. Update VITE_API_URL in Vercel dashboard with backend URL" -ForegroundColor White
Write-Host "  4. Update CORS in backend/main.py with frontend URL" -ForegroundColor White

Set-Location ..

