@echo off
REM Regular Test Case API - Dynamic Complete Windows Deployment Launcher
REM This script launches the complete regular WSL deployment with dynamic path resolution

echo ================================================================
echo   🚀 Regular Test Case API - Dynamic Deployment Launcher
echo ================================================================
echo.
echo This will deploy a regular (non-secure) Test Case Generation API
echo with the following features:
echo.
echo   ✓ Regular Flask application (no SSL/security features)
echo   ✓ Web interfaces (client and admin)
echo   ✓ AI-powered test case generation via Ollama
echo   ✓ Systemd service with automatic startup
echo   ✓ Windows integration through port forwarding
echo.
echo Target: WSL2 Ubuntu at /opt/test_case_api
echo Ports: WSL 5009 → Windows 8009
echo.

REM Check prerequisites
echo Checking prerequisites...

REM Check WSL
wsl --list --verbose >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ WSL not found or not running
    echo Please install WSL2 with Ubuntu2204
    pause
    exit /b 1
) else (
    echo ✓ WSL is available
)

REM Check Ollama
curl.exe -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Ollama not running on Windows
    echo Please install Ollama from https://ollama.ai
    echo Then run: ollama pull phi4:14b
    pause
    exit /b 1
) else (
    echo ✓ Ollama is running
)

echo.
echo ================================================================
echo Ready to deploy! This will take 2-3 minutes.
echo ================================================================
echo.
pause

REM Phase 1: WSL Deployment
echo.
echo 🚀 Phase 1: Deploying to WSL...
echo ================================================================

REM Get the script's directory and convert to WSL path
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"  REM Remove trailing backslash

REM Convert Windows path to WSL path (assuming D: drive)
set "WSL_PATH=%SCRIPT_DIR%"
set "WSL_PATH=%WSL_PATH:D:\=/mnt/d/%"
set "WSL_PATH=%WSL_PATH:\=/%"

wsl -d Ubuntu2204 -- bash -c "cd '%WSL_PATH%' && chmod +x deploy-regular-wsl.sh && ./deploy-regular-wsl.sh"

if %errorlevel% neq 0 (
    echo.
    echo ❌ WSL deployment failed!
    echo Check the error messages above.
    pause
    exit /b 1
)


echo.
echo ✓ WSL deployment completed successfully!
echo.

REM Phase 2: Windows Configuration
echo 🪟 Phase 2: Configuring Windows (requires Administrator)...
echo ================================================================
echo.
echo The next step requires Administrator privileges to configure:
echo   • Port forwarding (8009→WSL:5009)
echo   • Windows Firewall rules
echo.
echo.
echo Please run the following command as Administrator:
echo   powershell -ExecutionPolicy Bypass -File "setup-windows.ps1"
echo.
echo Or right-click setup-windows.ps1 and select "Run with PowerShell as Administrator"
echo.
pause

echo.
echo Running Windows setup...
powershell -ExecutionPolicy Bypass -Command "Start-Process powershell -ArgumentList '-ExecutionPolicy Bypass -File \"%~dp0setup-windows.ps1\"' -Verb RunAs -Wait"

if %errorlevel% neq 0 (
    echo.
    echo ⚠ Windows configuration may have failed or been cancelled.
    echo Please run setup-windows.ps1 manually as Administrator if needed.
    echo.
) else (
    echo.
    echo ✓ Windows configuration completed!
)

REM Phase 3: Final Testing
echo.
echo 🧪 Phase 3: Testing deployment...
echo ================================================================

REM Wait a moment for services to stabilize
timeout /t 3 >nul

REM Test connectivity
curl.exe -s http://localhost:8009/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ External connectivity working
) else (
    echo ⚠ External test failed (may be normal if still starting)
)

echo.
echo ================================================================
echo 🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!
echo ================================================================
echo.
echo Your regular Test Case API is ready at:
echo   • External: http://localhost:8009
echo   • Internal (WSL): http://localhost:5009
echo.
echo Web Interfaces:
echo   • Client Interface: http://localhost:8009/client
echo   • Admin Interface: http://localhost:8009/admin
echo.
echo Test the deployment:
echo   curl.exe http://localhost:8009/health
echo.
echo Service management (in WSL):
echo   sudo systemctl status test-case-api
echo   sudo journalctl -u test-case-api -f
echo.
pause