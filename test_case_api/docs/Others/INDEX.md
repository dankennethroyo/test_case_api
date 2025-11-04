# Test Case Generator API - File Structure & Documentation Guide

## 📁 Complete Project Structure

```
test_case_api/
├── 📄 WELCOME.md                   ← START HERE
├── 📄 QUICKSTART.md                ← 5-minute setup guide
├── 📄 README.md                    ← Full documentation
├── 📄 API_SPECIFICATION.md         ← Detailed API reference
├── 📄 PROJECT_OVERVIEW.md          ← Project information
├── 📄 CUSTOMIZATION_GUIDE.md       ← Customize test generation
│
├── 💻 app.py                       ← Flask API server (main application)
├── 🐍 client.py                    ← Python client library for API
├── 📋 requirements.txt             ← Python dependencies
│
├── ⚙️ .env.example                 ← Environment configuration template
├── 🐳 Dockerfile                   ← Docker container definition
├── 🐳 docker-compose.yml           ← Docker Compose setup (with Ollama)
│
├── 🧪 test_api.sh                  ← Bash script to test API endpoints
│
├── 📚 instructions/
│   └── 📄 system_instructions.md   ← System prompt for test case generation (CUSTOMIZABLE)
│
└── 📦 samples/
    ├── 📄 single_requirement.json  ← Example single requirement
    └── 📄 batch_requirements.json  ← Example batch of requirements
```

---

## 📖 Documentation Map

### For Getting Started
1. **QUICKSTART.md** (5 min read)
   - Prerequisites check
   - Installation steps
   - Run first test case
   - Troubleshooting quick fixes

2. **README.md** (20 min read)
   - Full setup and configuration
   - All API endpoints with examples
   - Complete workflow examples
   - Advanced usage

### For API Integration
3. **API_SPECIFICATION.md** (Reference)
   - All endpoints documented
   - Request/response formats
   - Data types and schemas
   - cURL examples

### For Understanding the Project
4. **PROJECT_OVERVIEW.md** (15 min read)
   - Project purpose and features
   - Architecture overview
   - Installation options
   - Troubleshooting guide

### For Customization
5. **CUSTOMIZATION_GUIDE.md** (15 min read)
   - System instructions explanation
   - Customization methods
   - Domain-specific examples
   - Best practices

---

## 🚀 Quick Navigation

### "I want to..."

#### ...get started quickly
→ Read **QUICKSTART.md**

#### ...understand the full API
→ Read **API_SPECIFICATION.md**

#### ...integrate with Python
→ See examples in **README.md** and **client.py**

#### ...customize test case generation
→ Read **CUSTOMIZATION_GUIDE.md**

#### ...understand the project architecture
→ Read **PROJECT_OVERVIEW.md**

#### ...deploy with Docker
→ See Dockerfile and docker-compose.yml, read **README.md** Docker section

#### ...run API tests
→ Execute `test_api.sh` or read **API_SPECIFICATION.md**

---

## 📊 File Descriptions

### Core Application Files

| File | Purpose | Language | Size |
|------|---------|----------|------|
| `app.py` | Main Flask API server with all endpoints | Python | ~450 lines |
| `client.py` | Python client library for programmatic access | Python | ~250 lines |
| `requirements.txt` | Python package dependencies | Text | ~4 lines |

### Configuration Files

| File | Purpose |
|------|---------|
| `.env.example` | Template for environment configuration (copy to `.env` and edit) |

### Testing & Scripts

| File | Purpose | Usage |
|------|---------|-------|
| `test_api.sh` | Automated API endpoint testing | `bash test_api.sh` |

### Documentation

| File | Audience | Read Time | Key Topics |
|------|----------|-----------|-----------|
| `QUICKSTART.md` | Everyone | 5 min | Setup, first test, troubleshooting |
| `README.md` | Developers | 20 min | Full documentation, examples, workflows |
| `API_SPECIFICATION.md` | API users | Reference | All endpoints, formats, schemas |
| `PROJECT_OVERVIEW.md` | Project leads | 15 min | Architecture, features, deployment |
| `CUSTOMIZATION_GUIDE.md` | QA engineers | 15 min | Customizing test generation |

### Data & Examples

| Directory | Contents | Purpose |
|-----------|----------|---------|
| `instructions/` | `system_instructions.md` | System prompt for LLM (CUSTOMIZE THIS) |
| `samples/` | JSON examples | Reference for API input formats |

---

## 🔧 Typical Workflows

### Workflow 1: Get Started (15 minutes)

1. Read `QUICKSTART.md`
2. Run setup commands
3. Test with `samples/single_requirement.json`
4. View generated test case

### Workflow 2: Integrate API (30 minutes)

1. Read `API_SPECIFICATION.md`
2. Choose integration method (REST/Python)
3. Create sample request
4. Test with curl or Python client
5. Integrate into workflow

### Workflow 3: Customize Generation (1-2 hours)

1. Read `CUSTOMIZATION_GUIDE.md`
2. Review `instructions/system_instructions.md`
3. Identify customizations needed
4. Edit instructions file or use API endpoint
5. Test with sample requirements
6. Iterate and refine

### Workflow 4: Production Integration (1-2 hours)

1. Read `PROJECT_OVERVIEW.md` integration section
2. Read `README.md` for advanced usage
3. Setup in production environment
4. Configure `.env` for your setup
5. Test thoroughly with your requirements
6. Integrate into your test workflow

---

## 📋 Key Concepts

### System Instructions
- **Located in**: `instructions/system_instructions.md`
- **Purpose**: Guides the LLM on test case generation style and approach
- **Customizable**: Yes, via file edit or API endpoint
- **Impact**: Direct effect on test case quality and style

### Input Format
```json
{
  "REQUIREMENTS_ID": "REQ-001-01",
  "DESCRIPTION": "...",
  "CATEGORY": "Functional",
  "PARAMETER_CATEGORY": "...",
  "Test_Case": ""
}
```

### Output Format
Same as input, but with `Test_Case` field populated and `Generated_At` timestamp added.

### Generation Methods
1. **Single**: `POST /generate` with one requirement
2. **Batch**: `POST /generate/batch` with multiple requirements
3. **File Upload**: `POST /generate/file` with JSON file
4. **Python Client**: Direct Python integration

---

## 🎯 Essential Information

### Prerequisites
- Python 3.8+
- Ollama running locally
- Ollama model pulled (e.g., `ollama pull llama2`)

### Installation (Quick)
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

### First Test
```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d @samples/single_requirement.json
```

### Key Configuration
- **OLLAMA_BASE_URL**: Where Ollama runs (default: `http://localhost:11434`)
- **OLLAMA_MODEL**: Which model to use (default: `llama2`)
- **PORT**: API server port (default: `5000`)
- **MAX_FILE_SIZE_MB**: File upload limit (default: `10`)

---

## 🆘 Troubleshooting Quick Links

| Problem | Solution | Documentation |
|---------|----------|-----------------|
| Can't connect to Ollama | Check `OLLAMA_BASE_URL` in `.env` | QUICKSTART.md § 1 |
| Model not found | Pull model: `ollama pull llama2` | README.md § 2 |
| API takes too long | Use faster model or increase timeout | CUSTOMIZATION_GUIDE.md § Performance |
| Poor test quality | Update system instructions | CUSTOMIZATION_GUIDE.md § Examples |
| Docker network issues | Use `http://host.docker.internal:11434` | README.md § Docker |

---

## 📚 Reading Order Recommendations

### For Quick Setup (30 min)
1. QUICKSTART.md
2. Run commands
3. Test with curl

### For Full Understanding (1-2 hours)
1. PROJECT_OVERVIEW.md
2. README.md
3. API_SPECIFICATION.md
4. Try examples

### For Integration (2-3 hours)
1. PROJECT_OVERVIEW.md § Architecture
2. API_SPECIFICATION.md § All endpoints
3. client.py (read code)
4. README.md § Example workflows
5. Implement integration

### For Customization (1-2 hours)
1. CUSTOMIZATION_GUIDE.md (full read)
2. instructions/system_instructions.md (review)
3. Create test requirements
4. Modify instructions
5. Test and iterate

---

## 💡 Key Features

✅ **System-level integration testing** - Black-box approach
✅ **Batch processing** - Multiple requirements at once
✅ **File upload** - Bulk requirement handling
✅ **Customizable instructions** - Control test generation style
✅ **Multiple models** - Choose Ollama model
✅ **Python client** - Easy programmatic access
✅ **Docker support** - Container deployment
✅ **JSON format** - Easy integration
✅ **No authentication** - Suitable for internal use
✅ **Fast API** - REST endpoints

---

## 📞 Getting Help

1. **Setup issues**: See QUICKSTART.md troubleshooting
2. **API questions**: See API_SPECIFICATION.md
3. **Custom test cases**: See CUSTOMIZATION_GUIDE.md
4. **Integration questions**: See README.md examples
5. **Architecture questions**: See PROJECT_OVERVIEW.md

---

## 🔄 Typical Usage Cycle

```
1. Install & Configure
   ↓
2. Test with samples
   ↓
3. Integrate into workflow
   ↓
4. Customize instructions
   ↓
5. Generate bulk test cases
   ↓
6. Review & refine
   ↓
7. Export for use
```

---

## ✨ Next Steps

1. **Read**: Start with QUICKSTART.md
2. **Setup**: Follow installation steps
3. **Test**: Run first API call
4. **Explore**: Try batch and file endpoints
5. **Customize**: Update instructions for your domain
6. **Integrate**: Use Python client or REST API in your workflow

---

## 📝 Notes

- All JSON files use UTF-8 encoding
- API responses include timestamps (ISO format)
- Test case generation is sequential (not parallel)
- Ollama models must be pre-pulled
- System instructions affect quality significantly
- Performance depends on model and requirement complexity

---

**Welcome to Test Case Generator API!**

Start with **QUICKSTART.md** for a 5-minute setup.

For questions, refer to the documentation map above.

Good luck with your test case generation! 🚀

---

**Version**: 1.0
**Last Updated**: October 2024
**Status**: Production Ready
