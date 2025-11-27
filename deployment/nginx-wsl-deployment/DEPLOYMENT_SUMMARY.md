# NGINX WSL Deployment - Technical Summary

## Overview
This deployment package provides a production-ready Test Case API with NGINX reverse proxy, Flask isolation, and Windows port forwarding integration.

## Deployment Information

### Target System
- **Platform**: WSL2 Ubuntu 22.04
- **Installation Path**: `/opt/test_case_api`
- **Python Environment**: Python 3.x with venv

### Network Configuration
```
Component      | Binding           | Port | Accessibility
---------------|-------------------|------|------------------
Flask App      | 127.0.0.1         | 5009 | Localhost only
NGINX Proxy    | 0.0.0.0           | 8080 | All interfaces
Windows Port   | 0.0.0.0           | 8009 | External access
Ollama Service | <Windows-Host-IP> | 11434| WSL access
```

### Architecture Flow
```
External Request
    ↓
Windows Firewall (Port 8009)
    ↓
Windows Port Proxy (8009 → WSL:8080)
    ↓
WSL NGINX (0.0.0.0:8080)
    ↓
Flask Backend (127.0.0.1:5009)
    ↓
Ollama AI (Windows:11434)
```

## Security Features

### 1. Flask Isolation
- Binds exclusively to 127.0.0.1 (localhost)
- Not directly accessible from network
- Only Ubuntu OS can access directly

### 2. NGINX Layer
- Single point of entry (0.0.0.0:8080)
- Security headers enabled:
  - X-Frame-Options: SAMEORIGIN
  - X-Content-Type-Options: nosniff
  - X-XSS-Protection: 1; mode=block
  - Referrer-Policy: no-referrer-when-downgrade

### 3. Systemd Hardening
- PrivateTmp=yes
- NoNewPrivileges=true
- Service restart on failure

### 4. Request Handling
- Client max body size: 10MB
- Proxy read timeout: 300s
- Connection timeout: 75s
- Buffering disabled for streaming

## File Locations

### Application Files
```
/opt/test_case_api/
├── app.py                    # Main Flask application
├── .env                      # Environment configuration
├── venv/                     # Python virtual environment
├── logs/                     # Application logs
├── output/                   # Generated test cases
├── converted/                # Converted results
├── admin_gui/                # Admin web interface
├── public_gui/               # Client web interface
├── instructions/             # AI system instructions
└── samples/                  # Sample requirement files
```

### System Configuration
```
/etc/nginx/
├── sites-available/test-case-api    # NGINX configuration
└── sites-enabled/test-case-api      # Symlink to active config

/etc/systemd/system/
└── test-case-api.service            # Flask systemd service

/var/log/nginx/
├── test-case-api-access.log         # NGINX access logs
└── test-case-api-error.log          # NGINX error logs
```

## Service Management

### Flask Service
```bash
# Status
sudo systemctl status test-case-api

# Control
sudo systemctl start test-case-api
sudo systemctl stop test-case-api
sudo systemctl restart test-case-api

# Logs
sudo journalctl -u test-case-api -f
sudo journalctl -u test-case-api -n 50
```

### NGINX Service
```bash
# Status
sudo systemctl status nginx

# Control
sudo systemctl start nginx
sudo systemctl stop nginx
sudo systemctl restart nginx
sudo systemctl reload nginx

# Configuration test
sudo nginx -t

# Logs
sudo tail -f /var/log/nginx/test-case-api-access.log
sudo tail -f /var/log/nginx/test-case-api-error.log
```

## Environment Variables

### Flask Configuration (.env)
```env
# Flask Server (Localhost only)
HOST=127.0.0.1
PORT=5009
FLASK_DEBUG=False
DEBUG_MODE=False

# Ollama Configuration
OLLAMA_BASE_URL=http://<auto-detected-ip>:11434
OLLAMA_MODEL=phi4:14b
OLLAMA_TIMEOUT=180

# Application Settings
MAX_FILE_SIZE_MB=10
LOG_LEVEL=INFO
TARGET_FILE=samples/batch_requirements.json
TARGET_FILE_NAME=batch_requirements.json
USE_STREAMING=True
```

## Port Forwarding Details

### Windows Configuration
```powershell
# Port proxy rule
netsh interface portproxy add v4tov4 `
    listenport=8009 `
    listenaddress=0.0.0.0 `
    connectport=8080 `
    connectaddress=<WSL-IP>

# Firewall rule
New-NetFirewallRule `
    -DisplayName "WSL Test Case API - NGINX" `
    -Direction Inbound `
    -LocalPort 8009 `
    -Protocol TCP `
    -Action Allow
```

### View Configuration
```powershell
# Show port forwarding
netsh interface portproxy show v4tov4

# Show firewall rules
Get-NetFirewallRule -DisplayName "WSL Test Case API - NGINX"
```

## API Endpoints

### Health & Status
- `GET /health` - Service health check
- `GET /models` - List available Ollama models

### Instructions Management
- `GET /instructions` - Get system instructions
- `POST /instructions` - Update system instructions

### Test Case Generation
- `POST /generate` - Generate single test case
- `POST /generate/batch` - Generate batch test cases
- `POST /generate/stream` - Generate with SSE streaming

### Web Interfaces
- `GET /` - Redirects to /client
- `GET /client` - Client web interface
- `GET /admin` - Admin web interface

## Performance Tuning

### NGINX Optimizations
- Keep-alive connections enabled (32 connections)
- Buffering disabled for streaming endpoints
- Request buffering off for large payloads
- HTTP/1.1 for upstream connections

### Timeout Configuration
```
proxy_read_timeout: 300s (AI generation)
proxy_connect_timeout: 75s
proxy_send_timeout: 300s
SSE timeout: 600s (streaming)
```

## Monitoring & Logs

### Application Logs
```bash
# Flask application logs
sudo journalctl -u test-case-api -f

# Recent logs
sudo journalctl -u test-case-api -n 100

# Logs since boot
sudo journalctl -u test-case-api -b
```

### NGINX Logs
```bash
# Access logs (HTTP requests)
sudo tail -f /var/log/nginx/test-case-api-access.log

# Error logs
sudo tail -f /var/log/nginx/test-case-api-error.log

# All NGINX logs
sudo tail -f /var/log/nginx/*.log
```

### System Resources
```bash
# Process status
ps aux | grep python
ps aux | grep nginx

# Port listening
sudo ss -tlnp | grep 5009  # Flask
sudo ss -tlnp | grep 8080  # NGINX

# Resource usage
systemctl status test-case-api
systemctl status nginx
```

## Backup & Recovery

### Backup Current Installation
```bash
# Automatic backup during deployment
sudo cp -r /opt/test_case_api /opt/test_case_api.backup.$(date +%Y%m%d_%H%M%S)
```

### Restore from Backup
```bash
# Stop services
sudo systemctl stop test-case-api

# Restore files
sudo rm -rf /opt/test_case_api
sudo cp -r /opt/test_case_api.backup.YYYYMMDD_HHMMSS /opt/test_case_api

# Restart services
sudo systemctl start test-case-api
```

## Troubleshooting

### Flask Not Starting
```bash
# Check logs
sudo journalctl -u test-case-api -n 50

# Check configuration
cat /opt/test_case_api/.env

# Test Python environment
cd /opt/test_case_api
source venv/bin/activate
python -c "import flask; print('OK')"
```

### NGINX Issues
```bash
# Test configuration
sudo nginx -t

# Check error logs
sudo tail -n 50 /var/log/nginx/test-case-api-error.log

# Verify config file
cat /etc/nginx/sites-available/test-case-api
```

### Port Forwarding Issues
```powershell
# From Windows (as Admin)
# Get WSL IP
wsl hostname -I

# Recreate port forward
netsh interface portproxy delete v4tov4 listenport=8009 listenaddress=0.0.0.0
netsh interface portproxy add v4tov4 listenport=8009 listenaddress=0.0.0.0 connectport=8080 connectaddress=<WSL-IP>
```

### Connectivity Tests
```bash
# From WSL
curl http://127.0.0.1:5009/health  # Flask direct
curl http://localhost:8080/health  # NGINX proxy

# From Windows
curl http://localhost:8009/health  # Via port forward
```

## Maintenance Tasks

### Update Application Code
```bash
cd /opt/test_case_api
sudo nano app.py
sudo systemctl restart test-case-api
```

### Update Dependencies
```bash
cd /opt/test_case_api
source venv/bin/activate
pip install --upgrade <package>
sudo systemctl restart test-case-api
```

### Update NGINX Configuration
```bash
sudo nano /etc/nginx/sites-available/test-case-api
sudo nginx -t
sudo systemctl reload nginx
```

### Rotate Logs
```bash
# NGINX logs are rotated automatically by logrotate
# Manual rotation if needed:
sudo nginx -s reopen
```

## Version Information

- **Package Version**: 1.0
- **Deployment Type**: Production (NGINX + Flask)
- **Last Updated**: 2025-11-27
- **Python Version**: 3.x
- **NGINX Version**: Latest from apt
- **Flask Version**: As per requirements.txt

## Additional Notes

### SSL/TLS (Future Enhancement)
To enable HTTPS:
1. Obtain SSL certificate (Let's Encrypt recommended)
2. Update NGINX configuration:
   ```nginx
   listen 443 ssl;
   ssl_certificate /path/to/cert.pem;
   ssl_certificate_key /path/to/key.pem;
   ```
3. Redirect HTTP to HTTPS
4. Update Windows port forwarding for port 443

### Rate Limiting (Future Enhancement)
Add to NGINX configuration:
```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
limit_req zone=api_limit burst=20;
```

### Authentication (Future Enhancement)
Add HTTP Basic Auth or integrate OAuth2/JWT at NGINX level

---

**For detailed usage instructions, see README.md**
