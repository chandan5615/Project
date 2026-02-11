#!/bin/bash
# Fix Sentinel Agent Docker Health Check Issue
# This script rebuilds the container with the updated healthcheck configuration

echo "=============================================="
echo "Fixing Sentinel Agent Health Check"
echo "=============================================="
echo ""

echo "Step 1: Stopping current container..."
docker-compose down

echo ""
echo "Step 2: Cleaning up old data (fresh start)..."
rm -f data/auth.db data/INITIAL_CREDENTIALS.txt data/*.json data/*.db

echo ""
echo "Step 3: Rebuilding container with healthcheck..."
docker-compose build --no-cache

echo ""
echo "Step 4: Starting container..."
docker-compose up -d

echo ""
echo "Step 5: Waiting for container to become healthy (30s)..."
sleep 30

echo ""
echo "Step 6: Checking container status..."
docker-compose ps

echo ""
echo "Step 7: Extracting admin credentials..."
docker-compose logs sentinel-agent | grep -A 3 "DEFAULT ADMIN CREDENTIALS"

echo ""
echo "=============================================="
echo "Health check fix complete!"
echo "=============================================="
echo ""
echo "Now run: python3 sentinel_auto.py setup"
echo "Then run: python3 sentinel_auto.py demo"
echo ""
