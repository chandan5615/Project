#!/usr/bin/env bash
################################################################################
#                                                                              #
#              SENTINEL AGENT v2.2 - ONE-CLICK AUTO INSTALLER                 #
#                                                                              #
#  This script automatically installs and configures everything needed to run  #
#  Sentinel Agent on a fresh Ubuntu/Debian system.                            #
#                                                                              #
#  Usage: chmod +x AUTO_INSTALL.sh && sudo ./AUTO_INSTALL.sh                  #
#                                                                              #
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   log_error "This script must be run with sudo or as root"
   echo "Usage: sudo ./AUTO_INSTALL.sh"
   exit 1
fi

# Get the actual user (not root when using sudo)
if [ -n "$SUDO_USER" ]; then
    ACTUAL_USER="$SUDO_USER"
    ACTUAL_HOME=$(eval echo ~$SUDO_USER)
else
    ACTUAL_USER=$(whoami)
    ACTUAL_HOME="$HOME"
fi

log_info "Running as: $ACTUAL_USER (Home: $ACTUAL_HOME)"

# Welcome banner
clear
cat << "EOF"
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║               SENTINEL AGENT v2.2 - AUTO INSTALLER                       ║
║                                                                          ║
║              AI-Powered Security Monitoring System                       ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
EOF

echo ""
log_info "This installer will set up everything automatically:"
echo "  ✓ Docker & Docker Compose"
echo "  ✓ System dependencies"
echo "  ✓ Ollama LLM (if not installed)"
echo "  ✓ Sentinel Agent containers"
echo "  ✓ Database initialization"
echo "  ✓ Security monitoring"
echo ""
read -p "Press ENTER to continue or Ctrl+C to cancel..."

################################################################################
# STEP 1: Update system packages
################################################################################
log_step "STEP 1: Updating System Packages"

log_info "Updating package list..."
apt-get update -qq

log_success "System packages updated"

################################################################################
# STEP 2: Install Docker
################################################################################
log_step "STEP 2: Installing Docker"

if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    log_success "Docker already installed: $DOCKER_VERSION"
else
    log_info "Installing Docker..."
    
    # Install prerequisites
    apt-get install -y -qq \
        ca-certificates \
        curl \
        gnupg \
        lsb-release
    
    # Add Docker's official GPG key
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg
    
    # Add Docker repository
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker Engine
    apt-get update -qq
    apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    # Start Docker service
    systemctl start docker
    systemctl enable docker
    
    # Add user to docker group
    usermod -aG docker $ACTUAL_USER
    
    log_success "Docker installed successfully"
fi

################################################################################
# STEP 3: Install Docker Compose
################################################################################
log_step "STEP 3: Installing Docker Compose"

if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version)
    log_success "Docker Compose already installed: $COMPOSE_VERSION"
else
    log_info "Installing Docker Compose..."
    
    # Download Docker Compose
    COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
    curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    
    log_success "Docker Compose installed successfully"
fi

################################################################################
# STEP 4: Install system dependencies
################################################################################
log_step "STEP 4: Installing System Dependencies"

log_info "Installing required packages..."
apt-get install -y -qq \
    python3 \
    python3-pip \
    apache2 \
    git \
    curl \
    wget \
    net-tools \
    iptables \
    ufw \
    nano

# Start Apache
systemctl start apache2
systemctl enable apache2

log_success "System dependencies installed"

################################################################################
# STEP 5: Check/Install Ollama
################################################################################
log_step "STEP 5: Checking Ollama Installation"

if command -v ollama &> /dev/null; then
    log_success "Ollama is already installed"
    
    # Check if ollama is running
    if pgrep -x "ollama" > /dev/null; then
        log_success "Ollama service is running"
    else
        log_info "Starting Ollama service..."
        sudo -u $ACTUAL_USER bash -c 'ollama serve' &
        sleep 3
    fi
else
    log_warning "Ollama is NOT installed"
    log_info "Installing Ollama..."
    
    curl -fsSL https://ollama.com/install.sh | sh
    
    # Start Ollama service
    sudo -u $ACTUAL_USER bash -c 'ollama serve' &
    sleep 5
    
    log_success "Ollama installed and started"
fi

# Pull llama3:8b model
log_info "Checking for llama3:8b model..."
if sudo -u $ACTUAL_USER ollama list | grep -q "llama3:8b"; then
    log_success "llama3:8b model already downloaded"
else
    log_info "Downloading llama3:8b model (this may take a few minutes)..."
    sudo -u $ACTUAL_USER ollama pull llama3:8b
    log_success "llama3:8b model downloaded"
fi

# Configure Ollama for Docker access (CRITICAL FIX)
log_info "Configuring Ollama network binding for Docker access..."

# Check current binding
CURRENT_BINDING=$(ss -tlnp 2>/dev/null | grep 11434 | head -n1 || echo "")

if echo "$CURRENT_BINDING" | grep -q "127.0.0.1:11434"; then
    log_warning "Ollama is bound to localhost only - fixing for Docker access..."
    
    # Create systemd override
    mkdir -p /etc/systemd/system/ollama.service.d/
    cat > /etc/systemd/system/ollama.service.d/override.conf <<EOF
# Sentinel Agent - Ollama Network Configuration
# Makes Ollama accessible to Docker containers
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
EOF
    
    # Reload and restart
    systemctl daemon-reload
    systemctl restart ollama
    sleep 3
    
    # Verify
    NEW_BINDING=$(ss -tlnp 2>/dev/null | grep 11434 | head -n1 || echo "")
    if echo "$NEW_BINDING" | grep -q "\*:11434\|:::11434"; then
        log_success "✅ Ollama configured for Docker access (listening on all interfaces)"
    else
        log_warning "⚠️  Ollama binding may need manual verification"
    fi
else
    log_success "Ollama is already accessible on network"
fi

################################################################################
# STEP 6: Configure firewall (optional)
################################################################################
log_step "STEP 6: Configuring Firewall"

log_info "Setting up UFW firewall rules..."

# Allow SSH
ufw allow 22/tcp comment 'SSH'

# Allow HTTP/HTTPS (Apache)
ufw allow 80/tcp comment 'Apache HTTP'
ufw allow 443/tcp comment 'Apache HTTPS'

# Allow Sentinel ports
ufw allow 8000/tcp comment 'Sentinel API'
ufw allow 8501/tcp comment 'Sentinel Dashboard'

# Allow Ollama
ufw allow 11434/tcp comment 'Ollama LLM'

log_info "Firewall rules configured (but not enabled yet)"
log_warning "To enable firewall, run: sudo ufw enable"

################################################################################
# STEP 7: Setup project directory
################################################################################
log_step "STEP 7: Setting Up Project Directory"

PROJECT_DIR="$ACTUAL_HOME/Project"

if [ -d "$PROJECT_DIR" ]; then
    log_info "Project directory already exists at: $PROJECT_DIR"
else
    log_info "Project directory should be at: $PROJECT_DIR"
    log_warning "Please ensure all Sentinel Agent files are in this directory"
fi

# Change to project directory
cd "$PROJECT_DIR" || {
    log_error "Cannot access directory: $PROJECT_DIR"
    log_error "Please create the directory and copy all files there"
    exit 1
}

log_success "Using project directory: $PROJECT_DIR"

################################################################################
# STEP 8: Create environment file
################################################################################
log_step "STEP 8: Creating Environment Configuration"

cat > .env << 'ENVEOF'
# Ollama Configuration
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=llama3:8b

# Log Paths
AUTH_LOG_PATH=/var/log/auth.log
WEB_LOG_PATH=/var/log/apache2/access.log

# Container Configuration
DATA_DIR=/app/data
LOG_DIR=/app/logs

# Security
SENTINEL_ADMIN_USER=sentinel
SENTINEL_ADMIN_PASS=sentinel

# Skip Ollama check (already verified)
SENTINEL_SKIP_OLLAMA_CHECK=0
ENVEOF

log_success ".env file created"

################################################################################
# STEP 9: Set file permissions
################################################################################
log_step "STEP 9: Setting File Permissions"

log_info "Setting correct ownership..."
chown -R $ACTUAL_USER:$ACTUAL_USER "$PROJECT_DIR"

log_info "Making scripts executable..."
chmod +x *.sh 2>/dev/null || true

log_success "Permissions configured"

################################################################################
# STEP 10: Stop old containers (if any)
################################################################################
log_step "STEP 10: Cleaning Up Old Containers"

if [ -f "docker-compose.yml" ]; then
    log_info "Stopping any existing containers..."
    sudo -u $ACTUAL_USER docker-compose down 2>/dev/null || true
    log_success "Old containers stopped"
else
    log_warning "docker-compose.yml not found in current directory"
fi

################################################################################
# STEP 11: Build and start containers
################################################################################
log_step "STEP 11: Building Sentinel Agent Containers"

if [ -f "docker-compose.yml" ]; then
    log_info "Building Docker images (this may take 5-10 minutes)..."
    sudo -u $ACTUAL_USER docker-compose build --no-cache
    
    log_success "Docker images built successfully"
    
    log_info "Starting Sentinel Agent containers..."
    sudo -u $ACTUAL_USER docker-compose up -d
    
    sleep 5
    
    log_success "Containers started"
else
    log_error "docker-compose.yml not found!"
    log_error "Please ensure you're in the Sentinel Agent project directory"
    exit 1
fi

################################################################################
# STEP 12: Verify installation
################################################################################
log_step "STEP 12: Verifying Installation"

log_info "Checking container status..."
sleep 5

if sudo -u $ACTUAL_USER docker-compose ps | grep -q "Up"; then
    log_success "Containers are running"
else
    log_error "Containers may not be running properly"
    log_info "Check logs with: docker-compose logs"
fi

log_info "Checking API health..."
sleep 3

if curl -s http://localhost:8000/api/health | grep -q "ok"; then
    log_success "API is responding"
else
    log_warning "API may still be starting up"
fi

################################################################################
# STEP 13: Display access information
################################################################################
log_step "INSTALLATION COMPLETE!"

# Get server IP
SERVER_IP=$(hostname -I | awk '{print $1}')

cat << EOF

${GREEN}╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║                    🎉 SENTINEL AGENT IS READY! 🎉                        ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝${NC}

${CYAN}Access URLs:${NC}
  📊 Dashboard:  http://$SERVER_IP:8501
  🔌 API:        http://$SERVER_IP:8000
  💚 Health:     http://$SERVER_IP:8000/api/health

${CYAN}Default Credentials:${NC}
  Username: ${GREEN}sentinel${NC}
  Password: ${GREEN}sentinel${NC}

${CYAN}Useful Commands:${NC}
  View logs:     ${YELLOW}docker-compose logs -f sentinel-agent${NC}
  Restart:       ${YELLOW}docker-compose restart${NC}
  Stop:          ${YELLOW}docker-compose down${NC}
  Start:         ${YELLOW}docker-compose up -d${NC}
  Status:        ${YELLOW}docker-compose ps${NC}

${CYAN}Test Attacks:${NC}
  Generate tests: ${YELLOW}python3 test_web_attacks.py${NC}
  Continuous:     ${YELLOW}python3 continuous_attacks.py --interval 10 --duration 5${NC}

${CYAN}Monitoring:${NC}
  Ollama:        ${YELLOW}ollama list${NC}
  Apache:        ${YELLOW}systemctl status apache2${NC}
  Docker:        ${YELLOW}docker ps${NC}

${YELLOW}⚠️  IMPORTANT NOTES:${NC}
  1. If you used sudo, ${RED}LOGOUT AND LOGIN${NC} for Docker group to take effect
  2. Firewall is configured but ${RED}NOT ENABLED${NC} - enable with: ${YELLOW}sudo ufw enable${NC}
  3. Change default password after first login!
  4. AI analysis only runs for ${GREEN}HIGH severity${NC} attacks (optimized performance)

${GREEN}System is monitoring:${NC}
  ✓ SSH brute force attacks (/var/log/auth.log)
  ✓ Web attacks (/var/log/apache2/access.log)
  ✓ SQL injection, XSS, path traversal, etc.
  ✓ Automated threat response
  ✓ AI crew analysis for critical threats

${CYAN}For support or issues:${NC}
  Check logs:    docker-compose logs -f
  Rebuild:       docker-compose down && docker-compose up -d --build

${GREEN}Happy monitoring! 🛡️${NC}

EOF

exit 0
