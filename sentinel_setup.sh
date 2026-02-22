#!/bin/bash
# sentinel_setup.sh - Automated Sentinel Agent Setup & Testing
# This script automates: password extraction, token generation, and attack testing

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_URL="http://localhost:8000"
MAX_RETRIES=30
RETRY_DELAY=2
TOKEN_FILE=".sentinel_token"
PASSWORD_FILE=".sentinel_password"

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Sentinel Agent v2.2 - Automated Setup & Testing     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"

# ============================================================================
# FUNCTION: Wait for container to be healthy
# ============================================================================
wait_for_container() {
    echo -e "\n${YELLOW}⏳ Waiting for Sentinel Agent to be healthy...${NC}"
    
    for i in $(seq 1 $MAX_RETRIES); do
        STATUS=$(docker-compose ps sentinel-agent 2>/dev/null | grep -i healthy || echo "")
        if [ -n "$STATUS" ]; then
            echo -e "${GREEN}✓ Container is healthy${NC}"
            return 0
        fi
        
        if [ $((i % 5)) -eq 0 ]; then
            echo "  Attempt $i/$MAX_RETRIES..."
        fi
        sleep $RETRY_DELAY
    done
    
    echo -e "${RED}✗ Container did not become healthy after ${MAX_RETRIES} attempts${NC}"
    echo "   Run: docker-compose logs sentinel-agent"
    return 1
}

# ============================================================================
# FUNCTION: Extract password from container logs
# ============================================================================
extract_password() {
    echo -e "\n${YELLOW}🔑 Extracting admin password...${NC}"
    
    # Try to get password from logs
    PASSWORD=$(docker-compose logs sentinel-agent 2>/dev/null | \
        grep -A 2 "DEFAULT ADMIN CREDENTIALS" | \
        grep "^Password:" | \
        awk '{print $NF}' || echo "")
    
    if [ -z "$PASSWORD" ]; then
        echo -e "${RED}✗ Could not extract password from logs${NC}"
        echo "   Check if container has fully started with: docker-compose logs sentinel-agent"
        return 1
    fi
    
    echo "$PASSWORD" > "$PASSWORD_FILE"
    echo -e "${GREEN}✓ Password extracted and saved to $PASSWORD_FILE${NC}"
    echo -e "  Password: ${YELLOW}${PASSWORD:0:8}...${PASSWORD: -4}${NC} (masked)"
    return 0
}

# ============================================================================
# FUNCTION: Get API token
# ============================================================================
get_api_token() {
    echo -e "\n${YELLOW}🔐 Getting API token...${NC}"
    
    if [ ! -f "$PASSWORD_FILE" ]; then
        echo -e "${RED}✗ Password file not found${NC}"
        return 1
    fi
    
    PASSWORD=$(cat "$PASSWORD_FILE")
    
    # Try to get token
    for i in $(seq 1 10); do
        RESPONSE=$(curl -s -X POST "$API_URL/api/auth/login" \
            -H "Content-Type: application/x-www-form-urlencoded" \
            -d "username=admin&password=$PASSWORD" 2>/dev/null)
        
        TOKEN=$(echo "$RESPONSE" | jq -r '.token // empty' 2>/dev/null || echo "")
        
        if [ -n "$TOKEN" ] && [ "$TOKEN" != "null" ]; then
            echo "$TOKEN" > "$TOKEN_FILE"
            echo -e "${GREEN}✓ API token obtained${NC}"
            echo -e "  Token: ${YELLOW}${TOKEN:0:20}...${NC} (masked)"
            return 0
        fi
        
        if [ $i -lt 10 ]; then
            echo "  Attempt $i/10..."
            sleep 2
        fi
    done
    
    echo -e "${RED}✗ Failed to authenticate. Check password:${NC}"
    echo "   $RESPONSE"
    return 1
}

# ============================================================================
# FUNCTION: Test API connectivity
# ============================================================================
test_api() {
    echo -e "\n${YELLOW}🧪 Testing API connectivity...${NC}"
    
    # Test health endpoint (no auth required)
    HEALTH=$(curl -s "$API_URL/api/health")
    STATUS=$(echo "$HEALTH" | jq -r '.status // empty' 2>/dev/null || echo "")
    
    if [ "$STATUS" == "healthy" ]; then
        echo -e "${GREEN}✓ API is healthy${NC}"
        echo "$HEALTH" | jq '.'
        return 0
    else
        echo -e "${RED}✗ API health check failed${NC}"
        echo "   Response: $HEALTH"
        return 1
    fi
}

# ============================================================================
# FUNCTION: Get baseline metrics
# ============================================================================
get_baseline() {
    echo -e "\n${YELLOW}📊 Getting baseline metrics...${NC}"
    
    if [ ! -f "$TOKEN_FILE" ]; then
        echo -e "${RED}✗ Token file not found${NC}"
        return 1
    fi
    
    TOKEN=$(cat "$TOKEN_FILE")
    
    METRICS=$(curl -s -H "X-API-Key: $TOKEN" \
        "$API_URL/api/metrics/detection" 2>/dev/null)
    
    echo "$METRICS" | jq '.' > baseline_metrics.json
    
    TOTAL=$(echo "$METRICS" | jq '.total_events_analyzed // 0')
    THREATS=$(echo "$METRICS" | jq '.threats_detected // 0')
    
    echo -e "${GREEN}✓ Baseline captured${NC}"
    echo -e "  Total events analyzed: ${YELLOW}$TOTAL${NC}"
    echo -e "  Threats detected: ${YELLOW}$THREATS${NC}"
    
    return 0
}

# ============================================================================
# FUNCTION: Run SSH Brute Force test
# ============================================================================
test_ssh_brute_force() {
    echo -e "\n${YELLOW}🚀 Running SSH Brute Force test...${NC}"
    
    ATTEMPTS=20
    echo "  Simulating $ATTEMPTS failed login attempts..."
    
    for i in $(seq 1 $ATTEMPTS); do
        ssh -o StrictHostKeyChecking=no -o ConnectTimeout=1 \
            "wrong_user_${i}@localhost" 2>/dev/null || true
        
        if [ $((i % 5)) -eq 0 ]; then
            echo -n "."
        fi
    done
    
    echo -e "\n${GREEN}✓ SSH brute force test completed${NC}"
    echo "  Check results with: ./sentinel_test.sh check"
}

# ============================================================================
# FUNCTION: Run SQL Injection test
# ============================================================================
test_sql_injection() {
    echo -e "\n${YELLOW}🚀 Running SQL Injection test...${NC}"
    
    # Check if web server is running
    if ! curl -s http://localhost/ > /dev/null 2>&1; then
        echo -e "${RED}✗ Web server not running on localhost:80${NC}"
        echo "  Start with: sudo systemctl start apache2"
        return 1
    fi
    
    PAYLOADS=(
        "1' OR '1'='1"
        "admin'--"
        "1 UNION SELECT NULL--"
        "' OR 1=1--"
    )
    
    echo "  Testing ${#PAYLOADS[@]} SQL injection payloads..."
    
    for payload in "${PAYLOADS[@]}"; do
        ENCODED=$(python3 -c "import urllib.parse; print(urllib.parse.quote('''${payload}'''))" 2>/dev/null || echo "$payload")
        curl -s "http://localhost/search?q=${ENCODED}" > /dev/null 2>&1 || true
    done
    
    echo -e "${GREEN}✓ SQL injection test completed${NC}"
}

# ============================================================================
# FUNCTION: Run DDoS/Rate Limit test
# ============================================================================
test_ddos() {
    echo -e "\n${YELLOW}🚀 Running DDoS/Rate Limit test...${NC}"
    
    echo "  Sending 100 concurrent requests..."
    
    for i in {1..100}; do
        curl -s http://localhost/ > /dev/null 2>&1 &
    done
    
    wait
    echo -e "${GREEN}✓ DDoS test completed${NC}"
}

# ============================================================================
# FUNCTION: Check test results
# ============================================================================
check_results() {
    echo -e "\n${YELLOW}📋 Checking for detected incidents...${NC}"
    
    if [ ! -f "$TOKEN_FILE" ]; then
        echo -e "${RED}✗ Token file not found. Run setup first.${NC}"
        return 1
    fi
    
    TOKEN=$(cat "$TOKEN_FILE")
    
    # Wait a bit for detection
    echo "  Waiting for analysis (this may take 30-90 seconds)..."
    sleep 30
    
    # Get incidents
    INCIDENTS=$(curl -s -H "X-API-Key: $TOKEN" \
        "$API_URL/api/incidents/recent" 2>/dev/null)
    
    COUNT=$(echo "$INCIDENTS" | jq 'length')
    
    if [ "$COUNT" -gt 0 ]; then
        echo -e "${GREEN}✓ Found $COUNT incidents${NC}\n"
        echo "$INCIDENTS" | jq '.[] | {type, source_ip, severity, status}' | head -30
        
        # Save to file
        echo "$INCIDENTS" | jq '.' > incident_results.json
        echo -e "\n${GREEN}✓ Results saved to incident_results.json${NC}"
    else
        echo -e "${RED}✗ No incidents detected yet${NC}"
        echo "  This could mean:"
        echo "  - Attacks didn't trigger detection patterns"
        echo "  - Log files not being monitored"
        echo "  - Insufficient time for analysis"
        echo ""
        echo "  Check logs: docker-compose logs sentinel-agent"
    fi
    
    # Get current metrics
    echo -e "\n${YELLOW}📊 Current Metrics:${NC}"
    METRICS=$(curl -s -H "X-API-Key: $TOKEN" \
        "$API_URL/api/metrics/detection" 2>/dev/null)
    
    echo "$METRICS" | jq '{total_events_analyzed, threats_detected, detection_rate, most_common_threat}' 
    echo "$METRICS" | jq '.' > current_metrics.json
}

# ============================================================================
# FUNCTION: Show status dashboard
# ============================================================================
show_dashboard() {
    echo -e "\n${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║              Sentinel Agent Status Dashboard            ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
    
    if [ ! -f "$TOKEN_FILE" ]; then
        echo -e "${RED}✗ Not initialized. Run: ./sentinel_setup.sh setup${NC}"
        return 1
    fi
    
    TOKEN=$(cat "$TOKEN_FILE")
    
    # Health
    echo -e "\n${YELLOW}System Health:${NC}"
    HEALTH=$(curl -s "$API_URL/api/health")
    echo "$HEALTH" | jq '{status, version, uptime_seconds}'
    
    # Metrics
    echo -e "\n${YELLOW}Detection Metrics:${NC}"
    METRICS=$(curl -s -H "X-API-Key: $TOKEN" "$API_URL/api/metrics/detection")
    echo "$METRICS" | jq '{total_events_analyzed, threats_detected, detection_rate}'
    
    # Recent Incidents
    echo -e "\n${YELLOW}Recent Incidents:${NC}"
    INCIDENTS=$(curl -s -H "X-API-Key: $TOKEN" "$API_URL/api/incidents/recent")
    echo "$INCIDENTS" | jq '.[0:5] | .[] | {type, severity, source_ip}' || echo "No incidents"
    
    # IP Lists
    echo -e "\n${YELLOW}IP Lists:${NC}"
    LISTS=$(curl -s -H "X-API-Key: $TOKEN" "$API_URL/api/lists/summary")
    echo "$LISTS" | jq '{whitelisted_count, blacklisted_count}'
}

# ============================================================================
# FUNCTION: Auto detection demo (all tests at once)
# ============================================================================
auto_demo() {
    echo -e "\n${BLUE}Running Full Detection Demo...${NC}"
    
    echo -e "\n${YELLOW}1. Getting baseline metrics...${NC}"
    get_baseline || return 1
    
    echo -e "\n${YELLOW}2. Running SSH Brute Force attack...${NC}"
    test_ssh_brute_force || return 1
    
    echo -e "\n${YELLOW}3. Running SQL Injection attack...${NC}"
    test_sql_injection || return 1
    
    echo -e "\n${YELLOW}4. Running DDoS attack test...${NC}"
    test_ddos || return 1
    
    check_results
}

# ============================================================================
# MAIN - Command Line Interface
# ============================================================================

case "${1:-help}" in
    setup)
        echo -e "\n${BLUE}Running Full Setup...${NC}"
        wait_for_container || exit 1
        test_api || exit 1
        extract_password || exit 1
        get_api_token || exit 1
        get_baseline || exit 1
        echo -e "\n${GREEN}✓ Setup Complete!${NC}"
        echo -e "  Next: ./sentinel_setup.sh demo"
        ;;
    
    password)
        extract_password
        ;;
    
    token)
        get_api_token
        ;;
    
    test-ssh)
        test_ssh_brute_force
        echo -e "  Results available in 60 seconds: ./sentinel_setup.sh check"
        ;;
    
    test-sql)
        test_sql_injection
        echo -e "  Results available in 60 seconds: ./sentinel_setup.sh check"
        ;;
    
    test-ddos)
        test_ddos
        echo -e "  Results available in 60 seconds: ./sentinel_setup.sh check"
        ;;
    
    check)
        check_results
        ;;
    
    demo)
        auto_demo
        ;;
    
    status)
        show_dashboard
        ;;
    
    *)
        cat << 'EOF'
Sentinel Agent v2.2 - Automated Setup & Testing Script

USAGE:
  ./sentinel_setup.sh [COMMAND]

COMMANDS:
  setup              Complete setup (password, token, baseline)
  password           Extract admin password from logs
  token              Get API authentication token
  test-ssh           Run SSH brute force test
  test-sql           Run SQL injection test  
  test-ddos          Run DDoS/rate limit test
  check              Check for detected incidents
  demo               Run all tests automatically
  status             Show system dashboard
  help               Show this help message

EXAMPLES:
  # First time setup
  ./sentinel_setup.sh setup
  
  # Run detection demo (all attacks + check results)
  ./sentinel_setup.sh demo
  
  # Check current status
  ./sentinel_setup.sh status
  
  # Run individual tests
  ./sentinel_setup.sh test-ssh
  ./sentinel_setup.sh check

WORKFLOW:
  1. ./sentinel_setup.sh setup    (Extract password & token)
  2. ./sentinel_setup.sh demo     (Run all automated tests)
  3. ./sentinel_setup.sh status   (View results dashboard)

FILES CREATED:
  .sentinel_password      - Admin password (keep secret!)
  .sentinel_token         - API token (expires in 24 hours)
  baseline_metrics.json   - Initial metrics snapshot
  incident_results.json   - Detected incidents
  current_metrics.json    - Latest metrics

TROUBLESHOOTING:
  - Check container: docker-compose ps
  - View logs:      docker-compose logs sentinel-agent
  - API health:     curl http://localhost:8000/api/health

EOF
        ;;
esac
