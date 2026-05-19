@echo off
REM ========================================
REM SENTINEL AGENT - ATTACK TEST LAUNCHER
REM ========================================
echo.
echo ========================================
echo SENTINEL AGENT - ATTACK TEST LAUNCHER
echo ========================================
echo.
echo This will launch REAL attacks against:
echo   Target: http://10.87.146.89 (Apache)
echo.
echo Attack types:
echo   - SQL Injection
echo   - XSS (Cross-Site Scripting)
echo   - Path Traversal
echo   - Command Injection
echo   - Suspicious User-Agents
echo   - DoS Simulation
echo.
echo Monitor results:
echo   Dashboard: http://10.87.146.89:8501
echo   API:       http://10.87.146.89:8000/api/attacks
echo.
pause

echo.
echo [*] Launching web attacks...
python test_web_attacks.py

echo.
echo ========================================
echo ATTACKS COMPLETED!
echo ========================================
echo.
echo Next steps:
echo   1. Open dashboard: http://10.87.146.89:8501
echo   2. Login with: sentinel / sentinel
echo   3. View detected attacks in real-time
echo.
pause
