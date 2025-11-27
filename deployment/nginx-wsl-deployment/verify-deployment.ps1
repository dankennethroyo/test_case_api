#####################################################################
#          Deployment Verification - NGINX Version                 #
#####################################################################
# This script verifies the NGINX-based deployment
# Tests all components and connectivity
# Run from Windows PowerShell (as Administrator)
#####################################################################

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "   NGINX Deployment Verification" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

$testsPassed = 0
$testsFailed = 0

# ====================================================================
# TEST 1: WSL Service Status
# ====================================================================
Write-Host "[TEST 1] Checking Flask service status..." -ForegroundColor Yellow
try {
    $serviceStatus = wsl bash -c "sudo systemctl is-active test-case-api"
    if ($serviceStatus -eq "active") {
        Write-Host "[OK] Flask service is active" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host "[FAIL] Flask service is not active" -ForegroundColor Red
        $testsFailed++
    }
} catch {
    Write-Host "[FAIL] Could not check Flask service" -ForegroundColor Red
    $testsFailed++
}

# ====================================================================
# TEST 2: NGINX Service Status
# ====================================================================
Write-Host ""
Write-Host "[TEST 2] Checking NGINX service status..." -ForegroundColor Yellow
try {
    $nginxStatus = wsl bash -c "sudo systemctl is-active nginx"
    if ($nginxStatus -eq "active") {
        Write-Host "[OK] NGINX service is active" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host "[FAIL] NGINX service is not active" -ForegroundColor Red
        $testsFailed++
    }
} catch {
    Write-Host "[FAIL] Could not check NGINX service" -ForegroundColor Red
    $testsFailed++
}

# ====================================================================
# TEST 3: Flask Internal Access (WSL localhost:5009)
# ====================================================================
Write-Host ""
Write-Host "[TEST 3] Testing Flask internal access (127.0.0.1:5009)..." -ForegroundColor Yellow
try {
    $flaskResponse = wsl bash -c "curl -s http://127.0.0.1:5009/health"
    if ($flaskResponse -match '"status":"healthy"') {
        Write-Host "[OK] Flask responding on localhost" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host "[FAIL] Flask not responding correctly" -ForegroundColor Red
        $testsFailed++
    }
} catch {
    Write-Host "[FAIL] Cannot reach Flask internally" -ForegroundColor Red
    $testsFailed++
}

# ====================================================================
# TEST 4: NGINX Proxy (WSL localhost:8080)
# ====================================================================
Write-Host ""
Write-Host "[TEST 4] Testing NGINX proxy (localhost:8080)..." -ForegroundColor Yellow
try {
    $nginxResponse = wsl bash -c "curl -s http://localhost:8080/health"
    if ($nginxResponse -match '"status":"healthy"') {
        Write-Host "[OK] NGINX proxy working" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host "[FAIL] NGINX proxy not working" -ForegroundColor Red
        $testsFailed++
    }
} catch {
    Write-Host "[FAIL] Cannot reach NGINX" -ForegroundColor Red
    $testsFailed++
}

# ====================================================================
# TEST 5: Port Forwarding Configuration
# ====================================================================
Write-Host ""
Write-Host "[TEST 5] Checking Windows port forwarding..." -ForegroundColor Yellow
try {
    $portForward = netsh interface portproxy show v4tov4 | Select-String "8009"
    if ($portForward) {
        Write-Host "[OK] Port forwarding configured (8009 -> WSL 8080)" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host "[FAIL] Port forwarding not configured" -ForegroundColor Red
        $testsFailed++
    }
} catch {
    Write-Host "[FAIL] Could not check port forwarding" -ForegroundColor Red
    $testsFailed++
}

# ====================================================================
# TEST 6: Windows Firewall Rule
# ====================================================================
Write-Host ""
Write-Host "[TEST 6] Checking Windows firewall rule..." -ForegroundColor Yellow
try {
    $firewallRule = Get-NetFirewallRule -DisplayName "WSL Test Case API - NGINX" -ErrorAction Stop
    if ($firewallRule.Enabled -eq "True") {
        Write-Host "[OK] Firewall rule exists and enabled" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host "[FAIL] Firewall rule disabled" -ForegroundColor Red
        $testsFailed++
    }
} catch {
    Write-Host "[FAIL] Firewall rule not found" -ForegroundColor Red
    $testsFailed++
}

# ====================================================================
# TEST 7: Windows Local Access (localhost:8009)
# ====================================================================
Write-Host ""
Write-Host "[TEST 7] Testing Windows local access (localhost:8009)..." -ForegroundColor Yellow
try {
    $windowsResponse = Invoke-WebRequest -Uri "http://localhost:8009/health" -TimeoutSec 10 -UseBasicParsing
    if ($windowsResponse.StatusCode -eq 200) {
        Write-Host "[OK] API accessible from Windows" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host "[FAIL] Unexpected response code: $($windowsResponse.StatusCode)" -ForegroundColor Red
        $testsFailed++
    }
} catch {
    Write-Host "[FAIL] Cannot access API from Windows" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    $testsFailed++
}

# ====================================================================
# TEST 8: Ollama Connectivity
# ====================================================================
Write-Host ""
Write-Host "[TEST 8] Testing Ollama connectivity from WSL..." -ForegroundColor Yellow
try {
    $winHostIp = wsl bash -c "ip route show | grep default | awk '{print `$3}'"
    $ollamaTest = wsl bash -c "curl -s http://$winHostIp:11434/api/tags"
    if ($ollamaTest -match '"models"') {
        Write-Host "[OK] Ollama accessible from WSL" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host "[FAIL] Ollama not accessible" -ForegroundColor Red
        $testsFailed++
    }
} catch {
    Write-Host "[FAIL] Cannot test Ollama connectivity" -ForegroundColor Red
    $testsFailed++
}

# ====================================================================
# TEST 9: Security Check - Flask External Isolation
# ====================================================================
Write-Host ""
Write-Host "[TEST 9] Security check - Flask isolation..." -ForegroundColor Yellow
try {
    $wslIp = wsl hostname -I
    $wslIp = $wslIp.Trim().Split(' ')[0]
    
    # Try to access Flask directly from Windows (should fail)
    try {
        $directAccess = Invoke-WebRequest -Uri "http://${wslIp}:5009/health" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
        Write-Host "[FAIL] Flask is accessible externally (security issue!)" -ForegroundColor Red
        $testsFailed++
    } catch {
        Write-Host "[OK] Flask properly isolated to localhost" -ForegroundColor Green
        $testsPassed++
    }
} catch {
    Write-Host "[WARN] Could not perform security check" -ForegroundColor Yellow
}

# ====================================================================
# SUMMARY
# ====================================================================
Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "   Verification Summary" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

$totalTests = $testsPassed + $testsFailed
Write-Host "Total Tests: $totalTests" -ForegroundColor White
Write-Host "Passed:      $testsPassed" -ForegroundColor Green
Write-Host "Failed:      $testsFailed" -ForegroundColor $(if ($testsFailed -gt 0) { "Red" } else { "Green" })
Write-Host ""

if ($testsFailed -eq 0) {
    Write-Host "All tests passed! Deployment is healthy." -ForegroundColor Green
    Write-Host ""
    Write-Host "Access URLs:" -ForegroundColor Cyan
    Write-Host "  Local:  http://localhost:8009" -ForegroundColor White
    Write-Host "  Client: http://localhost:8009/client" -ForegroundColor White
    Write-Host "  Admin:  http://localhost:8009/admin" -ForegroundColor White
    Write-Host ""
    
    # Get Windows IP for network access
    try {
        $windowsIp = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.PrefixOrigin -eq 'Dhcp' -or $_.PrefixOrigin -eq 'Manual' } | Select-Object -First 1).IPAddress
        Write-Host "  Network: http://${windowsIp}:8009" -ForegroundColor White
    } catch {}
} else {
    Write-Host "Some tests failed. Please check the errors above." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "  Flask logs:  wsl sudo journalctl -u test-case-api -n 20" -ForegroundColor White
    Write-Host "  NGINX logs:  wsl sudo tail -f /var/log/nginx/test-case-api-error.log" -ForegroundColor White
    Write-Host "  Service status: wsl sudo systemctl status test-case-api nginx" -ForegroundColor White
}

Write-Host ""
