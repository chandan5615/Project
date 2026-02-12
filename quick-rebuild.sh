#!/bin/bash
#
# Quick Rebuild - Fix python-multipart dependency
# Handles permission issues automatically
#

echo "============================================================"
echo "  Quick Rebuild - Adding Missing Dependency"
echo "============================================================"
echo ""
echo "Adding python-multipart to requirements..."
echo ""

# Stop container
echo "[1/4] Stopping container..."
docker-compose down

# Clean data with sudo (Docker creates files as root)
echo ""
echo "[2/4] Cleaning old data (requires sudo)..."
echo "This removes Docker-created files owned by root"
sudo rm -rf data/ logs/ 2>/dev/null || {
    echo "⚠ Could not remove data/logs (trying without sudo)..."
    rm -rf data/ logs/ 2>/dev/null || echo "⚠ Some files remain (will be overwritten)"
}
echo "✓ Cleaned"

# Rebuild (this will install python-multipart)
echo ""
echo "[3/4] Rebuilding container with python-multipart..."
echo "This will take 3-5 minutes..."
docker-compose build --no-cache

# Start
echo ""
echo "[4/4] Starting container..."
docker-compose up -d

echo ""
echo "============================================================"
echo "Waiting for container to start (60 seconds)..."
echo "============================================================"
echo ""

# Watch logs for 60 seconds
timeout 60 docker-compose logs -f sentinel-agent &
LOGS_PID=$!

# Wait for healthy status
for i in {1..60}; do
    sleep 1
    
    # Check if healthy
    if docker-compose ps | grep -q "healthy"; then
        echo ""
        echo "============================================================"
        echo "✓ Container is HEALTHY!"
        echo "============================================================"
        kill $LOGS_PID 2>/dev/null || true
        break
    fi
    
    # Check if crashed
    if docker-compose ps | grep -q "Restarting"; then
        echo ""
        echo "✗ Container is restarting (check logs above)"
        kill $LOGS_PID 2>/dev/null || true
        exit 1
    fi
done

echo ""
echo "Getting admin password..."
sleep 2

PASSWORD=$(docker-compose logs sentinel-agent 2>/dev/null | grep "Password:" | tail -1 | awk '{print $NF}')

if [ -z "$PASSWORD" ]; then
    echo "⚠ Could not extract password from logs"
    echo ""
    echo "Get it manually:"
    echo "  docker-compose logs sentinel-agent | grep Password"
else
    echo ""
    echo "============================================================"
    echo "  ADMIN CREDENTIALS"
    echo "============================================================"
    echo "  Username: admin"
    echo "  Password: $PASSWORD"
    echo "============================================================"
    echo ""
fi

echo "Next: Test authentication"
echo "  python3 sentinel_auto.py setup"
echo ""
