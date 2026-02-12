@echo off
REM CLI Dashboard Launcher for Windows
REM Ensures database initialization before starting dashboard

echo ============================================================
echo Sentinel Agent - CLI Dashboard Launcher
echo ============================================================
echo.

REM Step 1: Initialize databases
echo [1/2] Initializing databases...
python init_database.py
if errorlevel 1 (
    echo Warning: Database initialization had issues
    echo Attempting to continue anyway...
)
echo.

REM Step 2: Launch dashboard
echo [2/2] Starting CLI dashboard...
echo.
python dashboard\cli_dashboard.py

echo.
echo Dashboard stopped
pause
