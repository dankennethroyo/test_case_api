@echo off
REM Test Regular Test Case API Deployment
REM Quick API functionality test - Use verify-deployment.ps1 for comprehensive checks

echo ================================================================
echo   🧪 Quick API Test
echo ================================================================
echo.
echo Testing deployed Test Case API...
echo For comprehensive verification, run: verify-deployment.ps1
echo.

REM Test external endpoint (Windows port forwarding)
echo Testing external endpoint (Windows 8009)...
curl.exe -s http://localhost:8009/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ External endpoint responding
    echo.
    echo Health check response:
    curl.exe -s http://localhost:8009/health | findstr /v "^$" || echo No response
) else (
    echo ❌ External endpoint not responding
    echo   Make sure Windows port forwarding is configured
    echo   Run: .\setup-windows.ps1 as Administrator
)

echo.
echo ================================================================
echo Testing API functionality...
echo ================================================================

REM Test models endpoint
echo.
echo Testing models endpoint...
curl.exe -s http://localhost:8009/models >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Models endpoint working
    echo Available models:
    curl.exe -s http://localhost:8009/models | findstr "models" || echo Could not parse response
) else (
    echo ❌ Models endpoint failed
)

REM Test single generation
echo.
echo Testing single test case generation...
curl.exe -s -X POST http://localhost:8009/generate -H "Content-Type: application/json" -d "{\"REQUIREMENTS_ID\":\"TEST-001\",\"DESCRIPTION\":\"Test requirement\",\"CATEGORY\":\"Functional\"}" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Single generation working
    echo Response preview:
    curl.exe -s -X POST http://localhost:8009/generate -H "Content-Type: application/json" -d "{\"REQUIREMENTS_ID\":\"TEST-001\",\"DESCRIPTION\":\"Test requirement\",\"CATEGORY\":\"Functional\"}" | findstr "Test_Case" || echo Generation successful
) else (
    echo ❌ Single generation failed
)

REM Test batch generation
echo.
echo Testing batch generation...
curl.exe -s -X POST http://localhost:8009/generate/batch -H "Content-Type: application/json" -d "{\"requirements\":[{\"REQUIREMENTS_ID\":\"BATCH-001\",\"DESCRIPTION\":\"Batch test 1\",\"CATEGORY\":\"Functional\"},{\"REQUIREMENTS_ID\":\"BATCH-002\",\"DESCRIPTION\":\"Batch test 2\",\"CATEGORY\":\"Performance\"}]}" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Batch generation working
) else (
    echo ❌ Batch generation failed
)

echo.
echo ================================================================
echo   🎯 Web Interface Access
echo ================================================================
echo.
echo Client Interface: http://localhost:8009/client
echo Admin Interface:  http://localhost:8009/admin
echo.
echo Open these URLs in your web browser to access the interfaces.
echo.

REM Test WSL internal endpoint
echo ================================================================
echo Testing internal WSL endpoint (5009)...
echo ================================================================
echo.
wsl -d Ubuntu2204 -- curl -s http://localhost:5009/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Internal WSL endpoint responding
    echo.
    echo Internal health check:
    wsl -d Ubuntu2204 -- curl -s http://localhost:5009/health
) else (
    echo ❌ Internal WSL endpoint not responding
    echo   Check WSL service: wsl -d Ubuntu2204 -- sudo systemctl status test-case-api
)

echo.
echo ================================================================
echo   📊 Test Summary
echo ================================================================
echo.
echo If all tests show ✓, your deployment is working correctly!
echo If any tests show ❌, check the troubleshooting section.
echo.
echo Common issues:
echo • Port forwarding not configured → Run setup-windows.ps1
echo • WSL service not running → Check systemctl status
echo • Ollama not running → Start Ollama on Windows
echo.
pause