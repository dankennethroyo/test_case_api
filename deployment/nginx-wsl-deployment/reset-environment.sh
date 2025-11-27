#!/usr/bin/env bash
#####################################################################
#          Environment Reset Script - NGINX Deployment             #
#####################################################################
# This script removes the NGINX-based deployment completely
# Usage: ./reset-environment.sh

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${YELLOW}═══════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}   Environment Reset - NGINX Deployment${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════${NC}"
echo ""
echo -e "${RED}WARNING: This will:${NC}"
echo -e "  • Stop and remove test-case-api service"
echo -e "  • Remove NGINX configuration"
echo -e "  • Delete /opt/test_case_api directory"
echo -e "  • Clean up Python environments"
echo ""

read -p "Are you sure you want to reset? (yes/no): " -r
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo -e "${YELLOW}Reset cancelled.${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}Starting reset process...${NC}"

# ====================================================================
# STEP 1: Stop and Remove Services
# ====================================================================
echo ""
echo -e "${BLUE}STEP 1: Stopping and removing services${NC}"

if systemctl list-unit-files | grep -q "test-case-api.service"; then
    echo -e "${YELLOW}Stopping test-case-api service...${NC}"
    sudo systemctl stop test-case-api 2>/dev/null || true
    sudo systemctl disable test-case-api 2>/dev/null || true
    echo -e "${GREEN}✓ Service stopped and disabled${NC}"
    
    if [ -f /etc/systemd/system/test-case-api.service ]; then
        sudo rm /etc/systemd/system/test-case-api.service
        sudo systemctl daemon-reload
        echo -e "${GREEN}✓ Service file removed${NC}"
    fi
else
    echo -e "${GREEN}✓ No test-case-api service found${NC}"
fi

# ====================================================================
# STEP 2: Remove Application Directory
# ====================================================================
echo ""
echo -e "${BLUE}STEP 2: Removing application directory${NC}"

if [ -d /opt/test_case_api ]; then
    echo -e "${YELLOW}Removing /opt/test_case_api...${NC}"
    sudo rm -rf /opt/test_case_api
    echo -e "${GREEN}✓ Application directory removed${NC}"
else
    echo -e "${GREEN}✓ No application directory found${NC}"
fi

# Remove backups (optional)
BACKUP_COUNT=$(sudo find /opt -maxdepth 1 -type d -name "test_case_api.backup.*" 2>/dev/null | wc -l)
if [ $BACKUP_COUNT -gt 0 ]; then
    echo -e "${YELLOW}Found $BACKUP_COUNT backup(s). Remove them? (y/n)${NC}"
    read -p "" -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo rm -rf /opt/test_case_api.backup.* 2>/dev/null || true
        echo -e "${GREEN}✓ Backups removed${NC}"
    else
        echo -e "${YELLOW}Backups kept${NC}"
    fi
fi

# ====================================================================
# STEP 3: Remove NGINX Configuration
# ====================================================================
echo ""
echo -e "${BLUE}STEP 3: Removing NGINX configuration${NC}"

if [ -f /etc/nginx/sites-enabled/test-case-api ] || [ -f /etc/nginx/sites-available/test-case-api ]; then
    echo -e "${YELLOW}Removing NGINX configuration...${NC}"
    
    # Remove symlink
    if [ -L /etc/nginx/sites-enabled/test-case-api ]; then
        sudo rm /etc/nginx/sites-enabled/test-case-api
        echo -e "${GREEN}✓ Removed symlink from sites-enabled${NC}"
    fi
    
    # Remove config file
    if [ -f /etc/nginx/sites-available/test-case-api ]; then
        sudo rm /etc/nginx/sites-available/test-case-api
        echo -e "${GREEN}✓ Removed config from sites-available${NC}"
    fi
    
    # Reload NGINX
    if systemctl is-active --quiet nginx; then
        sudo systemctl reload nginx
        echo -e "${GREEN}✓ NGINX reloaded${NC}"
    fi
else
    echo -e "${GREEN}✓ No NGINX configuration found${NC}"
fi

# Note about NGINX itself
echo -e "${YELLOW}Note: NGINX itself is NOT removed (may be used by other apps)${NC}"
echo -e "${YELLOW}To remove NGINX: sudo apt-get remove nginx${NC}"

# ====================================================================
# STEP 4: Clean Python Cache
# ====================================================================
echo ""
echo -e "${BLUE}STEP 4: Cleaning Python cache${NC}"

# Remove any __pycache__ in user directory
if [ -d "$HOME/.cache/pip" ]; then
    rm -rf "$HOME/.cache/pip"
    echo -e "${GREEN}✓ Pip cache cleared${NC}"
fi

# ====================================================================
# RESET COMPLETE
# ====================================================================
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}   Reset Completed!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}Summary:${NC}"
echo -e "  ✓ Services stopped and removed"
echo -e "  ✓ Application directory deleted"
echo -e "  ✓ NGINX configuration removed"
echo -e "  ✓ Python cache cleared"
echo ""
echo -e "${YELLOW}You can now run a fresh deployment with:${NC}"
echo -e "  ./deploy-nginx-wsl.sh"
echo ""
echo -e "${YELLOW}Don't forget to reset Windows side:${NC}"
echo -e "  From Windows (as Admin): reset-windows.bat"
echo ""
