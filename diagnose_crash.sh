#!/bin/bash
# Complete Container Diagnostic Script
# Checks why container is crashing/restarting

echo "============================================================"
echo "Sentinel Agent - Container Crash Diagnostics"
echo "============================================================"
echo ""

# Check container status
echo "[1/5] Checking container status..."
STATUS=$(docker-compose ps sentinel-agent 2>/dev/null | grep sentinel-agent | awk '{print $4}')

echo "Container state: $STATUS"

if [ "$STATUS" = "Restarting" ]; then
    echo "⚠ Container is in RESTART LOOP (crashing repeatedly)"
    echo ""
    
    echo "[2/5] Getting last 100 lines of container logs..."
    echo "================================================================"
    docker-compose logs --tail=100 sentinel-agent
    echo "================================================================"
    echo ""
    
    echo "[3/5] Checking for common issues..."
    
    # Check for Python errors
    if docker-compose logs sentinel-agent 2>/dev/null | grep -qi "ModuleNotFoundError\|ImportError"; then
        echo "✗ FOUND: Python import errors"
        echo "  Issue: Missing Python dependencies"
        echo "  Fix: Rebuild container with --no-cache"
    fi
    
    # Check for port conflicts
    if docker-compose logs sentinel-agent 2>/dev/null | grep -qi "Address already in use"; then
        echo "✗ FOUND: Port conflict"
        echo "  Issue: Port 8000 or 8501 already in use"
        echo "  Fix: Stop conflicting service or change ports"
    fi
    
    # Check for Ollama connection
    if docker-compose logs sentinel-agent 2>/dev/null | grep -qi "ollama.*refused\|ollama.*timeout"; then
        echo "⚠ FOUND: Ollama connection issues"
        echo "  Issue: Cannot connect to Ollama"
        echo "  Note: This is usually OK, agent will continue without AI"
    fi
    
    # Check for database errors
    if docker-compose logs sentinel-agent 2>/dev/null | grep -qi "database.*error\|sqlite.*error"; then
        echo "✗ FOUND: Database errors"
        echo "  Issue: Database initialization failed"
        echo "  Fix: Remove data/ folder and restart"
    fi
    
    # Check for permission errors
    if docker-compose logs sentinel-agent 2>/dev/null | grep -qi "permission denied"; then
        echo "✗ FOUND: Permission errors"
        echo "  Issue: File/folder permission problems"
        echo "  Fix: Check ownership of data/ and logs/ folders"
    fi
    
    echo ""
    echo "[4/5] Attempting to identify the exact error..."
    
    # Get the last error before crash
    LAST_ERROR=$(docker-compose logs sentinel-agent 2>/dev/null | grep -i "error\|exception\|traceback" | tail -5)
    
    if [ ! -z "$LAST_ERROR" ]; then
        echo "Last errors found:"
        echo "$LAST_ERROR"
    else
        echo "No obvious errors in logs (check full logs above)"
    fi
    
    echo ""
    echo "[5/5] Recommended fixes:"
    echo ""
    echo "1. Check the full logs above for the actual error"
    echo ""
    echo "2. If it's a Python import error:"
    echo "   docker-compose down"
    echo "   docker-compose build --no-cache"
    echo "   docker-compose up -d"
    echo ""
    echo "3. If it's a port conflict:"
    echo "   sudo lsof -i :8000"
    echo "   sudo lsof -i :8501"
    echo "   # Kill the conflicting process"
    echo ""
    echo "4. If it's a database error:"
    echo "   docker-compose down"
    echo "   rm -rf data/"
    echo "   docker-compose up -d"
    echo ""
    echo "5. If it's a permissions error:"
    echo "   sudo chown -R $USER:$USER data/ logs/"
    echo "   docker-compose restart sentinel-agent"

elif [ "$STATUS" = "Up" ]; then
    echo "✓ Container is running"
    
    # Check if healthy
    if docker-compose ps sentinel-agent | grep -q "healthy"; then
        echo "✓ Container is healthy"
        echo ""
        echo "All systems operational!"
    else
        echo "⚠ Container is running but not healthy yet"
        echo ""
        echo "Give it more time or check health with:"
        echo "  docker-compose logs -f sentinel-agent"
    fi
    
else
    echo "✗ Container is not running"
    echo ""
    echo "Start it with:"
    echo "  docker-compose up -d"
fi

echo ""
echo "============================================================"
echo "Diagnostics complete"
echo "============================================================"
