# Regular Test Case API - Isolated Deployment Package

This folder contains everything needed for a **regular (non-secure) WSL deployment** of the Test Case Generation API with web interfaces and AI-powered test case generation.

## 🔄 Environment Reset

If you need to reset your environment to run the deployment from scratch:

### Step 1: Windows Cleanup (Run First - As Administrator)
```cmd
reset-windows.bat
```

### Step 2: WSL Reset (Run Second)
```bash
# From WSL terminal
./reset-environment.sh
```

This will:
- ✅ Remove port forwarding and firewall rules (Windows)
- ✅ Stop and remove the systemd service (WSL)
- ✅ Delete application directory (WSL)
- ✅ Reset NGINX configuration (WSL)
- ✅ Clean up Python environments (WSL)

## 🚀 One-Command Deployment

### Method 1: Windows Launcher (Easiest)

**Just double-click `DEPLOY.bat` from Windows Explorer!**

This Windows batch file will:
- ✓ Check prerequisites (WSL, Ollama)
- ✓ Run automated WSL deployment (`deploy-regular-wsl.sh`)
- ✓ Configure Windows port forwarding (`setup-windows.ps1`)
- ✓ Test the complete installation
- ✓ Display access URLs

**Location:** `regular-wsl-deployment\DEPLOY.bat`

### 2. Manual WSL Command

**From WSL terminal (Ubuntu2204):**
```bash
cd /mnt/d/DK\$/_Projects/test_case_api/deployment/regular-wsl-deployment
chmod +x deploy-regular-wsl.sh
./deploy-regular-wsl.sh
```

Then Windows setup (PowerShell as Administrator):
```powershell
cd "d:\DK$\_Projects\test_case_api\deployment\regular-wsl-deployment"
.\setup-windows.ps1
```

## 📦 What's Included

### Core Deployment
- `DEPLOY.bat` - **Windows launcher** (just double-click to deploy!)
- `deploy-regular-wsl.sh` - **WSL deployment script**
- `setup-windows.ps1` - **Windows port forwarding** setup script
- `requirements.txt` - **Python dependencies**

### Complete Web Application
- `app/` - **Complete web application** (self-contained)
  - `app.py` - **Regular Flask application**
  - `admin_gui/` - **Admin web interface**
  - `public_gui/` - **Public client interface**
  - `instructions/` - **AI system instructions**
  - `samples/` - **Sample requirements data**

## 🔧 Configuration

### Environment Variables

The deployment creates a `.env` file in the application directory (`/opt/test_case_api/.env`) with default settings. You can modify these settings after deployment:

```bash
# Edit the environment file
sudo nano /opt/test_case_api/.env

# Restart the service to apply changes
sudo systemctl restart test-case-api
```

**Key Configuration Options:**

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://<windows-host-ip>:11434` | **Auto-detected** Windows host IP for Ollama |
| `OLLAMA_MODEL` | `llama3:latest` | AI model for test case generation |
| `HOST` | `0.0.0.0` | Bind to all interfaces (required for port forwarding) |
| `PORT` | `5009` | WSL internal port |
| `FLASK_DEBUG` | `False` | Debug mode (keep False for production) |
| `MAX_FILE_SIZE_MB` | `10` | Maximum upload file size |

### Model Configuration

To use a different Ollama model:

1. **Pull the model on Windows:**
   ```powershell
   ollama pull mistral:instruct  # or any other model
   ```

2. **Update the .env file:**
   ```bash
   sudo sed -i 's/OLLAMA_MODEL=.*/OLLAMA_MODEL=mistral:instruct/' /opt/test_case_api/.env
   ```

3. **Restart the service:**
   ```bash
   sudo systemctl restart test-case-api
   ```

## 🎯 Quick Start Steps

### 1. Deploy to WSL

```bash
# From WSL terminal (Ubuntu2204)
cd /mnt/d/DK\$/_Projects/test_case_api/deployment/regular-wsl-deployment

# Make script executable and run
chmod +x deploy-regular-wsl.sh
./deploy-regular-wsl.sh
```

### 2. Configure Windows (PowerShell as Administrator)

```powershell
# Navigate to deployment directory
cd "d:\DK$\_Projects\test_case_api\deployment\regular-wsl-deployment"

# Run Windows setup
.\setup-windows.ps1
```

### 3. Test the Deployment

```bash
# From WSL - test health endpoint
curl http://localhost:5009/health

# Test with API key (use key from deployment output)
curl http://localhost:5009/models
```

### 4. Access Web Interfaces

**Client Interface:**
```
http://localhost:8009/client
```
- Generate single test cases
- View results in web interface

**Admin Interface:**
```
http://localhost:8009/admin
```
- Batch processing capabilities
- System monitoring

## 🔄 Ports Configuration

| Component | WSL Port | Windows Port | Purpose |
|-----------|----------|--------------|---------|
| Flask API | 5009 | 8009 | Main API endpoint |
| Web Interfaces | 5009 | 8009 | Client/Admin GUIs |

## 🔧 Service Management

### Check Status
```bash
# Service status
sudo systemctl status test-case-api

# View logs
sudo journalctl -u test-case-api -f

# Restart service
sudo systemctl restart test-case-api
```

## 🌐 Web Interfaces

### Landing Page / Client Interface
**URL:** http://localhost:8009 or http://localhost:8009/client
- Generate single test cases
- Upload batch requirements (JSON)
- View and download results
- User-friendly interface

### Admin Interface
**URL:** http://localhost:8009/admin
- Batch processing
- System monitoring
- Configuration

## 🔒 Security Configuration

### Port Forwarding Access
The API is configured to bind to all interfaces (`HOST=0.0.0.0`) to enable Windows port forwarding:

**Access Patterns:**
- ✅ **WSL Internal:** `http://localhost:5009` - Direct access within WSL
- ✅ **Windows Host:** `http://localhost:8009` - Through port forwarding
- ✅ **Network PCs:** `http://[windows-ip]:8009` - Through port forwarding

**Security Benefits:**
- WSL network is isolated from external networks
- Windows Firewall controls access to port 8009
- Port forwarding provides centralized access control
- Can easily enable/disable access by managing port forwarding rules

## 🔍 Troubleshooting

### Common Issues

**"Connection refused"**
```bash
# Check if service is running
sudo systemctl status test-case-api

# Check port forwarding (Windows)
netsh interface portproxy show v4tov4
```

**"Ollama connection failed"**
```bash
# Test Ollama from WSL
WIN_IP=$(ip route show | grep default | awk '{print $3}')
curl http://$WIN_IP:11434/api/tags

# Check Windows Ollama
# From Windows: curl http://localhost:11434/api/tags

# If connection fails, update .env and restart:
sudo sed -i "s|OLLAMA_BASE_URL=.*|OLLAMA_BASE_URL=http://$WIN_IP:11434|" /opt/test_case_api/.env
sudo systemctl restart test-case-api
```

**Port forwarding issues**
```powershell
# From Windows PowerShell (Administrator)
netsh interface portproxy show v4tov4
.\setup-windows.ps1  # Re-run if needed
```

**Network access from other PCs**
```powershell
# Find your Windows IP first
ipconfig  # Look for IPv4 Address

# Then access from network using:
http://[your-windows-ip]:8009/health
http://[your-windows-ip]:8009/client
http://[your-windows-ip]:8009/admin
```

## 🎯 API Usage Examples

**List Available Models:**
```bash
curl http://localhost:8009/models
```

**Generate Single Test Case:**
```bash
curl http://localhost:8009/generate \
  -X POST -H "Content-Type: application/json" \
  -d '{
    "REQUIREMENTS_ID": "REQ-001",
    "DESCRIPTION": "The system shall validate user input",
    "CATEGORY": "Functional"
  }'
```

**Batch Generation:**
```bash
curl http://localhost:8009/generate/batch \
  -X POST -H "Content-Type: application/json" \
  -d '{
    "requirements": [
      {"REQUIREMENTS_ID": "REQ-001", "DESCRIPTION": "Requirement 1", "CATEGORY": "Functional"},
      {"REQUIREMENTS_ID": "REQ-002", "DESCRIPTION": "Requirement 2", "CATEGORY": "Performance"}
    ]
  }'
```

## 📁 File Structure

```
regular-wsl-deployment/
├── DEPLOY.bat                    # 🚀 Windows launcher (one-click)
├── deploy-regular-wsl.sh        # 🔧 WSL deployment script
├── setup-windows.ps1            # 🪟 Windows port forwarding
├── verify-deployment.ps1        # ✅ Comprehensive verification
├── test-api.bat                 # 🧪 Quick API test
├── reset-windows.bat            # 🔄 Windows cleanup
├── reset-environment.sh         # 🔄 WSL cleanup
├── requirements.txt             # 📦 Python dependencies
├── README.md                    # 📖 This file
├── DEPLOYMENT_SUMMARY.md        # 📋 Quick reference
├── FIXES_APPLIED.md             # 🔧 Technical fixes document
└── app/                         # 🖥️ Complete web application
    ├── app.py                   # Main Flask application
    ├── admin_gui/               # Admin web interface
    ├── public_gui/              # Client web interface
    ├── instructions/            # AI system instructions
    └── samples/                 # Sample requirements data
```

## 🎯 Key Features

### Regular Deployment (No Security)
- Regular Flask application (no SSL/TLS)
- No API key authentication required
- No rate limiting
- Simple HTTP access
- Development-friendly setup

### Production Ready
- Systemd service management
- Automatic startup
- Log rotation ready
- Port forwarding configuration
- Web interface access

### AI Integration
- Ollama AI model integration
- Test case generation
- Model selection support
- Windows host connectivity

## 📞 Support

**For deployment issues:**
1. Check the deployment script output for errors
2. Verify prerequisites (WSL, Ollama, network connectivity)
3. Check service logs: `sudo journalctl -u test-case-api -n 50`

**For API issues:**
1. Test health endpoint: `curl http://localhost:8009/health`
2. Check Ollama connectivity: `curl http://localhost:11434/api/tags` (from Windows)

---

**Your regular Test Case API will be ready in under 5 minutes!** 🚀