#!/usr/bin/env bash
#####################################################################
#          REGULAR WSL DEPLOYMENT - ONE COMMAND                    #
#####################################################################
# This script performs the complete regular WSL deployment
# Usage: ./deploy-regular-wsl.sh
# Target: /opt/test_case_api (regular isolated installation)

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

# Use local app directory (everything is self-contained)
SOURCE_APP="$SCRIPT_DIR/app"
SOURCE_DEPLOY="$SCRIPT_DIR"

# Verify local app directory exists
if [ ! -d "$SOURCE_APP" ]; then
    echo -e "${RED}ERROR: App directory not found: $SOURCE_APP${NC}"
    echo "The isolated deployment package seems incomplete."
    exit 1
fi

echo -e "${CYAN}═══════════════════════════════════════════════════${NC}"
echo -e "${CYAN}   🚀 REGULAR WSL DEPLOYMENT${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}This script will:${NC}"
echo -e "  ${YELLOW}→${NC} Create application directory"
echo -e "  ${YELLOW}→${NC} Copy application files"
echo -e "  ${YELLOW}→${NC} Set up Python environment"
echo -e "  ${YELLOW}→${NC} Create systemd service"
echo -e "  ${YELLOW}→${NC} Start services"
echo -e "  ${YELLOW}→${NC} Test the installation"
echo ""
echo -e "${GREEN}Target:${NC} $WSL_TARGET"
echo -e "${GREEN}Port:${NC} 5009 (WSL)"
echo ""

# Ask for confirmation
read -p "Continue with regular deployment? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Deployment cancelled.${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}Starting deployment...${NC}"

# =================================================================
# STEP 1: Create Application Directory and Copy Files
# =================================================================
echo ""
echo -e "${BLUE}STEP 1: Setting up application files${NC}"

# Create backup if target exists
if [ -d "$WSL_TARGET" ]; then
    echo -e "${YELLOW}Creating backup...${NC}"
    sudo cp -r "$WSL_TARGET" "$BACKUP_DIR"
    echo -e "${GREEN}✓ Backup created: $BACKUP_DIR${NC}"
fi

# Create target directory
echo -e "${YELLOW}Creating directory structure...${NC}"
sudo mkdir -p "$WSL_TARGET"
sudo mkdir -p "$WSL_TARGET/logs"
sudo mkdir -p "$WSL_TARGET/output"
sudo mkdir -p "$WSL_TARGET/converted"
sudo chown -R $(whoami):$(whoami) "$WSL_TARGET"
echo -e "${GREEN}✓ Directory structure created${NC}"

# Copy core application files
echo -e "${YELLOW}Copying application files...${NC}"

# Copy app.py as the main app
if [ -f "$SOURCE_APP/app.py" ]; then
    sudo cp "$SOURCE_APP/app.py" "$WSL_TARGET/"
    echo -e "${GREEN}  ✓ app.py${NC}"
else
    echo -e "${RED}  ✗ app.py not found!${NC}"
    exit 1
fi

# Copy GUI directories
for gui_dir in admin_gui public_gui instructions samples; do
    if [ -d "$SOURCE_APP/$gui_dir" ]; then
        sudo rm -rf "$WSL_TARGET/$gui_dir" 2>/dev/null || true
        sudo cp -r "$SOURCE_APP/$gui_dir" "$WSL_TARGET/"
        echo -e "${GREEN}  ✓ $gui_dir/${NC}"
    else
        echo -e "${YELLOW}  ⚠ $gui_dir/ not found, skipping${NC}"
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

# Create .env file with deployment-specific settings
echo -e "${YELLOW}Creating environment configuration...${NC}"
# Get Windows host IP for Ollama connection
WIN_HOST_IP=$(ip route show | grep default | awk '{print $3}')
echo -e "${GREEN}  ✓ Windows host IP detected: $WIN_HOST_IP${NC}"
sudo tee "$WSL_TARGET/.env" > /dev/null << EOF
# Test Case Generator API Configuration - Regular Deployment

# Ollama Configuration
# URL where Ollama is running (Windows host from WSL)
OLLAMA_BASE_URL=http://$WIN_HOST_IP:11434

# Ollama model to use for test case generation
OLLAMA_MODEL=phi4:14b

# Timeout for Ollama API calls (seconds)
OLLAMA_TIMEOUT=180

# Flask Configuration
# Host and port for the API server
# 0.0.0.0 allows port forwarding from Windows host
HOST=0.0.0.0
PORT=5009

# Debug mode (False for production deployment)
FLASK_DEBUG=False
DEBUG_MODE=False

# File Upload Configuration
# Maximum file size in MB
MAX_FILE_SIZE_MB=10

# Logging
LOG_LEVEL=INFO

# Target file for batch requirements
TARGET_FILE=samples/batch_requirements.json
TARGET_FILE_NAME=batch_requirements.json

USE_STREAMING=True
EOF
sudo chown $(whoami):$(whoami) "$WSL_TARGET/.env"
echo -e "${GREEN}✓ Environment configuration created${NC}"

echo -e "${GREEN}✓ Application files copied${NC}"

# =================================================================
# STEP 2: Set Up Python Environment
# =================================================================
echo ""
echo -e "${BLUE}STEP 2: Setting up Python environment${NC}"

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
# STEP 3: Create Systemd Service
# =================================================================
echo ""
echo -e "${BLUE}STEP 3: Creating systemd service${NC}"

# Get current user
CURRENT_USER=$(whoami)

# Create service file
sudo tee /etc/systemd/system/test-case-api.service > /dev/null << EOF
[Unit]
Description=Test Case API Service
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$WSL_TARGET
Environment=PATH=$WSL_TARGET/venv/bin
ExecStart=$WSL_TARGET/venv/bin/python $WSL_TARGET/app.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✓ Service file created${NC}"

# =================================================================
# STEP 4: Start Services
# =================================================================
echo ""
echo -e "${BLUE}STEP 4: Starting services${NC}"

# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable test-case-api
sudo systemctl start test-case-api

# Check status
if sudo systemctl is-active --quiet test-case-api; then
    echo -e "${GREEN}✓ Service started successfully${NC}"
else
    echo -e "${RED}✗ Service failed to start${NC}"
    echo -e "${YELLOW}Check logs: sudo journalctl -u test-case-api -n 20${NC}"
    exit 1
fi

# =================================================================
# STEP 5: Test Installation
# =================================================================
echo ""
echo -e "${BLUE}STEP 5: Testing installation${NC}"

# Wait a moment for service to fully start
sleep 3

# Test health endpoint
echo -e "${YELLOW}Testing API endpoint...${NC}"
if curl -s http://localhost:5009/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ API is responding${NC}"

    # Get full health response
    HEALTH_RESPONSE=$(curl -s http://localhost:5009/health)
    echo -e "${GREEN}Health check response:${NC}"
    echo "$HEALTH_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$HEALTH_RESPONSE"
else
    echo -e "${RED}✗ API test failed${NC}"
    echo -e "${YELLOW}Service may still be starting. Check logs: sudo journalctl -u test-case-api -f${NC}"
fi

# =================================================================
# DEPLOYMENT COMPLETE
# =================================================================
echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════${NC}"
echo -e "${CYAN}   🎉 REGULAR DEPLOYMENT COMPLETED!${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}Your Test Case API is running at:${NC}"
echo -e "  ${BLUE}Internal (WSL):${NC} http://localhost:5009"
echo -e "  ${BLUE}External (Windows):${NC} http://localhost:8009 (after Windows setup)"
echo ""
echo -e "${GREEN}Service management:${NC}"
echo -e "  ${YELLOW}Status:${NC} sudo systemctl status test-case-api"
echo -e "  ${YELLOW}Logs:${NC} sudo journalctl -u test-case-api -f"
echo -e "  ${YELLOW}Restart:${NC} sudo systemctl restart test-case-api"
echo ""
echo -e "${GREEN}Application location:${NC} $WSL_TARGET"
echo ""
echo -e "${CYAN}Next: Run setup-windows.ps1 on Windows for port forwarding!${NC}"
echo ""

# Display service logs for verification
echo -e "${YELLOW}Recent service logs:${NC}"
sudo journalctl -u test-case-api -n 5 --no-pager