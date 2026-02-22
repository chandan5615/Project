@echo off
REM Fix Ollama Connection - Upload updated files and restart container

echo ==========================================
echo Fixing Ollama Connection Issue
echo ==========================================
echo.

set SERVER=ubuntu@192.168.31.91
set PROJECT_DIR=~/Project

echo [1/5] Uploading Dockerfile (with line ending fix)...
scp Dockerfile %SERVER%:%PROJECT_DIR%/

echo.
echo [2/5] Uploading docker-compose.yml...
scp docker-compose.yml %SERVER%:%PROJECT_DIR%/

echo.
echo [3/5] Uploading docker-entrypoint.sh...
scp docker-entrypoint.sh %SERVER%:%PROJECT_DIR%/

echo.
echo [4/5] Stopping container...
ssh %SERVER% "cd %PROJECT_DIR% && docker-compose down"

echo.
echo [5/5] Rebuilding container (this will fix line endings automatically)...
ssh %SERVER% "cd %PROJECT_DIR% && docker-compose up -d --build"

echo.
echo ==========================================
echo ✓ Fix applied!
echo ==========================================
echo.
echo The container should now connect to Ollama at:
echo   - http://host.docker.internal:11434
echo   - http://192.168.31.91:11434
echo.
echo Check logs with:
echo   ssh %SERVER% "cd %PROJECT_DIR% && docker-compose logs -f sentinel-agent"
echo.
pause
