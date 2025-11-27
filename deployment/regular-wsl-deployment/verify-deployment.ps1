# Deployment Verification Script
# Tests all aspects of the regular WSL deployment

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "   Regular WSL Deployment Verification" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

$allPassed = $true

# Test 1: WSL Service
Write-Host "Test 1: WSL Service Status" -ForegroundColor Yellow
$wslStatus = wsl -d Ubuntu2204 -- bash -c "systemctl is-active test-case-api" 2>$null
if ($wslStatus -eq "active") {
    Write-Host "  [OK] Service is running" -ForegroundColor Green
} else {
    Write-Host "  [FAIL] Service is not running (Status: $wslStatus)" -ForegroundColor Red
    $allPassed = $false
}

# Test 2: WSL Internal Access
Write-Host ""
Write-Host "Test 2: WSL Internal Access (localhost:5009)" -ForegroundColor Yellow
$wslHealth = wsl -d Ubuntu2204 -- curl -s http://localhost:5009/health 2>$null
if ($wslHealth) {
    Write-Host "  [OK] WSL internal access working" -ForegroundColor Green
    Write-Host "    Response: $wslHealth" -ForegroundColor Cyan
} else {
    Write-Host "  [FAIL] WSL internal access failed" -ForegroundColor Red
    $allPassed = $false
}

# Test 3: Port Forwarding Configuration
Write-Host ""
Write-Host "Test 3: Port Forwarding Configuration" -ForegroundColor Yellow
$portForward = netsh interface portproxy show v4tov4 | Select-String "8009"
if ($portForward) {
    Write-Host "  [OK] Port forwarding configured" -ForegroundColor Green
    Write-Host "    $portForward" -ForegroundColor Cyan
} else {
    Write-Host "  [FAIL] Port forwarding not configured" -ForegroundColor Red
    Write-Host "    Run setup-windows.ps1 as Administrator" -ForegroundColor Yellow
    $allPassed = $false
}

# Test 4: Firewall Rule
Write-Host ""
Write-Host "Test 4: Windows Firewall Rule" -ForegroundColor Yellow
$firewallRule = Get-NetFirewallRule -DisplayName "WSL Test Case API - Regular" -ErrorAction SilentlyContinue
if ($firewallRule) {
    Write-Host "  [OK] Firewall rule exists" -ForegroundColor Green
} else {
    Write-Host "  [FAIL] Firewall rule not found" -ForegroundColor Red
    Write-Host "    Run setup-windows.ps1 as Administrator" -ForegroundColor Yellow
    $allPassed = $false
}

# Test 5: External Access
Write-Host ""
Write-Host "Test 5: External Access (localhost:8009)" -ForegroundColor Yellow
$externalHealth = curl.exe -s --connect-timeout 5 http://localhost:8009/health 2>$null
if ($LASTEXITCODE -eq 0 -and $externalHealth) {
    Write-Host "  [OK] External access working" -ForegroundColor Green
    Write-Host "    Response: $externalHealth" -ForegroundColor Cyan
} else {
    Write-Host "  [FAIL] External access failed" -ForegroundColor Red
    Write-Host "    Ensure port forwarding is configured" -ForegroundColor Yellow
    $allPassed = $false
}

# Test 6: Ollama Connectivity
Write-Host ""
Write-Host "Test 6: Ollama Connectivity" -ForegroundColor Yellow
if ($wslHealth -and ($wslHealth -like '*ollama*connected*')) {
    Write-Host "  [OK] Ollama is connected" -ForegroundColor Green
} elseif ($wslHealth -and ($wslHealth -like '*ollama*disconnected*')) {
    Write-Host "  [FAIL] Ollama is disconnected" -ForegroundColor Red
    Write-Host "    Check Windows host IP in .env file" -ForegroundColor Yellow
    $allPassed = $false
} else {
    Write-Host "  [WARN] Could not verify Ollama status" -ForegroundColor Yellow
}

# Summary
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
if ($allPassed) {
    Write-Host "   ALL TESTS PASSED!" -ForegroundColor Green
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Your deployment is working correctly!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Access URLs:" -ForegroundColor Yellow
    Write-Host "  - Landing Page: http://localhost:8009 (redirects to client)" -ForegroundColor Cyan
    Write-Host "  - Client GUI: http://localhost:8009/client" -ForegroundColor Cyan
    Write-Host "  - Admin GUI: http://localhost:8009/admin" -ForegroundColor Cyan
    Write-Host "  - Health Check: http://localhost:8009/health" -ForegroundColor Cyan
    Write-Host ""
    
    # Get Windows IP for network access
    $windowsIp = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias "Ethernet*","Wi-Fi*" | Where-Object {$_.IPAddress -notlike "169.254.*"} | Select-Object -First 1).IPAddress
    if ($windowsIp) {
        Write-Host "Network Access (from other PCs):" -ForegroundColor Yellow
        Write-Host "  - http://${windowsIp}:8009 (landing page)" -ForegroundColor Cyan
        Write-Host "  - http://${windowsIp}:8009/client" -ForegroundColor Cyan
        Write-Host "  - http://${windowsIp}:8009/admin" -ForegroundColor Cyan
    }
} else {
    Write-Host "   SOME TESTS FAILED" -ForegroundColor Yellow
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Please review the failed tests above and take corrective action." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Common fixes:" -ForegroundColor Yellow
    Write-Host "  - Run setup-windows.ps1 as Administrator for port forwarding" -ForegroundColor Cyan
    Write-Host "  - Check service: wsl -d Ubuntu2204 sudo systemctl status test-case-api" -ForegroundColor Cyan
    Write-Host "  - View logs: wsl -d Ubuntu2204 sudo journalctl -u test-case-api -n 20" -ForegroundColor Cyan
}

Write-Host ""
Read-Host "Press Enter to exit"
