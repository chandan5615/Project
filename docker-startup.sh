#!/bin/bash
# Sentinel Agent Docker Startup Script
# Starts both monitoring (main.py) and API (sentinel_api.py)

set -e

echo "Starting Sentinel Agent services..."
echo ""

# Start main.py (monitoring) in background
echo "[1/2] Starting Sentinel Agent monitor (main.py)..."
python main.py &
MAIN_PID=$!
echo "      Monitor started (PID: $MAIN_PID)"

# Give main.py a moment to initialize
sleep 3

# Start sentinel_api.py (REST API) in foreground
echo "[2/2] Starting REST API server (sentinel_api.py on port 8000)..."
echo ""

# Run the API in foreground (so container doesn't exit)
python sentinel_api.py
