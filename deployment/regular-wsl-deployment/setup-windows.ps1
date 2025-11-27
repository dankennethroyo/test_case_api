# Regular Test Case API - Windows Port Forwarding Setup
# Configures port forwarding from Windows 8009 to WSL 5009

param(
    [switch]$Force
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   🪟 Windows Port Forwarding Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This script configures Windows port forwarding:" -ForegroundColor Green
Write-Host "  • Windows port 8009 → WSL port 5009" -ForegroundColor Yellow
Write-Host "  • Windows Firewall rule s for HTTP access" -ForegroundColor Yellow
Write-Host ""

# Check if running as administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "❌ This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✓ Running as Administrator" -ForegroundColor Green
Write-Host ""

# Get WSL IP address
Write-Host "Getting WSL IP address..." -ForegroundColor Yellow
$wslIp = wsl -d Ubuntu2204 hostname -I 2>$null
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($wslIp)) {
    Write-Host "❌ Failed to get WSL IP address" -ForegroundColor Red
    Write-Host "Make sure WSL Ubuntu2204 is running" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}
$wslIp = $wslIp.Trim().Split()[0]  # Take first IP if multiple
Write-Host "✓ WSL IP: $wslIp" -ForegroundColor Green

# Check existing port forwarding
Write-Host ""
Write-Host "Checking existing port forwarding..." -ForegroundColor Yellow
$existingRules = netsh interface portproxy show v4tov4 2>$null
$port8009Exists = $existingRules | Select-String "8009"

if ($port8009Exists -and -not $Force) {
    Write-Host "⚠ Port 8009 forwarding already exists:" -ForegroundColor Yellow
    $existingRules | Select-String "8009"
    Write-Host ""
    $overwrite = Read-Host "Overwrite existing rule? (y/n)"
    if ($overwrite -notmatch "^[Yy]$") {
        Write-Host "Port forwarding setup cancelled." -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 0
    }
}

# Remove existing rule if it exists
if ($port8009Exists) {
    Write-Host "Removing existing port 8009 rule..." -ForegroundColor Yellow
    netsh interface portproxy delete v4tov4 listenport=8009 listenaddress=0.0.0.0 >$null 2>&1
    Write-Host "✓ Existing rule removed" -ForegroundColor Green
}

# Add new port forwarding rule
Write-Host ""
Write-Host "Adding port forwarding rule..." -ForegroundColor Yellow
Write-Host "  Windows 8009 → WSL $wslIp`:5009" -ForegroundColor Cyan

$result = netsh interface portproxy add v4tov4 listenport=8009 listenaddress=0.0.0.0 connectport=5009 connectaddress=$wslIp 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Port forwarding rule added successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to add port forwarding rule" -ForegroundColor Red
    Write-Host "Error: $result" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Configure Windows Firewall
Write-Host ""
Write-Host "Configuring Windows Firewall..." -ForegroundColor Yellow

# Check if firewall rule already exists
$firewallRule = Get-NetFirewallRule -DisplayName "WSL Test Case API - Regular" -ErrorAction SilentlyContinue

if ($firewallRule -and -not $Force) {
    Write-Host "⚠ Firewall rule 'WSL Test Case API - Regular' already exists" -ForegroundColor Yellow
    $overwrite = Read-Host "Overwrite existing firewall rule? (y/n)"
    if ($overwrite -notmatch "^[Yy]$") {
        Write-Host "Firewall setup cancelled." -ForegroundColor Yellow
        Read-Host "Press Enter to continue"
    } else {
        Remove-NetFirewallRule -DisplayName "WSL Test Case API - Regular" -ErrorAction SilentlyContinue
        Write-Host "✓ Existing firewall rule removed" -ForegroundColor Green
    }
} elseif ($firewallRule) {
    Remove-NetFirewallRule -DisplayName "WSL Test Case API - Regular" -ErrorAction SilentlyContinue
    Write-Host "✓ Existing firewall rule removed" -ForegroundColor Green
}

# Add firewall rule
$firewallResult = New-NetFirewallRule -DisplayName "WSL Test Case API - Regular" -Direction Inbound -Protocol TCP -LocalPort 8009 -Action Allow -ErrorAction SilentlyContinue
if ($firewallResult) {
    Write-Host "✓ Firewall rule added successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to add firewall rule" -ForegroundColor Red
    Write-Host "You may need to manually allow port 8009 in Windows Firewall" -ForegroundColor Yellow
}

# Verify configuration
Write-Host ""
Write-Host "Verifying configuration..." -ForegroundColor Yellow

# Check port forwarding
$verifyProxy = netsh interface portproxy show v4tov4 | Select-String "8009"
if ($verifyProxy) {
    Write-Host "✓ Port forwarding verified:" -ForegroundColor Green
    $verifyProxy | ForEach-Object { Write-Host "  $_" -ForegroundColor Cyan }
} else {
    Write-Host "❌ Port forwarding verification failed" -ForegroundColor Red
}

# Check firewall rule
$verifyFirewall = Get-NetFirewallRule -DisplayName "WSL Test Case API - Regular" -ErrorAction SilentlyContinue
if ($verifyFirewall) {
    Write-Host "✓ Firewall rule verified" -ForegroundColor Green
} else {
    Write-Host "❌ Firewall rule verification failed" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   ✅ Windows Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Port forwarding configuration:" -ForegroundColor Green
Write-Host "  • Windows port 8009 → WSL $wslIp`:5009" -ForegroundColor Cyan
Write-Host ""
Write-Host "Test the setup:" -ForegroundColor Green
Write-Host "  curl.exe http://localhost:8009/health" -ForegroundColor Yellow
Write-Host ""
Write-Host "Web interfaces:" -ForegroundColor Green
Write-Host "  • Client: http://localhost:8009/client" -ForegroundColor Yellow
Write-Host "  • Admin:  http://localhost:8009/admin" -ForegroundColor Yellow
Write-Host ""

# Test connectivity
Write-Host "Testing connectivity..." -ForegroundColor Yellow
$testResponse = curl.exe -s --connect-timeout 5 http://localhost:8009/health 2>$null
if ($LASTEXITCODE -eq 0 -and $testResponse) {
    Write-Host "✓ Connectivity test successful" -ForegroundColor Green
    Write-Host "  Response: $testResponse" -ForegroundColor Cyan
} else {
    Write-Host "⚠ Connectivity test failed" -ForegroundColor Yellow
    Write-Host "  This is normal if the WSL service is still starting" -ForegroundColor Yellow
    Write-Host "  Wait a few seconds and try: curl.exe http://localhost:8009/health" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Setup complete! Your regular Test Case API should be accessible." -ForegroundColor Green
Write-Host ""

Read-Host "Press Enter to exit"