@echo off
REM ====================================================================
REM     Windows Environment Reset - NGINX Deployment
REM ====================================================================
REM This script removes Windows port forwarding and firewall rules
REM Usage: Run as Administrator
REM ====================================================================

setlocal

echo.
echo ========================================================
echo    Windows Environment Reset - NGINX Deployment
echo ========================================================
echo.
echo WARNING: This will remove:
echo   - Port forwarding (8009 -^> WSL 8080)
echo   - Firewall rule (WSL Test Case API - NGINX)
echo.
pause

REM Check administrator privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    powershell -Command "Write-Host 'ERROR: This script requires administrator privileges!' -ForegroundColor Red"
    echo.
    echo Please right-click and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo.
echo [STEP 1] Removing port forwarding...
netsh interface portproxy delete v4tov4 listenport=8009 listenaddress=0.0.0.0
if %errorlevel% equ 0 (
    powershell -Command "Write-Host 'OK: Port forwarding removed' -ForegroundColor Green"
) else (
    powershell -Command "Write-Host 'Note: No port forwarding found or already removed' -ForegroundColor Yellow"
)

echo.
echo [STEP 2] Removing firewall rule...
powershell -Command "try { Remove-NetFirewallRule -DisplayName 'WSL Test Case API - NGINX' -ErrorAction Stop; Write-Host 'OK: Firewall rule removed' -ForegroundColor Green } catch { Write-Host 'Note: No firewall rule found or already removed' -ForegroundColor Yellow }"

echo.
echo [STEP 3] Verifying cleanup...
echo.
echo Current port forwarding rules:
netsh interface portproxy show v4tov4
echo.

echo ========================================================
echo    Windows Reset Completed!
echo ========================================================
echo.
echo You can now run a fresh deployment with DEPLOY.bat
echo.
pause
