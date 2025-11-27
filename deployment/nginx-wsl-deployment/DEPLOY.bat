@echo off
REM ====================================================================
REM     NGINX WSL DEPLOYMENT - TURNKEY WINDOWS LAUNCHER
REM ====================================================================
REM This batch file orchestrates the complete NGINX-based deployment:
REM 1. Checks prerequisites (WSL, Ollama)
REM 2. Runs WSL deployment script (deploy-nginx-wsl.sh)
REM 3. Configures Windows port forwarding (setup-windows.ps1)
REM 4. Verifies complete installation
REM
REM Usage: Just double-click DEPLOY.bat or run from cmd
REM ====================================================================

setlocal enabledelayedexpansion

REM Color codes (using PowerShell for colored output)
set "PS_GREEN=[System.ConsoleColor]::Green"
set "PS_YELLOW=[System.ConsoleColor]::Yellow"
set "PS_RED=[System.ConsoleColor]::Red"
set "PS_CYAN=[System.ConsoleColor]::Cyan"

echo.
echo ========================================================
echo   NGINX WSL DEPLOYMENT - TURNKEY INSTALLER
echo ========================================================
echo.
echo This will deploy the Test Case API with NGINX to WSL
echo.
echo Architecture:
echo   - Flask: 127.0.0.1:5009 (localhost only)
echo   - NGINX: 0.0.0.0:8080 (reverse proxy)
echo   - Windows Port: 8009 -^> WSL NGINX 8080
echo.
pause

REM ====================================================================
REM STEP 0: Administrator Check (Optional)
REM ====================================================================
echo.
echo [STEP 0] Checking administrator privileges...
net session >nul 2>&1
if %errorlevel% neq 0 (
    powershell -Command "Write-Host 'WARNING: Not running as administrator' -ForegroundColor Yellow"
    echo.
    echo This script can run without admin privileges, but you will need to:
    echo - Manually configure Windows port forwarding (8009 -> WSL)
    echo - Manually create Windows Firewall rules for port 8009
    echo.
    echo Continue anyway? (Y/N)
    set /p choice=
    if /i not "!choice!"=="y" (
        echo Deployment cancelled.
        pause
        exit /b 1
    )
    set "IS_ADMIN=false"
    powershell -Command "Write-Host 'OK: Proceeding without administrator privileges' -ForegroundColor Cyan"
) else (
    set "IS_ADMIN=true"
    powershell -Command "Write-Host 'OK: Running with administrator privileges' -ForegroundColor Green"
)

REM ====================================================================
REM STEP 1: Check Prerequisites
REM ====================================================================
echo.
echo [STEP 1] Checking prerequisites...

REM Check WSL
powershell -Command "Write-Host 'Checking WSL installation...' -ForegroundColor Yellow"
wsl --list --verbose >nul 2>&1
if %errorlevel% neq 0 (
    powershell -Command "Write-Host 'ERROR: WSL is not installed or not running!' -ForegroundColor Red"
    echo.
    echo Please install WSL2 with Ubuntu:
    echo   wsl --install -d Ubuntu-22.04
    echo.
    echo Or check if WSL is running:
    echo   wsl --list --verbose
    echo.
    pause
    exit /b 1
)
powershell -Command "Write-Host 'OK: WSL is installed and running' -ForegroundColor Green"

REM Check Ollama
powershell -Command "Write-Host 'Checking Ollama service...' -ForegroundColor Yellow"
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:11434/api/tags' -TimeoutSec 5 -UseBasicParsing; Write-Host 'OK: Ollama is running' -ForegroundColor Green; exit 0 } catch { Write-Host 'ERROR: Ollama is not running!' -ForegroundColor Red; exit 1 }"
if %errorlevel% neq 0 (
    echo.
    echo Please start Ollama:
    echo   1. Open Ollama application
    echo   2. Verify it's running in system tray
    echo.
    pause
    exit /b 1
)

powershell -Command "Write-Host 'All prerequisites satisfied!' -ForegroundColor Green"

REM ====================================================================
REM STEP 2: Run WSL Deployment
REM ====================================================================
echo.
echo [STEP 2] Running WSL deployment script...
powershell -Command "Write-Host 'This will clean existing installation and deploy fresh...' -ForegroundColor Yellow"

REM Get the current directory and convert to WSL path
set "SCRIPT_DIR=%~dp0"
REM Remove trailing backslash
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
REM Convert backslashes to forward slashes for wslpath
set "SCRIPT_DIR_UNIX=%SCRIPT_DIR:\=/%"

REM Convert Windows path to WSL path using wslpath
for /f "delims=" %%i in ('wsl wslpath "%SCRIPT_DIR_UNIX%"') do set "WSL_PATH=%%i"

powershell -Command "Write-Host 'Deploying to WSL...' -ForegroundColor Cyan"
powershell -Command "Write-Host 'Windows Path: %SCRIPT_DIR%' -ForegroundColor Gray"
powershell -Command "Write-Host 'WSL Path: %WSL_PATH%' -ForegroundColor Gray"
wsl bash -c "cd '%WSL_PATH%' && chmod +x deploy-nginx-wsl.sh && ./deploy-nginx-wsl.sh"

if %errorlevel% neq 0 (
    powershell -Command "Write-Host 'ERROR: WSL deployment failed!' -ForegroundColor Red"
    echo.
    echo Check the error messages above
    echo.
    pause
    exit /b 1
)

powershell -Command "Write-Host 'WSL deployment completed successfully!' -ForegroundColor Green"

REM ====================================================================
REM STEP 3: Configure Windows Port Forwarding
REM ====================================================================
echo.
echo [STEP 3] Configuring Windows port forwarding...
if "%IS_ADMIN%"=="true" (
    powershell -Command "Write-Host 'Setting up port forwarding (8009 -> WSL NGINX 8080)...' -ForegroundColor Yellow"
    REM Get WSL IP for port forwarding
    for /f "tokens=1" %%i in ('wsl hostname -I') do set "WSL_IP=%%i"
    powershell -Command "Write-Host 'WSL IP detected: %WSL_IP%' -ForegroundColor Cyan"
    
    REM Remove existing port forward
    netsh interface portproxy delete v4tov4 listenport=8009 listenaddress=0.0.0.0 >nul 2>&1
    
    REM Create new port forward
    netsh interface portproxy add v4tov4 listenport=8009 listenaddress=0.0.0.0 connectport=8080 connectaddress=%WSL_IP%
    if %errorlevel% equ 0 (
        powershell -Command "Write-Host 'OK: Port forwarding created (8009 -> %WSL_IP%:8080)' -ForegroundColor Green"
    ) else (
        powershell -Command "Write-Host 'ERROR: Failed to create port forwarding' -ForegroundColor Red"
    )
    
    REM Create firewall rule
    netsh advfirewall firewall delete rule name="WSL Test Case API - NGINX" >nul 2>&1
    netsh advfirewall firewall add rule name="WSL Test Case API - NGINX" dir=in action=allow protocol=TCP localport=8009
    if %errorlevel% equ 0 (
        powershell -Command "Write-Host 'OK: Firewall rule created' -ForegroundColor Green"
    ) else (
        powershell -Command "Write-Host 'WARNING: Firewall rule creation failed' -ForegroundColor Yellow"
    )

) else (
    powershell -Command "Write-Host 'Skipping Windows setup (no admin privileges)' -ForegroundColor Yellow"
    echo.
    echo To complete the setup, run these commands as administrator:
    echo.
    echo 1. Configure port forwarding:
    echo    netsh interface portproxy add v4tov4 listenport=8009 listenaddress=0.0.0.0 connectport=8080 connectaddress=^<WSL-IP^>
    echo.
    echo 2. Create firewall rule:
    echo    New-NetFirewallRule -DisplayName "WSL Test Case API - NGINX" -Direction Inbound -LocalPort 8009 -Protocol TCP -Action Allow
    echo.
    echo 3. Or run the setup script as admin:
    echo    powershell -ExecutionPolicy Bypass -File "setup-windows.ps1"
    echo.
    echo Your WSL IP can be found with: wsl hostname -I
    echo.
)

REM ====================================================================
REM STEP 4: Verify Complete Installation
REM ====================================================================
echo.
echo [STEP 4] Verifying installation...
powershell -Command "Write-Host 'Running verification tests...' -ForegroundColor Cyan"

timeout /t 3 /nobreak >nul

REM Test WSL internal access
powershell -Command "Write-Host 'Testing WSL internal access (localhost:8080)...' -ForegroundColor Yellow"
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8080/health' -TimeoutSec 10 -UseBasicParsing; Write-Host 'OK: API accessible from WSL' -ForegroundColor Green } catch { Write-Host 'WARNING: WSL internal access test failed' -ForegroundColor Yellow }"

REM Test Windows access (only if admin setup was done)
if "%IS_ADMIN%"=="true" (
    powershell -Command "Write-Host 'Testing Windows access (localhost:8009)...' -ForegroundColor Yellow"
    powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8009/health' -TimeoutSec 10 -UseBasicParsing; Write-Host 'OK: API accessible from Windows' -ForegroundColor Green } catch { Write-Host 'WARNING: Windows access test failed - check port forwarding' -ForegroundColor Yellow }"
) else (
    powershell -Command "Write-Host 'Skipping Windows access test (port forwarding not configured)' -ForegroundColor Yellow"
    echo.
    echo To test Windows access after manual setup:
    echo   curl http://localhost:8009/health
    echo.
)

REM ====================================================================
REM DEPLOYMENT COMPLETE
REM ====================================================================
echo.
echo ========================================================
echo   DEPLOYMENT COMPLETED!
echo ========================================================
echo.
powershell -Command "Write-Host 'Your Test Case API is now running with NGINX!' -ForegroundColor Green"
echo.
if "%IS_ADMIN%"=="true" (
    echo Access URLs:
    echo   WSL Internal: http://localhost:8080
    echo   Windows:      http://localhost:8009
    echo   Network:      http://^<your-windows-ip^>:8009
    echo.
    echo Architecture:
    echo   Flask:  127.0.0.1:5009 (localhost only, secure)
    echo   NGINX:  0.0.0.0:8080   (reverse proxy)
    echo   Windows Port Forward: 8009 -^> WSL 8080
) else (
    echo Access URLs:
    echo   WSL Internal: http://localhost:8080
    echo   Windows:      NOT CONFIGURED (needs manual setup)
    echo   Network:      NOT CONFIGURED (needs manual setup)
    echo.
    echo Next Steps (run as administrator):
    echo   1. Configure port forwarding and firewall
    echo   2. Test with: curl http://localhost:8009/health
    echo.
    echo Architecture:
    echo   Flask:  127.0.0.1:5009 (localhost only, secure)
    echo   NGINX:  0.0.0.0:8080   (reverse proxy)
    echo   Windows Port Forward: MANUAL SETUP REQUIRED
)
echo.
echo Management Commands:
echo   View Flask logs:  wsl sudo journalctl -u test-case-api -f
echo   View NGINX logs:  wsl sudo tail -f /var/log/nginx/test-case-api-error.log
echo   Restart Flask:    wsl sudo systemctl restart test-case-api
echo   Restart NGINX:    wsl sudo systemctl restart nginx
echo.
echo Test the API:
echo   curl http://localhost:8080/health  (WSL internal)
if "%IS_ADMIN%"=="true" (
    echo   curl http://localhost:8009/health  (Windows)
)
echo   curl http://localhost:8009/models
echo.
echo Open in browser:
echo   http://localhost:8080/client  (WSL internal)
if "%IS_ADMIN%"=="true" (
    echo   http://localhost:8009/client  (Windows)
    echo   http://localhost:8009/admin   (Windows)
)
echo.
powershell -Command "Write-Host 'Happy testing!' -ForegroundColor Cyan"
echo.
pause
