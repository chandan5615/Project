#!/bin/bash
# Quick Fix - Replace entrypoint script in running container (30 seconds)

echo "=========================================="
echo "Quick Fix - Updating entrypoint in container"
echo "=========================================="
echo ""

SERVER="ubuntu@10.87.146.89"
PROJECT_DIR="~/Project"

echo "[1/4] Uploading updated docker-entrypoint.sh to server..."
scp docker-entrypoint.sh $SERVER:$PROJECT_DIR/

echo ""
echo "[2/4] Converting line endings on server..."
ssh $SERVER "cd $PROJECT_DIR && sed -i 's/\r$//' docker-entrypoint.sh"

echo ""
echo "[3/4] Copying updated script into running container..."
ssh $SERVER "docker cp $PROJECT_DIR/docker-entrypoint.sh sentinel-agent:/usr/local/bin/"

echo ""
echo "[4/4] Restarting container..."
ssh $SERVER "cd $PROJECT_DIR && docker-compose restart sentinel-agent"

echo ""
echo "=========================================="
echo "✓ Quick fix applied!"
echo "=========================================="
echo ""
echo "Wait 10 seconds, then check logs:"
echo "  ssh $SERVER 'cd $PROJECT_DIR && docker-compose logs -f sentinel-agent'"
echo ""
echo "Look for: [SUCCESS] Found Ollama via host.docker.internal"
echo ""
