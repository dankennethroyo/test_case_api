# Test Case Generator API - Project Overview

## Purpose

A Flask-based REST API that generates **detailed system-level integration and black-box test cases** from software requirements using Ollama LLM.

**Key Focus:**
- System-level integration testing (not unit testing)
- Black-box testing approach (external behavior, not implementation)
- Hardware/embedded systems testing
- Executable, detailed test cases with specific data and parameters

---

## Project Structure

```
test_case_api/
├── app.py                          # Main Flask application
├── client.py                       # Python client library
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment configuration template
├── test_api.sh                     # Bash test script
├── README.md                       # Full documentation
├── QUICKSTART.md                   # 5-minute quick start
├── API_SPECIFICATION.md            # Detailed API reference
├── PROJECT_OVERVIEW.md             # This file
├── instructions/
│   └── system_instructions.md      # System prompt for test case generation
└── samples/
    ├── single_requirement.json     # Example single requirement
    └── batch_requirements.json     # Example batch of requirements
```

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment (optional)
cp .env.example .env

# 3. Start the API
python app.py

# 4. In another terminal, test it
curl http://localhost:5000/health

# 5. Generate a test case
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d @samples/single_requirement.json
```

See `QUICKSTART.md` for detailed setup instructions.

---

## Core Features

### 1. Single Requirement Test Case Generation
Generate a test case for one requirement via REST API or Python client.

```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "REQUIREMENTS_ID": "REQ-001-01",
    "DESCRIPTION": "The input voltage shall be sensed by the MCU with a dedicated ADC line.",
    "CATEGORY": "Functional"
  }'
```

### 2. Batch Processing
Generate test cases for multiple requirements in one request.

```bash
curl -X POST http://localhost:5000/generate/batch \
  -H "Content-Type: application/json" \
  -d @batch_requirements.json
```

### 3. File Upload
Upload a JSON file containing requirements and generate test cases for all.

```bash
curl -X POST http://localhost:5000/generate/file \
  -F "file=@requirements.json"
```

### 4. Customizable Instructions
Modify system instructions without restarting the API.

```bash
# Get current instructions
curl http://localhost:5000/instructions

# Update instructions
curl -X POST http://localhost:5000/instructions \
  -H "Content-Type: application/json" \
  -d '{"instructions": "Your custom instructions"}'
```

### 5. Model Selection
Choose which Ollama model to use for generation.

```bash
# List available models
curl http://localhost:5000/models

# Generate with specific model
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "REQUIREMENTS_ID": "REQ-001-01",
    "DESCRIPTION": "...",
    "CATEGORY": "Functional",
    "model": "mistral"
  }'
```

---

## Test Case Output

Generated test cases are returned in the same JSON format as input, with the `Test_Case` field populated:

```json
{
  "REQUIREMENTS_ID": "REQ-001-01",
  "DESCRIPTION": "The input voltage shall be sensed by the MCU with a dedicated ADC line.",
  "CATEGORY": "Functional",
  "PARAMETER_CATEGORY": "INPUT VOLTAGE",
  "Test_Case": "OBJECTIVE:\nVerify that the MCU correctly senses input voltage through a dedicated ADC line.\n\nPRECONDITIONS:\n- MCU is powered on and configured\n- ADC is calibrated\n...",
  "Generated_At": "2025-10-20T12:34:56.789012"
}
```

### Test Case Structure

Each generated test case includes:
1. **Objective**: What the test verifies
2. **Preconditions**: Setup required before execution
3. **Test Steps**: Numbered actions with expected results
4. **Expected Result**: Final verification criteria
5. **Postconditions**: Cleanup or state verification
6. **Test Data**: Specific values, ranges, tolerances
7. **Edge Cases**: Boundary conditions tested

---

## System Instructions

The system instructions (in `instructions/system_instructions.md`) guide the LLM on:
- **Test approach**: System-level integration and black-box testing
- **Test specificity**: Using concrete values, measurable criteria
- **Domain focus**: Hardware/embedded systems, power systems, integration points
- **Test structure**: Clear formatting and organization
- **Quality criteria**: Independence, executability, completeness

**Customize instructions via:**
1. Edit `instructions/system_instructions.md` directly, or
2. Use API endpoint: `POST /instructions`

---

## Prerequisites

### Required
- **Python 3.8+**
- **Ollama** (https://ollama.ai)
- **Ollama model** (e.g., `ollama pull llama2`)

### Optional
- Docker (for containerized deployment)
- curl or Postman (for API testing)
- jq (for JSON formatting)

---

## Installation & Setup

### 1. Verify Ollama
```bash
# Check if running
curl http://localhost:11434/api/tags

# If needed, pull a model
ollama pull llama2
ollama pull mistral  # Recommended for faster generation
```

### 2. Setup Python Environment
```bash
cd /Users/emersonsolahd/EMR_SOLAHD/00_DCUPS/sdu_ups/01_plan/test_case_api

python3 -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure (Optional)
```bash
cp .env.example .env
# Edit .env if needed (most defaults work)
```

### 4. Run
```bash
python app.py
# API starts at http://localhost:5000
```

---

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Check API and Ollama status |
| GET | `/models` | List available Ollama models |
| POST | `/generate` | Generate test case for single requirement |
| POST | `/generate/batch` | Generate test cases for multiple requirements |
| POST | `/generate/file` | Generate from uploaded JSON file |
| GET | `/instructions` | Get current system instructions |
| POST | `/instructions` | Update system instructions |

See `API_SPECIFICATION.md` for detailed endpoint documentation.

---

## Usage Workflows

### Workflow 1: Single Requirement
```bash
# Create requirement file
echo '{
  "REQUIREMENTS_ID": "REQ-001-01",
  "DESCRIPTION": "System shall...",
  "CATEGORY": "Functional"
}' > my_req.json

# Generate test case
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d @my_req.json > test_case.json

# View result
jq '.Test_Case' test_case.json
```

### Workflow 2: Batch Processing
```bash
# Generate for multiple requirements
curl -X POST http://localhost:5000/generate/batch \
  -H "Content-Type: application/json" \
  -d @requirements.json > results.json

# Extract successful results
jq '.results[] | select(.status=="success") | .data' results.json > test_cases.json
```

### Workflow 3: File Upload
```bash
# Upload and process file
curl -X POST http://localhost:5000/generate/file \
  -F "file=@all_requirements.json" > results.json

# Count successful generations
jq '.successful' results.json
```

### Workflow 3: Python Client
```python
from client import TestCaseGeneratorClient

client = TestCaseGeneratorClient()

# Single requirement
result = client.generate({
    "REQUIREMENTS_ID": "REQ-001-01",
    "DESCRIPTION": "System shall...",
    "CATEGORY": "Functional"
})

# Batch
results = client.generate_batch(requirements_list)

# From file
results = client.generate_from_file("requirements.json")

# Save results
client.save_results(results, "output/test_cases.json")
```

---

## Configuration

### Environment Variables

```bash
# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
OLLAMA_TIMEOUT=180

# Flask
HOST=0.0.0.0
PORT=5000
FLASK_DEBUG=False

# File handling
MAX_FILE_SIZE_MB=10
```

### Model Selection

| Model | Pros | Cons |
|-------|------|------|
| `llama2` | Good quality, widely available | Slower |
| `mistral` | Fast inference | Medium quality |
| `neural-chat` | Good balance | Medium speed |
| `dolphin-mixtral` | Excellent reasoning | Slow |

**Recommendation**: Start with `mistral` for fast results, upgrade to `dolphin-mixtral` if quality needs improvement.

---

## Advanced Usage

### Using Different Ollama Models

```bash
# Generate with a specific model
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "REQUIREMENTS_ID": "REQ-001-01",
    "DESCRIPTION": "...",
    "CATEGORY": "Functional",
    "model": "mistral"
  }'
```

### Processing Large Batches

For large number of requirements (>20):

```bash
# Process in chunks
curl -X POST http://localhost:5000/generate/batch \
  -H "Content-Type: application/json" \
  -d @requirements_chunk_1.json > results_1.json

curl -X POST http://localhost:5000/generate/batch \
  -H "Content-Type: application/json" \
  -d @requirements_chunk_2.json > results_2.json

# Combine results
jq -s 'map(.results[])' results_*.json > all_results.json
```

---

## Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| Single test case | 5-30s | Depends on model and requirement complexity |
| Batch of 5 | 25-150s | Sequential processing |
| Batch of 10 | 50-300s | Sequential processing |
| Health check | <1s | Fast connectivity check |

**Tips for performance:**
- Use `mistral` model for faster generation (vs `llama2`)
- Batch processing is sequential, so plan accordingly
- Network latency affects timeout requirements

---

## Troubleshooting

### Issue: Connection refused to Ollama
**Solution:**
1. Verify Ollama running: `curl http://localhost:11434/api/tags`
2. Check `OLLAMA_BASE_URL` in `.env`
3. For Docker: use `http://host.docker.internal:11434`

### Issue: Model not found
**Solution:**
1. List available: `curl http://localhost:5000/models`
2. Pull model: `ollama pull mistral`

### Issue: Timeout
**Solution:**
1. Increase `OLLAMA_TIMEOUT` in `.env`
2. Use faster model
3. Simplify requirements

### Issue: Poor quality test cases
**Solution:**
1. Update system instructions via API or edit file
2. Try different model
3. Add more context to requirement description

---

## Testing

### Using Bash Script
```bash
chmod +x test_api.sh
./test_api.sh
```

### Using Python Client
```python
from client import TestCaseGeneratorClient

client = TestCaseGeneratorClient()
assert client.health_check(), "API not healthy"
```

### Using curl
```bash
# All endpoints
curl -I http://localhost:5000/health
curl http://localhost:5000/models
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{...}'
```

---

## Integration Examples

### With Test Management System
```python
# Export test cases to standard format
results = client.generate_batch(requirements)
for r in results:
    if r.status == "success":
        test_case = {
            "id": r.requirement_id,
            "title": f"Test {r.requirement_id}",
            "steps": r.test_case,
            "expected_results": "..."
        }
        # Import into test management system
```

### CI/CD Pipeline
```yaml
# GitHub Actions example
- name: Generate Test Cases
  run: |
    python client.py --file requirements.json --output test_cases.json
    
- name: Upload Test Cases
  run: |
    # Upload to test management system
```

---

## Files Reference

| File | Purpose |
|------|---------|
| `app.py` | Flask application and endpoints |
| `client.py` | Python client library |
| `requirements.txt` | Python dependencies |
| `.env.example` | Environment template |
| `Dockerfile` | Container image definition |
| `docker-compose.yml` | Multi-container orchestration |
| `test_api.sh` | API testing script |
| `instructions/system_instructions.md` | System prompt for LLM |
| `samples/` | Example JSON files |

---

## Security Considerations

- **No authentication**: Suitable for local/internal use only
- **CORS enabled**: All origins allowed
- **File uploads**: Limited to 10MB by default
- **Input validation**: Basic validation on required fields
- **Ollama**: Running on localhost for production safety

---

## License

See LICENSE in repository root.

---

## Support

For issues or questions:
1. Check `QUICKSTART.md` for common setup issues
2. Review `API_SPECIFICATION.md` for endpoint details
3. Check troubleshooting section above
4. Review system instructions for generation quality

---

## Version History

- **v1.0**: Initial release
  - Single and batch test case generation
  - File upload support
  - Customizable system instructions
  - Python client library
  - Docker support

---

## Future Enhancements

Potential improvements:
- [ ] Authentication and API keys
- [ ] Rate limiting
- [ ] Persistent result storage
- [ ] Test case export formats (XLS, PDF, HTML)
- [ ] Generation history tracking
- [ ] Advanced filtering and search
- [ ] WebUI dashboard
- [ ] Webhook notifications
- [ ] Multiple language support

---

**Created**: October 2025
**Status**: Active
**Maintenance**: Ongoing
