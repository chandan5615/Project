@echo off
REM ###############################################################################
REM                                                                               
REM               SENTINEL AGENT v2.2 - WINDOWS SETUP HELPER                      
REM                                                                               
REM  This script helps set up Sentinel Agent for testing on Windows.             
REM  For production deployment, use the Linux installer on Ubuntu server.        
REM                                                                               
REM ###############################################################################

setlocal enabledelayedexpansion

REM Colors (using Windows 10+ ANSI support)
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "CYAN=[96m"
set "NC=[0m"

cls
echo ================================================================================
echo.
echo                  SENTINEL AGENT v2.2 - WINDOWS SETUP
echo.
echo              AI-Powered Security Monitoring System
echo.
echo ================================================================================
echo.
echo  This script will help you:
echo    1. Check prerequisites (Python, Git, Docker Desktop)
echo    2. Install Python packages
echo    3. Connect to remote Ubuntu server
echo    4. Deploy Sentinel Agent on server
echo.
echo  %YELLOW%Note: For production, deploy on Linux/Ubuntu server%NC%
echo.
pause

echo.
echo ================================================================================
echo  STEP 1: Checking Prerequisites
echo ================================================================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%[ERROR]%NC% Python is not installed!
    echo.
    echo Please install Python 3.10+ from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
) else (
    for /f "tokens=*" %%i in ('python --version') do set PYTHON_VER=%%i
    echo %GREEN%[OK]%NC% !PYTHON_VER!
)

REM Check Git
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %YELLOW%[WARNING]%NC% Git is not installed
    echo Install from: https://git-scm.com/download/win
) else (
    for /f "tokens=*" %%i in ('git --version') do set GIT_VER=%%i
    echo %GREEN%[OK]%NC% !GIT_VER!
)

REM Check Docker Desktop
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %YELLOW%[WARNING]%NC% Docker Desktop is not installed
    echo Download from: https://www.docker.com/products/docker-desktop/
    echo %CYAN%Note:%NC% Docker is optional on Windows - use for local testing only
) else (
    for /f "tokens=*" %%i in ('docker --version') do set DOCKER_VER=%%i
    echo %GREEN%[OK]%NC% !DOCKER_VER!
)

REM Check SSH
ssh -V >nul 2>&1
if %errorlevel% neq 0 (
    echo %YELLOW%[WARNING]%NC% SSH client not found
    echo OpenSSH should be available on Windows 10+
) else (
    echo %GREEN%[OK]%NC% SSH client available
)

echo.
echo ================================================================================
echo  STEP 2: Installing Python Dependencies
echo ================================================================================
echo.

echo Installing required Python packages...
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

if %errorlevel% equ 0 (
    echo %GREEN%[SUCCESS]%NC% Python packages installed
) else (
    echo %RED%[ERROR]%NC% Failed to install packages
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo  STEP 3: Configuration
echo ================================================================================
echo.

set /p "USE_REMOTE=Do you want to deploy to a remote Ubuntu server? (Y/N): "

if /i "%USE_REMOTE%"=="Y" (
    echo.
    echo Enter your Ubuntu server details:
    set /p "SERVER_IP=Server IP address (e.g., 10.87.146.89): "
    set /p "SERVER_USER=Username (default: ubuntu): "
    if "!SERVER_USER!"=="" set "SERVER_USER=ubuntu"
    
    echo.
    echo Testing connection to !SERVER_USER!@!SERVER_IP!...
    ssh -o ConnectTimeout=5 !SERVER_USER!@!SERVER_IP! "echo Connected successfully"
    
    if %errorlevel% equ 0 (
        echo %GREEN%[SUCCESS]%NC% Connection successful!
        
        echo.
        echo ================================================================================
        echo  STEP 4: Deploying to Server
        echo ================================================================================
        echo.
        
        echo Copying files to server...
        scp -r * !SERVER_USER!@!SERVER_IP!:~/Project/
        
        echo.
        echo Running installer on server...
        echo.
        echo %CYAN%The server will now install Docker, Ollama, and Sentinel Agent%NC%
        echo %CYAN%This may take 10-15 minutes...%NC%
        echo.
        
        ssh -t !SERVER_USER!@!SERVER_IP! "cd ~/Project && chmod +x AUTO_INSTALL.sh && sudo ./AUTO_INSTALL.sh"
        
        echo.
        echo ================================================================================
        echo  DEPLOYMENT COMPLETE!
        echo ================================================================================
        echo.
        echo %GREEN%Access your Sentinel Agent at:%NC%
        echo   Dashboard: http://!SERVER_IP!:8501
        echo   API:       http://!SERVER_IP!:8000
        echo.
        echo %CYAN%Default Login:%NC%
        echo   Username: sentinel
        echo   Password: sentinel
        echo.
        echo %YELLOW%Test attacks from this Windows machine:%NC%
        echo   python test_web_attacks.py
        echo   python continuous_attacks.py --interval 10 --duration 5
        echo.
        
    ) else (
        echo %RED%[ERROR]%NC% Cannot connect to server
        echo.
        echo Troubleshooting:
        echo   1. Check if server IP is correct
        echo   2. Ensure SSH is enabled on server: sudo systemctl status ssh
        echo   3. Check firewall allows SSH: sudo ufw allow 22
        echo   4. Verify you can ping the server: ping !SERVER_IP!
        echo.
        pause
        exit /b 1
    )
) else (
    echo.
    echo ================================================================================
    echo  Local Testing Mode
    echo ================================================================================
    echo.
    echo %YELLOW%Note:%NC% Full Sentinel Agent requires Linux/Docker
    echo.
    echo You can test individual components:
    echo   1. Attack generator: python test_web_attacks.py
    echo   2. Log analyzer: python main.py (requires Apache logs)
    echo   3. Dashboard mockup: cd dashboard ^&^& python app.py
    echo.
    echo %GREEN%For production deployment:%NC%
    echo   1. Set up an Ubuntu server   2. Run this script again and choose "Y" for remote deployment
    echo   - OR -
    echo   3. Manually copy files to server and run: sudo ./AUTO_INSTALL.sh
    echo.
)

echo.
echo ================================================================================
echo  Quick Reference
echo ================================================================================
echo.
echo %CYAN%Windows Commands (Attack Testing):%NC%
echo   python test_web_attacks.py              - One-time attack burst
echo   python continuous_attacks.py            - Continuous attack stream
echo   python check_crewai_api.py              - Verify CrewAI installation
echo.
echo %CYAN%Connect to Server:%NC%
if not "!SERVER_IP!"=="" (
    echo   ssh !SERVER_USER!@!SERVER_IP!                  - SSH login
    echo   scp file.txt !SERVER_USER!@!SERVER_IP!:~/      - Copy files
)
echo.
echo %CYAN%Server Commands (via SSH):%NC%
echo   docker-compose logs -f                  - View live logs
echo   docker-compose restart                  - Restart containers
echo   docker-compose ps                       - Container status
echo   sudo ./AUTO_INSTALL.sh                  - Re-run installer
echo.

pause
endlocal
