@echo off
REM Docker Installation & Health Check Script for Sentinel Agent (Windows)
REM Verifies Docker Desktop setup, services, and connectivity

setlocal enabledelayedexpansion

REM Counters
set TESTS_PASSED=0
set TESTS_FAILED=0

cls
echo.
echo ================================================
echo   SENTINEL AGENT - DOCKER HEALTH CHECK (Windows)
echo ================================================
echo.

REM ========================================================================
REM 1. SYSTEM REQUIREMENTS
REM ========================================================================
echo [1] SYSTEM REQUIREMENTS CHECK
echo ================================================
echo.

REM Check Docker installed
echo Checking: Docker installed...
docker --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    for /f "tokens=*" %%A in ('docker --version') do echo   OK: %%A
    set /a TESTS_PASSED+=1
) else (
    echo   ERROR: Docker not found
    echo   Install from: https://www.docker.com/products/docker-desktop
    set /a TESTS_FAILED+=1
)

REM Check Docker daemon running
echo.
echo Checking: Docker daemon running...
docker info >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   OK: Docker daemon is running
    set /a TESTS_PASSED+=1
) else (
    echo   ERROR: Docker daemon not running
    echo   Start Docker Desktop from Windows Start menu
    set /a TESTS_FAILED+=1
)

REM Check Docker Compose installed
echo.
echo Checking: Docker Compose installed...
docker-compose --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    for /f "tokens=*" %%A in ('docker-compose --version') do echo   OK: %%A
    set /a TESTS_PASSED+=1
) else (
    echo   ERROR: Docker Compose not found
    echo   It should be included with Docker Desktop
    set /a TESTS_FAILED+=1
)

REM Check disk space
echo.
echo Checking: Disk space ^(need 10GB minimum^)...
for /f "tokens=3" %%A in ('dir /-S ^| find "bytes free"') do set DISK_FREE=%%A
if defined DISK_FREE (
    echo   Available disk space detected
    set /a TESTS_PASSED+=1
) else (
    echo   WARNING: Could not determine disk space
)

REM ========================================================================
REM 2. PROJECT STRUCTURE
REM ========================================================================
echo.
echo [2] PROJECT FILES CHECK
echo ================================================
echo.

REM Check required files
setlocal enabledelayedexpansion
for %%F in (docker-compose.yml Dockerfile docker-entrypoint.sh requirements.txt main.py) do (
    if exist "%%F" (
        echo   OK: %%F
        set /a TESTS_PASSED+=1
    ) else (
        echo   ERROR: %%F not found
        set /a TESTS_FAILED+=1
    )
)

REM ========================================================================
REM 3. DOCKER IMAGES
REM ========================================================================
echo.
echo [3] DOCKER IMAGES CHECK
echo ================================================
echo.

echo Checking: Sentinel Agent image...
docker images 2>nul | findstr "sentinel-agent" >nul
if %ERRORLEVEL% EQU 0 (
    echo   OK: sentinel-agent image found
    set /a TESTS_PASSED+=1
) else (
    echo   WARNING: No sentinel-agent image found
    echo   It will be built on first run with: docker-compose build
)

REM ========================================================================
REM 4. DOCKER SERVICES
REM ========================================================================
echo.
echo [4] DOCKER SERVICES CHECK
echo ================================================
echo.

echo Checking: Network sentinel-network...
docker network ls 2>nul | findstr "sentinel-network" >nul
if %ERRORLEVEL% EQU 0 (
    echo   OK: sentinel-network exists
    set /a TESTS_PASSED+=1
) else (
    echo   INFO: Network will be created on first run
)

echo.
echo Checking: Services defined in docker-compose...
if exist docker-compose.yml (
    echo   OK: docker-compose.yml found
    set /a TESTS_PASSED+=1
) else (
    echo   ERROR: docker-compose.yml not found
    set /a TESTS_FAILED+=1
)

REM ========================================================================
REM 5. PORT AVAILABILITY
REM ========================================================================
echo.
echo [5] PORT AVAILABILITY CHECK
echo ================================================
echo.

REM Check common ports
for %%P in (8000 8501 11434) do (
    echo Checking: Port %%P available...
    netstat -ano 2>nul | findstr ":%%P " >nul
    if %ERRORLEVEL% EQU 0 (
        echo   WARNING: Port %%P is already in use
    ) else (
        echo   OK: Port %%P available
        set /a TESTS_PASSED+=1
    )
)

REM ========================================================================
REM 6. DOCKER-COMPOSE VALIDATION
REM ========================================================================
echo.
echo [6] DOCKER-COMPOSE VALIDATION
echo ================================================
echo.

echo Checking: docker-compose.yml syntax...
docker-compose config >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   OK: docker-compose.yml syntax valid
    set /a TESTS_PASSED+=1
) else (
    echo   ERROR: Invalid docker-compose.yml syntax
    set /a TESTS_FAILED+=1
)

REM ========================================================================
REM 7. CONNECTIVITY TESTS
REM ========================================================================
echo.
echo [7] CONNECTIVITY TESTS
echo ================================================
echo.

REM Check if containers are running
docker-compose ps 2>nul | findstr "Up" >nul
set RUNNING=%ERRORLEVEL%

if %RUNNING% EQU 0 (
    echo Checking: Sentinel API responding...
    curl -s -f http://localhost:8000/api/health >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo   OK: API is responding
        set /a TESTS_PASSED+=1
    ) else (
        echo   WARNING: API not responding (may still be starting)
    )

    echo.
    echo Checking: Ollama responding...
    curl -s -f http://localhost:11434/api/tags >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo   OK: Ollama is responding
        set /a TESTS_PASSED+=1
    ) else (
        echo   INFO: Ollama not running (optional)
    )
) else (
    echo   INFO: Services not running yet
    echo   Start with: docker-compose up -d
)

REM ========================================================================
REM 8. SUMMARY
REM ========================================================================
echo.
echo [8] TEST SUMMARY
echo ================================================
echo.
echo Tests Passed: %TESTS_PASSED%
echo Tests Failed: %TESTS_FAILED%
echo.

if %TESTS_FAILED% EQU 0 (
    echo ✓ All checks passed! Ready to deploy.
    echo.
    echo Next steps:
    echo   1. docker-compose build
    echo   2. docker-compose up -d
    echo   3. docker-compose logs -f
    echo.
    pause
    exit /b 0
) else (
    echo ✗ Some checks failed. See above for details.
    echo.
    pause
    exit /b 1
)
