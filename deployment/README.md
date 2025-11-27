# Test Case API - Deployment Packages

This directory contains production-ready deployment packages for the Test Case Generator API on WSL2.

## 📦 Available Deployments

### 1. **Regular WSL Deployment** (Development)
Simple, direct deployment for development and testing.

**Location**: `regular-wsl-deployment/`

**Features**:
- ✅ Quick setup (~2 minutes)
- ✅ Direct Flask access
- ✅ Simple troubleshooting
- ✅ Development-focused

**Best For**: Development, testing, learning

[→ Read Documentation](regular-wsl-deployment/README.md)

---

### 2. **NGINX WSL Deployment** (Production) ⭐
Production-ready deployment with NGINX reverse proxy and Flask isolation.

**Location**: `nginx-wsl-deployment/`

**Features**:
- ✅ Flask isolated to localhost (security)
- ✅ NGINX reverse proxy
- ✅ Enhanced security headers
- ✅ Production-ready architecture
- ✅ SSL/TLS capable
- ✅ Load balancing ready

**Best For**: Production, team collaboration, network access

[→ Read Documentation](nginx-wsl-deployment/README.md)

---

## 🔍 Which One Should I Use?

| Your Need | Recommended Package |
|-----------|---------------------|
| Quick local testing | **Regular** |
| Learning the API | **Regular** |
| Development work | **Regular** |
| Production deployment | **NGINX** ⭐ |
| Network access needed | **NGINX** ⭐ |
| Security is priority | **NGINX** ⭐ |
| Multiple users | **NGINX** ⭐ |
| Need SSL/TLS | **NGINX** ⭐ |

[→ Detailed Comparison](DEPLOYMENT_COMPARISON.md)

---

## 🚀 Quick Start

### Regular Deployment
```cmd
cd regular-wsl-deployment
DEPLOY.bat
```

### NGINX Deployment (Recommended for Production)
```cmd
cd nginx-wsl-deployment
DEPLOY.bat
```

**Requirements**:
- Windows with WSL2 (Ubuntu 22.04)
- Ollama running on Windows
- Administrator privileges

---

## 🏗️ Architecture Comparison

### Regular Deployment
```
Network → Windows:8009 → WSL Flask:5009 (0.0.0.0)
```

### NGINX Deployment
```
Network → Windows:8009 → WSL NGINX:8080 → Flask:5009 (127.0.0.1)
```

---

## 📋 Package Contents

### Both Packages Include:
- ✅ **DEPLOY.bat** - Turnkey Windows launcher
- ✅ **WSL deployment script** - Automated setup
- ✅ **Windows setup script** - Port forwarding
- ✅ **Reset scripts** - Environment cleanup
- ✅ **Verification tools** - Health checks
- ✅ **Complete documentation**
- ✅ **Web application** - GUI interfaces
- ✅ **Sample data** - Ready-to-use examples

### NGINX Package Adds:
- ✅ **NGINX configuration** - Production-ready
- ✅ **Enhanced security** - Headers & isolation
- ✅ **Better performance** - Request buffering
- ✅ **SSL/TLS ready** - Certificate support

---

## 🔄 Switching Between Deployments

### From Regular → NGINX
```cmd
REM Reset regular
cd regular-wsl-deployment
reset-windows.bat
wsl ./reset-environment.sh

REM Deploy NGINX
cd ..\nginx-wsl-deployment
DEPLOY.bat
```

### From NGINX → Regular
```cmd
REM Reset NGINX
cd nginx-wsl-deployment
reset-windows.bat
wsl ./reset-environment.sh

REM Deploy regular
cd ..\regular-wsl-deployment
DEPLOY.bat
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [DEPLOYMENT_COMPARISON.md](DEPLOYMENT_COMPARISON.md) | Detailed comparison guide |
| [regular-wsl-deployment/README.md](regular-wsl-deployment/README.md) | Regular deployment docs |
| [nginx-wsl-deployment/README.md](nginx-wsl-deployment/README.md) | NGINX deployment docs |

---

## 🔧 Common Tasks

### View Logs
```bash
# Flask logs (both deployments)
wsl sudo journalctl -u test-case-api -f

# NGINX logs (NGINX deployment only)
wsl sudo tail -f /var/log/nginx/test-case-api-error.log
```

### Restart Services
```bash
# Flask (both deployments)
wsl sudo systemctl restart test-case-api

# NGINX (NGINX deployment only)
wsl sudo systemctl restart nginx
```

### Test API
```cmd
# From deployment directory
test-api.bat
```

### Complete Reset
```cmd
# As Administrator
reset-windows.bat

# From WSL
wsl ./reset-environment.sh
```

---

## 🌐 Access URLs

After deployment, access your API:

| Interface | URL |
|-----------|-----|
| Client GUI | `http://localhost:8009/client` |
| Admin GUI | `http://localhost:8009/admin` |
| Health Check | `http://localhost:8009/health` |
| API Docs | Check README in package |
| Network Access | `http://<Windows-IP>:8009` |

---

## 🆘 Troubleshooting

### Deployment Failed?
1. Check you're running as Administrator
2. Verify WSL is running: `wsl --list --verbose`
3. Verify Ollama is running: `curl http://localhost:11434/api/tags`
4. Check logs in deployment output

### Can't Access API?
1. Run verification script: `verify-deployment.ps1`
2. Check port forwarding: `netsh interface portproxy show v4tov4`
3. Check services: `wsl sudo systemctl status test-case-api`

### Need Fresh Start?
```cmd
REM Reset everything
reset-windows.bat
wsl ./reset-environment.sh

REM Redeploy
DEPLOY.bat
```

---

## 📞 Support Resources

### Documentation
- Package README files
- DEPLOYMENT_SUMMARY.md in each package
- QUICKSTART.md guides

### Tools
- `verify-deployment.ps1` - Check deployment health
- `test-api.bat` - Quick API test
- Reset scripts - Clean environment

### Logs
- Flask: `wsl sudo journalctl -u test-case-api -f`
- NGINX: `wsl sudo tail -f /var/log/nginx/test-case-api-error.log`
- System: Check deployment output

---

## 🔐 Security Notes

### Regular Deployment
- Flask exposed on all interfaces (`0.0.0.0`)
- Direct network access to Flask
- Basic Windows firewall protection
- Suitable for development

### NGINX Deployment
- Flask isolated to localhost (`127.0.0.1`)
- NGINX reverse proxy layer
- Enhanced security headers
- Defense in depth
- Production-ready

**Recommendation**: Use NGINX deployment for any production or network-accessible deployment.

---

## 🎯 Quick Decision Tree

```
Need production deployment? 
    YES → Use NGINX Deployment
    NO → 
        Multiple users?
            YES → Use NGINX Deployment
            NO → 
                Learning/Testing?
                    YES → Use Regular Deployment
                    NO → Use NGINX Deployment (safer)
```

---

## 📝 Version Information

- **Regular Deployment**: v1.0 (Development)
- **NGINX Deployment**: v1.0 (Production)
- **Last Updated**: 2025-11-27
- **Platform**: WSL2 Ubuntu 22.04
- **Python**: 3.x with venv

---

## 🚀 Ready to Deploy?

1. **Choose your package** (NGINX recommended for production)
2. **Navigate to package directory**
3. **Run DEPLOY.bat as Administrator**
4. **Access at http://localhost:8009**

**That's it!** Both packages are turnkey deployments. 🎉

---

**Happy Testing!** 🧪✨
