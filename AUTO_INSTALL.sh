#!/usr/bin/env bash
################################################################################
#                                                                              #
#              SENTINEL AGENT v2.3 - ONE-CLICK AUTO INSTALLER                 #
#                                                                              #
#  Supports: Default Apache, XAMPP, LAMPP                                     #
#  Usage: chmod +x AUTO_INSTALL.sh && sudo ./AUTO_INSTALL.sh                  #
#                                                                              #
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

log_info()    { echo -e "${CYAN}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
}

# ── Root check ────────────────────────────────────────────────────────────────
if [[ $EUID -ne 0 ]]; then
    log_error "This script must be run with sudo or as root"
    echo "Usage: sudo ./AUTO_INSTALL.sh"
    exit 1
fi

if [ -n "$SUDO_USER" ]; then
    ACTUAL_USER="$SUDO_USER"
    ACTUAL_HOME=$(eval echo ~$SUDO_USER)
else
    ACTUAL_USER=$(whoami)
    ACTUAL_HOME="$HOME"
fi

# ── Welcome banner ────────────────────────────────────────────────────────────
clear
cat << "EOF"
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║               SENTINEL AGENT v2.3 - AUTO INSTALLER                      ║
║                                                                          ║
║              AI-Powered Security Monitoring System                       ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
EOF

echo ""
log_info "Running as: $ACTUAL_USER (Home: $ACTUAL_HOME)"
echo ""

################################################################################
# WEB SERVER SELECTION MENU
################################################################################
log_step "WEB SERVER SELECTION"

echo -e "${MAGENTA}  Sentinel monitors your web server access logs for attacks."
echo -e "  Please select which web server you are using:${NC}"
echo ""
echo -e "  ${GREEN}[1]${NC} Default Apache   (installed via apt — /var/log/apache2/access.log)"
echo -e "  ${GREEN}[2]${NC} XAMPP             (Windows-style, installed to /opt/lampp)"
echo -e "  ${GREEN}[3]${NC} LAMPP             (Linux XAMPP variant, installed to /opt/lampp)"
echo -e "  ${GREEN}[4]${NC} Custom path       (I will enter the log path manually)"
echo ""

while true; do
    read -p "  Enter choice [1-4]: " WEB_SERVER_CHOICE
    case $WEB_SERVER_CHOICE in
        1|2|3|4) break ;;
        *) echo -e "  ${RED}Invalid choice. Please enter 1, 2, 3, or 4.${NC}" ;;
    esac
done

# ── Set paths based on selection ──────────────────────────────────────────────
case $WEB_SERVER_CHOICE in
    1)
        WEB_SERVER_TYPE="apache"
        WEB_SERVER_NAME="Default Apache (apt)"
        WEB_LOG_PATH="/var/log/apache2/access.log"
        WEB_ERROR_LOG="/var/log/apache2/error.log"
        WEB_SERVICE_NAME="apache2"
        WEB_INSTALL_CMD="apt-get install -y apache2"
        WEB_START_CMD="systemctl start apache2 && systemctl enable apache2"
        WEB_CONFIG_DIR="/etc/apache2"
        WEB_ROOT="/var/www/html"
        INSTALL_APACHE=true
        ;;
    2)
        WEB_SERVER_TYPE="xampp"
        WEB_SERVER_NAME="XAMPP"
        WEB_LOG_PATH="/opt/lampp/logs/access_log"
        WEB_ERROR_LOG="/opt/lampp/logs/error_log"
        WEB_SERVICE_NAME="lampp"
        WEB_INSTALL_CMD=""  # XAMPP must be pre-installed
        WEB_START_CMD="/opt/lampp/lampp startapache"
        WEB_CONFIG_DIR="/opt/lampp/etc"
        WEB_ROOT="/opt/lampp/htdocs"
        INSTALL_APACHE=false
        ;;
    3)
        WEB_SERVER_TYPE="lampp"
        WEB_SERVER_NAME="LAMPP"
        WEB_LOG_PATH="/opt/lampp/logs/access_log"
        WEB_ERROR_LOG="/opt/lampp/logs/error_log"
        WEB_SERVICE_NAME="lampp"
        WEB_INSTALL_CMD=""  # LAMPP must be pre-installed
        WEB_START_CMD="/opt/lampp/lampp startapache"
        WEB_CONFIG_DIR="/opt/lampp/etc"
        WEB_ROOT="/opt/lampp/htdocs"
        INSTALL_APACHE=false
        ;;
    4)
        WEB_SERVER_TYPE="custom"
        WEB_SERVER_NAME="Custom"
        echo ""
        read -p "  Enter full path to access log: " WEB_LOG_PATH
        read -p "  Enter full path to error log (or press ENTER to skip): " WEB_ERROR_LOG
        WEB_SERVICE_NAME="custom"
        WEB_START_CMD=""
        WEB_CONFIG_DIR=""
        WEB_ROOT=""
        INSTALL_APACHE=false
        ;;
esac

echo ""
log_success "Selected: ${WEB_SERVER_NAME}"
log_info   "Access log path: ${WEB_LOG_PATH}"
if [ -n "$WEB_ERROR_LOG" ]; then
    log_info "Error log path:  ${WEB_ERROR_LOG}"
fi
echo ""

# ── Validate XAMPP/LAMPP is installed if selected ─────────────────────────────
if [[ "$WEB_SERVER_TYPE" == "xampp" || "$WEB_SERVER_TYPE" == "lampp" ]]; then
    if [ ! -d "/opt/lampp" ]; then
        log_error "XAMPP/LAMPP not found at /opt/lampp"
        log_error "Please install XAMPP first from: https://www.apachefriends.org/download.html"
        log_info  "Then re-run this installer."
        exit 1
    fi

    if [ ! -f "/opt/lampp/lampp" ]; then
        log_error "/opt/lampp/lampp control script not found"
        log_error "XAMPP/LAMPP installation appears incomplete"
        exit 1
    fi

    log_success "XAMPP/LAMPP found at /opt/lampp"

    # Create log directory if it doesn't exist
    mkdir -p /opt/lampp/logs
    touch "$WEB_LOG_PATH" 2>/dev/null || true

    # Make sure Apache is running
    log_info "Starting XAMPP Apache..."
    /opt/lampp/lampp startapache 2>/dev/null || true
    log_success "XAMPP Apache started"
fi

# ── Validate custom log path ──────────────────────────────────────────────────
if [[ "$WEB_SERVER_TYPE" == "custom" ]]; then
    if [ ! -f "$WEB_LOG_PATH" ]; then
        log_warning "Log file not found: $WEB_LOG_PATH"
        log_warning "Sentinel will watch this path and begin monitoring once the file is created"
    else
        log_success "Log file found: $WEB_LOG_PATH"
    fi
fi

read -p "Press ENTER to continue with installation..."

################################################################################
# STEP 1: Update system packages
################################################################################
log_step "STEP 1: Updating System Packages"
apt-get update -qq
log_success "System packages updated"

################################################################################
# STEP 2: Install Docker
################################################################################
log_step "STEP 2: Installing Docker"

if command -v docker &> /dev/null; then
    log_success "Docker already installed: $(docker --version)"
else
    log_info "Installing Docker..."
    apt-get install -y -qq ca-certificates curl gnupg lsb-release
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    apt-get update -qq
    apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    systemctl start docker
    systemctl enable docker
    usermod -aG docker $ACTUAL_USER
    log_success "Docker installed successfully"
fi

################################################################################
# STEP 3: Install Docker Compose
################################################################################
log_step "STEP 3: Installing Docker Compose"

if command -v docker-compose &> /dev/null; then
    log_success "Docker Compose already installed: $(docker-compose --version)"
else
    log_info "Installing Docker Compose..."
    COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
    curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    log_success "Docker Compose installed successfully"
fi

################################################################################
# STEP 4: Install system dependencies + web server
################################################################################
log_step "STEP 4: Installing System Dependencies"

BASE_PACKAGES="python3 python3-pip git curl wget net-tools iptables ufw nano"

if [ "$INSTALL_APACHE" = true ]; then
    log_info "Installing Default Apache + base packages..."
    apt-get install -y -qq $BASE_PACKAGES apache2
    systemctl start apache2
    systemctl enable apache2
    log_success "Apache installed and started"
else
    log_info "Installing base packages (skipping Apache — using $WEB_SERVER_NAME)..."
    apt-get install -y -qq $BASE_PACKAGES
    log_success "Base packages installed"
fi

################################################################################
# STEP 5: Configure web server log path
################################################################################
log_step "STEP 5: Configuring Web Server Log Access"

case $WEB_SERVER_TYPE in
    apache)
        # Enable Apache logging (should be on by default)
        if [ -f "/etc/apache2/mods-available/log_config.load" ]; then
            a2enmod log_config 2>/dev/null || true
        fi

        # Ensure combined log format is enabled
        if ! grep -q "CustomLog" /etc/apache2/sites-enabled/*.conf 2>/dev/null; then
            log_info "Ensuring Apache combined log format is enabled..."
            cat >> /etc/apache2/conf-available/sentinel-logging.conf << 'APACHEEOF'
# Sentinel Agent - Ensure combined log format
LogFormat "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\"" combined
CustomLog ${APACHE_LOG_DIR}/access.log combined
APACHEEOF
            a2enconf sentinel-logging 2>/dev/null || true
        fi

        systemctl reload apache2 2>/dev/null || true
        log_success "Apache logging configured"
        ;;

    xampp|lampp)
        # Check if XAMPP Apache is logging
        XAMPP_HTTP_CONF="/opt/lampp/etc/httpd.conf"

        if [ -f "$XAMPP_HTTP_CONF" ]; then
            # Check if CustomLog is already configured
            if grep -q "CustomLog" "$XAMPP_HTTP_CONF"; then
                log_success "XAMPP Apache logging already configured"
            else
                log_info "Adding access log configuration to XAMPP httpd.conf..."
                cat >> "$XAMPP_HTTP_CONF" << 'XAMPPEOF'

# Sentinel Agent - Access Log Configuration
LogFormat "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\"" combined
CustomLog /opt/lampp/logs/access_log combined
XAMPPEOF
                log_success "XAMPP logging configured"
            fi

            # Restart XAMPP Apache to apply
            /opt/lampp/lampp stopapache 2>/dev/null || true
            sleep 1
            /opt/lampp/lampp startapache 2>/dev/null || true
            log_success "XAMPP Apache restarted with new logging config"
        else
            log_warning "XAMPP httpd.conf not found — logging may not be configured"
        fi

        # Ensure log file exists and is readable
        touch "$WEB_LOG_PATH" 2>/dev/null || true
        chmod 644 "$WEB_LOG_PATH" 2>/dev/null || true
        log_info "Log file ready: $WEB_LOG_PATH"
        ;;

    custom)
        # Make log file readable if it exists
        if [ -f "$WEB_LOG_PATH" ]; then
            chmod 644 "$WEB_LOG_PATH" 2>/dev/null || true
            log_success "Custom log file is accessible"
        else
            log_warning "Custom log file not found yet — will be monitored when created"
        fi
        ;;
esac

# Mount path for Docker — convert to container-accessible path
# Docker will mount /var/log or /opt/lampp/logs depending on selection
if [[ "$WEB_SERVER_TYPE" == "xampp" || "$WEB_SERVER_TYPE" == "lampp" ]]; then
    DOCKER_LOG_MOUNT="/opt/lampp/logs:/opt/lampp/logs:ro"
    CONTAINER_LOG_PATH="$WEB_LOG_PATH"
elif [[ "$WEB_SERVER_TYPE" == "apache" ]]; then
    DOCKER_LOG_MOUNT="/var/log:/var/log:ro"
    CONTAINER_LOG_PATH="$WEB_LOG_PATH"
else
    # Custom — mount parent directory
    CUSTOM_LOG_DIR=$(dirname "$WEB_LOG_PATH")
    DOCKER_LOG_MOUNT="${CUSTOM_LOG_DIR}:${CUSTOM_LOG_DIR}:ro"
    CONTAINER_LOG_PATH="$WEB_LOG_PATH"
fi

log_success "Docker log mount configured: $DOCKER_LOG_MOUNT"

################################################################################
# STEP 6: Check/Install Ollama
################################################################################
log_step "STEP 6: Checking Ollama Installation"

if command -v ollama &> /dev/null; then
    log_success "Ollama already installed"
    if pgrep -x "ollama" > /dev/null; then
        log_success "Ollama service is running"
    else
        log_info "Starting Ollama service..."
        sudo -u $ACTUAL_USER bash -c 'ollama serve' &
        sleep 3
    fi
else
    log_info "Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
    sudo -u $ACTUAL_USER bash -c 'ollama serve' &
    sleep 5
    log_success "Ollama installed and started"
fi

log_info "Checking for llama3:8b model..."
if sudo -u $ACTUAL_USER ollama list | grep -q "llama3:8b"; then
    log_success "llama3:8b model already downloaded"
else
    log_info "Downloading llama3:8b model (this may take a few minutes)..."
    sudo -u $ACTUAL_USER ollama pull llama3:8b
    log_success "llama3:8b model downloaded"
fi

# Configure Ollama for Docker access
log_info "Configuring Ollama network binding for Docker access..."
CURRENT_BINDING=$(ss -tlnp 2>/dev/null | grep 11434 | head -n1 || echo "")
if echo "$CURRENT_BINDING" | grep -q "127.0.0.1:11434"; then
    mkdir -p /etc/systemd/system/ollama.service.d/
    cat > /etc/systemd/system/ollama.service.d/override.conf << 'OLLAMAEOF'
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
OLLAMAEOF
    systemctl daemon-reload
    systemctl restart ollama
    sleep 3
    log_success "Ollama configured for Docker access"
else
    log_success "Ollama already accessible on network"
fi

################################################################################
# STEP 7: Configure firewall
################################################################################
log_step "STEP 7: Configuring Firewall"

ufw allow 22/tcp   comment 'SSH'    2>/dev/null || true
ufw allow 80/tcp   comment 'HTTP'   2>/dev/null || true
ufw allow 443/tcp  comment 'HTTPS'  2>/dev/null || true
ufw allow 8000/tcp comment 'Sentinel API'       2>/dev/null || true
ufw allow 8501/tcp comment 'Sentinel Dashboard' 2>/dev/null || true
ufw allow 11434/tcp comment 'Ollama LLM'        2>/dev/null || true

if [[ "$WEB_SERVER_TYPE" == "xampp" || "$WEB_SERVER_TYPE" == "lampp" ]]; then
    ufw allow 8080/tcp comment 'XAMPP HTTP'  2>/dev/null || true
    ufw allow 8443/tcp comment 'XAMPP HTTPS' 2>/dev/null || true
fi

log_info "Firewall rules configured (not enabled yet)"
log_warning "To enable: sudo ufw enable"

################################################################################
# STEP 8: Setup project directory
################################################################################
log_step "STEP 8: Setting Up Project Directory"

PROJECT_DIR="$ACTUAL_HOME/Project"

if [ -d "$PROJECT_DIR" ]; then
    log_info "Project directory exists at: $PROJECT_DIR"
else
    log_warning "Project directory not found at: $PROJECT_DIR"
    log_error "Please copy all Sentinel Agent files to: $PROJECT_DIR"
    exit 1
fi

cd "$PROJECT_DIR" || exit 1
log_success "Using project directory: $PROJECT_DIR"

################################################################################
# STEP 9: Update docker-compose.yml for selected web server
################################################################################
log_step "STEP 9: Configuring Docker for $WEB_SERVER_NAME"

if [[ "$WEB_SERVER_TYPE" == "xampp" || "$WEB_SERVER_TYPE" == "lampp" ]]; then
    log_info "Updating docker-compose.yml to mount XAMPP/LAMPP log directory..."

    # Backup original
    cp docker-compose.yml docker-compose.yml.backup

    # Replace the /var/log volume mount with the XAMPP logs mount
    sed -i 's|      - /var/log:/var/log:ro|      - /var/log:/var/log:ro\n      - /opt/lampp/logs:/opt/lampp/logs:ro|g' docker-compose.yml

    log_success "docker-compose.yml updated to include XAMPP log mount"

elif [[ "$WEB_SERVER_TYPE" == "custom" ]]; then
    log_info "Updating docker-compose.yml for custom log path..."
    cp docker-compose.yml docker-compose.yml.backup
    CUSTOM_LOG_DIR=$(dirname "$WEB_LOG_PATH")
    sed -i "s|      - /var/log:/var/log:ro|      - /var/log:/var/log:ro\n      - ${CUSTOM_LOG_DIR}:${CUSTOM_LOG_DIR}:ro|g" docker-compose.yml
    log_success "docker-compose.yml updated to mount $CUSTOM_LOG_DIR"
fi

################################################################################
# STEP 10: Create environment file
################################################################################
log_step "STEP 10: Creating Environment Configuration"

# Auto-detect server IP
DETECTED_IP=$(ip route get 8.8.8.8 2>/dev/null | grep -oP 'src \K[0-9.]+' | head -1)
if [ -z "$DETECTED_IP" ] || [ "$DETECTED_IP" = "127.0.0.1" ]; then
    DETECTED_IP=$(hostname -I 2>/dev/null | awk '{print $1}')
fi
if [ -z "$DETECTED_IP" ]; then
    DETECTED_IP="127.0.0.1"
    log_warning "Could not detect network IP — using localhost"
else
    log_success "Detected server IP: $DETECTED_IP"
fi

cat > .env << EOF
# Sentinel Agent Environment Configuration
# Auto-generated by AUTO_INSTALL.sh on $(date)
# Web Server: $WEB_SERVER_NAME

# Dashboard binding (auto-detected)
DASHBOARD_BIND_IP=$DETECTED_IP

# Ollama Configuration
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=llama3:8b
OLLAMA_HOST=http://host.docker.internal:11434
OLLAMA_API_BASE=http://host.docker.internal:11434

# Performance
CREW_TIMEOUT=60
OLLAMA_TIMEOUT=60
OLLAMA_TEMPERATURE=0.1
OLLAMA_TOP_P=0.9
OLLAMA_MAX_TOKENS=512
CREW_VERBOSE=0

# Logging
LITELLM_LOG=ERROR
CREWAI_TELEMETRY_OPT_OUT=1
LOG_LEVEL=INFO

# Web Server Log Paths
AUTH_LOG_PATH=/var/log/auth.log
WEB_LOG_PATH=$CONTAINER_LOG_PATH
WEB_SERVER_TYPE=$WEB_SERVER_TYPE

# Database
SENTINEL_DB_PATH=/app/data/sentinel_intel.db
SENTINEL_DATA_DIR=/app/data
SENTINEL_LOG_DIR=/app/logs

# API
API_HOST=0.0.0.0
API_PORT=8000
DASHBOARD_PORT=8501

# DDoS Detection
DDOS_THRESHOLD=50
DDOS_WINDOW=10
PORT_SCAN_THRESHOLD=20
EOF

chown $ACTUAL_USER:$ACTUAL_USER .env 2>/dev/null || true
log_success ".env file created with WEB_LOG_PATH=$CONTAINER_LOG_PATH"

################################################################################
# STEP 11: Set permissions
################################################################################
log_step "STEP 11: Setting File Permissions"

chown -R $ACTUAL_USER:$ACTUAL_USER "$PROJECT_DIR"
chmod +x *.sh 2>/dev/null || true
log_success "Permissions configured"

################################################################################
# STEP 12: Stop old containers
################################################################################
log_step "STEP 12: Cleaning Up Old Containers"

sudo -u $ACTUAL_USER docker-compose down 2>/dev/null || true
log_success "Old containers cleared"

################################################################################
# STEP 13: Build and start containers
################################################################################
log_step "STEP 13: Building and Starting Sentinel Agent"

log_info "Building Docker images (5-10 minutes)..."
sudo -u $ACTUAL_USER docker-compose build --no-cache
log_success "Docker images built"

log_info "Starting containers..."
sudo -u $ACTUAL_USER docker-compose up -d
sleep 8
log_success "Containers started"

################################################################################
# STEP 14: Verify installation
################################################################################
log_step "STEP 14: Verifying Installation"

sleep 5

if sudo -u $ACTUAL_USER docker-compose ps | grep -q "Up"; then
    log_success "Containers are running"
else
    log_warning "Containers may still be starting — check: docker-compose logs"
fi

log_info "Checking API health..."
sleep 3
if curl -s http://localhost:8000/api/health | grep -q "ok\|healthy"; then
    log_success "API is responding"
else
    log_warning "API still starting — wait 30 seconds then visit http://localhost:8000/api/health"
fi

# Verify log path is accessible inside container
log_info "Verifying log path inside container..."
if docker exec sentinel-agent test -f "$CONTAINER_LOG_PATH" 2>/dev/null; then
    log_success "Log file accessible inside container: $CONTAINER_LOG_PATH"
elif docker exec sentinel-agent test -d "$(dirname $CONTAINER_LOG_PATH)" 2>/dev/null; then
    log_warning "Log directory exists but log file not yet created — will monitor when Apache writes to it"
else
    log_warning "Log path not yet accessible: $CONTAINER_LOG_PATH"
    log_warning "Make sure $WEB_SERVER_NAME is running and has received at least one request"
fi

################################################################################
# STEP 15: Final summary
################################################################################
log_step "INSTALLATION COMPLETE!"

cat << EOF

${GREEN}╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║                    SENTINEL AGENT IS READY                               ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝${NC}

${CYAN}Web Server Configuration:${NC}
  Type:          ${GREEN}$WEB_SERVER_NAME${NC}
  Access log:    ${GREEN}$WEB_LOG_PATH${NC}
  Auth log:      ${GREEN}/var/log/auth.log${NC}

${CYAN}Access URLs:${NC}
  Dashboard:  http://$DETECTED_IP:8501  ${GREEN}(local network only)${NC}
  API:        http://$DETECTED_IP:8000
  Health:     http://$DETECTED_IP:8000/api/health

${CYAN}Default Credentials:${NC}
  Username: ${GREEN}admin${NC}
  Password: ${YELLOW}docker logs sentinel-agent | grep "DEFAULT ADMIN"${NC}
  ${RED}Change password immediately after first login!${NC}

${CYAN}Useful Commands:${NC}
  View logs:   ${YELLOW}docker-compose logs -f sentinel-agent${NC}
  Restart:     ${YELLOW}docker-compose restart${NC}
  Stop:        ${YELLOW}docker-compose down${NC}
  Start:       ${YELLOW}docker-compose up -d${NC}
  Test attacks:${YELLOW}python3 test_attacks.py${NC}

EOF

# Web-server-specific notes
if [[ "$WEB_SERVER_TYPE" == "xampp" || "$WEB_SERVER_TYPE" == "lampp" ]]; then
cat << EOF
${CYAN}XAMPP/LAMPP Notes:${NC}
  Start Apache: ${YELLOW}sudo /opt/lampp/lampp startapache${NC}
  Stop Apache:  ${YELLOW}sudo /opt/lampp/lampp stopapache${NC}
  Web root:     ${GREEN}/opt/lampp/htdocs${NC}
  Log file:     ${GREEN}$WEB_LOG_PATH${NC}
  Config:       ${GREEN}/opt/lampp/etc/httpd.conf${NC}

  ${YELLOW}If you restart XAMPP, Sentinel will automatically detect new log entries.${NC}

EOF
elif [[ "$WEB_SERVER_TYPE" == "custom" ]]; then
cat << EOF
${CYAN}Custom Web Server Notes:${NC}
  Log file:  ${GREEN}$WEB_LOG_PATH${NC}
  Make sure your web server writes Apache Combined Log Format to this path.

EOF
fi

cat << EOF
${YELLOW}Important:${NC}
  1. If you used sudo — LOGOUT AND LOGIN for Docker group to take effect
  2. Firewall configured but NOT enabled — run: ${YELLOW}sudo ufw enable${NC}
  3. AI analysis only runs for HIGH severity attacks (performance optimization)
  4. Docker compose backup saved to: docker-compose.yml.backup

${GREEN}Monitoring active for:${NC}
  SSH brute force, SQL injection, XSS, command injection,
  directory traversal, SSRF, DDoS, scanners, CSRF and more.

${GREEN}Happy monitoring!${NC}

EOF

exit 0