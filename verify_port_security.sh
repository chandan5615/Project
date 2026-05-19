#!/bin/bash
# ============================================================================
# Port 8501 Security Verification Script
# Checks if dashboard is properly restricted to local network only
# ============================================================================

echo "🔍 Sentinel Dashboard Port Security Check"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Check Docker port binding
echo "Test 1: Checking Docker port binding..."
PORT_BINDING=$(docker port sentinel-agent 8501 2>/dev/null | grep -v "0.0.0.0" | head -1)

if echo "$PORT_BINDING" | grep -q "10.87.146.89\|127.0.0.1"; then
    echo -e "${GREEN}✅ PASS${NC}: Dashboard bound to local address: $PORT_BINDING"
    SECURE_BINDING=true
elif echo "$PORT_BINDING" | grep -q "0.0.0.0"; then
    echo -e "${RED}❌ FAIL${NC}: Dashboard exposed to ALL interfaces: $PORT_BINDING"
    echo -e "${YELLOW}   FIX: Change docker-compose.yml line 95 to use local IP${NC}"
    SECURE_BINDING=false
else
    echo -e "${YELLOW}⚠️  WARNING${NC}: Could not determine port binding"
    SECURE_BINDING=unknown
fi
echo ""

# Test 2: Check netstat
echo "Test 2: Checking netstat output..."
NETSTAT_OUTPUT=$(sudo netstat -tulpn 2>/dev/null | grep ":8501" | head -1)

if echo "$NETSTAT_OUTPUT" | grep -q "10.87.146.89:8501\|127.0.0.1:8501"; then
    echo -e "${GREEN}✅ PASS${NC}: Port listening on local address only"
    echo "   $NETSTAT_OUTPUT"
elif echo "$NETSTAT_OUTPUT" | grep -q "0.0.0.0:8501"; then
    echo -e "${RED}❌ FAIL${NC}: Port listening on ALL interfaces (INSECURE!)"
    echo "   $NETSTAT_OUTPUT"
else
    echo -e "${YELLOW}⚠️  INFO${NC}: netstat not available or port not listening"
fi
echo ""

# Test 3: Try to access from localhost
echo "Test 3: Testing local access (should work)..."
LOCAL_ACCESS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 http://localhost:8501 2>/dev/null || echo "000")

if [ "$LOCAL_ACCESS" = "200" ] || [ "$LOCAL_ACCESS" = "302" ]; then
    echo -e "${GREEN}✅ PASS${NC}: Dashboard accessible from localhost (HTTP $LOCAL_ACCESS)"
elif [ "$LOCAL_ACCESS" = "000" ]; then
    echo -e "${YELLOW}⚠️  WARNING${NC}: Dashboard not responding on localhost"
    echo "   This may be normal if dashboard is still starting up"
else
    echo -e "${YELLOW}⚠️  INFO${NC}: Unexpected HTTP code: $LOCAL_ACCESS"
fi
echo ""

# Test 4: Check from LAN IP
echo "Test 4: Testing LAN access (should work)..."
LAN_ACCESS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 http://10.87.146.89:8501 2>/dev/null || echo "000")

if [ "$LAN_ACCESS" = "200" ] || [ "$LAN_ACCESS" = "302" ]; then
    echo -e "${GREEN}✅ PASS${NC}: Dashboard accessible from LAN IP (HTTP $LAN_ACCESS)"
elif [ "$LAN_ACCESS" = "000" ]; then
    echo -e "${RED}❌ FAIL${NC}: Dashboard NOT accessible from LAN IP"
    echo -e "${YELLOW}   This might indicate binding issue${NC}"
else
    echo -e "${YELLOW}⚠️  INFO${NC}: HTTP code: $LAN_ACCESS"
fi
echo ""

# Test 5: Check firewall rules
echo "Test 5: Checking iptables firewall rules..."
IPTABLES_8501=$(sudo iptables -L INPUT -n -v 2>/dev/null | grep "8501" | head -1)

if [ -n "$IPTABLES_8501" ]; then
    if echo "$IPTABLES_8501" | grep -q "DROP"; then
        echo -e "${GREEN}✅ INFO${NC}: Firewall rule found (blocking external access)"
        echo "   $IPTABLES_8501"
    else
        echo -e "${YELLOW}⚠️  INFO${NC}: Firewall rule found (not blocking)"
        echo "   $IPTABLES_8501"
    fi
else
    echo -e "${YELLOW}⚠️  INFO${NC}: No specific firewall rule for port 8501"
    echo "   (This is OK if port is bound to local IP only)"
fi
echo ""

# Test 6: Check authentication status
echo "Test 6: Checking authentication configuration..."
if grep -q "authenticated" /app/dashboard/web_dashboard.py 2>/dev/null || \
   docker exec sentinel-agent grep -q "authenticated" /app/dashboard/web_dashboard.py 2>/dev/null; then
    echo -e "${GREEN}✅ PASS${NC}: Authentication code found in web_dashboard.py"
else
    echo -e "${YELLOW}⚠️  WARNING${NC}: Could not verify authentication status"
fi
echo ""

# Final Summary
echo "=========================================="
echo "📊 SECURITY SUMMARY"
echo "=========================================="

TOTAL_SCORE=0
MAX_SCORE=0

# Binding check (most important)
if [ "$SECURE_BINDING" = "true" ]; then
    echo -e "${GREEN}✅ Port binding: SECURE (local only)${NC}"
    TOTAL_SCORE=$((TOTAL_SCORE + 50))
elif [ "$SECURE_BINDING" = "false" ]; then
    echo -e "${RED}❌ Port binding: VULNERABLE (exposed to all)${NC}"
else
    echo -e "${YELLOW}⚠️  Port binding: UNKNOWN${NC}"
    TOTAL_SCORE=$((TOTAL_SCORE + 25))
fi
MAX_SCORE=$((MAX_SCORE + 50))

# Access tests
if [ "$LOCAL_ACCESS" = "200" ] || [ "$LOCAL_ACCESS" = "302" ]; then
    echo -e "${GREEN}✅ Local access: Working${NC}"
    TOTAL_SCORE=$((TOTAL_SCORE + 25))
fi
MAX_SCORE=$((MAX_SCORE + 25))

if [ "$LAN_ACCESS" = "200" ] || [ "$LAN_ACCESS" = "302" ]; then
    echo -e "${GREEN}✅ LAN access: Working${NC}"
    TOTAL_SCORE=$((TOTAL_SCORE + 25))
fi
MAX_SCORE=$((MAX_SCORE + 25))

echo ""
SCORE_PERCENT=$((TOTAL_SCORE * 100 / MAX_SCORE))
echo "🏆 Security Score: $TOTAL_SCORE/$MAX_SCORE ($SCORE_PERCENT%)"

if [ $SCORE_PERCENT -ge 80 ]; then
    echo -e "${GREEN}✅ Status: SECURE${NC}"
    echo "   Dashboard is properly restricted to local network"
elif [ $SCORE_PERCENT -ge 50 ]; then
    echo -e "${YELLOW}⚠️  Status: NEEDS IMPROVEMENT${NC}"
    echo "   Some security measures in place, but can be better"
else
    echo -e "${RED}❌ Status: VULNERABLE${NC}"
    echo "   Dashboard may be exposed to public internet!"
    echo ""
    echo "🔧 RECOMMENDED FIXES:"
    echo "   1. Edit docker-compose.yml, change line 95:"
    echo "      FROM: 0.0.0.0:8501:8501"
    echo "      TO:   10.87.146.89:8501:8501"
    echo "   2. Rebuild container: docker-compose down && docker-compose up -d"
    echo "   3. Run this script again to verify"
fi

echo ""
echo "📚 For detailed security guide, see:"
echo "   ~/Project/SECURE_DASHBOARD_PORT_8501.md"
echo ""
