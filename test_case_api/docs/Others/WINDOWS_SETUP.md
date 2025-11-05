# Windows Setup Guide - Test Case API

## 🪟 Running on Windows

Since you're on Windows, here's how to get started:

## Option 1: Using WSL2 (Recommended)

### Step 1: Install WSL2
```powershell
# Run in PowerShell as Administrator
wsl --install
# Restart computer when prompted
```

### Step 2: Install Docker Desktop
1. Download from https://www.docker.com/products/docker-desktop
2. Install and enable WSL2 integration
3. Restart computer

### Step 3: Open WSL Terminal
```powershell
# In PowerShell or Command Prompt
wsl
```

### Step 4: Navigate and Deploy
```bash
cd /mnt/c/Projects/test_case_api/deployment
chmod +x deploy.sh
./deploy.sh
```

## Option 2: Docker Desktop Only

### Step 1: Install Docker Desktop
1. Download from https://www.docker.com/products/docker-desktop
2. Install (will install WSL2 automatically if needed)
3. Restart computer

### Step 2: Convert Scripts for Windows

Create `deploy.bat` in deployment folder:
```batch
@echo off
echo Test Case API Deployment
echo ========================
echo.
echo Select deployment mode:
echo 1) Development (with admin interface)
echo 2) Production (client interface only, with SSL)
set /p MODE="Enter choice (1-2): "

if "%MODE%"=="1" (
    set ENV_FILE=.env.development
    echo.
    echo Development Deployment
) else if "%MODE%"=="2" (
    set ENV_FILE=.env.production
    echo.
    echo Production Deployment
) else (
    echo Invalid choice
    exit /b 1
)

echo.
echo Building and starting services...
docker-compose build --no-cache
docker-compose --env-file %ENV_FILE% up -d

echo.
echo Waiting for services...
timeout /t 10 /nobreak

echo.
echo Service Status:
docker-compose ps

echo.
echo Deployment complete!
echo.
if "%MODE%"=="1" (
    echo Admin Interface:  http://localhost/admin
    echo Client Interface: http://localhost/client
    echo API:              http://localhost/api/
) else (
    echo Client Interface: https://localhost/client
    echo API:              https://localhost/api/
)
echo.
pause
```

### Step 3: Run Deployment
```powershell
cd C:\Projects\test_case_api\deployment
.\deploy.bat
```

## Option 3: Manual Python Setup (No Docker)

### Step 1: Install Python
1. Download Python 3.11+ from https://www.python.org/downloads/
2. Check "Add Python to PATH" during installation
3. Verify: `python --version`

### Step 2: Install Ollama
1. Download from https://ollama.ai/download/windows
2. Install and run
3. Pull model: `ollama pull llama3`

### Step 3: Setup Python Environment
```powershell
cd C:\Projects\test_case_api\test_case_api

# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Create Environment File
Create `.env` file:
```env
ENVIRONMENT=development
HOST=0.0.0.0
PORT=5000
FLASK_DEBUG=true
DEBUG_MODE=true
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3:latest
```

### Step 5: Run Application
```powershell
python app.py
```

Access:
- Admin: http://localhost:5000/admin
- Client: http://localhost:5000/client
- API: http://localhost:5000/api/

## 🎯 Quick Start (Easiest for Windows)

### Using Docker Desktop (Recommended)

1. **Install Docker Desktop**
   - Download: https://www.docker.com/products/docker-desktop
   - Install and restart

2. **Open PowerShell in Project Directory**
   ```powershell
   cd C:\Projects\test_case_api\deployment
   ```

3. **Copy Environment File**
   ```powershell
   copy .env.development .env
   ```

4. **Start Services**
   ```powershell
   docker-compose up -d
   ```

5. **Pull Ollama Model**
   ```powershell
   docker exec test-case-ollama ollama pull llama3:latest
   ```

6. **Access Interfaces**
   - Admin: http://localhost/admin
   - Client: http://localhost/client

## 🔧 Windows-Specific Commands

### Managing Services
```powershell
# Start
docker-compose up -d

# Stop
docker-compose down

# View logs
docker-compose logs -f

# Restart
docker-compose restart

# Check status
docker-compose ps
```

### Ollama Management
```powershell
# List models
docker exec test-case-ollama ollama list

# Pull model
docker exec test-case-ollama ollama pull llama3:latest

# Remove model
docker exec test-case-ollama ollama rm model-name
```

### Troubleshooting
```powershell
# Check Docker is running
docker ps

# Check health
curl http://localhost/health

# View all logs
docker-compose logs -f

# Restart everything
docker-compose restart

# Clean up
docker system prune -a
```

## 🐛 Common Windows Issues

### Issue: WSL2 not installed
**Solution**:
```powershell
wsl --install
# Restart computer
```

### Issue: Docker Desktop not starting
**Solution**:
1. Enable Virtualization in BIOS
2. Enable Hyper-V:
   ```powershell
   # Run as Administrator
   Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
   ```
3. Restart computer

### Issue: Permission denied
**Solution**:
- Run PowerShell as Administrator
- Or add user to docker-users group:
  ```powershell
  net localgroup docker-users "YOUR_USERNAME" /ADD
  ```

### Issue: Port already in use
**Solution**:
```powershell
# Find process using port 80
netstat -ano | findstr :80

# Kill process (use PID from above)
taskkill /PID <PID> /F

# Or change port in docker-compose.yml
```

### Issue: Scripts won't run
**Solution**:
```powershell
# Enable script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or use batch files instead of bash scripts
```

## 📁 Windows File Paths

When editing configuration files, use Windows paths:

```env
# In .env file
SYSTEM_INSTRUCTION_FILE=C:\Projects\test_case_api\test_case_api\instructions\system_instructions.md
```

In Docker, paths are mapped automatically:
```yaml
# docker-compose.yml handles mapping
volumes:
  - ./output:/app/output  # Works on Windows
```

## 🚀 Recommended Setup for Windows

### Best Option: Docker Desktop + WSL2

1. Install Docker Desktop with WSL2
2. Use WSL2 terminal for commands
3. Files remain on Windows (C:\Projects\...)
4. Best performance and compatibility

### Alternative: Docker Desktop Only

1. Install Docker Desktop
2. Use PowerShell for commands
3. Create `.bat` files for automation
4. Good compatibility

### For Development: Python + Ollama Native

1. Install Python and Ollama for Windows
2. Use PowerShell/Command Prompt
3. No Docker needed
4. Easier debugging

## 🎯 Next Steps

1. Choose your setup method above
2. Follow the steps
3. Access http://localhost/admin (development)
4. Test the interfaces

## 📖 Additional Resources

- Docker Desktop: https://docs.docker.com/desktop/windows/
- WSL2 Setup: https://docs.microsoft.com/en-us/windows/wsl/install
- Python on Windows: https://docs.python.org/3/using/windows.html
- Ollama: https://ollama.ai/

---

**For complete documentation, see**:
- DEPLOYMENT_GUIDE.md (deployment/)
- NEW_FEATURES_README.md (root)
- QUICK_REFERENCE.md (root)
