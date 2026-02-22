#!/bin/bash
# Sentinel Agent - Fresh Clone Setup Verification Script
# Usage: bash verify_setup.sh

echo "=================================================="
echo "Sentinel Agent v2.2 - Setup Verification"
echo "=================================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_count=0
pass_count=0

check_item() {
    local name=$1
    local command=$2
    
    check_count=$((check_count + 1))
    echo -n "[$check_count] $name... "
    
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC}"
        pass_count=$((pass_count + 1))
        return 0
    else
        echo -e "${RED}✗${NC}"
        return 1
    fi
}

# Checks
echo "System Requirements:"
check_item "Docker installed" "docker --version"
check_item "Docker Compose installed" "docker-compose --version"
check_item "Python 3.7+ installed" "python3 --version"

echo ""
echo "Project Files:"
check_item "docker-compose.yml exists" "test -f docker-compose.yml"
check_item "Dockerfile exists" "test -f Dockerfile"
check_item "sentinel_api.py exists" "test -f sentinel_api.py"
check_item "sentinel_auto.py exists" "test -f sentinel_auto.py"
check_item "auth.py exists" "test -f auth.py"

echo ""
echo "Ollama (Must be running on host!):"
check_item "Ollama is reachable" "curl -s http://localhost:11434/api/tags > /dev/null"

if [ $check_count -gt 9 ]; then
    ollama_status=$?
    if [ $ollama_status -ne 0 ]; then
        echo -e "${YELLOW}⚠ Ollama not running! Start it first:${NC}"
        echo "  ollama serve"
        echo ""
    fi
fi

echo ""
echo "Docker Container:"
check_item "Container built" "docker images | grep sentinel-agent"
check_item "Container running" "docker-compose ps | grep sentinel-agent | grep -q Up"

if [ $check_count -gt 12 ]; then
    if docker-compose ps | grep sentinel-agent | grep -q -i "unhealthy"; then
        echo -e "${YELLOW}⚠ Container is unhealthy. Checking logs...${NC}"
        docker-compose logs sentinel-agent | tail -20
        echo ""
    fi
fi

echo ""
echo "API Endpoints:"
check_item "API health check" "curl -s http://localhost:8000/api/health | grep -q healthy"

echo ""
echo "Credentials:"
check_item "auth.db exists (fresh)" "test -f data/auth.db"
check_item "INITIAL_CREDENTIALS.txt exists" "test -f data/INITIAL_CREDENTIALS.txt"

echo ""
echo "Automation Tools:"
check_item "requests library installed" "python3 -c 'import requests' 2>/dev/null"
check_item ".sentinel_token exists (after setup)" "test -f .sentinel_token"
check_item ".sentinel_password exists (after setup)" "test -f .sentinel_password"

echo ""
echo "=================================================="
echo "Summary: $pass_count/$check_count checks passed"
echo "=================================================="

if [ $pass_count -eq $check_count ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Run: python3 sentinel_auto.py setup"
    echo "  2. Run: python3 sentinel_auto.py demo"
    echo "  3. Check: python3 sentinel_auto.py status"
    exit 0
else
    echo -e "${RED}✗ Some checks failed. See messages above.${NC}"
    echo ""
    echo "Common fixes:"
    echo "  - Ollama not running? Start it: ollama serve"
    echo "  - Old database? Remove it: rm data/auth.db"
    echo "  - Container unhealthy? Check logs: docker-compose logs"
    echo "  - Missing requests? Install: pip3 install requests"
    exit 1
fi
