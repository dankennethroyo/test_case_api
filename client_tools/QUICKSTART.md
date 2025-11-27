# Test Case API - Client Tools

Client-side utilities for the Test Case Generator API deployed on WSL.

## 📦 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy example configuration
cp .env.example .env

# Edit .env to match your setup
# API_SERVER should point to http://localhost:8009 (Windows port forwarding to WSL)
```

### 3. Generate Test Cases

**Option A: From Existing JSON**
```bash
python client.py
# Uses settings from .env file
```

**Option B: From Excel File**
```bash
# Convert Excel to JSON
python transform_requirements.py --file your_requirements.xlsx --output

# Update .env to point to the generated JSON
# TARGET_FILE=your_requirements.json

# Generate test cases
python client.py
```

**Option C: Convert Generated Results**
```bash
# Convert JSON results to TXT/MD/CSV
python convert_results.py output/your_results.json
```

**Option D: Disable System Instructions**
```bash
# Generate test cases without system instructions
python client.py --no-instructions

# Or programmatically in your script:
from client import TestCaseGeneratorClient
client = TestCaseGeneratorClient()
result = client.generate(requirement="...", use_instructions=False)
```

## 🔧 Tools Overview

### client.py
Python API client for test case generation
- Connect to deployed API (http://localhost:8009)
- Single/batch test case generation
- Incremental saving for large batches
- Health checks and model listing

### transform_requirements.py
Excel to JSON/CSV converter
- Read requirement documents from Excel
- Extract structured data
- Export to API-compatible JSON format
- Generate CSV for review

### convert_results.py
Test case results formatter
- Convert JSON results to TXT/MD/CSV
- Parse structured test case fields
- Individual files per requirement
- Consolidated CSV with all test cases

## 📁 Package Structure

```
client_tools/
├── README.md                      # This file
├── QUICKSTART.md                  # Quick reference guide
├── requirements.txt               # Python dependencies
├── .env.example                   # Configuration template
├── client.py                      # API client
├── transform_requirements.py     # Excel transformer
├── convert_results.py            # Results converter
├── samples/                       # Sample files
│   ├── single_requirement.json
│   ├── batch_requirements.json
│   └── sample_w_model.json
├── templates/                     # Excel templates
│   └── Requirement_Template.xlsx (create your own)
└── output/                        # Generated files (auto-created)
    └── converted/                 # Converted results (auto-created)
```

## ⚙️ Configuration (.env)

```env
# API Configuration
API_SERVER=http://localhost:8009    # Windows port forwarding to WSL
OLLAMA_MODEL=phi4:14b               # AI model to use

# File Paths
TARGET_FILE=samples/batch_requirements.json
TARGET_FILE_NAME=batch_requirements.json

# Debug Mode
DEBUG_MODE=False
```

## 🧠 System Instructions Control

The API uses system instructions to guide the AI model for better test case generation. You can control this behavior:

### Command Line
```bash
# Use system instructions (default)
python client.py

# Disable system instructions
python client.py --no-instructions
```

### Programmatic API
```python
from client import TestCaseGeneratorClient

client = TestCaseGeneratorClient()

# With system instructions (default)
result = client.generate(requirement="...", use_instructions=True)

# Without system instructions
result = client.generate(requirement="...", use_instructions=False)
```

### Environment Variable
Set `USE_SYSTEM_INSTRUCTIONS=false` in your environment to disable by default.

**Note**: Using system instructions is recommended for consistent, high-quality test case generation.

## 📊 Excel Template Format

Your Excel file should have these columns:

| Column | Required | Description |
|--------|----------|-------------|
| PARAMETER_CATEGORY | No | Parameter grouping |
| PARENT_ID | No | Parent requirement ID |
| REQUIREMENTS_ID | Yes | Unique requirement ID |
| DESCRIPTION | Yes | Requirement description |
| CATEGORY | Yes | Category (Functional, Performance, etc.) |
| VERIFICATION_PLAN | No | How to verify |
| VALIDATION_CRITERIA | No | Validation criteria |
| Test_Case | No | Generated test case (output) |

## 🎯 Common Workflows

### Workflow 1: Excel → Test Cases → Formatted Output
```bash
# Step 1: Convert Excel to JSON
python transform_requirements.py --file requirements.xlsx --output

# Step 2: Generate test cases
# Edit .env: TARGET_FILE=requirements.json
python client.py

# Step 3: Convert results to readable formats
python convert_results.py output/requirements_phi414b.json
```

### Workflow 2: Direct JSON → Test Cases
```bash
# Step 1: Edit samples/batch_requirements.json with your data

# Step 2: Generate test cases
# Edit .env: TARGET_FILE=samples/batch_requirements.json
python client.py

# Step 3: View results in output/ directory
```

### Workflow 3: API Health Check
```bash
# Check if API is accessible
python -c "from client import TestCaseGeneratorClient; c = TestCaseGeneratorClient(); print('API OK' if c.health_check() else 'API DOWN')"
```

## 🔍 Troubleshooting

### API Connection Error
```bash
# Verify WSL deployment is running
# In WSL: sudo systemctl status test-case-api

# Check Windows port forwarding
netsh interface portproxy show v4tov4

# Test API health
curl http://localhost:8009/health
```

### Excel Read Error
```bash
# Install Excel support
pip install openpyxl

# Check file path
ls -la *.xlsx
```

### JSON Format Error
```bash
# Validate JSON structure
python -m json.tool your_file.json
```

## 📝 API Endpoints Reference

- `GET /health` - Health check
- `GET /models` - List available models
- `GET /instructions` - Get system instructions
- `POST /instructions` - Update system instructions
- `POST /generate` - Generate single test case
- `POST /generate/batch` - Generate batch test cases

## 💡 Tips

1. **Large Batches**: Use `incremental_save=True` in client.py to save results as they're generated
2. **Model Selection**: Check available models with `client.list_models()`
3. **Debug Mode**: Set `DEBUG_MODE=True` in .env for detailed logging
4. **Excel Tips**: Remove commas from cells to avoid CSV issues
5. **Network Access**: Use your Windows IP (10.161.225.18:8009) for network clients

## 📚 See Also

- Main deployment: `regular-wsl-deployment/`
- API documentation: `test_case_api/docs/`
- Sample files: `samples/`

---

**Version**: 1.1  
**Last Updated**: 2025-01-10
