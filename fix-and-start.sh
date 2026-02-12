#!/bin/bash
#
# Sentinel Agent - Complete Fix and Start Script
# This script applies all fixes and starts the container fresh
#
# What it does:
# 1. Removes bcrypt/cryptography dependencies (uses built-in Python hashlib)
# 2. Fixes permissions (runs as root, chmod 777 on data/)
# 3. Rebuilds container from scratch
# 4. Starts fresh with new credentials
#

set -e

echo "============================================================"
echo "  Sentinel Agent - Complete Fix and Start"
echo "============================================================"
echo ""
echo "This will:"
echo "  1. Stop and remove old containers"
echo "  2. Delete old data (fresh credentials)"
echo "  3. Rebuild container (no bcrypt dependency)"
echo "  4. Start with root permissions (no permission errors)"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 1
fi

echo ""
echo "[1/5] Stopping and removing old containers..."
docker-compose down -v 2>/dev/null || true
docker rm -f sentinel-agent 2>/dev/null || true
echo "✓ Old containers removed"

echo ""
echo "[2/5] Cleaning old data for fresh start..."
# Use sudo to remove Docker-created files (owned by root)
sudo rm -rf data/ logs/ 2>/dev/null || true
rm -f .api_token 2>/dev/null || true
echo "✓ Old data cleaned"

echo ""
echo "[3/5] Rebuilding container (no cache)..."
echo "This will take 3-5 minutes..."
docker-compose build --no-cache

echo ""
echo "[4/5] Starting container..."
docker-compose up -d

echo ""
echo "[5/5] Waiting for startup (60 seconds)..."
echo "The container will:"
echo "  - Create databases with SIMPLIFIED password hashing (no bcrypt)"
echo "  - Run as ROOT (no permission issues)"  
echo "  - Generate new admin credentials"
echo ""

# Show logs in real-time
echo "Showing container logs (press Ctrl+C to stop watching)..."
echo "============================================================"
sleep 3
docker-compose logs -f sentinel-agent &
LOGS_PID=$!

# Wait for container to be healthy or show error
for i in {1..60}; do
    sleep 1
    
    # Check if container crashed
    if ! docker-compose ps | grep -q "sentinel-agent"; then
        echo ""
        echo "✗ Container stopped/crashed!"
        echo ""
        echo "Showing last 50 lines of logs:"
        docker-compose logs --tail=50 sentinel-agent
        kill $LOGS_PID 2>/dev/null || true
        exit 1
    fi
    
    # Check if healthy
    if docker-compose ps | grep -q "healthy"; then
        echo ""
        echo "============================================================"
        echo "✓ Container is HEALTHY!"
        echo "============================================================"
        kill $LOGS_PID 2>/dev/null || true
        break
    fi
    
    if [ $((i % 10)) == 0 ]; then
        echo "Still waiting... ($i/60 seconds)"
    fi
done

echo ""
echo "Getting admin credentials..."
sleep 2

# Extract password from logs
PASSWORD=$(docker-compose logs sentinel-agent 2>/dev/null | grep "Password:" | tail -1 | awk '{print $NF}')

if [ -z "$PASSWORD" ]; then
    echo "⚠ Could not extract password from logs"
    echo "Check logs manually:"
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
    echo "SAVE THESE CREDENTIALS NOW!"
    echo ""
fi

echo "Next steps:"
echo ""
echo "1. Test authentication:"
echo "   python3 sentinel_auto.py setup"
echo ""
echo "2. Run attack demonstration:"
echo "   python3 sentinel_auto.py demo"
echo ""
echo "3. View dashboard:"
echo "   python3 run_dashboard.py"
echo ""
echo "4. Check API:"
echo "   curl http://localhost:8000/api/health"
echo ""

echo "If container keeps restarting, check logs:"
echo "  docker-compose logs --tail=100 sentinel-agent"
echo ""
