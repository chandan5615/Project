@echo off
REM Sentinel Agent - Setup Script for Windows CMD
REM Creates a virtual environment and installs all dependencies

echo 🚀 Setting up Sentinel Agent environment...

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo ✅ Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

echo.
echo ✅ Setup complete!
echo.
echo To activate the environment, run:
echo   venv\Scripts\activate.bat
echo.
echo Note: On Windows, this project requires WSL or a Linux environment
echo for full functionality (auth.log monitoring and iptables).
echo.

pause
