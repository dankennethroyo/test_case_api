# Test Case API - WSL Deployment Guide (Docker-Free)

## 📋 Overview

This guide shows how to deploy the Test Case API on Windows Subsystem for Linux (WSL) **without Docker**, avoiding all Docker Desktop licensing concerns for Emerson Electric employees.

### ✅ Benefits of WSL Deployment
- **No Docker Desktop license required** - completely free for enterprise use
- **Native Linux environment** on Windows
- **Better performance** than Docker Desktop on Windows
- **Direct access** to Linux tools and packages
- **No licensing concerns** - all open source components

### 🎯 What You'll Deploy
- Flask API server (Python)
- Ollama AI engine
- Nginx reverse proxy (optional)
- SSL/TLS support
- Production-ready configuration

---

## 📦 Prerequisites

### 1. Enable WSL2 on Windows

Open PowerShell as Administrator and run:

```powershell
# Enable WSL
wsl --install

# Or if already installed, update to WSL2
wsl --set-default-version 2

# Install Ubuntu (recommended)
wsl --install -d Ubuntu-22.04
```

**Reboot your computer after installation.**

### 2. Verify WSL Installation

```powershell
wsl --list --verbose
```

You should see Ubuntu running with version 2.

### 3. Enter WSL

```powershell
wsl
```

You're now in a Linux terminal!

---

## 🚀 Installation Steps

### Step 1: Update System Packages

```bash
# Update package lists
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv curl wget nginx git
```

### Step 2: Ollama Setup (Choose One Option)

You have two options for Ollama:

#### **Option A: Use Existing Windows Ollama (RECOMMENDED)**

If Ollama is already installed and running on Windows, **skip installation** and just configure the connection:

```bash
# No installation needed! 
# Your Windows Ollama is accessible from WSL at: http://localhost:11434
# or use the Windows host IP (see below)

# Test connection to Windows Ollama
curl http://localhost:11434/api/tags
```

### How to call Ollama from WSL in NAT mode
```bash

Find Windows host IP from WSL:
ShellWIN_HOST=$(ip route show | awk '/default/ {print $3}')echo $WIN_HOSTShow more lines
Example: 172.26.96.1


Curl using that IP:
Shellcurl "http://$WIN_HOST:11434/api/tags"Show more lines


Important: Ollama must listen on 0.0.0.0:11434 (not just 127.0.0.1):

On Windows, set environment variable:
OLLAMA_HOST=0.0.0.0:11434


Restart Ollama service/app.
Ensure Windows Firewall allows TCP 11434 on Private network.
```

**Benefit:** No duplication, uses your existing Windows installation and models.

#### **Option B: Install Ollama in WSL (Optional)**

Only if you want a separate Ollama instance in WSL:

```bash
# Download and install Ollama in WSL
curl -fsSL https://ollama.com/install.sh | sh

# Verify installation
ollama --version

# Start Ollama service
ollama serve &

# Pull your desired model
ollama pull llama3:latest
```

**Note:** This creates a separate instance with its own models (uses more disk space).

---

**Which should you choose?**
- **Use Option A** if Ollama is already working on Windows (most common)
- **Use Option B** only if you need WSL-specific configuration or isolation

### Step 3: Set Up Application Directory

```bash
# Create application directory
mkdir -p /opt/test-case-api
cd /opt/test-case-api

# Copy ONLY the required application files from Windows
# (WSL can access Windows files via /mnt/c/)
cp /mnt/c/Projects/test_case_api/test_case_api/app.py .
cp -r /mnt/c/Projects/test_case_api/test_case_api/admin_gui .
cp -r /mnt/c/Projects/test_case_api/test_case_api/public_gui .
cp -r /mnt/c/Projects/test_case_api/test_case_api/instructions .
cp -r /mnt/c/Projects/test_case_api/test_case_api/samples . # Optional: for testing

# OR Method 2: Clone from Git if you have a repository
# git clone <your-repo-url> .
# Then keep only: app.py, admin_gui/, public_gui/, instructions/, samples/

# Verify copied files
ls -la
# Should see: app.py, admin_gui/, public_gui/, instructions/, samples/

# Create output directories (for generated files)
mkdir -p output converted
```

### Step 4: Create Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install flask flask-cors requests python-dotenv gunicorn
```

### Step 5: Configure Environment Variables

```bash
# Create production environment file
cat > .env << 'EOF'
# Test Case Generator API Configuration

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3:latest
OLLAMA_TIMEOUT=180

# Flask Configuration
HOST=0.0.0.0
PORT=5000
FLASK_DEBUG=False
DEBUG_MODE=False

# Environment Type (development or production)
ENVIRONMENT=production

# File Upload Configuration
MAX_FILE_SIZE_MB=10

# Logging
LOG_LEVEL=INFO
EOF

# Verify .env file
cat .env
```

**Configuration Notes:**

**For Production Deployment:**
- `ENVIRONMENT=production` - Blocks admin GUI, only exposes client interface
- `FLASK_DEBUG=False` - Disables Flask debug mode for security
- `DEBUG_MODE=False` - Disables application debug output
- `OLLAMA_BASE_URL=http://localhost:11434` - Connects to Windows Ollama (WSL2 shares network)

**For Development with Admin GUI:**
```bash
# Edit .env and change:
ENVIRONMENT=development
FLASK_DEBUG=True
DEBUG_MODE=True
```

**Model Selection:**
- Check available models on Windows: `ollama list` (from PowerShell)
- Update `OLLAMA_MODEL` to match your Windows Ollama model
- Common options: `llama3:latest`, `llama4:latest`, `mistral:latest`, `mistral:instruct`

### Step 6: Test the Application

```bash
# Activate virtual environment if not already active
source venv/bin/activate

# Verify Ollama connectivity first (critical!)
curl http://localhost:11434/api/tags
# Should return JSON with available models

# Run the application directly (testing)
python app.py
```

You should see startup messages:
```
🚀 Starting Test Case Generator API
📡 Ollama Base URL: http://localhost:11434
🤖 Default Model: llama3:latest
📄 System Instructions File: /opt/test-case-api/instructions/system_instructions.md
🌐 Server will run on http://0.0.0.0:5000
```

Open another PowerShell terminal and test:

```powershell
# From Windows PowerShell, test the API
curl http://localhost:5000/health

# Test available models
curl http://localhost:5000/models

# Test client GUI (if using browser)
# Navigate to: http://localhost:5000/client
```

You should see JSON responses. Press `Ctrl+C` in WSL to stop the test server.

**Common Startup Issues:**

1. **Ollama not accessible**: Make sure Ollama is running on Windows
   ```powershell
   # From Windows PowerShell
   ollama serve
   ```

2. **Port 5000 already in use**: Change `PORT=5001` in `.env`

3. **Missing instructions file**: Verify `instructions/system_instructions.md` exists

---

## 🔧 Production Setup with Systemd

### Create Systemd Service

This ensures your application starts automatically and runs in the background.

```bash
# Create systemd service file
sudo nano /etc/systemd/system/test-case-api.service
```

Add the following content:

```ini
[Unit]
Description=Test Case API Server
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/opt/test-case-api
Environment="PATH=/opt/test-case-api/venv/bin"
ExecStart=/opt/test-case-api/venv/bin/gunicorn --workers 4 --bind 0.0.0.0:5000 --timeout 300 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Replace `your-username` with your actual WSL username** (check with `whoami`).

### Enable and Start the Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable test-case-api

# Start the service
sudo systemctl start test-case-api

# Check status
sudo systemctl status test-case-api

# View logs
sudo journalctl -u test-case-api -f
```

---

## 🔒 Nginx Reverse Proxy Setup (Optional but Recommended)

### Step 1: Configure Nginx

```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/test-case-api
```

Add the following configuration:

```nginx
# Rate limiting
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

server {
    listen 80;
    server_name localhost;

    # Security headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Client interface (public)
    location /client {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API endpoints
    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
    }

    # Block admin in production
    location /admin {
        deny all;
        return 403;
    }

    # Health check
    location /health {
        proxy_pass http://127.0.0.1:5000;
        access_log off;
    }
}
```

### Step 2: Enable and Test Nginx

```bash
# Enable the site
sudo ln -s /etc/nginx/sites-available/test-case-api /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx

# Enable Nginx to start on boot
sudo systemctl enable nginx
```

### Step 3: Access Your Application

- **API**: `http://localhost/health`
- **Client GUI**: `http://localhost/client`
- **From Windows**: Access via `http://localhost` in your browser

---

## 🔐 SSL/TLS Setup (HTTPS)

### Option 1: Self-Signed Certificate (Development/Internal Use)

```bash
# Create SSL directory
sudo mkdir -p /etc/nginx/ssl

# Generate self-signed certificate
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/nginx-selfsigned.key \
  -out /etc/nginx/ssl/nginx-selfsigned.crt \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

# Update Nginx configuration
sudo nano /etc/nginx/sites-available/test-case-api
```

Add SSL configuration:

```nginx
server {
    listen 443 ssl http2;
    server_name localhost;

    ssl_certificate /etc/nginx/ssl/nginx-selfsigned.crt;
    ssl_certificate_key /etc/nginx/ssl/nginx-selfsigned.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # ... rest of configuration from above
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name localhost;
    return 301 https://$host$request_uri;
}
```

```bash
# Restart Nginx
sudo nginx -t && sudo systemctl restart nginx
```

### Option 2: Let's Encrypt (Production with Domain)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain certificate (replace your-domain.com)
sudo certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
# Test renewal
sudo certbot renew --dry-run
```

---

## 🌐 Accessing from Windows

### Local Access

From Windows, your WSL services are accessible via:

- `http://localhost` (if Nginx is configured)
- `http://localhost:5000` (direct to Flask)
- `http://127.0.0.1`

### Network Access

To access from other computers on your network:

1. **Find your Windows IP address:**

```powershell
# In PowerShell
ipconfig
# Look for IPv4 Address under your active network adapter
```

2. **Configure Windows Firewall:**

```powershell
# Allow port 80 (HTTP)
New-NetFirewallRule -DisplayName "WSL HTTP" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow

# Allow port 443 (HTTPS)
New-NetFirewallRule -DisplayName "WSL HTTPS" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow

# Allow port 5000 (Flask direct access)
New-NetFirewallRule -DisplayName "WSL Flask" -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow
```

3. **Access from other computers:**

```
http://YOUR_WINDOWS_IP
http://YOUR_WINDOWS_IP:5000
```

---

## 📊 Monitoring and Logs

### Application Logs

```bash
# Follow application logs
sudo journalctl -u test-case-api -f

# View recent logs
sudo journalctl -u test-case-api -n 100

# View logs for specific time
sudo journalctl -u test-case-api --since "1 hour ago"
```

### Nginx Logs

```bash
# Access logs
sudo tail -f /var/log/nginx/access.log

# Error logs
sudo tail -f /var/log/nginx/error.log
```

### Ollama Logs

**If using Windows Ollama (Option A - Recommended):**

```powershell
# From Windows PowerShell, check Ollama status
Get-Process ollama

# Check Ollama service in Windows Services
Get-Service -Name "Ollama*"

# Test from WSL
curl http://localhost:11434/api/tags
```

**If using WSL Ollama (Option B):**

```bash
# Check if Ollama is running in WSL
ps aux | grep ollama

# Restart Ollama if needed
pkill ollama
ollama serve &
```

---

## 🔄 Maintenance Commands

### Update Application Code

```bash
cd /opt/test-case-api

# Backup current version
sudo cp -r /opt/test-case-api /opt/test-case-api.backup.$(date +%Y%m%d_%H%M%S)

# Update specific files (from Windows)
cp /mnt/c/Projects/test_case_api/test_case_api/app.py .
cp -r /mnt/c/Projects/test_case_api/test_case_api/admin_gui/* admin_gui/
cp -r /mnt/c/Projects/test_case_api/test_case_api/public_gui/* public_gui/
cp -r /mnt/c/Projects/test_case_api/test_case_api/instructions/* instructions/

# Preserve your .env file (don't overwrite production config)
# If you need to update .env, do it manually

# Restart service
sudo systemctl restart test-case-api

# Check if restart was successful
sudo systemctl status test-case-api

# View logs for any errors
sudo journalctl -u test-case-api -n 50
```

### Update Python Dependencies

```bash
cd /opt/test-case-api
source venv/bin/activate
pip install --upgrade flask flask-cors requests python-dotenv gunicorn
sudo systemctl restart test-case-api
```

### Update Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
sudo systemctl restart test-case-api
```

### Update System Packages

```bash
sudo apt update && sudo apt upgrade -y
```

---

## 🚨 Troubleshooting

### Application Won't Start

```bash
# Check service status
sudo systemctl status test-case-api

# Check logs for errors
sudo journalctl -u test-case-api -n 50

# Test manually
cd /opt/test-case-api
source venv/bin/activate
python app.py
```

### Ollama Connection Issues

**If using Windows Ollama (most common):**

```bash
# From WSL, test connection to Windows Ollama
curl http://localhost:11434/api/tags

# If that fails, try using Windows host IP
curl http://$(ip route | grep default | awk '{print $3}'):11434/api/tags
```

From Windows PowerShell, check Ollama:

```powershell
# Check if Ollama is running on Windows
Get-Process ollama

# Restart Ollama on Windows (if needed)
# Stop Ollama from system tray or:
Stop-Process -Name ollama -Force

# Start Ollama again (it should auto-start)
# Or run: ollama serve
```

**If using WSL Ollama:**

```bash
# Check if Ollama is running in WSL
curl http://localhost:11434/api/tags

# Restart Ollama in WSL
pkill ollama
ollama serve &
```

### Nginx Issues

```bash
# Test configuration
sudo nginx -t

# Check Nginx status
sudo systemctl status nginx

# View error logs
sudo tail -f /var/log/nginx/error.log
```

### Port Already in Use

```bash
# Find what's using port 5000
sudo lsof -i :5000

# Kill the process (replace PID)
sudo kill -9 <PID>
```

### Cannot Access from Windows

```bash
# In WSL, check if service is listening on 0.0.0.0
sudo netstat -tlnp | grep 5000

# Should show: 0.0.0.0:5000 (not 127.0.0.1:5000)
```

---

## 🔧 Development vs Production

### Development Mode (with Admin GUI)

Edit `.env` file:

```bash
cd /opt/test-case-api
nano .env
```

Change:
```
ENVIRONMENT=development
```

Restart service:
```bash
sudo systemctl restart test-case-api
```

Access admin interface:
```
http://localhost/admin
```

### Production Mode (Client GUI only)

Edit `.env` file:

```bash
cd /opt/test-case-api
nano .env
```

Change:
```
ENVIRONMENT=production
```

Restart service:
```bash
sudo systemctl restart test-case-api
```

Admin interface will be blocked. Only client interface accessible:
```
http://localhost/client
```

---

## 📈 Performance Tuning

### Gunicorn Workers

Edit systemd service:

```bash
sudo nano /etc/systemd/system/test-case-api.service
```

Adjust workers based on CPU cores (formula: 2-4 × CPU cores):

```ini
ExecStart=/opt/test-case-api/venv/bin/gunicorn --workers 8 --bind 0.0.0.0:5000 --timeout 300 app:app
```

Reload and restart:

```bash
sudo systemctl daemon-reload
sudo systemctl restart test-case-api
```

### Nginx Worker Processes

```bash
sudo nano /etc/nginx/nginx.conf
```

Set based on CPU cores:

```nginx
worker_processes auto;  # or specific number like 4
```

---

## 🎯 Quick Reference Commands

### Service Management
```bash
# Flask API Service
sudo systemctl start test-case-api      # Start service
sudo systemctl stop test-case-api       # Stop service
sudo systemctl restart test-case-api    # Restart service
sudo systemctl status test-case-api     # Check status
sudo systemctl enable test-case-api     # Enable auto-start on boot

# Nginx (if configured)
sudo systemctl restart nginx            # Restart nginx
sudo systemctl status nginx             # Check nginx status
sudo nginx -t                           # Test nginx config
```

### Monitoring & Logs
```bash
# Application logs
sudo journalctl -u test-case-api -f              # Follow logs (live)
sudo journalctl -u test-case-api -n 100          # Last 100 lines
sudo journalctl -u test-case-api --since "1h ago" # Last hour
sudo journalctl -u test-case-api --since today   # Today's logs

# Nginx logs (if configured)
sudo tail -f /var/log/nginx/access.log          # Access logs (live)
sudo tail -f /var/log/nginx/error.log           # Error logs (live)
```

### Testing Endpoints
```bash
# From WSL
curl http://localhost:5000/health               # Health check
curl http://localhost:5000/models               # List models
curl http://localhost:5000/                     # API info

# If Nginx configured
curl http://localhost/health                    # Through nginx
curl http://localhost/client                    # Client GUI
```

### Ollama Management (Windows)
```powershell
# From Windows PowerShell
ollama list                                     # List installed models
ollama pull llama3:latest                       # Download model
ollama pull mistral:latest                      # Download another model
ollama serve                                    # Start Ollama (usually auto-starts)
Get-Process ollama                              # Check if running
```

```bash
# Test Ollama from WSL
curl http://localhost:11434/api/tags            # List models
curl http://localhost:11434/api/version         # Ollama version
```

### File Operations
```bash
# View/Edit configuration
cd /opt/test-case-api
nano .env                                       # Edit environment variables
cat .env                                        # View current config
nano instructions/system_instructions.md       # Edit prompts

# Check file structure
ls -la /opt/test-case-api                       # List files
du -sh /opt/test-case-api/*                     # Check disk usage
```

### Network & Connectivity
```bash
# Check listening ports
sudo netstat -tlnp | grep 5000                  # Check Flask port
sudo netstat -tlnp | grep 80                    # Check nginx port

# Check if services are accessible
curl -I http://localhost:5000/health            # HTTP headers only
curl -v http://localhost:11434/api/tags         # Verbose Ollama test
```

### Performance Monitoring
```bash
# Check resource usage
htop                                            # Interactive process viewer (install: sudo apt install htop)
top                                             # Standard process viewer
ps aux | grep gunicorn                          # Check gunicorn workers
ps aux | grep ollama                            # Check Ollama (if WSL-installed)

# Disk space
df -h                                           # Disk usage
du -sh /opt/test-case-api                       # App directory size
```

---

## 📝 License Compliance Summary

All components are **100% free for commercial use**:

| Component | License | Commercial Use |
|-----------|---------|----------------|
| Ubuntu (WSL) | Various Open Source | ✅ Free |
| Python | PSF License | ✅ Free |
| Flask | BSD-3-Clause | ✅ Free |
| Gunicorn | MIT | ✅ Free |
| Nginx | 2-clause BSD | ✅ Free |
| Ollama | MIT | ✅ Free |
| Your Application | MIT | ✅ Free |

**Zero licensing costs. Zero compliance concerns. Enterprise-ready.**

---

## 🎉 Summary

You now have a production-ready Test Case API running on WSL without Docker:

✅ No Docker Desktop licensing concerns
✅ Native Linux performance on Windows
✅ Production-grade with systemd services
✅ Nginx reverse proxy with SSL support
✅ Rate limiting and security headers
✅ Automatic service restart on failure
✅ Comprehensive logging and monitoring
✅ Easy maintenance and updates

**Perfect for Emerson Electric enterprise deployment!**

---

## 📚 Additional Resources

- [WSL Documentation](https://docs.microsoft.com/en-us/windows/wsl/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Ollama Documentation](https://ollama.com/)

---

## 🆘 Need Help?

If you encounter issues:

1. **Check the [Troubleshooting](#-troubleshooting) section** for common issues
2. **Review logs:** `sudo journalctl -u test-case-api -n 100`
3. **Test components individually:**
   - Ollama: `curl http://localhost:11434/api/tags`
   - Flask: `curl http://localhost:5000/health`
   - Nginx: `sudo nginx -t`
4. **Verify file structure:**
   ```bash
   ls -la /opt/test-case-api
   # Should have: app.py, admin_gui/, public_gui/, instructions/, venv/, .env
   ```
5. **Check environment variables:** `cat /opt/test-case-api/.env`

---

## 📋 Deployment Checklist

Use this checklist to verify your deployment:

- [ ] WSL2 installed and Ubuntu running
- [ ] Python 3, pip, venv installed
- [ ] Application files copied to `/opt/test-case-api/`
- [ ] Python virtual environment created and activated
- [ ] Dependencies installed (flask, flask-cors, requests, python-dotenv, gunicorn)
- [ ] `.env` file configured with correct values
- [ ] Ollama accessible from WSL (`curl http://localhost:11434/api/tags`)
- [ ] Correct model specified in `.env` (check with `ollama list` on Windows)
- [ ] Application starts without errors (`python app.py`)
- [ ] Health check responds (`curl http://localhost:5000/health`)
- [ ] Systemd service file created (`/etc/systemd/system/test-case-api.service`)
- [ ] Service enabled and started (`sudo systemctl enable test-case-api`)
- [ ] Service running successfully (`sudo systemctl status test-case-api`)
- [ ] Client GUI accessible (http://localhost:5000/client)
- [ ] (Optional) Nginx configured and running
- [ ] (Optional) SSL certificates configured
- [ ] Logs are being generated (`sudo journalctl -u test-case-api -n 10`)

**Your deployment is now Docker-free and license-worry-free!** 🚀
