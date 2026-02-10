#!/bin/bash
# Sentinel Agent Docker Startup Script
# Starts both monitoring (main.py) and API (sentinel_api.py)

set -e

echo "Starting Sentinel Agent services..."
echo ""

# Initialize databases first
echo "[0/4] Initializing databases..."
python init_database.py
echo ""

# Generate test attacks to verify detection is working
echo "[1/4] Generating test attacks for verification..."
python test_attacks.py --auth-count 20 --web-count 20
echo ""

# Start main.py (monitoring) in background
echo "[2/4] Starting Sentinel Agent monitor (main.py)..."
python main.py &
MAIN_PID=$!
echo "      Monitor started (PID: $MAIN_PID)"

# Give main.py time to detect the test attacks
echo ""
echo "      Waiting for agent to detect attacks..."
sleep 5

# Start sentinel_api.py (REST API) in foreground
echo "[3/4] Starting REST API server (sentinel_api.py on port 8000)..."
echo "[4/4] Dashboard available at http://localhost:8000"
echo ""

# Run the API in foreground (so container doesn't exit)
python sentinel_api.py
