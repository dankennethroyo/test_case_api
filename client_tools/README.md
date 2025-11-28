# Test Case API - Client Tools Package

This package contains client-side tools for working with the Test Case Generator API.

## 📦 Package Contents

### 1. **client.py** - API Client
Python client for programmatic access to the Test Case Generator API.

**Features:**
- Single test case generation
- Batch test case generation
- Generate from JSON files
- Health checks and model listing
- Incremental saving for large batches
- **System instructions control** (use instructions or let LLM decide format)

**Usage:**
```bash
python client.py [options]
```

**Command-line Options:**
```bash
--model MODEL          # Override default model
--no-instructions      # Disable system instructions (let LLM decide format)
--server URL          # Override API server URL
```

### 2. **transform_requirements.py** - Excel to JSON/CSV Converter
Converts requirement documents from Excel to JSON/CSV format for API consumption.

**Features:**
- Reads Excel requirement documents
- Extracts relevant columns
- Exports to JSON and CSV formats
- Removes commas from strings for CSV compatibility

**Usage:**
```bash
# Display preview only
python transform_requirements.py --file Requirement_Document.xlsx

# Generate output files
python transform_requirements.py --file Requirement_Document.xlsx --output
```

### 4. **selenium_tests/** - Comprehensive Web UI Testing
Selenium-based test suite for validating the deployed web interface and API functionality using pytest.

**Features:**
- Automated browser testing of the web UI using pytest framework
- Comprehensive validation of all 4 instruction conditions
- Output verification and logic testing
- HTML and JSON report generation
- Cross-platform compatibility (Chrome WebDriver)
- Parametrized tests for instruction conditions

**Setup:**
```bash
# Install dependencies (includes pytest)
pip install -r requirements.txt
```

**Usage:**
```bash
# Run all tests with pytest
pytest selenium_tests/test_selenium_pytest.py

# Or use the runner scripts
# Windows
run_selenium_tests_pytest.bat

# Linux/Mac
./run_selenium_tests_pytest.sh
```

**Test Coverage:**
- ✅ Page loading and basic functionality
- ✅ Tab navigation (Single, Batch, Instructions)
- ✅ Single requirement generation
- ✅ All 4 instruction conditions (parametrized):
  - Checked + Modified instructions
  - Checked + Unmodified instructions
  - Unchecked + Modified instructions
  - Unchecked + Unmodified instructions
- ✅ Import/Export functionality
- ✅ Result display and validation

**Reports:**
- Console output with pytest formatting
- HTML Report: `selenium_test_report.html` (self-contained)
- JSON reports can be generated with additional pytest plugins

**Configuration:**
- pytest.ini configures test discovery and HTML reporting
- Tests run in headless Chrome by default
- Timeout: 120 seconds for generation tests

### 5. **selenium_tests/run_selenium_tests.py** - Test Runner
Simple wrapper script to run the Selenium test suite with proper error handling.

**Usage:**
```bash
python selenium_tests/run_selenium_tests.py
```

## 📋 Requirements

### Python Dependencies
```bash
pip install -r requirements.txt
```

**Required packages:**
- `requests` - HTTP client for API calls
- `python-dotenv` - Environment variable management
- `pandas` - Excel/CSV processing
- `openpyxl` - Excel file reading
- `selenium` - Web browser automation
- `webdriver-manager` - Automatic WebDriver management

## 🔧 Configuration

Create a `.env` file in this directory:

```env
# API Configuration
API_SERVER=http://localhost:8009
OLLAMA_MODEL=phi4:14b

# File Paths
TARGET_FILE=samples/batch_requirements.json
TARGET_FILE_NAME=batch_requirements.json

# Debug Mode
DEBUG_MODE=False
```

## 📁 Directory Structure

```
client_tools/
├── README.md                      # This file
├── requirements.txt               # Python dependencies
├── .env.example                   # Example environment configuration
├── client.py                      # API client
├── transform_requirements.py     # Excel to JSON/CSV converter
├── convert_results.py            # Results converter
├── selenium_tests/                # Selenium test suite
│   ├── selenium_test_suite.py    # Comprehensive test suite
│   └── run_selenium_tests.py     # Test runner script
├── samples/                       # Sample requirement files
│   ├── single_requirement.json
│   ├── batch_requirements.json
│   └── sample_w_model.json
├── templates/                     # Excel templates
│   └── Requirement_Template.xlsx
└── output/                        # Generated outputs (auto-created)
    └── converted/                 # Converted results (auto-created)
```

## 🚀 Quick Start

### 1. Transform Excel to JSON
```bash
# Prepare your requirements
python transform_requirements.py --file my_requirements.xlsx --output

# This creates:
# - my_requirements.json (for API)
# - my_requirements.csv (for review)
```

### 2. Generate Test Cases
```bash
# Edit .env to point to your JSON file
# Set TARGET_FILE=my_requirements.json

# Run generation
python client.py

# Output saved to: output/my_requirements_phi414b.json
```

### 3. Convert Results
```bash
# Convert to multiple formats
python convert_results.py output/my_requirements_phi414b.json

# Creates:
# - converted/my_requirements_phi414b_TIMESTAMP/txt/*.txt
# - converted/my_requirements_phi414b_TIMESTAMP/md/*.md
# - converted/my_requirements_phi414b_TIMESTAMP/csv/*.csv
```

## 📊 Excel Template Format

Your Excel file should have these columns:

| Column | Required | Description |
|--------|----------|-------------|
| REQUIREMENTS_ID | Yes | Unique requirement identifier |
| DESCRIPTION | Yes | Requirement description |
| CATEGORY | Yes | Requirement category (Functional, Performance, etc.) |
| PARAMETER_CATEGORY | No | Parameter grouping |
| PARENT_ID | No | Parent requirement ID |
| VERIFICATION_PLAN | No | How to verify |
| VALIDATION_CRITERIA | No | Validation criteria |
| Test_Case | No | Generated test case (output) |

## 🎛️ System Instructions Control

Control whether the AI uses predefined system instructions or decides response format independently.

### Command Line
```bash
# Use system instructions (default)
python client.py

# Let LLM decide format
python client.py --no-instructions
```

### Programmatic Usage
```python
# Use system instructions (default)
result = client.generate(requirement, use_instructions=True)

# Let LLM decide format
result = client.generate(requirement, use_instructions=False)

# Batch with custom setting
results = client.generate_batch(requirements, use_instructions=False)
```

### Environment Variable
```env
# In .env file (affects default behavior)
USE_SYSTEM_INSTRUCTIONS=true  # Default: true
```

**When to use:**
- **With instructions** (default): Structured, consistent test cases
- **Without instructions**: Creative, varied responses from LLM

## 💡 Examples

### Example 1: Single Test Case
```python
from client import TestCaseGeneratorClient

client = TestCaseGeneratorClient()

requirement = {
    "REQUIREMENTS_ID": "REQ-001",
    "DESCRIPTION": "System shall validate user input",
    "CATEGORY": "Functional"
}

result = client.generate(requirement)
print(result.test_case)
```

### Example 2: Batch Generation
```python
requirements = [
    {"REQUIREMENTS_ID": "REQ-001", "DESCRIPTION": "Test 1", "CATEGORY": "Functional"},
    {"REQUIREMENTS_ID": "REQ-002", "DESCRIPTION": "Test 2", "CATEGORY": "Performance"}
]

results = client.generate_batch(requirements)
client.save_results(results, "output/batch.json")
```

### Example 3: Generate from File
```python
results = client.generate_from_file(
    "samples/batch_requirements.json",
    model="phi4:14b",
    incremental_save=True,
    output_file="output/results.json"
)
```

## 🆘 Troubleshooting

### Connection Refused
```bash
# Check API is running
curl http://localhost:8009/health

# Verify .env API_SERVER setting
cat .env | grep API_SERVER
```

### Excel File Not Found
```bash
# Check file path
ls -la *.xlsx

# Use absolute path
python transform_requirements.py --file /full/path/to/file.xlsx --output
```

### JSON Decode Error
```bash
# Validate JSON
python -m json.tool samples/batch_requirements.json
```

## 📞 Support

For issues or questions:
1. Check the API server is running: `http://localhost:8009/health`
2. Verify your `.env` configuration
3. Check the output logs for detailed error messages

---

**Happy Testing!** 🎉
