#!/bin/bash
# Docker Installation & Health Check Script for Sentinel Agent
# Verifies Docker setup, services, and connectivity

set +e  # Don't exit on errors, we want to show all checks

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TESTS_PASSED=0
TESTS_FAILED=0

# Helper functions
print_header() {
    echo -e "\n${BLUE}═══════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════${NC}\n"
}

print_check() {
    echo -n "✓ Checking: $1... "
}

print_pass() {
    echo -e "${GREEN}✓ PASS${NC}"
    ((TESTS_PASSED++))
}

print_fail() {
    echo -e "${RED}✗ FAIL${NC}"
    echo -e "  → $1"
    ((TESTS_FAILED++))
}

print_warning() {
    echo -e "${YELLOW}⚠ WARNING${NC}"
    echo -e "  → $1"
}

# ============================================================================
# 1. SYSTEM REQUIREMENTS
# ============================================================================
print_header "1. SYSTEM REQUIREMENTS CHECK"

print_check "Docker installed"
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    echo -e "${GREEN}✓ PASS${NC}"
    echo "  Version: $DOCKER_VERSION"
    ((TESTS_PASSED++))
else
    print_fail "Docker not found. Install from https://docker.com"
fi

print_check "Docker daemon running"
if docker info &> /dev/null; then
    print_pass
else
    print_fail "Docker daemon not running. Start with: sudo systemctl start docker"
fi

print_check "Docker Compose installed"
if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version)
    echo -e "${GREEN}✓ PASS${NC}"
    echo "  Version: $COMPOSE_VERSION"
    ((TESTS_PASSED++))
else
    print_fail "Docker Compose not found. Install from https://docs.docker.com/compose"
fi

print_check "Sudo access (for privileged operations)"
if sudo -n docker ps &> /dev/null; then
    print_pass
else
    print_warning "You may need sudo for Docker commands"
fi

print_check "Disk space (need 10GB minimum)"
DISK_AVAIL=$(df . | tail -1 | awk '{print $4}')
DISK_AVAIL_GB=$((DISK_AVAIL / 1024 / 1024))
if [ $DISK_AVAIL_GB -gt 10240 ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    echo "  Available: ${DISK_AVAIL_GB}GB"
    ((TESTS_PASSED++))
else
    print_fail "Insufficient disk space. Need 10GB, have ${DISK_AVAIL_GB}GB"
fi

print_check "Memory (checking available RAM)"
RAM_AVAIL=$(free -m | awk 'NR==2{print $7}')
if [ $RAM_AVAIL -gt 2048 ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    echo "  Available: ${RAM_AVAIL}MB"
    ((TESTS_PASSED++))
else
    print_warning "Limited memory. Have ${RAM_AVAIL}MB, recommended 8GB+"
fi

# ============================================================================
# 2. PROJECT STRUCTURE
# ============================================================================
print_header "2. PROJECT FILES CHECK"

FILES=(
    "docker-compose.yml"
    "Dockerfile"
    "docker-entrypoint.sh"
    "requirements.txt"
    "main.py"
)

for file in "${FILES[@]}"; do
    print_check "File: $file"
    if [ -f "$file" ]; then
        print_pass
    else
        print_fail "File not found: $file"
    fi
done

# ============================================================================
# 3. DOCKER IMAGES
# ============================================================================
print_header "3. DOCKER IMAGES CHECK"

print_check "Sentinel Agent image exists"
if docker images | grep -q "sentinel-agent"; then
    IMAGE_ID=$(docker images | grep "sentinel-agent" | head -1 | awk '{print $3}')
    echo -e "${GREEN}✓ PASS${NC}"
    echo "  Image ID: $IMAGE_ID"
    ((TESTS_PASSED++))
else
    print_warning "No sentinel-agent image found. Building..."
    echo "  Run: docker-compose build"
fi

print_check "Base Python image available"
if docker images | grep -q "python.*3.10"; then
    print_pass
else
    print_warning "Python 3.10 image not found locally. Docker will auto-download."
fi

# ============================================================================
# 4. DOCKER SERVICES
# ============================================================================
print_header "4. DOCKER SERVICES CHECK"

print_check "Network sentinel-network exists"
if docker network ls | grep -q "sentinel-network"; then
    print_pass
else
    print_warning "Network not created yet. Will be created on first run."
fi

print_check "Services defined in compose"
if [ -f "docker-compose.yml" ]; then
    SERVICES=$(grep "^  [a-z].*:" docker-compose.yml | grep -v "^  #" | cut -d: -f1 | xargs)
    echo -e "${GREEN}✓ PASS${NC}"
    echo "  Services: $SERVICES"
    ((TESTS_PASSED++))
else
    print_fail "docker-compose.yml not found"
fi

# ============================================================================
# 5. PORT AVAILABILITY
# ============================================================================
print_header "5. PORT AVAILABILITY CHECK"

PORTS=(8000 8501 11434)
for port in "${PORTS[@]}"; do
    print_check "Port $port available"
    if netstat -tuln 2>/dev/null | grep -q ":$port "; then
        print_warning "Port $port is already in use"
    else
        print_pass
    fi
done

# ============================================================================
# 6. CONFIGURATION
# ============================================================================
print_header "6. CONFIGURATION CHECK"

print_check "Environment file (.env)"
if [ -f ".env" ]; then
    print_pass
else
    echo -e "${YELLOW}⚠ WARNING${NC}"
    echo "  .env file not found. Using default environment variables."
fi

print_check "docker-compose variables"
if grep -q "OLLAMA_BASE_URL" docker-compose.yml; then
    print_pass
else
    print_fail "OLLAMA_BASE_URL not defined in docker-compose.yml"
fi

# ============================================================================
# 7. CONNECTIVITY TESTS (if services running)
# ============================================================================
print_header "7. CONNECTIVITY TESTS"

# Check if containers are running
RUNNING=$(docker-compose ps 2>/dev/null | grep -c "Up" || echo 0)

if [ $RUNNING -gt 0 ]; then
    print_check "Sentinel API responding"
    if curl -sf http://localhost:8000/api/health &> /dev/null; then
        print_pass
    else
        print_warning "API not responding. Services may still be starting..."
    fi

    print_check "Ollama responding"
    if curl -sf http://localhost:11434/api/tags &> /dev/null; then
        print_pass
    else
        print_warning "Ollama not running. Start with: docker-compose --profile with-ollama up -d"
    fi

    print_check "Dashboard responding"
    if curl -sf http://localhost:8501 &> /dev/null; then
        print_pass
    else
        print_warning "Dashboard not responding (may be optional)"
    fi
else
    echo -e "${YELLOW}⚠ INFO${NC}: Services not running. Start with:"
    echo "  docker-compose up -d"
    echo ""
    echo "  Then re-run this script to test connectivity."
fi

# ============================================================================
# 8. DOCKER-COMPOSE VALIDATION
# ============================================================================
print_header "8. DOCKER-COMPOSE VALIDATION"

print_check "Compose file syntax"
if docker-compose config &> /dev/null; then
    print_pass
else
    print_fail "Invalid docker-compose.yml syntax"
fi

# ============================================================================
# 9. SUMMARY
# ============================================================================
print_header "TEST SUMMARY"

TOTAL=$((TESTS_PASSED + TESTS_FAILED))
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}/$TOTAL"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}/$TOTAL"

if [ $TESTS_FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ All checks passed! Ready to deploy.${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. docker-compose build"
    echo "  2. docker-compose up -d"
    echo "  3. docker-compose logs -f"
    exit 0
else
    echo ""
    echo -e "${RED}✗ Some checks failed. See above for details.${NC}"
    exit 1
fi
