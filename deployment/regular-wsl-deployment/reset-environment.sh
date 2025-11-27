#!/bin/bash

# Test Case API - Environment Reset Script
# Resets WSL environment to pre-deployment state

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo "================================================================"
echo "   🔄 Test Case API - Environment Reset"
echo "================================================================"
echo ""
echo "This script will reset your environment to pre-deployment state:"
echo "  • Stop and remove test-case-api systemd service"
echo "  • Remove application directory (/opt/test_case_api)"
echo "  • Reset NGINX configuration to default"
echo "  • Clear port forwarding rules"
echo "  • Remove firewall rules"
echo ""
echo "⚠️  WARNING: This will remove all deployment artifacts!"
echo ""

# Confirm with user
echo -n "Are you sure you want to reset the environment? (yes/no): "
read -r REPLY
echo
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "Reset cancelled."
    exit 0
fi

echo ""
echo "Starting environment reset..."

# =================================================================
# STEP 1: Stop and Remove Systemd Service
# =================================================================
echo ""
echo "STEP 1: Removing systemd service"

if systemctl is-active --quiet test-case-api 2>/dev/null; then
    echo "Stopping test-case-api service..."
    sudo systemctl stop test-case-api
    echo "✓ Service stopped"
else
    echo "Service not running"
fi

if systemctl is-enabled --quiet test-case-api 2>/dev/null; then
    echo "Disabling test-case-api service..."
    sudo systemctl disable test-case-api
    echo "✓ Service disabled"
fi

# Remove service file
if [ -f /etc/systemd/system/test-case-api.service ]; then
    echo "Removing service file..."
    sudo rm /etc/systemd/system/test-case-api.service
    sudo systemctl daemon-reload
    echo "✓ Service file removed"
else
    echo "Service file not found"
fi

# =================================================================
# STEP 2: Remove Application Directory
# =================================================================
echo ""
echo "STEP 2: Removing application directory"

if [ -d /opt/test_case_api ]; then
    echo "Removing /opt/test_case_api..."
    sudo rm -rf /opt/test_case_api
    echo "✓ Application directory removed"
else
    echo "Application directory not found"
fi

# =================================================================
# STEP 3: Reset NGINX Configuration
# =================================================================
echo ""
echo "STEP 3: Resetting NGINX configuration"

# Check if test-case-api nginx config exists
if [ -f /etc/nginx/conf.d/test-case-api.nginx.conf ] || [ -f /etc/nginx/sites-available/test-case-api ] || [ -f /etc/nginx/sites-enabled/test-case-api ]; then
    echo "Removing test-case-api nginx configurations..."

    # Remove from conf.d
    if [ -f /etc/nginx/conf.d/test-case-api.nginx.conf ]; then
        sudo rm /etc/nginx/conf.d/test-case-api.nginx.conf
        echo "✓ Removed /etc/nginx/conf.d/test-case-api.nginx.conf"
    fi

    # Remove from sites-available/sites-enabled
    if [ -f /etc/nginx/sites-available/test-case-api ]; then
        sudo rm /etc/nginx/sites-available/test-case-api
        echo "✓ Removed /etc/nginx/sites-available/test-case-api"
    fi

    if [ -L /etc/nginx/sites-enabled/test-case-api ]; then
        sudo rm /etc/nginx/sites-enabled/test-case-api
        echo "✓ Removed symlink /etc/nginx/sites-enabled/test-case-api"
    fi

    # Reload nginx
    if sudo systemctl is-active --quiet nginx; then
        echo "Reloading nginx..."
        sudo systemctl reload nginx
        echo "✓ Nginx reloaded"
    fi
else
    echo "No test-case-api nginx configurations found"
fi

# =================================================================
# STEP 4: Clear Port Forwarding Rules (Windows)
# =================================================================
echo ""
echo "STEP 4: Clearing Windows port forwarding"

# Note: This requires running from Windows PowerShell
echo "Note: Port forwarding rules need to be cleared from Windows"
echo "Run this command in Windows PowerShell (as Administrator):"
echo "  netsh interface portproxy delete v4tov4 listenport=8009 listenaddress=0.0.0.0"
echo ""

# =================================================================
# STEP 5: Remove Firewall Rules (Windows)
# =================================================================
echo ""
echo "STEP 5: Removing Windows firewall rules"

echo "Note: Firewall rules need to be removed from Windows"
echo "Run this command in Windows PowerShell (as Administrator):"
echo "  Remove-NetFirewallRule -DisplayName \"WSL Test Case API - Regular\" -ErrorAction SilentlyContinue"
echo ""

# =================================================================
# STEP 6: Clean Up Python Virtual Environments
# =================================================================
echo ""
echo "STEP 6: Cleaning up Python environments"

# Remove any orphaned virtual environments
if [ -d ~/test_case_api_env ] || [ -d ~/venv_test_case ] || [ -d ~/.virtualenvs/test_case_api ]; then
    echo "Removing orphaned virtual environments..."
    rm -rf ~/test_case_api_env ~/venv_test_case ~/.virtualenvs/test_case_api 2>/dev/null || true
    echo "✓ Orphaned environments cleaned"
else
    echo "No orphaned environments found"
fi

# =================================================================
# STEP 7: Verify Reset
# =================================================================
echo ""
echo "STEP 7: Verifying reset"

echo "Checking for remaining artifacts..."

# Check if service still exists
if systemctl list-units --type=service | grep -q test-case-api; then
    echo "⚠️  Service still exists"
else
    echo "✓ Service removed"
fi

# Check if directory still exists
if [ -d /opt/test_case_api ]; then
    echo "⚠️  Application directory still exists"
else
    echo "✓ Application directory removed"
fi

# Check nginx configs
if [ -f /etc/nginx/conf.d/test-case-api.nginx.conf ] || [ -f /etc/nginx/sites-available/test-case-api ] || [ -f /etc/nginx/sites-enabled/test-case-api ]; then
    echo "⚠️  NGINX configurations still exist"
else
    echo "✓ NGINX configurations removed"
fi

# =================================================================
# RESET COMPLETE
# =================================================================
echo ""
echo "================================================================"
echo "   ✅ ENVIRONMENT RESET COMPLETE!"
echo "================================================================"
echo ""
echo "Your environment has been reset to pre-deployment state."
echo ""
echo "Next steps:"
echo "  1. Run Windows cleanup commands (port forwarding & firewall)"
echo "  2. Run deployment: ./DEPLOY.bat"
echo ""
echo "Windows cleanup commands:"
echo "  netsh interface portproxy delete v4tov4 listenport=8009 listenaddress=0.0.0.0"
echo "  Remove-NetFirewallRule -DisplayName \"WSL Test Case API - Regular\" -ErrorAction SilentlyContinue"
echo ""