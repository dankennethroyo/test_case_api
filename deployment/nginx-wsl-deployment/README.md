# NGINX Test Case API - Production Deployment Package

This folder contains everything needed for a **production-ready NGINX-based WSL deployment** of the Test Case Generation API with enhanced security, reverse proxy, and scalability features.

## 🏗️ Architecture

```
External Network (Clients)
          ↓
Windows Host :8009 (Port Forward)
          ↓
WSL2 NGINX :8080 (Reverse Proxy - 0.0.0.0)
          ↓
Flask API :5009 (Localhost Only - 127.0.0.1)
          ↓
Ollama :11434 (Windows Host)
```

### 🔒 Security Model

- **Flask Isolation**: Binds to `127.0.0.1:5009` (localhost only - Ubuntu OS access only)
- **NGINX Gateway**: Single public entry point on `0.0.0.0:8080`
- **Windows Bridge**: Port forwarding from `:8009` → WSL NGINX `:8080`
- **External Access**: Only through NGINX (Flask is completely isolated)

---

## 🚀 One-Command Deployment

### **Just Double-Click `DEPLOY.bat`!** ✨

This turnkey Windows launcher will:
- ✅ Check prerequisites (WSL, Ollama)
- ✅ **Clean existing deployment automatically**
- ✅ Install and configure NGINX
- ✅ Deploy Flask application (localhost binding)
- ✅ Set up systemd services
- ✅ Configure Windows port forwarding
- ✅ Set up firewall rules
- ✅ Verify complete installation

**Location:** `nginx-wsl-deployment\DEPLOY.bat`

**Requirements:**
- Run as **Administrator**
- WSL2 with Ubuntu 22.04
- Ollama running on Windows

---

## 🔄 Environment Reset

### If you need to start fresh:

**Step 1: Windows Cleanup (Run as Administrator)**
```cmd
reset-windows.bat
```

**Step 2: WSL Cleanup**
```bash
./reset-environment.sh
```

This will:
- ✅ Stop and remove all services
- ✅ Delete application directory
- ✅ Remove NGINX configuration
- ✅ Remove port forwarding
- ✅ Remove firewall rules
- ✅ Clean Python cache

---

## 📦 What's Included

### Core Deployment Scripts
- `DEPLOY.bat` - **Turnkey Windows launcher** (run as Admin)
- `deploy-nginx-wsl.sh` - **WSL deployment script** with auto-cleanup
- `setup-windows.ps1` - **Windows port forwarding** setup
- `requirements.txt` - **Python dependencies**

### NGINX Configuration
- `nginx/test-case-api.nginx.conf` - **Production NGINX config**
  - Reverse proxy to Flask
  - Security headers
  - SSE streaming support
  - Request buffering
  - Timeout handling

### System Services
- `systemd/` - **Service file templates**
  - Flask backend service
  - NGINX integration

### Complete Web Application
- `app/` - **Self-contained application**
  - `app.py` - Flask application
  - `admin_gui/` - Admin interface
  - `public_gui/` - Client interface
  - `instructions/` - AI system instructions
  - `samples/` - Sample data

### Utilities
- `reset-environment.sh` - WSL environment reset
- `reset-windows.bat` - Windows cleanup
- `test-api.bat` - Quick API test

---

## 🔧 Configuration

### Flask Configuration (.env)

Auto-generated during deployment at `/opt/test_case_api/.env`:

```env
# Flask binds to localhost ONLY (127.0.0.1:5009)
HOST=127.0.0.1
PORT=5009

# Ollama Configuration
OLLAMA_BASE_URL=http://<auto-detected-windows-ip>:11434
OLLAMA_MODEL=phi4:14b
OLLAMA_TIMEOUT=180

# Security
FLASK_DEBUG=False
DEBUG_MODE=False

# File Upload
MAX_FILE_SIZE_MB=10
```

### NGINX Configuration

Located at `/etc/nginx/sites-available/test-case-api`:

**Key Features:**
- Listens on `0.0.0.0:8080` (all interfaces)
- Proxies to `127.0.0.1:5009` (Flask)
- Security headers (X-Frame-Options, X-XSS-Protection, etc.)
- 300s timeout for AI generation
- SSE streaming support
- Request buffering disabled

### Windows Port Forwarding

```
listenaddress: 0.0.0.0:8009
connectaddress: <WSL-IP>:8080
```

---

## 📊 Comparison: NGINX vs Regular Deployment

| Feature | Regular Deployment | **NGINX Deployment** |
|---------|-------------------|----------------------|
| **Flask Binding** | `0.0.0.0:5009` | `127.0.0.1:5009` ✅ |
| **Public Interface** | Flask directly | **NGINX :8080** ✅ |
| **Windows Port** | 8009 → Flask 5009 | **8009 → NGINX 8080** ✅ |
| **Flask Isolation** | Exposed | **Localhost only** ✅ |
| **Security Headers** | None | **Yes** ✅ |
| **Request Buffering** | Limited | **NGINX handles** ✅ |
| **SSL/TLS Ready** | No | **Yes** ✅ |
| **Load Balancing** | No | **Capable** ✅ |
| **Static File Serving** | Flask | **NGINX optimized** ✅ |
| **DDoS Protection** | Basic | **NGINX layer** ✅ |

---

## 🌐 Access URLs

After deployment:

| Access Point | URL | Description |
|--------------|-----|-------------|
| **WSL Internal** | `http://localhost:8080` | NGINX (WSL only) |
| **Flask Direct** | `http://127.0.0.1:5009` | Flask (WSL localhost only) ✅ |
| **Windows Local** | `http://localhost:8009` | Via port forward |
| **Network Access** | `http://<Windows-IP>:8009` | From other computers |
| **Client GUI** | `http://localhost:8009/client` | Web interface |
| **Admin GUI** | `http://localhost:8009/admin` | Admin interface |

---

## 🛠️ Management Commands

### Service Management

```bash
# Flask Service
sudo systemctl status test-case-api
sudo systemctl restart test-case-api
sudo systemctl stop test-case-api
sudo journalctl -u test-case-api -f

# NGINX Service
sudo systemctl status nginx
sudo systemctl restart nginx
sudo nginx -t  # Test configuration
```

### Logs

```bash
# Flask logs
sudo journalctl -u test-case-api -f
sudo journalctl -u test-case-api -n 50

# NGINX logs
sudo tail -f /var/log/nginx/test-case-api-error.log
sudo tail -f /var/log/nginx/test-case-api-access.log
```

### Configuration Updates

```bash
# Edit Flask environment
sudo nano /opt/test_case_api/.env
sudo systemctl restart test-case-api

# Edit NGINX config
sudo nano /etc/nginx/sites-available/test-case-api
sudo nginx -t  # Test first!
sudo systemctl reload nginx
```

### Windows Commands

```powershell
# View port forwarding
netsh interface portproxy show v4tov4

# Remove port forwarding
netsh interface portproxy delete v4tov4 listenport=8009

# View firewall rules
Get-NetFirewallRule -DisplayName "WSL Test Case API - NGINX"
```

---

## 🧪 Testing & Verification

### Quick Test

```bash
# From Windows
test-api.bat

# Or manually
curl http://localhost:8009/health
curl http://localhost:8009/models
```

### Security Verification

```bash
# From WSL - Flask should respond
curl http://127.0.0.1:5009/health  # ✅ Should work

# From WSL - NGINX should respond
curl http://localhost:8080/health  # ✅ Should work

# From external - Flask should NOT respond
curl http://<WSL-IP>:5009/health   # ❌ Should fail (security!)

# From external - NGINX should respond
curl http://<WSL-IP>:8080/health   # ✅ Should work
```

### Full Test Suite

```bash
# Check service status
sudo systemctl status test-case-api
sudo systemctl status nginx

# Check process listening
sudo ss -tlnp | grep 5009  # Flask on 127.0.0.1:5009
sudo ss -tlnp | grep 8080  # NGINX on 0.0.0.0:8080

# Test API endpoints
curl -X POST http://localhost:8009/generate \
  -H "Content-Type: application/json" \
  -d '{"REQUIREMENTS_ID":"TEST-001","DESCRIPTION":"Test requirement","CATEGORY":"Functional"}'
```

---

## 🔐 Security Features

### 1. **Flask Isolation**
- Binds to `127.0.0.1` only
- Not accessible from network
- Ubuntu OS access only

### 2. **NGINX Gateway**
- Single entry point
- Security headers enabled
- Request validation

### 3. **Security Headers**
```
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Referrer-Policy: no-referrer-when-downgrade
```

### 4. **Systemd Hardening**
```
PrivateTmp=yes
NoNewPrivileges=true
```

### 5. **Future Enhancements**
- ✅ Ready for SSL/TLS certificates
- ✅ Can add HTTP Basic Auth
- ✅ Can implement rate limiting
- ✅ Can add IP whitelisting
- ✅ Can enable request logging

---

## 📚 Directory Structure

```
/opt/test_case_api/                # Application root
├── app.py                         # Flask application
├── .env                           # Configuration
├── venv/                          # Python virtual environment
├── logs/                          # Application logs
├── output/                        # Generated test cases
├── converted/                     # Converted results
├── admin_gui/                     # Admin interface
├── public_gui/                    # Client interface
├── instructions/                  # AI instructions
└── samples/                       # Sample data

/etc/nginx/
├── sites-available/
│   └── test-case-api             # NGINX config
└── sites-enabled/
    └── test-case-api             # Symlink

/etc/systemd/system/
└── test-case-api.service         # Flask service

/var/log/nginx/
├── test-case-api-access.log      # Access logs
└── test-case-api-error.log       # Error logs
```

---

## 🚨 Troubleshooting

### Flask Not Starting

```bash
# Check logs
sudo journalctl -u test-case-api -n 50

# Common issues:
# 1. Port already in use
sudo ss -tlnp | grep 5009

# 2. Python dependencies
cd /opt/test_case_api
source venv/bin/activate
pip install -r requirements.txt

# 3. Ollama not accessible
curl http://<Windows-IP>:11434/api/tags
```

### NGINX Issues

```bash
# Test configuration
sudo nginx -t

# Check logs
sudo tail -f /var/log/nginx/test-case-api-error.log

# Restart NGINX
sudo systemctl restart nginx
```

### Port Forwarding Not Working

```powershell
# From Windows (as Admin)
# Check existing forwards
netsh interface portproxy show v4tov4

# Get WSL IP
wsl hostname -I

# Recreate forward
netsh interface portproxy delete v4tov4 listenport=8009 listenaddress=0.0.0.0
netsh interface portproxy add v4tov4 listenport=8009 listenaddress=0.0.0.0 connectport=8080 connectaddress=<WSL-IP>
```

### Can't Access from Network

```powershell
# Check firewall
Get-NetFirewallRule -DisplayName "WSL Test Case API - NGINX"

# Test Windows access first
curl http://localhost:8009/health

# Get Windows IP
ipconfig
```

---

## 🔄 Updating the Deployment

### Update Application Code

```bash
cd /opt/test_case_api
sudo nano app.py
sudo systemctl restart test-case-api
```

### Update NGINX Config

```bash
sudo nano /etc/nginx/sites-available/test-case-api
sudo nginx -t
sudo systemctl reload nginx
```

### Update Python Dependencies

```bash
cd /opt/test_case_api
source venv/bin/activate
pip install --upgrade <package>
sudo systemctl restart test-case-api
```

---

## 📖 Additional Resources

- **Client Tools**: `../client_tools/` - Standalone client package
- **Regular Deployment**: `../regular-wsl-deployment/` - Simple non-NGINX version
- **API Documentation**: `/opt/test_case_api/docs/`

---

## 🆘 Support

For issues or questions:

1. **Check Logs**:
   - Flask: `sudo journalctl -u test-case-api -f`
   - NGINX: `sudo tail -f /var/log/nginx/test-case-api-error.log`

2. **Verify Services**:
   ```bash
   sudo systemctl status test-case-api
   sudo systemctl status nginx
   ```

3. **Test Connectivity**:
   ```bash
   curl http://127.0.0.1:5009/health  # Flask
   curl http://localhost:8080/health  # NGINX
   curl http://localhost:8009/health  # Windows
   ```

4. **Reset and Redeploy**:
   ```bash
   ./reset-environment.sh  # WSL
   reset-windows.bat       # Windows (as Admin)
   DEPLOY.bat              # Fresh deployment
   ```

---

**Version**: 1.0  
**Deployment Type**: Production-Ready with NGINX  
**Last Updated**: 2025-11-27

**Happy Testing!** 🎉
