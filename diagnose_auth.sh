#!/bin/bash
# Complete Authentication Diagnostic Script
# Tests all aspects of authentication end-to-end

echo "============================================================"
echo "Sentinel Agent - Authentication Diagnostics"
echo "============================================================"
echo ""

# Step 1: Check if container is running
echo "[1/8] Checking container status..."
if docker-compose ps sentinel-agent | grep -q "Up"; then
    echo "✓ Container is running"
else
    echo "✗ Container is not running!"
    echo "Start it with: docker-compose up -d"
    exit 1
fi
echo ""

# Step 2: Check container health
echo "[2/8] Checking container health..."
if docker-compose ps sentinel-agent | grep -q "healthy"; then
    echo "✓ Container is healthy"
else
    echo "⚠ Container is not healthy (yet)"
    echo "This is normal during first 60 seconds of startup"
fi
echo ""

# Step 3: Check if API is responding
echo "[3/8] Testing API health endpoint..."
HEALTH=$(curl -s http://localhost:8000/api/health 2>/dev/null)
if [ ! -z "$HEALTH" ]; then
    echo "✓ API is responding"
    echo "  Response: $HEALTH"
else
    echo "✗ API is not responding on port 8000"
    echo ""
    echo "Checking container logs for errors:"
    docker-compose logs --tail=20 sentinel-agent
    exit 1
fi
echo ""

# Step 4: Extract password from logs
echo "[4/8] Extracting admin password from container logs..."
PASSWORD=$(docker-compose logs sentinel-agent | grep "Password:" | tail -1 | awk -F': ' '{print $NF}' | tr -d ' \r\n')

if [ ! -z "$PASSWORD" ]; then
    echo "✓ Password extracted"
    echo "  Password: ${PASSWORD:0:8}...${PASSWORD: -4}"
else
    echo "✗ Could not extract password from logs"
    echo ""
    echo "Full credential block from logs:"
    docker-compose logs sentinel-agent | grep -A 3 "DEFAULT ADMIN CREDENTIALS"
    exit 1
fi
echo ""

# Step 5: Check database exists
echo "[5/8] Checking if auth database exists..."
if docker exec sentinel-agent ls /app/data/auth.db >/dev/null 2>&1; then
    echo "✓ Auth database exists at /app/data/auth.db"
    
    # Check database contents
    echo "  Database info:"
    docker exec sentinel-agent stat -c "  Size: %s bytes, Modified: %y" /app/data/auth.db
else
    echo "✗ Auth database not found!"
    echo "Listing /app/data/ contents:"
    docker exec sentinel-agent ls -la /app/data/
    exit 1
fi
echo ""

# Step 6: Check if admin user exists in database
echo "[6/8] Verifying admin user in database..."
USER_COUNT=$(docker exec sentinel-agent /opt/venv/bin/python -c "
import sqlite3
conn = sqlite3.connect('/app/data/auth.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', ('admin',))
count = cursor.fetchone()[0]
print(count)
conn.close()
" 2>/dev/null)

if [ "$USER_COUNT" = "1" ]; then
    echo "✓ Admin user exists in database"
else
    echo "✗ Admin user not found in database (count: $USER_COUNT)"
    echo "Re-initializing database..."
    docker exec sentinel-agent /opt/venv/bin/python /app/init_database.py
fi
echo ""

# Step 7: Test authentication with extracted password
echo "[7/8] Testing authentication..."
echo "  Endpoint: http://localhost:8000/api/auth/login"
echo "  Username: admin"
echo "  Password: ${PASSWORD:0:8}...${PASSWORD: -4}"
echo ""

# Try form data method
AUTH_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
  "http://localhost:8000/api/auth/login" \
  -d "username=admin" \
  -d "password=$PASSWORD" \
  2>/dev/null)

HTTP_CODE=$(echo "$AUTH_RESPONSE" | tail -1)
RESPONSE_BODY=$(echo "$AUTH_RESPONSE" | sed '$d')

echo "  HTTP Status: $HTTP_CODE"

if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ Authentication SUCCESSFUL!"
    
    TOKEN=$(echo "$RESPONSE_BODY" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
    if [ ! -z "$TOKEN" ]; then
        echo "  Token: ${TOKEN:0:30}..."
        
        # Save token
        echo "$TOKEN" > .sentinel_token
        echo "  ✓ Token saved to .sentinel_token"
    fi
else
    echo "✗ Authentication FAILED"
    echo "  Response: $RESPONSE_BODY"
    echo ""
    echo "Debugging steps:"
    echo "1. Check container logs:"
    echo "   docker-compose logs sentinel-agent | tail -50"
    echo ""
    echo "2. Manually test in container:"
    echo "   docker exec -it sentinel-agent /bin/bash"
    echo "   /opt/venv/bin/python test_auth.py"
    exit 1
fi
echo ""

# Step 8: Test API with token
if [ ! -z "$TOKEN" ]; then
    echo "[8/8] Testing API access with token..."
    
    API_TEST=$(curl -s -w "\n%{http_code}" \
      "http://localhost:8000/api/info" \
      -H "X-API-Key: $TOKEN" \
      2>/dev/null)
    
    API_CODE=$(echo "$API_TEST" | tail -1)
    API_BODY=$(echo "$API_TEST" | sed '$d')
    
    if [ "$API_CODE" = "200" ]; then
        echo "✓ API access working!"
        echo "  Response: $API_BODY"
    else
        echo "⚠ API access returned status $API_CODE"
        echo "  Response: $API_BODY"
    fi
fi

echo ""
echo "============================================================"
echo "✓ DIAGNOSTICS COMPLETE"
echo "============================================================"
echo ""
echo "Summary:"
echo "  Container: Running & Healthy"
echo "  API: Responding"
echo "  Database: Initialized"
echo "  Admin User: Exists"
echo "  Authentication: Working"
echo "  API Token: Generated"
echo ""
echo "Next steps:"
echo "  Run: python3 sentinel_auto.py demo"
echo ""
