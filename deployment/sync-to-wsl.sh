#!/usr/bin/env bash
#####################################################################
#                  Sync Test Case API to WSL                        #
#####################################################################
# This script syncs the application files from Windows to WSL
# Usage: ./sync-to-wsl.sh [target-directory]
# Default target: /opt/test-case-api

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
WSL_TARGET="${1:-/opt/test-case-api}"
BACKUP_DIR="${WSL_TARGET}.backup.$(date +%Y%m%d_%H%M%S)"

# Detect Windows mount path
# Try to find the project on Windows filesystem
WIN_MOUNT_PATH=""
if [ -d "/mnt/d/DK\$/_Projects/test_case_api" ]; then
    WIN_MOUNT_PATH="/mnt/d/DK\$/_Projects/test_case_api"
elif [ -d "/mnt/c/Projects/test_case_api" ]; then
    WIN_MOUNT_PATH="/mnt/c/Projects/test_case_api"
elif [ -d "/mnt/c/Users/$USER/Projects/test_case_api" ]; then
    WIN_MOUNT_PATH="/mnt/c/Users/$USER/Projects/test_case_api"
else
    # Auto-detect from current directory
    if [[ "$SCRIPT_DIR" == /mnt/* ]]; then
        WIN_MOUNT_PATH="$PROJECT_ROOT"
    else
        echo -e "${RED}ERROR: Could not find Windows mount path${NC}"
        echo "Please run this script from WSL with access to Windows filesystem"
        echo "Or specify the Windows mount path manually"
        exit 1
    fi
fi

echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   Test Case API - Sync to WSL${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}Source (Windows):${NC} $WIN_MOUNT_PATH"
echo -e "${GREEN}Target (WSL):${NC} $WSL_TARGET"
echo ""

# Check if source exists
if [ ! -d "$WIN_MOUNT_PATH" ]; then
    echo -e "${RED}ERROR: Source directory not found: $WIN_MOUNT_PATH${NC}"
    exit 1
fi

# Ask for confirmation
read -p "Continue with sync? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Sync cancelled.${NC}"
    exit 0
fi

# Create backup if target exists
if [ -d "$WSL_TARGET" ]; then
    echo -e "${YELLOW}Creating backup...${NC}"
    sudo cp -r "$WSL_TARGET" "$BACKUP_DIR"
    echo -e "${GREEN}✓ Backup created: $BACKUP_DIR${NC}"
fi

# Create target directory if it doesn't exist
echo -e "${YELLOW}Creating target directory...${NC}"
sudo mkdir -p "$WSL_TARGET"
echo -e "${GREEN}✓ Target directory ready${NC}"

# Sync application files
echo ""
echo -e "${BLUE}Syncing application files...${NC}"

# Copy main application file
echo -e "${YELLOW}  → app.py${NC}"
sudo cp "$WIN_MOUNT_PATH/test_case_api/app.py" "$WSL_TARGET/"

# Copy GUI directories
echo -e "${YELLOW}  → admin_gui/${NC}"
sudo rm -rf "$WSL_TARGET/admin_gui"
sudo cp -r "$WIN_MOUNT_PATH/test_case_api/admin_gui" "$WSL_TARGET/"

echo -e "${YELLOW}  → public_gui/${NC}"
sudo rm -rf "$WSL_TARGET/public_gui"
sudo cp -r "$WIN_MOUNT_PATH/test_case_api/public_gui" "$WSL_TARGET/"

# Copy instructions
echo -e "${YELLOW}  → instructions/${NC}"
sudo rm -rf "$WSL_TARGET/instructions"
sudo cp -r "$WIN_MOUNT_PATH/test_case_api/instructions" "$WSL_TARGET/"

# Copy samples (optional)
if [ -d "$WIN_MOUNT_PATH/test_case_api/samples" ]; then
    echo -e "${YELLOW}  → samples/${NC}"
    sudo rm -rf "$WSL_TARGET/samples"
    sudo cp -r "$WIN_MOUNT_PATH/test_case_api/samples" "$WSL_TARGET/"
fi

# Copy deployment reference files
echo ""
echo -e "${BLUE}Syncing deployment reference files...${NC}"

if [ -d "$WIN_MOUNT_PATH/deployment/reference_from_WSL" ]; then
    echo -e "${YELLOW}  → .env (reference)${NC}"
    if [ -f "$WIN_MOUNT_PATH/deployment/reference_from_WSL/.env" ]; then
        sudo cp "$WIN_MOUNT_PATH/deployment/reference_from_WSL/.env" "$WSL_TARGET/.env.reference"
        echo -e "${GREEN}    ✓ Copied as .env.reference (review before using)${NC}"
    fi
    
    echo -e "${YELLOW}  → test-case-api.service (reference)${NC}"
    if [ -f "$WIN_MOUNT_PATH/deployment/reference_from_WSL/test-case-api.service" ]; then
        sudo cp "$WIN_MOUNT_PATH/deployment/reference_from_WSL/test-case-api.service" "$WSL_TARGET/test-case-api.service.reference"
        echo -e "${GREEN}    ✓ Copied as test-case-api.service.reference${NC}"
    fi
    
    echo -e "${YELLOW}  → generate-env.sh${NC}"
    if [ -f "$WIN_MOUNT_PATH/deployment/reference_from_WSL/generate-env.sh" ]; then
        sudo cp "$WIN_MOUNT_PATH/deployment/reference_from_WSL/generate-env.sh" "$WSL_TARGET/"
        sudo chmod +x "$WSL_TARGET/generate-env.sh"
        echo -e "${GREEN}    ✓ Copied and made executable${NC}"
    fi
fi

# Create output directories
echo ""
echo -e "${BLUE}Creating output directories...${NC}"
sudo mkdir -p "$WSL_TARGET/output"
sudo mkdir -p "$WSL_TARGET/converted"
echo -e "${GREEN}✓ Output directories created${NC}"

# Set permissions
echo ""
echo -e "${BLUE}Setting permissions...${NC}"
CURRENT_USER=$(whoami)
sudo chown -R $CURRENT_USER:$CURRENT_USER "$WSL_TARGET"
echo -e "${GREEN}✓ Permissions set for user: $CURRENT_USER${NC}"

# Check if .env exists, if not, prompt to generate or copy
echo ""
if [ ! -f "$WSL_TARGET/.env" ]; then
    echo -e "${YELLOW}⚠️  No .env file found in target directory${NC}"
    
    if [ -f "$WSL_TARGET/generate-env.sh" ]; then
        echo ""
        read -p "Generate .env file now? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            cd "$WSL_TARGET"
            ./generate-env.sh
            echo -e "${GREEN}✓ .env file generated${NC}"
        else
            echo -e "${YELLOW}  You can generate it later with: cd $WSL_TARGET && ./generate-env.sh${NC}"
        fi
    elif [ -f "$WSL_TARGET/.env.reference" ]; then
        echo ""
        read -p "Copy .env.reference to .env? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            sudo cp "$WSL_TARGET/.env.reference" "$WSL_TARGET/.env"
            echo -e "${GREEN}✓ .env file copied from reference${NC}"
            echo -e "${YELLOW}  Please review and update $WSL_TARGET/.env with your settings${NC}"
        fi
    fi
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# Summary
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Sync completed successfully!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}Synced files:${NC}"
echo "  • app.py"
echo "  • admin_gui/"
echo "  • public_gui/"
echo "  • instructions/"
echo "  • samples/"
echo "  • deployment references (generate-env.sh, .env.reference, service file)"
echo ""

if [ -d "$WSL_TARGET/venv" ]; then
    echo -e "${GREEN}Virtual environment detected.${NC}"
    echo -e "${YELLOW}Reminder: If you updated dependencies, run:${NC}"
    echo "  cd $WSL_TARGET"
    echo "  source venv/bin/activate"
    echo "  pip install --upgrade flask flask-cors requests python-dotenv gunicorn"
    echo ""
fi

echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Review configuration: nano $WSL_TARGET/.env"
echo "  2. Restart service: sudo systemctl restart test-case-api"
echo "  3. Check status: sudo systemctl status test-case-api"
echo "  4. View logs: sudo journalctl -u test-case-api -f"
echo ""

if [ -d "$BACKUP_DIR" ]; then
    echo -e "${GREEN}Backup saved to: $BACKUP_DIR${NC}"
    echo -e "${YELLOW}You can remove it after verifying the sync:${NC}"
    echo "  sudo rm -rf $BACKUP_DIR"
    echo ""
fi

echo -e "${GREEN}Done! 🚀${NC}"
