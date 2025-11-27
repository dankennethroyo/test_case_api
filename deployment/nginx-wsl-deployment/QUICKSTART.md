# NGINX WSL Deployment - Quick Start Guide

## 🚀 Deploy in 3 Steps

### Step 1: Open as Administrator
Right-click on `DEPLOY.bat` → **Run as administrator**

### Step 2: Confirm Deployment
The script will:
- ✅ Clean existing installation
- ✅ Install NGINX
- ✅ Deploy Flask (localhost binding)
- ✅ Configure port forwarding
- ✅ Set up firewall

### Step 3: Access Your API
Open browser: `http://localhost:8009/client`

**That's it!** 🎉

---

## 📋 Common Commands

### Quick Test
```cmd
test-api.bat
```

### View Logs
```bash
# Flask logs
wsl sudo journalctl -u test-case-api -f

# NGINX logs
wsl sudo tail -f /var/log/nginx/test-case-api-error.log
```

### Restart Services
```bash
# Flask
wsl sudo systemctl restart test-case-api

# NGINX
wsl sudo systemctl restart nginx
```

### Reset Everything
```cmd
REM As Administrator
reset-windows.bat

REM From WSL
wsl bash -c "cd /mnt/d/DK\$/_Projects/test_case_api/deployment/nginx-wsl-deployment && ./reset-environment.sh"
```

---

## 🌐 Access URLs

| Interface | URL |
|-----------|-----|
| Client GUI | `http://localhost:8009/client` |
| Admin GUI | `http://localhost:8009/admin` |
| Health Check | `http://localhost:8009/health` |
| Network Access | `http://<Your-Windows-IP>:8009` |

---

## 🔍 Troubleshooting

### Can't Access API?
```powershell
# Check services
wsl sudo systemctl status test-case-api nginx

# Check port forwarding
netsh interface portproxy show v4tov4

# Verify deployment
.\verify-deployment.ps1
```

### Need to Redeploy?
```cmd
REM 1. Reset (as Admin)
reset-windows.bat
wsl bash reset-environment.sh

REM 2. Deploy (as Admin)
DEPLOY.bat
```

---

## 🏗️ Architecture

```
Your Browser → Windows:8009 → WSL NGINX:8080 → Flask:5009 → Ollama
```

**Security**: Flask only listens on localhost (127.0.0.1) ✅

---

## 📚 More Help

- Full documentation: `README.md`
- Technical details: `DEPLOYMENT_SUMMARY.md`
- Verify installation: `verify-deployment.ps1`

---

**Questions?** Check the logs or reset and redeploy!
