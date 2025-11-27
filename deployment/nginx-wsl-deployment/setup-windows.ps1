#####################################################################
#          Windows Port Forwarding Setup - NGINX Version           #
#####################################################################
# This script configures Windows port forwarding to WSL NGINX
# Maps Windows :8009 -> WSL NGINX :8080
# Run as Administrator
#####################################################################

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "   Windows Port Forwarding Setup - NGINX Version" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# Check administrator privileges
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please right-click and select 'Run as Administrator'" -ForegroundColor Yellow
    Write-Host ""
    pause
    exit 1
}

Write-Host "OK: Running with administrator privileges" -ForegroundColor Green
Write-Host ""

# ====================================================================
# STEP 1: Get WSL IP Address
# ====================================================================
Write-Host "[STEP 1] Getting WSL IP address..." -ForegroundColor Yellow

try {
    $wslIp = wsl hostname -I
    $wslIp = $wslIp.Trim().Split(' ')[0]
    
    if ($wslIp -match '^\d{1,3}(\.\d{1,3}){3}$') {
        Write-Host "OK: WSL IP address detected: $wslIp" -ForegroundColor Green
    } else {
        throw "Invalid IP format"
    }
} catch {
    Write-Host "ERROR: Failed to get WSL IP address" -ForegroundColor Red
    Write-Host "Make sure WSL is running and accessible" -ForegroundColor Yellow
    pause
    exit 1
}

# ====================================================================
# STEP 2: Remove Existing Port Forward (if any)
# ====================================================================
Write-Host ""
Write-Host "[STEP 2] Removing existing port forwarding..." -ForegroundColor Yellow

try {
    $existingForward = netsh interface portproxy show v4tov4 | Select-String "8009"
    
    if ($existingForward) {
        Write-Host "Removing existing port forward on port 8009..." -ForegroundColor Yellow
        netsh interface portproxy delete v4tov4 listenport=8009 listenaddress=0.0.0.0
        Write-Host "OK: Existing forward removed" -ForegroundColor Green
    } else {
        Write-Host "OK: No existing forward found" -ForegroundColor Green
    }
} catch {
    Write-Host "WARNING: Could not check existing forwards" -ForegroundColor Yellow
}

# ====================================================================
# STEP 3: Create New Port Forward (8009 -> WSL NGINX 8080)
# ====================================================================
Write-Host ""
Write-Host "[STEP 3] Creating port forwarding (8009 -> WSL NGINX 8080)..." -ForegroundColor Yellow

try {
    netsh interface portproxy add v4tov4 listenport=8009 listenaddress=0.0.0.0 connectport=8080 connectaddress=$wslIp
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "OK: Port forwarding created" -ForegroundColor Green
        Write-Host "   Windows :8009 -> WSL NGINX :8080 ($wslIp)" -ForegroundColor Cyan
    } else {
        throw "netsh command failed"
    }
} catch {
    Write-Host "ERROR: Failed to create port forwarding" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    pause
    exit 1
}

# ====================================================================
# STEP 4: Configure Windows Firewall
# ====================================================================
Write-Host ""
Write-Host "[STEP 4] Configuring Windows Firewall..." -ForegroundColor Yellow

# Remove existing rule if it exists
try {
    $existingRule = Get-NetFirewallRule -DisplayName "WSL Test Case API - NGINX" -ErrorAction SilentlyContinue
    
    if ($existingRule) {
        Write-Host "Removing existing firewall rule..." -ForegroundColor Yellow
        Remove-NetFirewallRule -DisplayName "WSL Test Case API - NGINX"
        Write-Host "OK: Existing rule removed" -ForegroundColor Green
    }
} catch {
    Write-Host "OK: No existing firewall rule found" -ForegroundColor Green
}

# Create new firewall rule
try {
    New-NetFirewallRule -DisplayName "WSL Test Case API - NGINX" `
        -Direction Inbound `
        -LocalPort 8009 `
        -Protocol TCP `
        -Action Allow `
        -ErrorAction Stop | Out-Null
    
    Write-Host "OK: Firewall rule created" -ForegroundColor Green
    Write-Host "   Rule: WSL Test Case API - NGINX (Port 8009)" -ForegroundColor Cyan
} catch {
    Write-Host "ERROR: Failed to create firewall rule" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

# ====================================================================
# STEP 5: Verify Configuration
# ====================================================================
Write-Host ""
Write-Host "[STEP 5] Verifying configuration..." -ForegroundColor Yellow

# Show port forwarding
Write-Host ""
Write-Host "Current port forwarding rules:" -ForegroundColor Cyan
netsh interface portproxy show v4tov4

# Show firewall rule
Write-Host ""
Write-Host "Firewall rule status:" -ForegroundColor Cyan
Get-NetFirewallRule -DisplayName "WSL Test Case API - NGINX" | Format-Table -Property DisplayName, Enabled, Direction, Action

# ====================================================================
# STEP 6: Test Connectivity
# ====================================================================
Write-Host ""
Write-Host "[STEP 6] Testing connectivity..." -ForegroundColor Yellow

Start-Sleep -Seconds 2

# Test Windows access
Write-Host ""
Write-Host "Testing Windows access (localhost:8009)..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8009/health" -TimeoutSec 10 -UseBasicParsing
    Write-Host "OK: API accessible from Windows" -ForegroundColor Green
    Write-Host "Response: $($response.StatusCode) $($response.StatusDescription)" -ForegroundColor Cyan
} catch {
    Write-Host "WARNING: Windows access test failed" -ForegroundColor Yellow
    Write-Host "This is normal if WSL deployment isn't complete yet" -ForegroundColor Yellow
}

# Get Windows IP for network testing
Write-Host ""
Write-Host "Getting Windows IP address for network access..." -ForegroundColor Yellow
try {
    $windowsIp = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.PrefixOrigin -eq 'Dhcp' -or $_.PrefixOrigin -eq 'Manual' } | Select-Object -First 1).IPAddress
    Write-Host "Windows IP: $windowsIp" -ForegroundColor Cyan
    Write-Host "Network access URL: http://${windowsIp}:8009" -ForegroundColor Cyan
} catch {
    Write-Host "Could not determine Windows IP" -ForegroundColor Yellow
}

# ====================================================================
# SETUP COMPLETE
# ====================================================================
Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "   Windows Setup Completed!" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Configuration Summary:" -ForegroundColor Green
Write-Host "  Port Forward: 0.0.0.0:8009 -> $wslIp:8080" -ForegroundColor White
Write-Host "  Firewall Rule: Enabled for port 8009" -ForegroundColor White
Write-Host ""
Write-Host "Access URLs:" -ForegroundColor Green
Write-Host "  Local:   http://localhost:8009" -ForegroundColor White
if ($windowsIp) {
    Write-Host "  Network: http://${windowsIp}:8009" -ForegroundColor White
}
Write-Host ""
Write-Host "Architecture:" -ForegroundColor Green
Write-Host "  External -> Windows:8009 -> WSL NGINX:8080 -> Flask:5009" -ForegroundColor White
Write-Host ""
Write-Host "Management Commands:" -ForegroundColor Green
Write-Host "  View forwards:  netsh interface portproxy show v4tov4" -ForegroundColor White
Write-Host "  Remove forward: netsh interface portproxy delete v4tov4 listenport=8009" -ForegroundColor White
Write-Host ""
Write-Host "Ready to use!" -ForegroundColor Green
Write-Host ""
