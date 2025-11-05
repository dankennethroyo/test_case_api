# Test Case API - macOS Deployment Guide (Docker-Free)

## 📋 Overview

This guide shows how to deploy the Test Case API on macOS **without Docker Desktop**, avoiding all Docker Desktop licensing concerns for Emerson Electric employees.

### ✅ Benefits of Native macOS Deployment

- **No Docker Desktop license required** - completely free for enterprise use
- **Native performance** - runs directly on macOS without containerization overhead
- **Direct access** to macOS tools and package managers
- **Easy development** - seamless integration with macOS development tools
- **No licensing concerns** - all open source components

### 🎯 What You'll Deploy

- Flask API server (Python)
- Ollama AI engine
- Nginx reverse proxy (optional)
- SSL/TLS support
- Production-ready configuration

---

## 📦 Prerequisites

### 1. Install Homebrew (if not already installed)

Homebrew is the package manager for macOS.

```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Follow the post-installation instructions to add Homebrew to your PATH
# Usually involves adding to ~/.zprofile or ~/.bash_profile

# Verify installation
brew --version
```

### 2. Install Required System Packages

```bash
# Update Homebrew
brew update

# Install Python 3
brew install python@3.11

# Install nginx (optional, for reverse proxy)
brew install nginx

# Install git (usually pre-installed)
brew install git

# Verify installations
python3 --version
pip3 --version
nginx -v
```

---

## 🚀 Installation Steps

### Step 1: Install Ollama

```bash
# Download and install Ollama for macOS
curl -fsSL https://ollama.com/install.sh | sh

# OR download from https://ollama.com/download/mac

# Verify installation
ollama --version

# Start Ollama (it usually auto-starts after installation)
ollama serve &

# Or Ollama may run as a background service automatically
# Check if running:
pgrep -l ollama

# Pull your desired model
ollama pull llama3:latest

# Or for a smaller/faster model:
# ollama pull mistral:latest

# List available models
ollama list
```

**Note:** Ollama will run on `http://localhost:11434` by default.

### Step 2: Set Up Application Directory

```bash
# Create application directory
sudo mkdir -p /opt/test-case-api
cd /opt/test-case-api

# Change ownership to your user (replace YOUR_USERNAME)
sudo chown -R $(whoami):staff /opt/test-case-api

# Copy application files from your development location
# Adjust the source path to match your setup
cp ~/Projects/test_case_api/test_case_api/app.py .
cp -r ~/Projects/test_case_api/test_case_api/admin_gui .
cp -r ~/Projects/test_case_api/test_case_api/public_gui .
cp -r ~/Projects/test_case_api/test_case_api/instructions .
cp -r ~/Projects/test_case_api/test_case_api/samples .  # Optional: for testing

# OR clone from Git if you have a repository
# git clone <your-repo-url> .
# Then keep only: app.py, admin_gui/, public_gui/, instructions/, samples/

# Verify copied files
ls -la
# Should see: app.py, admin_gui/, public_gui/, instructions/, samples/

# Create output directories (for generated files)
mkdir -p output converted
```

### Step 3: Create Python Virtual Environment

```bash
# Navigate to application directory
cd /opt/test-case-api

# Create virtual environment using Python 3
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install flask flask-cors requests python-dotenv gunicorn
```

### Step 4: Configure Environment Variables

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
- `OLLAMA_BASE_URL=http://localhost:11434` - Connects to local Ollama

**For Development with Admin GUI:**
```bash
# Edit .env and change:
ENVIRONMENT=development
FLASK_DEBUG=True
DEBUG_MODE=True
```

**Model Selection:**
- Check available models: `ollama list`
- Update `OLLAMA_MODEL` to match your installed model
- Common options: `llama3:latest`, `llama4:latest`, `mistral:latest`, `mistral:instruct`

### Step 5: Test the Application

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

Open another Terminal window and test:

```bash
# Test the API
curl http://localhost:5000/health

# Test available models
curl http://localhost:5000/models

# Test client GUI (if using browser)
# Navigate to: http://localhost:5000/client
```

You should see JSON responses. Press `Ctrl+C` in the first Terminal to stop the test server.

**Common Startup Issues:**

1. **Ollama not accessible**: Make sure Ollama is running
   ```bash
   # Check if Ollama is running
   pgrep -l ollama
   
   # If not running, start it
   ollama serve &
   ```

2. **Port 5000 already in use**: 
   - AirPlay Receiver uses port 5000 on macOS Monterey and later
   - Either disable AirPlay Receiver in System Preferences → Sharing
   - Or change `PORT=5001` in `.env`

3. **Missing instructions file**: Verify `instructions/system_instructions.md` exists

---

## 🔧 Production Setup with LaunchAgent

### Create LaunchAgent Configuration

LaunchAgent ensures your application starts automatically and runs in the background.

```bash
# Create LaunchAgents directory if it doesn't exist
mkdir -p ~/Library/LaunchAgents

# Create LaunchAgent plist file
cat > ~/Library/LaunchAgents/com.emerson.test-case-api.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.emerson.test-case-api</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/opt/test-case-api/venv/bin/gunicorn</string>
        <string>--workers</string>
        <string>4</string>
        <string>--bind</string>
        <string>0.0.0.0:5000</string>
        <string>--timeout</string>
        <string>300</string>
        <string>app:app</string>
    </array>
    
    <key>WorkingDirectory</key>
    <string>/opt/test-case-api</string>
    
    <key>StandardOutPath</key>
    <string>/opt/test-case-api/logs/stdout.log</string>
    
    <key>StandardErrorPath</key>
    <string>/opt/test-case-api/logs/stderr.log</string>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <true/>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/opt/test-case-api/venv/bin:/usr/local/bin:/usr/bin:/bin</string>
    </dict>
</dict>
</plist>
EOF

# Create logs directory
mkdir -p /opt/test-case-api/logs

# Set proper permissions
chmod 644 ~/Library/LaunchAgents/com.emerson.test-case-api.plist
```

### Load and Start the Service

```bash
# Load the LaunchAgent
launchctl load ~/Library/LaunchAgents/com.emerson.test-case-api.plist

# Start the service
launchctl start com.emerson.test-case-api

# Check if service is running
launchctl list | grep test-case-api

# View logs
tail -f /opt/test-case-api/logs/stdout.log
tail -f /opt/test-case-api/logs/stderr.log
```

### Service Management Commands

```bash
# Stop the service
launchctl stop com.emerson.test-case-api

# Unload the service (disable auto-start)
launchctl unload ~/Library/LaunchAgents/com.emerson.test-case-api.plist

# Reload the service (after config changes)
launchctl unload ~/Library/LaunchAgents/com.emerson.test-case-api.plist
launchctl load ~/Library/LaunchAgents/com.emerson.test-case-api.plist
```

---

## 🔒 Nginx Reverse Proxy Setup (Optional but Recommended)

### Step 1: Configure Nginx

```bash
# Create nginx configuration
sudo mkdir -p /usr/local/etc/nginx/servers

# Create configuration file
sudo nano /usr/local/etc/nginx/servers/test-case-api.conf
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

    # Root redirect
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Step 2: Enable and Test Nginx

```bash
# Test nginx configuration
sudo nginx -t

# Start nginx
sudo brew services start nginx

# Or restart if already running
sudo brew services restart nginx

# Verify nginx is running
brew services list | grep nginx
```

### Step 3: Access Your Application

- **API**: `http://localhost/health`
- **Client GUI**: `http://localhost/client`
- **Direct to Flask** (bypass nginx): `http://localhost:5000`

---

## 🔐 SSL/TLS Setup (HTTPS)

### Option 1: Self-Signed Certificate (Development/Internal Use)

```bash
# Create SSL directory
sudo mkdir -p /usr/local/etc/nginx/ssl

# Generate self-signed certificate
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /usr/local/etc/nginx/ssl/nginx-selfsigned.key \
  -out /usr/local/etc/nginx/ssl/nginx-selfsigned.crt \
  -subj "/C=US/ST=State/L=City/O=Emerson/CN=localhost"

# Update Nginx configuration
sudo nano /usr/local/etc/nginx/servers/test-case-api.conf
```

Add SSL configuration:

```nginx
server {
    listen 443 ssl http2;
    server_name localhost;

    ssl_certificate /usr/local/etc/nginx/ssl/nginx-selfsigned.crt;
    ssl_certificate_key /usr/local/etc/nginx/ssl/nginx-selfsigned.key;
    
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
sudo nginx -t && sudo brew services restart nginx
```

### Option 2: Let's Encrypt (Production with Domain)

```bash
# Install certbot
brew install certbot

# Obtain certificate (replace your-domain.com)
sudo certbot certonly --nginx -d your-domain.com

# Auto-renewal is configured automatically via cron
# Test renewal
sudo certbot renew --dry-run
```

---

## 🌐 Network Access

### Local Access

From macOS, your service is accessible via:

- `http://localhost` (if Nginx is configured)
- `http://localhost:5000` (direct to Flask)
- `http://127.0.0.1`

### Network Access from Other Computers

To access from other computers on your network:

1. **Find your Mac's IP address:**

```bash
# Get IP address
ipconfig getifaddr en0  # for Wi-Fi
# OR
ipconfig getifaddr en1  # for Ethernet
```

2. **Configure macOS Firewall:**

```bash
# Open System Preferences → Security & Privacy → Firewall
# Allow incoming connections for:
# - Python (if running Flask directly)
# - nginx (if using nginx)

# Or use command line:
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/local/bin/nginx
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp /usr/local/bin/nginx
```

3. **Access from other computers:**

```
http://YOUR_MAC_IP
http://YOUR_MAC_IP:5000
```

---

## 📊 Monitoring and Logs

### Application Logs

```bash
# Follow application logs (if using LaunchAgent)
tail -f /opt/test-case-api/logs/stdout.log
tail -f /opt/test-case-api/logs/stderr.log

# View recent logs
tail -100 /opt/test-case-api/logs/stdout.log

# Search logs for errors
grep -i error /opt/test-case-api/logs/stderr.log
```

### Nginx Logs

```bash
# Access logs
tail -f /usr/local/var/log/nginx/access.log

# Error logs
tail -f /usr/local/var/log/nginx/error.log

# View last 100 lines
tail -100 /usr/local/var/log/nginx/error.log
```

### Ollama Logs

```bash
# Check if Ollama is running
pgrep -l ollama

# View Ollama logs (if running via Homebrew service)
brew services info ollama

# Test Ollama connectivity
curl http://localhost:11434/api/tags
```

---

## 🔄 Maintenance Commands

### Update Application Code

```bash
cd /opt/test-case-api

# Backup current version
sudo cp -r /opt/test-case-api /opt/test-case-api.backup.$(date +%Y%m%d_%H%M%S)

# Update specific files (adjust source path)
cp ~/Projects/test_case_api/test_case_api/app.py .
cp -r ~/Projects/test_case_api/test_case_api/admin_gui/* admin_gui/
cp -r ~/Projects/test_case_api/test_case_api/public_gui/* public_gui/
cp -r ~/Projects/test_case_api/test_case_api/instructions/* instructions/

# Preserve your .env file (don't overwrite production config)

# Restart service
launchctl stop com.emerson.test-case-api
launchctl start com.emerson.test-case-api

# Check if restart was successful
tail -50 /opt/test-case-api/logs/stdout.log
```

### Update Python Dependencies

```bash
cd /opt/test-case-api
source venv/bin/activate
pip install --upgrade flask flask-cors requests python-dotenv gunicorn

# Restart service
launchctl stop com.emerson.test-case-api
launchctl start com.emerson.test-case-api
```

### Update Ollama

```bash
# Update Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Or if installed via Homebrew
brew upgrade ollama

# Restart Ollama
pkill ollama
ollama serve &
```

### Update System Packages

```bash
# Update Homebrew
brew update

# Upgrade all packages
brew upgrade

# Upgrade specific packages
brew upgrade python nginx
```

---

## 🚨 Troubleshooting

### Application Won't Start

```bash
# Check LaunchAgent status
launchctl list | grep test-case-api

# Check logs for errors
tail -50 /opt/test-case-api/logs/stderr.log

# Test manually
cd /opt/test-case-api
source venv/bin/activate
python app.py
```

### Ollama Connection Issues

```bash
# Check if Ollama is running
pgrep -l ollama

# Test connection
curl http://localhost:11434/api/tags

# Restart Ollama
pkill ollama
ollama serve &

# Check Ollama models
ollama list
```

### Nginx Issues

```bash
# Test configuration
sudo nginx -t

# Check if nginx is running
brew services list | grep nginx

# View error logs
tail -50 /usr/local/var/log/nginx/error.log

# Restart nginx
sudo brew services restart nginx
```

### Port 5000 Already in Use (AirPlay Receiver)

```bash
# Option 1: Disable AirPlay Receiver
# System Preferences → Sharing → Uncheck "AirPlay Receiver"

# Option 2: Change Flask port
# Edit .env and set: PORT=5001

# Option 3: Find and kill process using port 5000
lsof -ti:5000 | xargs kill -9
```

### Cannot Access from Other Computers

```bash
# Check if Flask is listening on 0.0.0.0 (not 127.0.0.1)
lsof -i :5000
# Should show: *:5000 (not localhost:5000)

# Check macOS firewall settings
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate
```

### Permission Issues

```bash
# Fix ownership of application directory
sudo chown -R $(whoami):staff /opt/test-case-api

# Fix log file permissions
chmod 644 /opt/test-case-api/logs/*.log
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
FLASK_DEBUG=True
DEBUG_MODE=True
```

Restart service:
```bash
launchctl stop com.emerson.test-case-api
launchctl start com.emerson.test-case-api
```

Access admin interface:
```
http://localhost:5000/admin
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
FLASK_DEBUG=False
DEBUG_MODE=False
```

Restart service:
```bash
launchctl stop com.emerson.test-case-api
launchctl start com.emerson.test-case-api
```

Admin interface will be blocked. Only client interface accessible:
```
http://localhost:5000/client
```

---

## 📈 Performance Tuning

### Gunicorn Workers

Edit LaunchAgent plist:

```bash
nano ~/Library/LaunchAgents/com.emerson.test-case-api.plist
```

Adjust workers based on CPU cores (formula: 2-4 × CPU cores):

```xml
<string>--workers</string>
<string>8</string>  <!-- Change this number -->
```

Reload service:

```bash
launchctl unload ~/Library/LaunchAgents/com.emerson.test-case-api.plist
launchctl load ~/Library/LaunchAgents/com.emerson.test-case-api.plist
```

### Nginx Worker Processes

```bash
sudo nano /usr/local/etc/nginx/nginx.conf
```

Set based on CPU cores:

```nginx
worker_processes auto;  # or specific number like 4
```

---

## 🎯 Quick Reference Commands

### Service Management

```bash
# LaunchAgent Service
launchctl load ~/Library/LaunchAgents/com.emerson.test-case-api.plist    # Load service
launchctl unload ~/Library/LaunchAgents/com.emerson.test-case-api.plist  # Unload service
launchctl start com.emerson.test-case-api                                # Start service
launchctl stop com.emerson.test-case-api                                 # Stop service
launchctl list | grep test-case-api                                      # Check status

# Nginx (if configured)
sudo brew services start nginx                                           # Start nginx
sudo brew services stop nginx                                            # Stop nginx
sudo brew services restart nginx                                         # Restart nginx
brew services list | grep nginx                                          # Check nginx status
sudo nginx -t                                                            # Test nginx config
```

### Monitoring & Logs

```bash
# Application logs
tail -f /opt/test-case-api/logs/stdout.log                              # Follow stdout
tail -f /opt/test-case-api/logs/stderr.log                              # Follow stderr
tail -100 /opt/test-case-api/logs/stdout.log                            # Last 100 lines
grep -i error /opt/test-case-api/logs/stderr.log                        # Search for errors

# Nginx logs (if configured)
tail -f /usr/local/var/log/nginx/access.log                             # Access logs
tail -f /usr/local/var/log/nginx/error.log                              # Error logs
```

### Testing Endpoints

```bash
# From macOS
curl http://localhost:5000/health                                       # Health check
curl http://localhost:5000/models                                       # List models
curl http://localhost:5000/                                             # API info

# If Nginx configured
curl http://localhost/health                                            # Through nginx
curl http://localhost/client                                            # Client GUI

# From browser
open http://localhost:5000/client                                       # Open client GUI
```

### Ollama Management

```bash
# Ollama commands
ollama list                                                             # List installed models
ollama pull llama3:latest                                               # Download model
ollama pull mistral:latest                                              # Download another model
ollama serve &                                                          # Start Ollama
pgrep -l ollama                                                         # Check if running
pkill ollama                                                            # Stop Ollama

# Test Ollama
curl http://localhost:11434/api/tags                                    # List models
curl http://localhost:11434/api/version                                 # Ollama version
```

### File Operations

```bash
# View/Edit configuration
cd /opt/test-case-api
nano .env                                                               # Edit environment
cat .env                                                                # View config
nano instructions/system_instructions.md                               # Edit prompts

# Check file structure
ls -la /opt/test-case-api                                               # List files
du -sh /opt/test-case-api/*                                             # Check disk usage
```

### Network & Connectivity

```bash
# Check listening ports
lsof -i :5000                                                           # Check Flask port
lsof -i :80                                                             # Check nginx port

# Get IP address
ipconfig getifaddr en0                                                  # Wi-Fi IP
ipconfig getifaddr en1                                                  # Ethernet IP

# Test connectivity
curl -I http://localhost:5000/health                                    # HTTP headers only
curl -v http://localhost:11434/api/tags                                 # Verbose Ollama test
```

### Performance Monitoring

```bash
# Check resource usage
top -l 1 | head -10                                                     # CPU/Memory overview
ps aux | grep gunicorn                                                  # Check gunicorn workers
ps aux | grep ollama                                                    # Check Ollama

# Disk space
df -h                                                                   # Disk usage
du -sh /opt/test-case-api                                               # App directory size
```

---

## 📝 License Compliance Summary

All components are **100% free for commercial use**:

| Component | License | Commercial Use |
|-----------|---------|----------------|
| macOS | Apple EULA | ✅ Free (included with Mac) |
| Homebrew | BSD-2-Clause | ✅ Free |
| Python | PSF License | ✅ Free |
| Flask | BSD-3-Clause | ✅ Free |
| Gunicorn | MIT | ✅ Free |
| Nginx | 2-clause BSD | ✅ Free |
| Ollama | MIT | ✅ Free |
| Your Application | MIT | ✅ Free |

**Zero licensing costs. Zero compliance concerns. Enterprise-ready.**

---

## 🎉 Summary

You now have a production-ready Test Case API running on macOS without Docker:

✅ No Docker Desktop licensing concerns
✅ Native macOS performance
✅ Production-grade with LaunchAgent services
✅ Nginx reverse proxy with SSL support (optional)
✅ Rate limiting and security headers
✅ Automatic service restart on failure
✅ Comprehensive logging and monitoring
✅ Easy maintenance and updates

**Perfect for Emerson Electric enterprise deployment on Mac!**

---

## 📚 Additional Resources

- [Homebrew Documentation](https://docs.brew.sh/)
- [macOS LaunchAgents](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Ollama Documentation](https://ollama.com/)

---

## 🆘 Need Help?

If you encounter issues:

1. **Check the [Troubleshooting](#-troubleshooting) section** for common issues
2. **Review logs:** `tail -100 /opt/test-case-api/logs/stderr.log`
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
6. **Check service status:** `launchctl list | grep test-case-api`

---

## 📋 Deployment Checklist

Use this checklist to verify your deployment:

- [ ] Homebrew installed
- [ ] Python 3.11+ installed via Homebrew
- [ ] Ollama installed and running
- [ ] Application files copied to `/opt/test-case-api/`
- [ ] Python virtual environment created and activated
- [ ] Dependencies installed (flask, flask-cors, requests, python-dotenv, gunicorn)
- [ ] `.env` file configured with correct values
- [ ] Ollama accessible (`curl http://localhost:11434/api/tags`)
- [ ] Correct model specified in `.env` (check with `ollama list`)
- [ ] Application starts without errors (`python app.py`)
- [ ] Health check responds (`curl http://localhost:5000/health`)
- [ ] LaunchAgent plist file created
- [ ] LaunchAgent loaded and started
- [ ] Service running successfully (`launchctl list | grep test-case-api`)
- [ ] Client GUI accessible (http://localhost:5000/client)
- [ ] (Optional) Nginx configured and running
- [ ] (Optional) SSL certificates configured
- [ ] Logs are being generated (`tail /opt/test-case-api/logs/stdout.log`)
- [ ] (Optional) AirPlay Receiver disabled or port changed if using port 5000

**Your macOS deployment is now Docker-free and license-worry-free!** 🚀
