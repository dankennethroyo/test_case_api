#!/usr/bin/env bash
#####################################################################
#              Quick Update Test Case API in WSL                    #
#####################################################################
# This script quickly updates only the application code files
# Use this for rapid development iterations
# Usage: ./quick-update-wsl.sh [target-directory]
# Default target: /opt/test-case-api

set -e  # Exit on error

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
WSL_TARGET="${1:-/opt/test-case-api}"

# Detect Windows mount path
WIN_MOUNT_PATH=""
if [ -d "/mnt/d/DK\$/_Projects/test_case_api" ]; then
    WIN_MOUNT_PATH="/mnt/d/DK\$/_Projects/test_case_api"
elif [ -d "/mnt/c/Projects/test_case_api" ]; then
    WIN_MOUNT_PATH="/mnt/c/Projects/test_case_api"
else
    # Try to find from current script location
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    if [[ "$SCRIPT_DIR" == /mnt/* ]]; then
        WIN_MOUNT_PATH="$(dirname "$SCRIPT_DIR")"
    else
        echo -e "${RED}ERROR: Could not auto-detect Windows mount path${NC}"
        exit 1
    fi
fi

echo -e "${BLUE}Quick Update - Test Case API${NC}"
echo -e "Source: ${GREEN}$WIN_MOUNT_PATH${NC}"
echo -e "Target: ${GREEN}$WSL_TARGET${NC}"
echo ""

# Check if target exists
if [ ! -d "$WSL_TARGET" ]; then
    echo -e "${RED}ERROR: Target directory not found: $WSL_TARGET${NC}"
    echo "Run sync-to-wsl.sh first for initial setup"
    exit 1
fi

# Update files
echo -e "${YELLOW}Updating files...${NC}"

# Main app
echo -n "  • app.py ... "
sudo cp "$WIN_MOUNT_PATH/test_case_api/app.py" "$WSL_TARGET/"
echo -e "${GREEN}✓${NC}"

# Admin GUI
echo -n "  • admin_gui/ ... "
sudo cp -r "$WIN_MOUNT_PATH/test_case_api/admin_gui/"* "$WSL_TARGET/admin_gui/"
echo -e "${GREEN}✓${NC}"

# Public GUI
echo -n "  • public_gui/ ... "
sudo cp -r "$WIN_MOUNT_PATH/test_case_api/public_gui/"* "$WSL_TARGET/public_gui/"
echo -e "${GREEN}✓${NC}"

# Instructions
echo -n "  • instructions/ ... "
sudo cp -r "$WIN_MOUNT_PATH/test_case_api/instructions/"* "$WSL_TARGET/instructions/"
echo -e "${GREEN}✓${NC}"

# Fix permissions
CURRENT_USER=$(whoami)
sudo chown -R $CURRENT_USER:$CURRENT_USER "$WSL_TARGET"

echo ""
echo -e "${GREEN}✓ Update completed!${NC}"
echo ""
echo -e "${YELLOW}Restarting service...${NC}"
sudo systemctl restart test-case-api

sleep 2

# Show status
echo ""
echo -e "${BLUE}Service Status:${NC}"
sudo systemctl status test-case-api --no-pager -l | head -n 15

echo ""
echo -e "${GREEN}Done! 🚀${NC}"
echo -e "${YELLOW}View logs: ${NC}sudo journalctl -u test-case-api -f"
