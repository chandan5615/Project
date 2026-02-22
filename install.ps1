# ============================================================================
# Sentinel Agent - Professional Installation Script (Windows PowerShell)
# ============================================================================
# This script provides a clean, professional installation of the Sentinel Agent
# system with full dependency checking, validation, and post-installation setup.
# ============================================================================

param(
    [switch]$SkipOllamaCheck = $false,
    [switch]$SkipPythonCheck = $false,
    [switch]$Dev = $false
)

# Color definitions
$Colors = @{
    Success = "Green"
    Warning = "Yellow"
    Error   = "Red"
    Info    = "Cyan"
    Header  = "Magenta"
}

function Write-Header {
    param([string]$Text)
    Write-Host ""
    Write-Host ("=" * 70) -ForegroundColor $Colors.Header
    Write-Host $Text -ForegroundColor $Colors.Header
    Write-Host ("=" * 70) -ForegroundColor $Colors.Header
    Write-Host ""
}

function Write-Success {
    param([string]$Text)
    Write-Host "✅ $Text" -ForegroundColor $Colors.Success
}

function Write-Warning {
    param([string]$Text)
    Write-Host "⚠️  $Text" -ForegroundColor $Colors.Warning
}

function Write-Error-Custom {
    param([string]$Text)
    Write-Host "❌ $Text" -ForegroundColor $Colors.Error
}

function Write-Info {
    param([string]$Text)
    Write-Host "️  $Text" -ForegroundColor $Colors.Info
}

# ============================================================================
# MAIN INSTALLATION PROCESS
# ============================================================================

Write-Header "SENTINEL AGENT - COMPLETE INSTALLATION"

# Step 1: Check Python Installation
Write-Host "[STEP 1/8] Checking Python Installation..." -ForegroundColor $Colors.Info
if (-not $SkipPythonCheck) {
    try {
        $pythonVersion = python --version 2>&1
        Write-Success "Python found: $pythonVersion"
        
        # Check if Python version is 3.10+
        if ($pythonVersion -match "Python (\d+)\.(\d+)") {
            $major = [int]$matches[1]
            $minor = [int]$matches[2]
            
            if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 10)) {
                Write-Error-Custom "Python 3.10+ is required. Current version: $pythonVersion"
                Write-Info "Download Python 3.10+ from https://www.python.org/downloads/"
                exit 1
            }
        }
    }
    catch {
        Write-Error-Custom "Python is not installed or not in PATH"
        Write-Info "Download Python 3.10+ from https://www.python.org/downloads/"
        exit 1
    }
} else {
    Write-Warning "Skipping Python check (--SkipPythonCheck)"
}

# Step 2: Check for Ollama
Write-Host ""
Write-Host "[STEP 2/8] Checking Ollama Installation..." -ForegroundColor $Colors.Info
if (-not $SkipOllamaCheck) {
    try {
        $ollamaVersion = ollama --version 2>&1
        Write-Success "Ollama found: $ollamaVersion"
        Write-Info "Note: Make sure Ollama service is running: ollama serve"
    }
    catch {
        Write-Warning "Ollama is not installed or not in PATH"
        Write-Info "Ollama is required for AI features. Download from https://ollama.ai"
        Write-Info "After installation, run: ollama serve"
        Write-Warning "Continuing installation, but Ollama must be installed for full functionality"
    }
} else {
    Write-Warning "Skipping Ollama check (--SkipOllamaCheck)"
}

# Step 3: Remove existing venv if it exists
Write-Host ""
Write-Host "[STEP 3/8] Preparing Virtual Environment..." -ForegroundColor $Colors.Info
if (Test-Path "venv") {
    Write-Warning "Existing virtual environment found. Removing..."
    Remove-Item -Path "venv" -Recurse -Force
    Write-Success "Old environment removed"
}

# Step 4: Create Virtual Environment
Write-Host ""
Write-Host "[STEP 4/8] Creating Virtual Environment..." -ForegroundColor $Colors.Info
try {
    python -m venv venv
    Write-Success "Virtual environment created"
}
catch {
    Write-Error-Custom "Failed to create virtual environment: $_"
    exit 1
}

# Step 5: Activate Virtual Environment
Write-Host ""
Write-Host "[STEP 5/8] Activating Virtual Environment..." -ForegroundColor $Colors.Info
try {
    & .\venv\Scripts\Activate.ps1
    Write-Success "Virtual environment activated"
}
catch {
    Write-Error-Custom "Failed to activate virtual environment: $_"
    Write-Info "Try running: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser"
    exit 1
}

# Step 6: Upgrade pip and install tools
Write-Host ""
Write-Host "[STEP 6/8] Upgrading pip and Installation Tools..." -ForegroundColor $Colors.Info
try {
    python -m pip install --upgrade pip setuptools wheel --quiet
    Write-Success "pip upgraded successfully"
}
catch {
    Write-Error-Custom "Failed to upgrade pip: $_"
    exit 1
}

# Step 7: Install Requirements
Write-Host ""
Write-Host "[STEP 7/8] Installing Project Dependencies..." -ForegroundColor $Colors.Info
if (-not (Test-Path "requirements.txt")) {
    Write-Error-Custom "requirements.txt not found!"
    exit 1
}

try {
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Custom "Failed to install dependencies"
        exit 1
    }
    Write-Success "All dependencies installed successfully"
}
catch {
    Write-Error-Custom "Failed to install requirements: $_"
    exit 1
}

# Step 8: Initialize Databases
Write-Host ""
Write-Host "[STEP 8/8] Initializing Databases..." -ForegroundColor $Colors.Info
try {
    # Create database directory if it doesn't exist
    if (-not (Test-Path "data")) {
        New-Item -ItemType Directory -Path "data" | Out-Null
        Write-Success "Data directory created"
    }
    
    # Initialize databases through data_engine
    python -c "from data_engine import get_engine; engine = get_engine(); print('✅ Databases initialized')"
    
    Write-Success "Database initialization complete"
}
catch {
    Write-Warning "Database initialization had issues, but this may be resolved on first run: $_"
}

# ============================================================================
# POST-INSTALLATION CONFIGURATION
# ============================================================================

Write-Header "POST-INSTALLATION SETUP"

# Check for .env file
if (-not (Test-Path ".env")) {
    Write-Info "Creating .env file with default configuration..."
    @"
# Sentinel Agent Configuration
# Generated by installation script

# Ollama Configuration
OLLAMA_MODEL=llama3:8b
OLLAMA_HOST=http://localhost:11434

# API Configuration
API_HOST=127.0.0.1
API_PORT=8000
API_WORKERS=1

# Dashboard Configuration
DASHBOARD_PORT=8501

# Logging Configuration
LOG_LEVEL=INFO

# Analytics (optional)
ENABLE_METRICS=true
ENABLE_ANOMALY_DETECTION=true

# Feature Flags
ENABLE_THREAT_INTELLIGENCE=true
ENABLE_AUTHENTICATION=true
ENABLE_API=true
"@ | Out-File -Encoding UTF8 ".env"
    Write-Success ".env file created with default configuration"
} else {
    Write-Info ".env file already exists, skipping creation"
}

# ============================================================================
# VERIFICATION
# ============================================================================

Write-Header "INSTALLATION VERIFICATION"

# Verify all key files exist
$keyFiles = @(
    "main.py",
    "requirements.txt",
    "data_engine.py",
    "tasks.py",
    "threat_intelligence.py",
    "auth.py",
    "list_manager.py",
    "metrics.py",
    "sentinel_api.py",
    "anomaly_scorer.py"
)

$allFilesExist = $true
foreach ($file in $keyFiles) {
    if (Test-Path $file) {
        Write-Success "Found: $file"
    } else {
        Write-Error-Custom "Missing: $file"
        $allFilesExist = $false
    }
}

if (-not $allFilesExist) {
    Write-Error-Custom "Some key files are missing! Installation may be incomplete."
    exit 1
}

Write-Host ""
Write-Header "✅ INSTALLATION COMPLETE"

Write-Host "
╔════════════════════════════════════════════════════════════════════════════╗
║                    NEXT STEPS - GET STARTED IN 2 MINUTES                   ║
╚════════════════════════════════════════════════════════════════════════════╝

 PRE-REQUISITES:
   1. Ensure Ollama is running:
       ollama serve
      
   2. Verify Ollama has llama3:8b model:
       ollama pull llama3:8b

 START THE SYSTEM:

   Terminal 1 - Activate and Run Core System:
       .\venv\Scripts\Activate.ps1
       python main.py

   Terminal 2 - Start REST API (optional):
       .\venv\Scripts\Activate.ps1
       python sentinel_api.py
      
   Terminal 3 - Start Streamlit Dashboard (optional):
       .\venv\Scripts\Activate.ps1
       streamlit run dashboard/web_dashboard.py

 ACCESS POINTS:
   • REST API:        http://localhost:8000
   • Dashboard:       http://localhost:8501
   • Main System:     Console output in Terminal 1

 DOCUMENTATION:
   • README.md:            Project overview
   • docs_markdown/*:       Comprehensive guides
   • docs_markdown/INDEX.md: Documentation navigator

⚠️  TROUBLESHOOTING:
   • If Ollama fails: Check Ollama service is running
   • If modules missing: Ensure virtual environment is activated
   • If port conflicts: Edit .env to change ports

 FIRST RUN TEST:
   • The system will auto-initialize databases on first run
   • Sample data will be loaded for demonstrations
   • Check console output for status messages

" -ForegroundColor $Colors.Info

Write-Host "Virtual environment is ready! All dependencies installed." -ForegroundColor $Colors.Success
Write-Host "Run the commands above to start the Sentinel Agent." -ForegroundColor $Colors.Success
