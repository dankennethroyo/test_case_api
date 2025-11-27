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
REM STEP 0: Administrator Check
REM ====================================================================
echo.
echo [STEP 0] Checking administrator privileges...
net session >nul 2>&1
if %errorlevel% neq 0 (
    powershell -Command "Write-Host 'ERROR: This script requires administrator privileges!' -ForegroundColor Red"
    echo.
    echo Please right-click DEPLOY.bat and select "Run as administrator"
    echo.
    pause
    exit /b 1
)
powershell -Command "Write-Host 'OK: Running with administrator privileges' -ForegroundColor Green"

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
    pause
    exit /b 1
)
powershell -Command "Write-Host 'OK: WSL is installed' -ForegroundColor Green"

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

REM Get the current directory
set "SCRIPT_DIR=%~dp0"
set "WSL_PATH=/mnt/%SCRIPT_DIR::=%"
set "WSL_PATH=%WSL_PATH:\=/%"
set "WSL_PATH=%WSL_PATH: =\ %"

powershell -Command "Write-Host 'Deploying to WSL...' -ForegroundColor Cyan"
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
powershell -Command "Write-Host 'Setting up port forwarding (8009 -> WSL NGINX 8080)...' -ForegroundColor Yellow"

powershell -ExecutionPolicy Bypass -File "%SCRIPT_DIR%setup-windows.ps1"

if %errorlevel% neq 0 (
    powershell -Command "Write-Host 'WARNING: Windows setup had issues (check output above)' -ForegroundColor Yellow"
    echo.
    echo Deployment may still work internally
    echo.
)

REM ====================================================================
REM STEP 4: Verify Complete Installation
REM ====================================================================
echo.
echo [STEP 4] Verifying installation...
powershell -Command "Write-Host 'Running verification tests...' -ForegroundColor Cyan"

timeout /t 3 /nobreak >nul

REM Test Windows access
powershell -Command "Write-Host 'Testing Windows access (localhost:8009)...' -ForegroundColor Yellow"
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8009/health' -TimeoutSec 10 -UseBasicParsing; Write-Host 'OK: API accessible from Windows' -ForegroundColor Green } catch { Write-Host 'WARNING: Windows access test failed' -ForegroundColor Yellow }"

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
echo Access URLs:
echo   WSL Internal: http://localhost:8080
echo   Windows:      http://localhost:8009
echo   Network:      http://^<your-windows-ip^>:8009
echo.
echo Architecture:
echo   Flask:  127.0.0.1:5009 (localhost only, secure)
echo   NGINX:  0.0.0.0:8080   (reverse proxy)
echo   Windows Port Forward: 8009 -^> WSL 8080
echo.
echo Management Commands:
echo   View Flask logs:  wsl sudo journalctl -u test-case-api -f
echo   View NGINX logs:  wsl sudo tail -f /var/log/nginx/test-case-api-error.log
echo   Restart Flask:    wsl sudo systemctl restart test-case-api
echo   Restart NGINX:    wsl sudo systemctl restart nginx
echo.
echo Test the API:
echo   curl http://localhost:8009/health
echo   curl http://localhost:8009/models
echo.
echo Open in browser:
echo   http://localhost:8009/client
echo   http://localhost:8009/admin
echo.
powershell -Command "Write-Host 'Happy testing!' -ForegroundColor Cyan"
echo.
pause
