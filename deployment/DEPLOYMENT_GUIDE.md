# Test Case API - Deployment Guide

## 📋 Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Development Deployment](#development-deployment)
- [Production Deployment](#production-deployment)
- [Configuration](#configuration)
- [Security](#security)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)
- [Maintenance](#maintenance)

---

## 🎯 Overview

This guide covers deploying the Test Case API in both development and production environments. The application includes:

- **Backend API**: Flask-based REST API for test case generation
- **Admin GUI**: Development-only interface for system management
- **Client GUI**: Public-facing interface for end users
- **AI Engine**: Ollama LLM for intelligent test case generation

### Key Features
- ✅ **Environment-based configuration** (development/production)
- ✅ **Docker-based deployment** (production-ready)
- ✅ **Nginx reverse proxy** with SSL/TLS support
- ✅ **Security hardening** (rate limiting, headers, access control)
- ✅ **Open source and free for commercial use**
- ✅ **Health monitoring** and logging

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Nginx (HTTPS)                     │
│  - SSL Termination                                   │
│  - Rate Limiting                                     │
│  - Security Headers                                  │
└──────────────┬──────────────────────────────────────┘
               │
       ┌───────┴───────┐
       │               │
┌──────▼──────┐ ┌─────▼──────┐
│   /client   │ │   /admin   │
│  (Public)   │ │   (Dev)    │
└──────┬──────┘ └─────┬──────┘
       │               │
       └───────┬───────┘
               │
        ┌──────▼───────┐
        │   Flask API   │
        │  - REST API   │
        │  - File Proc  │
        └──────┬───────┘
               │
        ┌──────▼───────┐
        │    Ollama     │
        │   LLM Engine  │
        └───────────────┘
```

---

## 📦 Prerequisites

### Required
- **Docker** 20.10+ ([Install Docker](https://docs.docker.com/get-docker/))
- **Docker Compose** 1.29+ ([Install Docker Compose](https://docs.docker.com/compose/install/))
- **Linux/macOS/Windows** (with WSL2 for Windows)
- **4GB+ RAM** (8GB+ recommended)
- **10GB+ disk space**

### Optional
- **SSL Certificates** (Let's Encrypt or commercial CA)
- **Domain name** (for production deployment)
- **Certbot** (for Let's Encrypt certificates)

### System Requirements
| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 2 cores | 4+ cores |
| RAM | 4GB | 8GB+ |
| Disk | 10GB | 20GB+ |
| Network | 10 Mbps | 100 Mbps+ |

---

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone <repository-url>
cd test_case_api
```

### 2. Deploy (Automated)
```bash
cd deployment
chmod +x deploy.sh
./deploy.sh
```

Follow the prompts to select development or production mode.

### 3. Access Application
- **Development**: http://localhost/admin
- **Production**: https://yourdomain.com/client

---

## 💻 Development Deployment

### Overview
Development mode enables the admin interface for testing and configuration.

### Step-by-Step Setup

#### 1. Navigate to Deployment Directory
```bash
cd test_case_api/deployment
```

#### 2. Create Development Environment File
```bash
cp .env.development .env
```

Edit `.env` if needed:
```env
ENVIRONMENT=development
HOST=0.0.0.0
PORT=5000
FLASK_DEBUG=true
DEBUG_MODE=true
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama3:latest
```

#### 3. Start Services
```bash
docker-compose up -d
```

#### 4. Pull Ollama Model
```bash
docker exec test-case-ollama ollama pull llama3:latest
```

#### 5. Verify Deployment
```bash
# Check service status
docker-compose ps

# Check API health
curl http://localhost/health

# View logs
docker-compose logs -f
```

#### 6. Access Interfaces
- **Admin Dashboard**: http://localhost/admin
- **Client Interface**: http://localhost/client
- **API**: http://localhost/api/

### Development Features
✅ Admin interface enabled  
✅ Debug logging  
✅ Hot reload (not in Docker)  
✅ All endpoints accessible  
✅ Detailed error messages  

---

## 🏭 Production Deployment

### Overview
Production mode disables admin interface and enables security features.

### Step-by-Step Setup

#### 1. Prepare Server
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker & Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 2. Clone and Configure
```bash
git clone <repository-url>
cd test_case_api/deployment

# Create production environment file
cp .env.production .env
nano .env  # Edit configuration
```

Production `.env` example:
```env
ENVIRONMENT=production
HOST=0.0.0.0
PORT=5000
FLASK_DEBUG=false
DEBUG_MODE=false
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama3:latest
OLLAMA_TIMEOUT=180
MAX_FILE_SIZE_MB=10
LOG_LEVEL=INFO
```

#### 3. Setup SSL Certificates

**Option A: Let's Encrypt (Recommended)**
```bash
chmod +x setup-ssl.sh
./setup-ssl.sh
# Select option 2 and follow prompts
```

**Option B: Self-Signed (Testing Only)**
```bash
./setup-ssl.sh
# Select option 1
```

**Option C: Existing Certificates**
```bash
mkdir -p nginx/ssl
cp /path/to/cert.pem nginx/ssl/cert.pem
cp /path/to/key.pem nginx/ssl/key.pem
chmod 600 nginx/ssl/key.pem
```

#### 4. Deploy Application
```bash
chmod +x deploy.sh
./deploy.sh
# Select option 2 (Production)
```

#### 5. Configure Firewall
```bash
# Allow HTTPS
sudo ufw allow 443/tcp
sudo ufw allow 80/tcp  # For Let's Encrypt renewal
sudo ufw enable
```

#### 6. Verify Production Deployment
```bash
# Check services
docker-compose ps

# Check health
curl -k https://localhost/health

# Test client interface
curl -k https://localhost/client
```

#### 7. Configure Domain (Optional)
Update your DNS to point to your server:
```
A    yourdomain.com    -> YOUR_SERVER_IP
```

Update nginx config with your domain:
```bash
nano nginx/conf.d/default.conf
# Replace server_name _ with server_name yourdomain.com
docker-compose restart nginx
```

### Production Features
✅ Admin interface blocked  
✅ SSL/TLS encryption  
✅ Rate limiting enabled  
✅ Security headers  
✅ Production logging  
✅ Health monitoring  

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ENVIRONMENT` | deployment mode (development/production) | development | Yes |
| `HOST` | Flask host | 0.0.0.0 | Yes |
| `PORT` | Flask port | 5000 | Yes |
| `FLASK_DEBUG` | Flask debug mode | false | No |
| `DEBUG_MODE` | Application debug | false | No |
| `OLLAMA_BASE_URL` | Ollama API URL | http://ollama:11434 | Yes |
| `OLLAMA_MODEL` | Default model | llama3:latest | Yes |
| `OLLAMA_TIMEOUT` | Request timeout (seconds) | 180 | No |
| `MAX_FILE_SIZE_MB` | Max upload size | 10 | No |
| `LOG_LEVEL` | Logging level | INFO | No |

### Ollama Models

#### Available Models
```bash
# List models
docker exec test-case-ollama ollama list

# Pull a model
docker exec test-case-ollama ollama pull llama3:latest
docker exec test-case-ollama ollama pull mistral
docker exec test-case-ollama ollama pull codellama
```

#### Recommended Models
| Model | Size | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| llama3:latest | 4.7GB | Medium | Good | General purpose |
| mistral | 4.1GB | Fast | Medium | Quick generation |
| codellama | 3.8GB | Fast | Good | Technical specs |
| dolphin-mixtral | 26GB | Slow | Excellent | High quality |

### Nginx Configuration

Rate limiting (edit `nginx/nginx.conf`):
```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
```

Adjust as needed:
- `rate=10r/s`: 10 requests per second
- `burst=20`: Allow bursts up to 20 requests

### Docker Resources

Edit `docker-compose.yml` to set resource limits:
```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          memory: 2G
```

---

## 🔒 Security

### Built-in Security Features

#### 1. Environment-Based Access Control
- Admin interface only in development
- Production blocks `/admin` endpoint
- Environment variable validation

#### 2. SSL/TLS Encryption
- HTTPS enforced in production
- TLS 1.2 and 1.3 only
- Strong cipher suites
- HTTP to HTTPS redirect

#### 3. Security Headers
```
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000
Content-Security-Policy: default-src 'self'
```

#### 4. Rate Limiting
- 10 requests/second per IP
- Burst capacity: 20 requests
- 429 status code on limit

#### 5. Network Isolation
- Docker bridge network
- Services not exposed directly
- Only Nginx port open

### Additional Security Recommendations

#### 1. Use Strong SSL Certificates
```bash
# Let's Encrypt (Free, automated)
certbot certonly --standalone -d yourdomain.com

# Or purchase commercial certificate
```

#### 2. Enable Firewall
```bash
# Ubuntu/Debian
sudo ufw enable
sudo ufw allow 443/tcp
sudo ufw allow 80/tcp
sudo ufw default deny incoming
```

#### 3. Regular Updates
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Update Docker images
cd deployment
docker-compose pull
docker-compose up -d
```

#### 4. Monitor Logs
```bash
# API logs
docker-compose logs -f api

# Nginx logs
docker-compose logs -f nginx

# Access logs
tail -f deployment/nginx/logs/access.log
```

#### 5. Backup Configuration
```bash
# Backup environment files
cp .env .env.backup

# Backup SSL certificates
tar -czf ssl-backup.tar.gz nginx/ssl/

# Backup instructions
tar -czf instructions-backup.tar.gz ../test_case_api/instructions/
```

### Security Checklist
- [ ] SSL certificates installed and valid
- [ ] Firewall configured and enabled
- [ ] Admin interface disabled in production
- [ ] Strong passwords/secrets set
- [ ] Regular security updates scheduled
- [ ] Logs monitored regularly
- [ ] Backups configured
- [ ] Rate limiting configured
- [ ] Docker containers run as non-root
- [ ] File upload size limits set

---

## 📊 Monitoring

### Health Checks

#### API Health
```bash
curl https://yourdomain.com/health
```

Response:
```json
{
  "status": "healthy",
  "ollama": "connected",
  "timestamp": "2024-11-05T10:30:00"
}
```

#### Service Status
```bash
docker-compose ps
```

#### Container Health
```bash
docker ps --format "table {{.Names}}\t{{.Status}}"
```

### Logging

#### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f nginx
docker-compose logs -f ollama

# Last 100 lines
docker-compose logs --tail=100 api
```

#### Log Locations
- API logs: Docker stdout
- Nginx access: `deployment/nginx/logs/access.log`
- Nginx error: `deployment/nginx/logs/error.log`

### Metrics

#### Resource Usage
```bash
# Container stats
docker stats

# Disk usage
docker system df

# Image sizes
docker images
```

#### Performance Testing
```bash
# Load test with Apache Bench
ab -n 100 -c 10 https://yourdomain.com/health

# Monitor during load
watch -n 1 docker stats
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Service Won't Start
```bash
# Check logs
docker-compose logs api

# Check port conflicts
sudo netstat -tlnp | grep :5000
sudo netstat -tlnp | grep :80

# Restart services
docker-compose restart
```

#### 2. SSL Certificate Errors
```bash
# Verify certificate
openssl x509 -in nginx/ssl/cert.pem -text -noout

# Check certificate expiry
openssl x509 -in nginx/ssl/cert.pem -noout -dates

# Regenerate self-signed cert
./setup-ssl.sh
```

#### 3. Ollama Connection Failed
```bash
# Check Ollama service
docker-compose logs ollama

# Verify Ollama is running
docker exec test-case-ollama ollama list

# Restart Ollama
docker-compose restart ollama
```

#### 4. Model Not Found
```bash
# Pull the model
docker exec test-case-ollama ollama pull llama3:latest

# List available models
docker exec test-case-ollama ollama list
```

#### 5. Permission Denied
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
chmod +x deploy.sh setup-ssl.sh

# Fix SSL permissions
chmod 600 nginx/ssl/key.pem
chmod 644 nginx/ssl/cert.pem
```

#### 6. High Memory Usage
```bash
# Check container memory
docker stats

# Restart services
docker-compose restart

# Clear Docker cache
docker system prune -a
```

### Debug Mode

Enable debug logging:
```bash
# Edit .env
DEBUG_MODE=true
LOG_LEVEL=DEBUG

# Restart
docker-compose restart api
```

---

## 🔄 Maintenance

### Regular Tasks

#### Daily
- Monitor service health
- Check disk space
- Review error logs

#### Weekly
- Review access logs
- Check for Docker updates
- Backup configuration files

#### Monthly
- Update system packages
- Update Docker images
- Rotate logs
- Test backup restoration
- Review security settings

### Update Procedures

#### 1. Update Application Code
```bash
cd test_case_api
git pull origin main
cd deployment
docker-compose build --no-cache api
docker-compose up -d
```

#### 2. Update Docker Images
```bash
docker-compose pull
docker-compose up -d
```

#### 3. Update Ollama Model
```bash
docker exec test-case-ollama ollama pull llama3:latest
docker-compose restart api
```

#### 4. Renew SSL Certificate (Let's Encrypt)
```bash
sudo certbot renew
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/cert.pem
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/key.pem
docker-compose restart nginx
```

### Backup Strategy

#### What to Backup
- Environment files (`.env`)
- SSL certificates (`nginx/ssl/`)
- Custom instructions (`../test_case_api/instructions/`)
- Output files (`./output/`)
- Configuration files

#### Backup Script
```bash
#!/bin/bash
BACKUP_DIR="/backups/testcase-api"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p "$BACKUP_DIR"

# Backup configuration
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" \
    .env \
    nginx/ssl/ \
    ../test_case_api/instructions/

# Backup output
tar -czf "$BACKUP_DIR/output_$DATE.tar.gz" \
    ./output/

# Keep only last 30 days
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete
```

### Scaling Considerations

#### Horizontal Scaling
To scale the API service:
```yaml
services:
  api:
    deploy:
      replicas: 3
```

#### Load Balancing
Update nginx to load balance across replicas:
```nginx
upstream api_backend {
    server api_1:5000;
    server api_2:5000;
    server api_3:5000;
}
```

---

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Ollama Documentation](https://ollama.ai/docs)
- [Let's Encrypt](https://letsencrypt.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)

---

## 🆘 Support

For issues and questions:
1. Check this documentation
2. Review logs: `docker-compose logs -f`
3. Check GitHub issues
4. Contact support team

---

## 📝 License

This project is open source and free for commercial use. See LICENSE file for details.

---

**Version**: 1.0  
**Last Updated**: November 2024  
**Status**: Production Ready
