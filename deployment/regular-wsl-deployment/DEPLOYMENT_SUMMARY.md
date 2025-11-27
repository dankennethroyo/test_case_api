# ✅ Regular WSL Deployment - Complete Setup

**Date:** November 26, 2025  
**Project:** Test Case API - Regular WSL Deployment  
**Status:** ✅ READY FOR DEPLOYMENT

---

## 📦 What Was Created

A complete **regular (non-secure) isolated deployment** for the Test Case API on Ubuntu2204 WSL, with the following specifications:

### 🎯 Deployment Specifications Met

- ✅ **New folder created:** `regular-wsl-deployment/`
- ✅ **Ubuntu2204 WSL:** All scripts configured for Ubuntu2204
- ✅ **Port 5009 in WSL:** Flask app runs on port 5009
- ✅ **Windows port 8009:** Port forwarding from Windows 8009 to WSL 5009
- ✅ **One batch file deployment:** `DEPLOY.bat` orchestrates everything
- ✅ **Regular deployment:** No SSL, no security features, simple HTTP access
- ✅ **Isolated artifacts:** Self-contained with all necessary files

---

## 📁 Complete File Structure

```
regular-wsl-deployment/
├── DEPLOY.bat                    # 🚀 ONE-CLICK DEPLOYMENT (Windows)
├── deploy-regular-wsl.sh        # 🔧 WSL deployment script
├── setup-windows.ps1            # 🪟 Windows port forwarding (PowerShell)
├── test-api.bat                 # 🧪 API testing script (Windows)
├── requirements.txt             # 📦 Python dependencies
├── README.md                    # 📖 Quick start guide
└── app/                         # 🖥️ Complete web application
    ├── app.py                   # Main Flask application
    ├── admin_gui/               # Admin web interface
    ├── public_gui/              # Client web interface
    ├── instructions/            # AI system instructions
    └── samples/                 # Sample requirements data
```

---

## 🔒 Security Features

### Port Forwarding Architecture
- **WSL Access:** `http://localhost:5009` or `http://[wsl-ip]:5009` (within WSL network)
- **Windows Access:** `http://localhost:8009` (via port forwarding)
- **Network Access:** `http://[windows-ip]:8009` (via port forwarding + firewall)
- **API Binding:** `HOST=0.0.0.0` (required for port forwarding to work)

Security is provided by:
- WSL network isolation from external networks
- Windows Firewall protecting port 8009
- Centralized port forwarding control

---

If you need to reset and redeploy:

### Step 1: Windows Cleanup (As Administrator)
```cmd
reset-windows.bat
```

### Step 2: WSL Reset
```bash
reset-environment.sh
```

These scripts remove all deployment artifacts and reset to pre-deployment state.

## 🚀 Deployment Process

### **One-Command Deployment (Recommended)**

**Just double-click `DEPLOY.bat` from Windows Explorer!**

This single batch file will:
1. ✅ Check prerequisites (WSL Ubuntu2204, Ollama)
2. ✅ Deploy to WSL (`/opt/test_case_api`)
3. ✅ Configure Windows port forwarding (8009→5009)
4. ✅ Test the deployment
5. ✅ Display access URLs

### **Manual Deployment (Alternative)**

If you prefer step-by-step control:

1. **WSL Deployment:**
   ```bash
   cd /mnt/d/DK\$/_Projects/test_case_api/deployment/regular-wsl-deployment
   chmod +x deploy-regular-wsl.sh
   ./deploy-regular-wsl.sh
   ```

2. **Windows Setup:**
   ```powershell
   # As Administrator
   cd "d:\DK$\_Projects\test_case_api\deployment\regular-wsl-deployment"
   .\setup-windows.ps1
   ```

3. **Test:**
   ```cmd
   # Double-click test-api.bat
   ```

---

## 🔌 Port Configuration

| Component | Internal (WSL) | External (Windows) | Protocol |
|-----------|----------------|-------------------|----------|
| Flask API | `localhost:5009` | `localhost:8009` | HTTP |
| Web Interfaces | `localhost:5009` | `localhost:8009` | HTTP |

**Access URLs after deployment:**
- **Landing Page:** `http://localhost:8009` (→ redirects to client)
- **Client Interface:** `http://localhost:8009/client`
- **Admin Interface:** `http://localhost:8009/admin`
- **Health Check:** `http://localhost:8009/health`

---

## 🔧 Key Features

### **Regular Deployment (No Security)**
- ✅ Regular Flask application (no SSL/TLS encryption)
- ✅ No API key authentication required
- ✅ No rate limiting
- ✅ Simple HTTP access
- ✅ Development-friendly setup

### **Complete Web Application**
- ✅ Flask API with test case generation
- ✅ Admin web interface for batch processing
- ✅ Client web interface for single generation
- ✅ AI integration with Ollama models
- ✅ Sample data and instructions included
- ✅ **Environment configuration (.env file)** with deployment-specific settings

### **Production Ready**
- ✅ Systemd service management
- ✅ Automatic startup on boot
- ✅ Log management
- ✅ Port forwarding configuration
- ✅ Windows Firewall rules

---

## 📋 Prerequisites

**Before deployment:**

1. **WSL2 with Ubuntu2204:**
   ```powershell
   wsl --install -d Ubuntu2204
   wsl --list --verbose  # Should show Ubuntu2204 Running
   ```

2. **Ollama on Windows:**
   ```powershell
   # Install from https://ollama.ai
   ollama pull phi4:14b  # or any model
   curl http://localhost:11434/api/tags  # Verify running
   ```

---

## 🧪 Testing the Deployment

### **Comprehensive Verification (Recommended)**
Run the verification script to test all aspects:
```powershell
.\verify-deployment.ps1
```

This checks:
- ✅ WSL service status
- ✅ WSL internal access (port 5009)
- ✅ Port forwarding configuration
- ✅ Windows firewall rules
- ✅ External access (port 8009)
- ✅ Ollama connectivity

### **Quick API Test**
Double-click `test-api.bat` for a quick functionality test

### **Manual Testing**
```bash
# Health check
curl http://localhost:8009/health

# List models
curl http://localhost:8009/models

# Generate test case
curl -X POST http://localhost:8009/generate \
  -H "Content-Type: application/json" \
  -d '{"REQUIREMENTS_ID":"TEST-001","DESCRIPTION":"Test requirement","CATEGORY":"Functional"}'
```

---

## 🔄 Service Management

### **Check Status**
```bash
# In WSL
sudo systemctl status test-case-api
sudo journalctl -u test-case-api -f
```

### **Restart Service**
```bash
sudo systemctl restart test-case-api
```

### **View Logs**
```bash
sudo journalctl -u test-case-api -n 50
```

---

## 🆚 Comparison: Regular vs Secure Deployment

| Feature | Regular Deployment | Secure Deployment |
|---------|-------------------|-------------------|
| **SSL/TLS** | ❌ No encryption | ✅ HTTPS required |
| **Authentication** | ❌ None required | ✅ API keys required |
| **Rate Limiting** | ❌ None | ✅ Per endpoint limits |
| **Security Headers** | ❌ None | ✅ HSTS, CSP, etc. |
| **Port** | 8009 (HTTP) | 443 (HTTPS) |
| **Setup Complexity** | 🟢 Simple | 🔴 Complex |
| **Use Case** | Development/Testing | Production |

---

## 🎯 Usage Scenarios

### **Development Environment**
- ✅ Quick setup for development
- ✅ Easy testing without security overhead
- ✅ Simple HTTP access
- ✅ Fast deployment (< 5 minutes)

### **Testing Environment**
- ✅ Isolated deployment
- ✅ Easy to tear down and recreate
- ✅ No security configuration needed
- ✅ Focus on functionality testing

### **Learning/Training**
- ✅ Understand basic deployment process
- ✅ Learn WSL/Windows integration
- ✅ Simple architecture to study

---

## 📚 Documentation Included

### **README.md** - Quick Start Guide
- Prerequisites checklist
- One-command deployment
- Access URLs and testing
- Troubleshooting basics

### **Scripts Documentation**
- `DEPLOY.bat` - Orchestrates complete deployment
- `deploy-regular-wsl.sh` - WSL setup and service creation
- `setup-windows.ps1` - Port forwarding and firewall
- `test-api.bat` - Comprehensive testing

---

## ✅ Deployment Verification Checklist

After running `DEPLOY.bat`, verify:

- [ ] **Service Running:** `sudo systemctl status test-case-api`
- [ ] **Port Forwarding:** `netsh interface portproxy show v4tov4`
- [ ] **External Access:** `curl http://localhost:8009/health`
- [ ] **Web Interfaces:** Open `http://localhost:8009/client`
- [ ] **API Functionality:** Test generation endpoints
- [ ] **Ollama Integration:** Models endpoint working

---

## 🚀 Ready to Deploy!

**Your regular Test Case API isolated deployment is complete and ready!**

### **Quick Start:**
1. Double-click `DEPLOY.bat`
2. Wait for automated deployment (~3-5 minutes)
3. Access at `http://localhost:8009`

### **Test Everything:**
1. Double-click `test-api.bat`
2. Check all tests pass with ✅

### **Access Interfaces:**
- **Client:** `http://localhost:8009/client`
- **Admin:** `http://localhost:8009/admin`

---

**This deployment provides a simple, fast way to get the Test Case API running on WSL Ubuntu2204 with Windows integration!** 🎉