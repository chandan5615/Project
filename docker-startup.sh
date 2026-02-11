#!/bin/bash
# Sentinel Agent Docker Startup Script
# Starts both monitoring (main.py) and API (sentinel_api.py)

# Don't exit on errors - we want the API to start even if earlier steps fail
set +e

echo "Starting Sentinel Agent services..."
echo ""

# Initialize databases first
echo "[0/5] Initializing databases..."
if python init_database.py; then
    echo "      ✓ Databases initialized"
else
    echo "      ⚠ Database initialization had issues (continuing anyway)"
fi
echo ""

# Generate test attacks to verify detection is working
# NOTE: Skip in Docker because /var/log is mounted read-only
echo "[1/5] Checking test attacks..."
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
echo "[2/5] Starting Sentinel Agent monitor (main.py)..."
python main.py &
MAIN_PID=$!
echo "      ✓ Monitor started (PID: $MAIN_PID)"

# Give main.py time to detect the test attacks
echo ""
echo "[3/5] Waiting for agent to initialize (5 seconds)..."
sleep 5

# Start sentinel_api.py (REST API) in foreground
echo "[4/5] Starting REST API server (sentinel_api.py on port 8000)..."
echo "[5/5] Services ready!"
echo ""
echo "      API:       http://localhost:8000"
echo "      Dashboard: http://localhost:8501"
echo "      Health:    http://localhost:8000/api/health"
echo ""

# Run the API in foreground (so container doesn't exit)
# This MUST succeed for the container to stay running
exec python sentinel_api.py
