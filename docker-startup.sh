#!/bin/bash
# Sentinel Agent Docker Startup Script
# Starts both monitoring (main.py) and API (sentinel_api.py)

# Don't exit on errors - we want the API to start even if earlier steps fail
set +e

echo "Starting Sentinel Agent services..."
echo ""

# Ensure permissions are correct (run as root in container)
echo "[0/6] Setting up permissions..."
chmod -R 777 /app/data /app/logs 2>/dev/null || true
echo "      ✓ Permissions set"
echo ""

# Initialize databases first
echo "[1/6] Initializing databases..."
if python init_database.py 2>&1; then
    echo "      ✓ Databases initialized"
else
    echo "      ⚠ Database initialization had issues (continuing anyway)"
    echo "      This is normal if databases already exist"
fi
echo ""

# Generate test attacks to verify detection is working
# NOTE: Skip in Docker because /var/log is mounted read-only
echo "[2/6] Checking test attacks..."
if [ -w /var/log/auth.log ] 2>/dev/null; then
    echo "      Generating test attacks..."
    if python test_attacks.py --auth-count 20 --web-count 20 2>/dev/null; then
        echo "      ✓ Test attacks generated"
    else
        echo "      ⚠ Could not generate test attacks"
    fi
else
    echo "      ⚠ Skipping test attacks (logs not writable in Docker)"
    echo "      You can generate attacks from outside the container"
fi
echo ""

# Start main.py (monitoring) in background
echo "[3/6] Starting Sentinel Agent monitor (main.py)..."
python main.py 2>&1 &
MAIN_PID=$!
echo "      ✓ Monitor started (PID: $MAIN_PID)"

# Give main.py time to initialize
echo ""
echo "[4/6] Waiting for agent to initialize (5 seconds)..."
sleep 5

# Check if main.py is still running
if kill -0 $MAIN_PID 2>/dev/null; then
    echo "      ✓ Monitor is running"
else
    echo "      ⚠ Monitor may have crashed (check logs)"
fi
echo ""

# Start sentinel_api.py (REST API) in foreground
echo "[5/6] Starting REST API server (sentinel_api.py on port 8000)..."
echo "[6/6] Services ready!"
echo ""
echo "      API:       http://localhost:8000"
echo "      Dashboard: http://localhost:8501"
echo "      Health:    http://localhost:8000/api/health"
echo ""
echo "Starting API server..."
echo ""

# Run the API in foreground (so container doesn't exit)
# Use explicit error logging
if ! python sentinel_api.py 2>&1; then
    echo ""
    echo "ERROR: sentinel_api.py crashed!"
    echo "Check logs above for details"
    echo ""
    # Keep container alive for debugging
    echo "Keeping container alive for 1 hour for debugging..."
    sleep 3600
    exit 1
fi
