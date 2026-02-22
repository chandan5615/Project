#!/usr/bin/env python3
"""
============================================================================
Sentinel Agent - Cross-Platform Professional Installation Script
============================================================================
This Python-based installer provides a platform-independent installation
with full dependency checking, validation, and post-installation setup.

Usage:
    python install.py [--skip-ollama] [--skip-python-check] [--dev]
"""

import sys
import os
import subprocess
import platform
import shutil
import argparse
from pathlib import Path
from typing import Tuple, List

# Color codes
class Colors:
    SUCCESS = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    INFO = '\033[94m'
    HEADER = '\033[95m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def is_windows():
    return platform.system() == "Windows"

def is_macos():
    return platform.system() == "Darwin"

def is_linux():
    return platform.system() == "Linux"

def write_header(text: str):
    """Print formatted header"""
    print()
    print(f"{Colors.HEADER}{'=' * 78}{Colors.ENDC}")
    print(f"{Colors.HEADER}{text.center(78)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{'=' * 78}{Colors.ENDC}")
    print()

def write_success(text: str):
    """Print success message"""
    print(f"{Colors.SUCCESS}✅ {text}{Colors.ENDC}")

def write_warning(text: str):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def write_error(text: str):
    """Print error message"""
    print(f"{Colors.ERROR}❌ {text}{Colors.ENDC}")

def write_info(text: str):
    """Print info message"""
    print(f"{Colors.INFO}ℹ️  {text}{Colors.ENDC}")

def run_command(cmd: List[str], silent: bool = False) -> Tuple[bool, str]:
    """Run a command and return success status and output"""
    try:
        if silent:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                shell=False,
                check=False
            )
        else:
            result = subprocess.run(
                cmd,
                capture_output=False,
                text=True,
                shell=False,
                check=False
            )
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)

def check_python_version() -> bool:
    """Check if Python 3.10+ is installed"""
    print("[STEP 1/8] Checking Python Installation...")
    
    version_info = sys.version_info
    version_string = f"Python {version_info.major}.{version_info.minor}.{version_info.micro}"
    
    if version_info.major < 3 or (version_info.major == 3 and version_info.minor < 10):
        write_error(f"Python 3.10+ is required. Current: {version_string}")
        write_info("Download Python from: https://www.python.org/downloads/")
        return False
    
    write_success(f"Python found: {version_string}")
    return True

def check_ollama() -> bool:
    """Check if Ollama is installed"""
    print()
    print("[STEP 2/8] Checking Ollama Installation...")
    
    # Try to get ollama version
    success, output = run_command(["ollama", "--version"], silent=True)
    
    if success:
        write_success(f"Ollama found: {output.strip()}")
        write_info("Ensure Ollama service is running: ollama serve")
        return True
    else:
        write_warning("Ollama is not installed or not in PATH")
        write_info("Ollama is required for AI features")
        write_info("Download from: https://ollama.ai")
        write_warning("Continuing installation, but Ollama must be installed later")
        return False

def check_system_dependencies() -> bool:
    """Check for required system packages"""
    print()
    print("[STEP 3/8] Checking System Dependencies...")
    
    if is_linux():
        write_info("Checking for build tools...")
        success, _ = run_command(["gcc", "--version"], silent=True)
        if success:
            write_success("Build tools found")
        else:
            write_warning("gcc not found. Some packages may fail to compile.")
            write_info("Install with: sudo apt-get install build-essential python3-dev")
    else:
        write_success("System check skipped (Windows/macOS)")
    
    return True

def setup_venv() -> bool:
    """Create virtual environment"""
    print()
    print("[STEP 4/8] Preparing Virtual Environment...")
    
    venv_path = Path("venv")
    if venv_path.exists():
        write_warning("Existing virtual environment found. Removing...")
        shutil.rmtree(venv_path)
        write_success("Old environment removed")
    
    print()
    print("[STEP 5/8] Creating Virtual Environment...")
    success, output = run_command([sys.executable, "-m", "venv", "venv"])
    
    if not success:
        write_error(f"Failed to create virtual environment: {output}")
        return False
    
    write_success("Virtual environment created")
    return True

def upgrade_pip() -> bool:
    """Upgrade pip and install tools"""
    print()
    print("[STEP 6/8] Upgrading pip and Installation Tools...")
    
    if is_windows():
        pip_cmd = [".\\venv\\Scripts\\python.exe", "-m", "pip", "install", "--upgrade", 
                   "pip", "setuptools", "wheel", "--quiet"]
    else:
        pip_cmd = ["./venv/bin/python", "-m", "pip", "install", "--upgrade",
                   "pip", "setuptools", "wheel", "--quiet"]
    
    success, output = run_command(pip_cmd)
    if not success:
        write_error(f"Failed to upgrade pip: {output}")
        return False
    
    write_success("pip upgraded successfully")
    return True

def install_requirements() -> bool:
    """Install project dependencies"""
    print()
    print("[STEP 7/8] Installing Project Dependencies...")
    
    if not Path("requirements.txt").exists():
        write_error("requirements.txt not found!")
        return False
    
    if is_windows():
        pip_cmd = [".\\venv\\Scripts\\pip.exe", "install", "-r", "requirements.txt"]
    else:
        pip_cmd = ["./venv/bin/pip", "install", "-r", "requirements.txt"]
    
    write_info("This may take 2-5 minutes...")
    success, output = run_command(pip_cmd)
    
    if not success:
        write_error(f"Failed to install requirements: {output}")
        return False
    
    write_success("All dependencies installed successfully")
    return True

def initialize_databases() -> bool:
    """Initialize databases"""
    print()
    print("[STEP 8/8] Initializing Databases...")
    
    # Create data directory
    data_path = Path("data")
    if not data_path.exists():
        data_path.mkdir(parents=True)
        write_success("Data directory created")
    
    # Initialize databases
    if is_windows():
        python_cmd = ".\\venv\\Scripts\\python.exe"
    else:
        python_cmd = "./venv/bin/python"
    
    try:
        result = subprocess.run(
            [python_cmd, "-c", "from data_engine import get_engine; engine = get_engine()"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            write_success("Database initialization complete")
        else:
            write_warning("Database initialization skipped (will be done on first run)")
    except subprocess.TimeoutExpired:
        write_warning("Database initialization timed out (will be done on first run)")
    except Exception as e:
        write_warning(f"Database initialization had issues: {e}")
    
    return True

def create_env_file() -> bool:
    """Create .env configuration file"""
    write_header("POST-INSTALLATION SETUP")
    
    env_path = Path(".env")
    if env_path.exists():
        write_info(".env file already exists, skipping creation")
        return True
    
    write_info("Creating .env file with default configuration...")
    
    env_content = """# Sentinel Agent Configuration
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
"""
    
    try:
        env_path.write_text(env_content)
        write_success(".env file created with default configuration")
        return True
    except Exception as e:
        write_error(f"Failed to create .env file: {e}")
        return False

def verify_installation() -> bool:
    """Verify all key files exist"""
    write_header("INSTALLATION VERIFICATION")
    
    key_files = [
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
    ]
    
    all_exist = True
    for file in key_files:
        if Path(file).exists():
            write_success(f"Found: {file}")
        else:
            write_error(f"Missing: {file}")
            all_exist = False
    
    return all_exist

def print_next_steps():
    """Print next steps"""
    print()
    write_header("✅ INSTALLATION COMPLETE")
    
    if is_windows():
        activate_cmd = ".\\venv\\Scripts\\Activate.ps1"
        run_main = "python main.py"
        run_api = "python sentinel_api.py"
        run_dash = "streamlit run dashboard/web_dashboard.py"
    else:
        activate_cmd = "source venv/bin/activate"
        run_main = "python main.py"
        run_api = "python sentinel_api.py"
        run_dash = "streamlit run dashboard/web_dashboard.py"
    
    next_steps = f"""
╔════════════════════════════════════════════════════════════════════════════╗
║                    NEXT STEPS - GET STARTED IN 2 MINUTES                   ║
╚════════════════════════════════════════════════════════════════════════════╝

📋 PRE-REQUISITES:
   1. Ensure Ollama is running:
      💻 ollama serve
      
   2. Verify Ollama has llama3:8b model:
      💻 ollama pull llama3:8b

📊 START THE SYSTEM:

   Terminal 1 - Activate and Run Core System:
      💻 {activate_cmd}
      💻 {run_main}

   Terminal 2 - Start REST API (optional):
      💻 {activate_cmd}
      💻 {run_api}
      
   Terminal 3 - Start Streamlit Dashboard (optional):
      💻 {activate_cmd}
      💻 {run_dash}

🔗 ACCESS POINTS:
   • REST API:        http://localhost:8000
   • Dashboard:       http://localhost:8501
   • Main System:     Console output in Terminal 1

📚 DOCUMENTATION:
   • README.md:            Project overview
   • docs_markdown/*:       Comprehensive guides
   • docs_markdown/INDEX.md: Documentation navigator

⚠️  TROUBLESHOOTING:
   • If Ollama fails: Check Ollama service is running
   • If modules missing: Ensure virtual environment is activated
   • If port conflicts: Edit .env to change ports

🎯 FIRST RUN TEST:
   • The system will auto-initialize databases on first run
   • Sample data will be loaded for demonstrations
   • Check console output for status messages
"""
    
    print(next_steps)
    write_success("Virtual environment is ready! All dependencies installed.")
    write_success("Run the commands above to start the Sentinel Agent.")

def main():
    """Main installation routine"""
    parser = argparse.ArgumentParser(
        description="Sentinel Agent Installation Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python install.py                    # Standard installation
  python install.py --skip-ollama      # Skip Ollama check
  python install.py --dev              # Development mode
        """
    )
    
    parser.add_argument(
        "--skip-ollama",
        action="store_true",
        help="Skip Ollama installation check"
    )
    parser.add_argument(
        "--skip-python-check",
        action="store_true",
        help="Skip Python version check"
    )
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Development mode installation"
    )
    
    args = parser.parse_args()
    
    try:
        # Step 1: Check Python
        if not args.skip_python_check and not check_python_version():
            sys.exit(1)
        
        # Step 2: Check Ollama
        if not args.skip_ollama:
            check_ollama()
        else:
            write_warning("Skipping Ollama check (--skip-ollama)")
        
        # Step 3: Check system dependencies
        if not check_system_dependencies():
            sys.exit(1)
        
        # Step 4-5: Setup venv
        if not setup_venv():
            sys.exit(1)
        
        # Step 6: Upgrade pip
        if not upgrade_pip():
            sys.exit(1)
        
        # Step 7: Install requirements
        if not install_requirements():
            sys.exit(1)
        
        # Step 8: Initialize databases
        if not initialize_databases():
            write_warning("Database initialization failed, will retry on first run")
        
        # Create configuration
        if not create_env_file():
            write_warning("Failed to create .env file, please create manually")
        
        # Verify installation
        if not verify_installation():
            write_error("Installation verification failed!")
            sys.exit(1)
        
        # Print next steps
        print_next_steps()
        
    except KeyboardInterrupt:
        print()
        write_warning("Installation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print()
        write_error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
