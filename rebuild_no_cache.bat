@echo off
REM Force complete rebuild without Docker cache

echo ==========================================
echo Forcing Complete Rebuild (No Cache)
echo ==========================================
echo.

set SERVER=ubuntu@10.87.146.89
set PROJECT_DIR=~/Project

echo [1/6] Uploading Dockerfile...
scp Dockerfile %SERVER%:%PROJECT_DIR%/

echo.
echo [2/6] Uploading docker-compose.yml...
scp docker-compose.yml %SERVER%:%PROJECT_DIR%/

echo.
echo [3/6] Uploading docker-entrypoint.sh...
scp docker-entrypoint.sh %SERVER%:%PROJECT_DIR%/

echo.
echo [4/6] Uploading docker-startup.sh...
scp docker-startup.sh %SERVER%:%PROJECT_DIR%/

echo.
echo [5/6] Stopping and removing old container...
ssh %SERVER% "cd %PROJECT_DIR% && docker-compose down"

echo.
echo [6/6] Building from scratch (no cache - this will take 3-5 minutes)...
ssh %SERVER% "cd %PROJECT_DIR% && docker-compose build --no-cache && docker-compose up -d"

echo.
echo ==========================================
echo ✓ Complete rebuild finished!
echo ==========================================
echo.
echo The container should now connect to Ollama.
echo.
echo Check logs with:
echo   ssh %SERVER% "cd %PROJECT_DIR% && docker-compose logs -f sentinel-agent"
echo.
echo Look for:
echo   [SUCCESS] Found Ollama via host.docker.internal
echo.
pause
