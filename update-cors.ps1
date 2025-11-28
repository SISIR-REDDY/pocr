# Script to update CORS settings in backend/main.py
# Run this after you have both frontend and backend URLs

param(
    [Parameter(Mandatory=$true)]
    [string]$FrontendUrl,
    
    [Parameter(Mandatory=$false)]
    [string]$BackendFile = "backend/main.py"
)

Write-Host "Updating CORS settings..." -ForegroundColor Green
Write-Host "Frontend URL: $FrontendUrl" -ForegroundColor Cyan
Write-Host ""

# Read the file
$content = Get-Content $BackendFile -Raw

# Create the new CORS configuration
$newCorsConfig = @"
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "$FrontendUrl",
        "http://localhost:3000"  # For local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
"@

# Find and replace the CORS middleware section
$pattern = '(?s)app\.add_middleware\(\s*CORSMiddleware,.*?allow_headers=\["\*"\],\s*\)'
$content = $content -replace $pattern, $newCorsConfig

# Write back to file
Set-Content -Path $BackendFile -Value $content -NoNewline

Write-Host "✅ CORS settings updated!" -ForegroundColor Green
Write-Host ""
Write-Host "Updated allow_origins to include:" -ForegroundColor Yellow
Write-Host "  - $FrontendUrl" -ForegroundColor White
Write-Host "  - http://localhost:3000 (for local dev)" -ForegroundColor White
Write-Host ""
Write-Host "Don't forget to commit and push this change!" -ForegroundColor Yellow

