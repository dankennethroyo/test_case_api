#!/usr/bin/env bash
#####################################################################
#          NGINX WSL DEPLOYMENT - PRODUCTION READY                 #
#####################################################################
# This script performs complete NGINX-based WSL deployment with:
# - Flask isolated to localhost (127.0.0.1:5009)
# - NGINX as reverse proxy (0.0.0.0:8080)
# - Automatic cleanup of existing deployment
# - Security hardening
#
# Usage: ./deploy-nginx-wsl.sh
# Target: /opt/test_case_api

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WSL_TARGET="/opt/test_case_api"
BACKUP_DIR="${WSL_TARGET}.backup.$(date +%Y%m%d_%H%M%S)"

# Use local app directory (self-contained)
SOURCE_APP="$SCRIPT_DIR/app"
SOURCE_DEPLOY="$SCRIPT_DIR"
SOURCE_NGINX="$SCRIPT_DIR/nginx"

# Verify local app directory exists
if [ ! -d "$SOURCE_APP" ]; then
    echo -e "${RED}ERROR: App directory not found: $SOURCE_APP${NC}"
    echo "The deployment package seems incomplete."
    exit 1
fi

echo -e "${CYAN}═══════════════════════════════════════════════════${NC}"
echo -e "${CYAN}   🚀 NGINX WSL DEPLOYMENT (Production Ready)${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}Architecture:${NC}"
echo -e "  ${YELLOW}→${NC} Flask: 127.0.0.1:5009 (localhost only)"
echo -e "  ${YELLOW}→${NC} NGINX: 0.0.0.0:8080 (reverse proxy)"
echo -e "  ${YELLOW}→${NC} Windows: :8009 → WSL NGINX :8080"
echo ""
echo -e "${GREEN}This script will:${NC}"
echo -e "  ${YELLOW}→${NC} Clean existing deployment"
echo -e "  ${YELLOW}→${NC} Install/configure NGINX"
echo -e "  ${YELLOW}→${NC} Deploy Flask application"
echo -e "  ${YELLOW}→${NC} Set up systemd services"
echo -e "  ${YELLOW}→${NC} Configure security isolation"
echo -e "  ${YELLOW}→${NC} Test the installation"
echo ""
echo -e "${GREEN}Target:${NC} $WSL_TARGET"
echo ""

# Ask for confirmation
read -p "Continue with NGINX deployment? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Deployment cancelled.${NC}"
    exit 0
fi

# =================================================================
# STEP 0: Pre-Deployment Cleanup
# =================================================================
echo ""
echo -e "${BLUE}STEP 0: Cleaning existing deployment${NC}"

# Stop and disable existing services
if systemctl list-unit-files | grep -q "test-case-api.service"; then
    echo -e "${YELLOW}Stopping test-case-api service...${NC}"
    sudo systemctl stop test-case-api 2>/dev/null || true
    sudo systemctl disable test-case-api 2>/dev/null || true
    echo -e "${GREEN}✓ Service stopped${NC}"
fi

# Remove existing service file
if [ -f /etc/systemd/system/test-case-api.service ]; then
    echo -e "${YELLOW}Removing old service file...${NC}"
    sudo rm /etc/systemd/system/test-case-api.service
    sudo systemctl daemon-reload
    echo -e "${GREEN}✓ Service file removed${NC}"
fi

# Remove NGINX configuration if exists
if [ -f /etc/nginx/sites-enabled/test-case-api ]; then
    echo -e "${YELLOW}Removing old NGINX config...${NC}"
    sudo rm /etc/nginx/sites-enabled/test-case-api 2>/dev/null || true
    sudo rm /etc/nginx/sites-available/test-case-api 2>/dev/null || true
    echo -e "${GREEN}✓ NGINX config removed${NC}"
fi

# Backup and remove existing application directory
if [ -d "$WSL_TARGET" ]; then
    echo -e "${YELLOW}Creating backup of existing installation...${NC}"
    sudo cp -r "$WSL_TARGET" "$BACKUP_DIR" 2>/dev/null || true
    echo -e "${GREEN}✓ Backup created: $BACKUP_DIR${NC}"
    
    echo -e "${YELLOW}Removing existing application directory...${NC}"
    sudo rm -rf "$WSL_TARGET"
    echo -e "${GREEN}✓ Old installation removed${NC}"
fi

echo -e "${GREEN}✓ Cleanup completed${NC}"

# =================================================================
# STEP 1: Install and Configure NGINX
# =================================================================
echo ""
echo -e "${BLUE}STEP 1: Installing and configuring NGINX${NC}"

# Install NGINX if not present
if ! command -v nginx &> /dev/null; then
    echo -e "${YELLOW}Installing NGINX...${NC}"
    sudo apt-get update
    sudo apt-get install -y nginx
    echo -e "${GREEN}✓ NGINX installed${NC}"
else
    echo -e "${GREEN}✓ NGINX already installed${NC}"
fi

# Copy NGINX configuration
echo -e "${YELLOW}Configuring NGINX...${NC}"
sudo cp "$SOURCE_NGINX/test-case-api.nginx.conf" /etc/nginx/sites-available/test-case-api
sudo ln -sf /etc/nginx/sites-available/test-case-api /etc/nginx/sites-enabled/test-case-api

# Remove default site if it exists
if [ -f /etc/nginx/sites-enabled/default ]; then
    sudo rm /etc/nginx/sites-enabled/default
    echo -e "${GREEN}✓ Default site removed${NC}"
fi

# Test NGINX configuration
echo -e "${YELLOW}Testing NGINX configuration...${NC}"
if sudo nginx -t; then
    echo -e "${GREEN}✓ NGINX configuration valid${NC}"
else
    echo -e "${RED}✗ NGINX configuration test failed${NC}"
    exit 1
fi

# Enable and start NGINX
sudo systemctl enable nginx
sudo systemctl restart nginx
echo -e "${GREEN}✓ NGINX configured and running${NC}"

# =================================================================
# STEP 2: Create Application Directory and Copy Files
# =================================================================
echo ""
echo -e "${BLUE}STEP 2: Setting up application files${NC}"

# Create directory structure
echo -e "${YELLOW}Creating directory structure...${NC}"
sudo mkdir -p "$WSL_TARGET"
sudo mkdir -p "$WSL_TARGET/logs"
sudo mkdir -p "$WSL_TARGET/output"
sudo mkdir -p "$WSL_TARGET/converted"
sudo chown -R $(whoami):$(whoami) "$WSL_TARGET"
echo -e "${GREEN}✓ Directory structure created${NC}"

# Copy application files
echo -e "${YELLOW}Copying application files...${NC}"

# Copy app.py
if [ -f "$SOURCE_APP/app.py" ]; then
    sudo cp "$SOURCE_APP/app.py" "$WSL_TARGET/"
    echo -e "${GREEN}  ✓ app.py${NC}"
else
    echo -e "${RED}  ✗ app.py not found!${NC}"
    exit 1
fi

# Copy GUI directories and other assets
for dir in admin_gui public_gui instructions samples; do
    if [ -d "$SOURCE_APP/$dir" ]; then
        sudo rm -rf "$WSL_TARGET/$dir" 2>/dev/null || true
        sudo cp -r "$SOURCE_APP/$dir" "$WSL_TARGET/"
        echo -e "${GREEN}  ✓ $dir/${NC}"
    else
        echo -e "${YELLOW}  ⚠ $dir/ not found, skipping${NC}"
    fi
done

# Copy requirements.txt
if [ -f "$SOURCE_DEPLOY/requirements.txt" ]; then
    sudo cp "$SOURCE_DEPLOY/requirements.txt" "$WSL_TARGET/"
    echo -e "${GREEN}  ✓ requirements.txt${NC}"
else
    echo -e "${RED}  ✗ requirements.txt not found!${NC}"
    exit 1
fi

# Create .env file with localhost binding
echo -e "${YELLOW}Creating environment configuration...${NC}"
WIN_HOST_IP=$(ip route show | grep default | awk '{print $3}')
echo -e "${GREEN}  ✓ Windows host IP detected: $WIN_HOST_IP${NC}"

sudo tee "$WSL_TARGET/.env" > /dev/null << EOF
# Test Case Generator API Configuration - NGINX Deployment

# Ollama Configuration
# URL where Ollama is running (Windows host from WSL)
OLLAMA_BASE_URL=http://$WIN_HOST_IP:11434

# Ollama model to use for test case generation
OLLAMA_MODEL=phi4:14b

# Timeout for Ollama API calls (seconds)
OLLAMA_TIMEOUT=180

# Flask Configuration
# SECURITY: Bind to localhost only (127.0.0.1) - Ubuntu OS access only
# NGINX will handle external access on 0.0.0.0:8080
HOST=127.0.0.1
PORT=5009

# Debug mode (False for production deployment)
FLASK_DEBUG=False
DEBUG_MODE=False

# File Upload Configuration
MAX_FILE_SIZE_MB=10

# Logging
LOG_LEVEL=INFO

# Target file for batch requirements
TARGET_FILE=samples/batch_requirements.json
TARGET_FILE_NAME=batch_requirements.json

USE_STREAMING=True
EOF
sudo chown $(whoami):$(whoami) "$WSL_TARGET/.env"
echo -e "${GREEN}✓ Environment configuration created (Flask on 127.0.0.1:5009)${NC}"

echo -e "${GREEN}✓ Application files copied${NC}"

# =================================================================
# STEP 3: Set Up Python Environment
# =================================================================
echo ""
echo -e "${BLUE}STEP 3: Setting up Python environment${NC}"

# Create virtual environment
echo -e "${YELLOW}Creating virtual environment...${NC}"
cd "$WSL_TARGET"
python3 -m venv venv
echo -e "${GREEN}✓ Virtual environment created${NC}"

# Activate and install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# =================================================================
# STEP 4: Create Systemd Service
# =================================================================
echo ""
echo -e "${BLUE}STEP 4: Creating systemd service${NC}"

# Get current user
CURRENT_USER=$(whoami)

# Create service file
sudo tee /etc/systemd/system/test-case-api.service > /dev/null << EOF
[Unit]
Description=Test Case API Service (Flask Backend)
After=network.target
Requires=nginx.service

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$WSL_TARGET
Environment=PATH=$WSL_TARGET/venv/bin
ExecStart=$WSL_TARGET/venv/bin/python $WSL_TARGET/app.py
Restart=always
RestartSec=5

# Security: Flask should only listen on localhost
PrivateTmp=yes
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✓ Service file created${NC}"

# =================================================================
# STEP 5: Start Services
# =================================================================
echo ""
echo -e "${BLUE}STEP 5: Starting services${NC}"

# Reload systemd
sudo systemctl daemon-reload

# Enable and start Flask service
sudo systemctl enable test-case-api
sudo systemctl start test-case-api

# Check Flask status
if sudo systemctl is-active --quiet test-case-api; then
    echo -e "${GREEN}✓ Flask service started successfully${NC}"
else
    echo -e "${RED}✗ Flask service failed to start${NC}"
    echo -e "${YELLOW}Check logs: sudo journalctl -u test-case-api -n 20${NC}"
    exit 1
fi

# Ensure NGINX is running
sudo systemctl restart nginx
if sudo systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✓ NGINX service running${NC}"
else
    echo -e "${RED}✗ NGINX service failed${NC}"
    exit 1
fi

# =================================================================
# STEP 6: Test Installation
# =================================================================
echo ""
echo -e "${BLUE}STEP 6: Testing installation${NC}"

# Wait for services to fully start
sleep 3

# Test 1: Flask internal access (localhost only)
echo -e "${YELLOW}Testing Flask internal access (127.0.0.1:5009)...${NC}"
if curl -s http://127.0.0.1:5009/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Flask responding on localhost${NC}"
else
    echo -e "${RED}✗ Flask not responding on localhost${NC}"
    echo -e "${YELLOW}Check logs: sudo journalctl -u test-case-api -n 20${NC}"
fi

# Test 2: NGINX proxy access
echo -e "${YELLOW}Testing NGINX proxy access (localhost:8080)...${NC}"
if curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ NGINX proxy working${NC}"
    
    # Get health response through NGINX
    HEALTH_RESPONSE=$(curl -s http://localhost:8080/health)
    echo -e "${GREEN}Health check response (via NGINX):${NC}"
    echo "$HEALTH_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$HEALTH_RESPONSE"
else
    echo -e "${RED}✗ NGINX proxy test failed${NC}"
    echo -e "${YELLOW}Check NGINX logs: sudo tail -f /var/log/nginx/test-case-api-error.log${NC}"
fi

# Test 3: Security check - Flask should not be accessible externally
WSL_IP=$(ip addr show eth0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}')
echo -e "${YELLOW}Security check: Flask should NOT be accessible on $WSL_IP:5009...${NC}"
if timeout 2 curl -s http://$WSL_IP:5009/health > /dev/null 2>&1; then
    echo -e "${RED}⚠ WARNING: Flask is accessible externally (security issue)${NC}"
else
    echo -e "${GREEN}✓ Flask properly isolated to localhost${NC}"
fi

# =================================================================
# DEPLOYMENT COMPLETE
# =================================================================
echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════${NC}"
echo -e "${CYAN}   🎉 NGINX DEPLOYMENT COMPLETED!${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}Architecture:${NC}"
echo -e "  ${BLUE}Flask:${NC} 127.0.0.1:5009 (localhost only)"
echo -e "  ${BLUE}NGINX:${NC} 0.0.0.0:8080 (public interface)"
echo ""
echo -e "${GREEN}Access URLs:${NC}"
echo -e "  ${BLUE}WSL Internal:${NC} http://localhost:8080"
echo -e "  ${BLUE}Windows:${NC} http://localhost:8009 (after Windows setup)"
echo -e "  ${BLUE}Network:${NC} http://<Windows-IP>:8009 (after Windows setup)"
echo ""
echo -e "${GREEN}Service management:${NC}"
echo -e "  ${YELLOW}Flask Status:${NC} sudo systemctl status test-case-api"
echo -e "  ${YELLOW}Flask Logs:${NC} sudo journalctl -u test-case-api -f"
echo -e "  ${YELLOW}NGINX Status:${NC} sudo systemctl status nginx"
echo -e "  ${YELLOW}NGINX Logs:${NC} sudo tail -f /var/log/nginx/test-case-api-error.log"
echo -e "  ${YELLOW}Restart Flask:${NC} sudo systemctl restart test-case-api"
echo -e "  ${YELLOW}Restart NGINX:${NC} sudo systemctl restart nginx"
echo ""
echo -e "${GREEN}Application location:${NC} $WSL_TARGET"
echo ""
echo -e "${CYAN}Next: Run setup-windows.ps1 on Windows for port forwarding!${NC}"
echo ""

# Display recent service logs
echo -e "${YELLOW}Recent Flask service logs:${NC}"
sudo journalctl -u test-case-api -n 5 --no-pager
echo ""
echo -e "${YELLOW}NGINX status:${NC}"
sudo nginx -t
