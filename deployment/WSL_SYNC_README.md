# WSL Sync Scripts

These scripts help you sync/update your Test Case API from Windows to WSL for deployment.

## 📁 Files

1. **`sync-to-wsl.sh`** - Full sync with backup and configuration
2. **`quick-update-wsl.sh`** - Quick code updates only
3. **`reference_from_WSL/`** - Reference configuration files from WSL deployment

---

## 🚀 Usage

### Initial Setup (First Time)

```bash
# From WSL, navigate to the deployment directory
cd /mnt/d/DK\$/_Projects/test_case_api/deployment

# Make script executable
chmod +x sync-to-wsl.sh

# Run full sync (creates backup, copies all files)
./sync-to-wsl.sh

# Or specify custom target directory
./sync-to-wsl.sh /opt/my-custom-path
```

**What it does:**
- ✅ Creates backup of existing deployment
- ✅ Syncs all application files (app.py, GUIs, instructions)
- ✅ Copies deployment reference files (.env, service file, generate-env.sh)
- ✅ Creates output directories
- ✅ Sets proper permissions
- ✅ Prompts to generate .env file

---

### Quick Updates (Development)

After making code changes in Windows, quickly update WSL:

```bash
# From WSL deployment directory
cd /mnt/d/DK\$/_Projects/test_case_api/deployment

# Make script executable (first time only)
chmod +x quick-update-wsl.sh

# Run quick update
./quick-update-wsl.sh

# Or specify custom target
./quick-update-wsl.sh /opt/my-custom-path
```

**What it does:**
- ✅ Updates app.py, admin_gui, public_gui, instructions
- ✅ Fixes permissions
- ✅ Restarts the service
- ✅ Shows service status
- ⚡ **Much faster** than full sync (no backup, no config files)

---

## 📋 Reference Files

The `reference_from_WSL/` directory contains:

### **`.env`**
Production environment configuration with:
- Ollama base URL (Windows host IP for NAT mode)
- Model selection
- Port configuration (5005)
- Debug settings

### **`test-case-api.service`**
Systemd service file with:
- Service configuration
- User settings (dk)
- Port binding (5005)
- Auto-restart settings

### **`generate-env.sh`**
Script to auto-generate .env with correct Windows host IP:
```bash
cd /opt/test-case-api
./generate-env.sh
```

---

## 🔄 Typical Workflow

### **Initial Deployment:**
```bash
# 1. Full sync from Windows to WSL
./sync-to-wsl.sh

# 2. Generate or configure .env
cd /opt/test-case-api
./generate-env.sh
# OR manually edit: nano .env

# 3. Set up Python environment (if not exists)
python3 -m venv venv
source venv/bin/activate
pip install flask flask-cors requests python-dotenv gunicorn

# 4. Install and start service
sudo cp test-case-api.service.reference /etc/systemd/system/test-case-api.service
sudo systemctl daemon-reload
sudo systemctl enable test-case-api
sudo systemctl start test-case-api
```

### **Development Updates:**
```bash
# Make changes in Windows (edit files in VS Code, etc.)

# Quick update in WSL
cd /mnt/d/DK\$/_Projects/test_case_api/deployment
./quick-update-wsl.sh

# Check logs
sudo journalctl -u test-case-api -f
```

### **Configuration Changes:**
```bash
# If you need to update .env or service file
./sync-to-wsl.sh  # Full sync

# Or manually copy reference files
cd /opt/test-case-api
sudo cp .env.reference .env
nano .env  # Edit as needed

# Restart service
sudo systemctl restart test-case-api
```

---

## 🛠️ Troubleshooting

### **Script can't find Windows mount path**
```bash
# Manually specify in the script, or use absolute path
./sync-to-wsl.sh /opt/test-case-api
```

### **Permission denied**
```bash
# Make scripts executable
chmod +x sync-to-wsl.sh quick-update-wsl.sh
```

### **Service won't start after update**
```bash
# Check logs
sudo journalctl -u test-case-api -n 50

# Check file permissions
ls -la /opt/test-case-api

# Verify Python environment
cd /opt/test-case-api
source venv/bin/activate
python app.py  # Test manually
```

### **Wrong Ollama IP after Windows reboot**
```bash
# Regenerate .env with current Windows IP
cd /opt/test-case-api
./generate-env.sh
sudo systemctl restart test-case-api
```

---

## 📝 Notes

- **Backup Location**: Backups are created as `/opt/test-case-api.backup.YYYYMMDD_HHMMSS`
- **Default Target**: Scripts default to `/opt/test-case-api`
- **WSL IP Changes**: Use `generate-env.sh` to auto-update Windows host IP
- **Port Configuration**: Reference files use port 5005 (NAT mode)
- **User Settings**: Service runs as user `dk` (update in service file for your user)

---

## 🔐 Security Notes

- `.env` files contain sensitive configuration - never commit to git
- Reference files are examples - review before using in production
- Service file should match your actual WSL username
- Firewall rules needed for domain network access (see WSL_DEPLOYMENT_GUIDE.md)

---

## 📚 Related Documentation

- **WSL_DEPLOYMENT_GUIDE.md** - Complete WSL deployment instructions
- **DEPLOYMENT_GUIDE.md** - General deployment guide
- **MAC_DEPLOYMENT_GUIDE.md** - macOS deployment instructions

---

**Happy Deploying! 🚀**
