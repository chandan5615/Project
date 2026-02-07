# Sentinel Agent - Setup Script for Windows PowerShell
# Creates a virtual environment and installs all dependencies

Write-Host " Setting up Sentinel Agent environment..." -ForegroundColor Green

# Create virtual environment
Write-Host " Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv

# Activate virtual environment
Write-Host "✅ Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "⬆️  Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install dependencies
Write-Host " Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "To activate the environment, run:" -ForegroundColor Cyan
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Note: On Windows, this project requires WSL or a Linux environment" -ForegroundColor Yellow
Write-Host "for full functionality (auth.log monitoring and iptables)." -ForegroundColor Yellow
Write-Host ""
