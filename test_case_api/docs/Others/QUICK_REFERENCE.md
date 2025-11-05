# Test Case API - Quick Reference Guide

## 🚀 Quick Commands

### Start Application
```bash
cd deployment
./deploy.sh
# Select 1 for Development or 2 for Production
```

### Access Interfaces
- **Admin (Dev)**: http://localhost/admin
- **Client**: http://localhost/client or https://yourdomain.com/client
- **API**: http://localhost/api/ or https://yourdomain.com/api/

### Manage Services
```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart

# Logs
docker-compose logs -f

# Status
docker-compose ps
```

### Ollama Commands
```bash
# List models
docker exec test-case-ollama ollama list

# Pull model
docker exec test-case-ollama ollama pull llama3:latest

# Remove model
docker exec test-case-ollama ollama rm model-name
```

## 📁 File Structure

```
test_case_api/
├── test_case_api/
│   ├── app.py                  # Main API (Modified for GUIs)
│   ├── admin_gui/              # NEW: Development admin interface
│   │   ├── index.html
│   │   ├── styles.css
│   │   └── admin.js
│   ├── public_gui/             # NEW: Production client interface
│   │   ├── index.html
│   │   ├── styles.css
│   │   └── client.js
│   └── instructions/           # AI system prompts
│
└── deployment/                 # NEW: Production deployment
    ├── Dockerfile              # Container definition
    ├── docker-compose.yml      # Service orchestration
    ├── deploy.sh               # Deployment script
    ├── setup-ssl.sh            # SSL setup script
    ├── .env.development        # Dev configuration
    ├── .env.production         # Prod configuration
    ├── nginx/                  # Reverse proxy
    │   ├── nginx.conf
    │   └── conf.d/default.conf
    └── DEPLOYMENT_GUIDE.md     # Full documentation
```

## 🔑 Key Features

### Development Mode
- ✅ Admin interface at `/admin`
- ✅ Debug logging enabled
- ✅ All endpoints accessible
- ✅ System monitoring
- ✅ Model management

### Production Mode
- ✅ Client interface at `/client`
- ✅ Admin interface blocked
- ✅ SSL/TLS encryption
- ✅ Rate limiting (10 req/s)
- ✅ Security headers
- ✅ Production logging

## 🔧 Configuration

### Environment Variables
```env
# Development
ENVIRONMENT=development
FLASK_DEBUG=true
DEBUG_MODE=true

# Production
ENVIRONMENT=production
FLASK_DEBUG=false
DEBUG_MODE=false

# Common
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama3:latest
OLLAMA_TIMEOUT=180
MAX_FILE_SIZE_MB=10
```

### Change Configuration
1. Edit `.env` file in deployment directory
2. Restart services: `docker-compose restart`

## 🔐 SSL Setup

### Let's Encrypt (Production)
```bash
cd deployment
./setup-ssl.sh
# Select option 2
# Enter domain and email
```

### Self-Signed (Testing)
```bash
cd deployment
./setup-ssl.sh
# Select option 1
```

## 🐛 Troubleshooting

### Check Health
```bash
curl http://localhost/health
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f nginx
docker-compose logs -f ollama
```

### Common Fixes
```bash
# Restart services
docker-compose restart

# Rebuild containers
docker-compose build --no-cache
docker-compose up -d

# Clear Docker cache
docker system prune -a

# Fix permissions
chmod +x deploy.sh setup-ssl.sh
chmod 600 nginx/ssl/key.pem
```

### Admin Interface Not Available
Check environment:
```bash
grep ENVIRONMENT deployment/.env
# Should show: ENVIRONMENT=development
```

### Ollama Model Not Found
```bash
# Pull model
docker exec test-case-ollama ollama pull llama3:latest

# Verify
docker exec test-case-ollama ollama list
```

## 📊 Monitoring

### Resource Usage
```bash
docker stats
```

### Service Health
```bash
docker-compose ps
```

### Disk Usage
```bash
docker system df
```

## 🔄 Updates

### Update Application
```bash
git pull origin main
cd deployment
docker-compose build --no-cache
docker-compose up -d
```

### Update Models
```bash
docker exec test-case-ollama ollama pull llama3:latest
docker-compose restart api
```

### Renew SSL (Let's Encrypt)
```bash
sudo certbot renew
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem deployment/nginx/ssl/cert.pem
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem deployment/nginx/ssl/key.pem
docker-compose restart nginx
```

## 📝 API Endpoints

### Public Endpoints
- `GET /health` - Health check
- `GET /models` - List models
- `POST /generate` - Generate single test case
- `POST /generate/batch` - Batch generation
- `POST /generate/file` - File upload
- `GET /client` - Client interface
- `GET /instructions` - Get instructions
- `POST /instructions` - Update instructions

### Admin Only (Development)
- `GET /admin` - Admin dashboard
- Only accessible when `ENVIRONMENT=development`

## 🎯 Use Cases

### QA Engineer (Client Interface)
1. Go to `/client`
2. Enter requirement details
3. Click "Generate Test Case"
4. Download results

### Developer (Admin Interface)
1. Set `ENVIRONMENT=development`
2. Go to `/admin`
3. Monitor system
4. Manage models
5. Edit instructions

### Production Deployment
1. Set `ENVIRONMENT=production`
2. Setup SSL certificates
3. Run `./deploy.sh`
4. Configure firewall
5. Monitor logs

## 🆘 Support

### Documentation
- **Full Guide**: `deployment/DEPLOYMENT_GUIDE.md`
- **New Features**: `NEW_FEATURES_README.md`
- **Original**: `README.md`

### Check Logs
```bash
docker-compose logs -f
```

### Verify Configuration
```bash
cat deployment/.env
```

### Test Connections
```bash
# API health
curl http://localhost/health

# Ollama
docker exec test-case-ollama ollama list

# Nginx
docker-compose logs nginx
```

## 📚 Documentation Links

- [Complete Deployment Guide](deployment/DEPLOYMENT_GUIDE.md)
- [New Features Overview](NEW_FEATURES_README.md)
- [Original README](README.md)
- [API Specification](docs/Others/API_SPECIFICATION.md)

## 🔒 Security Checklist

- [ ] `ENVIRONMENT=production` for production
- [ ] SSL certificates installed
- [ ] Firewall configured (ports 80, 443)
- [ ] Admin interface blocked in production
- [ ] Strong passwords/secrets set
- [ ] Regular backups configured
- [ ] Logs monitored
- [ ] Updates scheduled

## 📞 Quick Support

**Issue**: Admin interface not loading  
**Fix**: Check `ENVIRONMENT=development` in `.env`

**Issue**: SSL errors  
**Fix**: Run `./setup-ssl.sh` to regenerate certificates

**Issue**: Ollama connection failed  
**Fix**: `docker exec test-case-ollama ollama pull llama3:latest`

**Issue**: Permission denied  
**Fix**: `chmod +x *.sh` and `chmod 600 nginx/ssl/key.pem`

---

**For detailed information, see [DEPLOYMENT_GUIDE.md](deployment/DEPLOYMENT_GUIDE.md)**
