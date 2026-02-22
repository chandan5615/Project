# ==============================================================================
# Deploy All Fixes to Ubuntu Server
# ==============================================================================
# This script copies all fixed files to Ubuntu and rebuilds the container
# ==============================================================================

Write-Host "🚀 Deploying Sentinel Agent Fixes to Ubuntu Server" -ForegroundColor Cyan
Write-Host ""

$SERVER = "ubuntu@192.168.31.91"
$PROJECT_PATH = "~/Project"

# Files to copy
$FILES = @(
    "main.py",
    "requirements.txt",
    "docker-compose.yml",
    "dashboard/app.py"
)

Write-Host "📦 Copying fixed files to server..." -ForegroundColor Yellow

foreach ($file in $FILES) {
    Write-Host "  → $file" -ForegroundColor Gray
    scp $file ${SERVER}:${PROJECT_PATH}/$file
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to copy $file" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "✅ All files copied successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "🔄 Rebuilding container on server..." -ForegroundColor Yellow
Write-Host ""

# SSH and rebuild
ssh $SERVER "cd $PROJECT_PATH && docker-compose down && docker-compose build --no-cache && docker-compose up -d"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Deployment complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 Services:" -ForegroundColor Cyan
    Write-Host "  - API:       http://192.168.31.91:8000" -ForegroundColor White
    Write-Host "  - Dashboard: http://192.168.31.91:8501" -ForegroundColor White
    Write-Host "  - Health:    http://192.168.31.91:8000/api/health" -ForegroundColor White
    Write-Host ""
    Write-Host "📝 View logs:" -ForegroundColor Cyan
    Write-Host "  ssh $SERVER 'cd $PROJECT_PATH && docker-compose logs -f sentinel-agent'" -ForegroundColor Gray
    Write-Host ""
    Write-Host "🧪 Run attack tests:" -ForegroundColor Cyan
    Write-Host "  python test_web_attacks.py" -ForegroundColor Gray
} else {
    Write-Host ""
    Write-Host "❌ Deployment failed!" -ForegroundColor Red
    exit 1
}
