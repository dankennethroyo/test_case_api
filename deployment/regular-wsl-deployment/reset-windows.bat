@echo off
REM Test Case API - Windows Environment Cleanup
REM Removes port forwarding and firewall rules

echo ================================================================
echo   🧹 Test Case API - Windows Environment Cleanup
echo ================================================================
echo.
echo This script removes Windows-specific configurations:
echo   • Port forwarding rules (8009)
echo   • Windows Firewall rules
echo.
echo Run this BEFORE running the WSL reset script.
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ This script must be run as Administrator!
    echo Right-click the batch file and select "Run as Administrator"
    pause
    exit /b 1
)

echo ✓ Running as Administrator
echo.

REM Remove port forwarding rules
echo Removing port forwarding rules...
netsh interface portproxy delete v4tov4 listenport=8009 listenaddress=0.0.0.0 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Port forwarding rule removed (8009)
) else (
    echo ⚠ Port forwarding rule not found or already removed
)

REM Remove firewall rules
echo.
echo Removing firewall rules...
powershell -Command "Remove-NetFirewallRule -DisplayName 'WSL Test Case API - Regular' -ErrorAction SilentlyContinue" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Firewall rule removed
) else (
    echo ⚠ Firewall rule not found or already removed
)

REM Verify cleanup
echo.
echo Verifying cleanup...
echo.

echo Current port forwarding rules:
netsh interface portproxy show v4tov4
echo.

echo Current firewall rules (searching for Test Case API):
powershell -Command "Get-NetFirewallRule | Where-Object { $_.DisplayName -like '*Test Case API*' } | Select-Object DisplayName" 2>nul
if %errorlevel% neq 0 (
    echo No Test Case API firewall rules found
)

echo.
echo ================================================================
echo   ✅ Windows Cleanup Complete!
echo ================================================================
echo.
echo Next: Run the WSL reset script:
echo   wsl -d Ubuntu2204 /mnt/d/DK\$/_Projects/test_case_api/deployment/regular-wsl-deployment/reset-environment.sh
echo.
pause