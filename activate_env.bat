@echo off
REM Quick activation script for Sentinel Agent virtual environment

if not exist "venv" (
    echo ❌ Virtual environment not found!
    echo Run setup.bat first to create the environment.
    pause
    exit /b 1
)

echo ✅ Activating virtual environment...
call venv\Scripts\activate.bat

echo ✅ Environment activated!
echo You can now run: sudo python main.py
echo.
echo To deactivate later, run: deactivate
echo.
