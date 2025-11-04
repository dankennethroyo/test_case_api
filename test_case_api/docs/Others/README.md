# Test Case Generator API

A Flask-based REST API for generating detailed **system-level integration and black-box test cases** using Ollama LLM.

## Overview

This API takes software requirements as input and generates comprehensive, executable test cases designed for:
- **System-level integration testing** (testing complete system behavior)
- **Black-box testing** (testing without knowledge of internal implementation)
- **End-to-end functional validation**
- **Hardware/embedded systems testing**

The generated test cases include:
- Clear objectives and preconditions
- Numbered test steps with expected results
- Specific test data and parameters
- Edge cases and boundary conditions
- Integration points and data flow verification

## Prerequisites

### Required
- **Python 3.8+**
- **Ollama** running locally (default: `http://localhost:11434`)
- **Ollama model** pulled (e.g., `ollama pull llama2`, `ollama pull mistral`, or `ollama pull neural-chat`)

### Optional
- `curl` for testing API endpoints
- `jq` for pretty-printing JSON responses

## Installation

### 1. Set Up Python Environment

```bash
cd /Users/emersonsolahd/EMR_SOLAHD/00_DCUPS/sdu_ups/01_plan/test_case_api

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
.\venv\Scripts\activate   # On Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env if needed (especially OLLAMA_BASE_URL and OLLAMA_MODEL)
# Default values are usually fine for local Ollama setup
```

### 4. Verify Ollama Installation

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, pull a model:
ollama pull llama2
# or
ollama pull mistral
```

## Starting the API

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate

# Run the Flask API server
python app.py

# The API will start at http://localhost:5000
```

You should see output like:
```
 * Running on http://0.0.0.0:5000
 * Press CTRL+C to quit
```

## API Endpoints

### 1. Health Check

**Endpoint:** `GET /health`

Check if the API and Ollama are running.

```bash
curl http://localhost:5000/health
```

**Response (healthy):**
```json
{
  "status": "healthy",
  "ollama": "connected",
  "timestamp": "2024-10-20T12:34:56.789012"
}
```

---

### 2. List Available Models

**Endpoint:** `GET /models`

List all available Ollama models.

```bash
curl http://localhost:5000/models
```

**Response:**
```json
{
  "models": ["llama2", "mistral", "neural-chat"],
  "default_model": "llama2"
}
```

---

### 3. Generate Single Test Case

**Endpoint:** `POST /generate`

Generate a test case for a single requirement.

**Request Body:**
```json
{
  "PARAMETER_CATEGORY": "INPUT VOLTAGE",
  "PARENT_ID": "REQ-001",
  "REQUIREMENTS_ID": "REQ-001-01",
  "DESCRIPTION": "The input voltage shall be sensed by the MCU with a dedicated ADC line.",
  "CATEGORY": "Functional",
  "VERIFICATION_PLAN": "Test (Functional)",
  "VALIDATION_CRITERIA": "Measure ADC input voltage reading vs applied voltage.",
  "Test_Case": "",
  "model": "llama2"
}
```

**Example with curl:**
```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "PARAMETER_CATEGORY": "INPUT VOLTAGE",
    "PARENT_ID": "REQ-001",
    "REQUIREMENTS_ID": "REQ-001-01",
    "DESCRIPTION": "The input voltage shall be sensed by the MCU with a dedicated ADC line.",
    "CATEGORY": "Functional",
    "VERIFICATION_PLAN": "Test (Functional)",
    "VALIDATION_CRITERIA": "Measure ADC input voltage reading vs applied voltage.",
    "Test_Case": ""
  }' | jq
```

**Response:**
```json
{
  "PARAMETER_CATEGORY": "INPUT VOLTAGE",
  "PARENT_ID": "REQ-001",
  "REQUIREMENTS_ID": "REQ-001-01",
  "DESCRIPTION": "The input voltage shall be sensed by the MCU with a dedicated ADC line.",
  "CATEGORY": "Functional",
  "VERIFICATION_PLAN": "Test (Functional)",
  "VALIDATION_CRITERIA": "Measure ADC input voltage reading vs applied voltage.",
  "Test_Case": "OBJECTIVE:\nVerify that the MCU correctly senses input voltage through a dedicated ADC line.\n\nPRECONDITIONS:\n- MCU is powered on and configured\n- ADC is calibrated\n- Test equipment (multimeter/function generator) is connected\n\nTEST STEPS:\n1. Apply 3.0V to the ADC input line\n   Expected: ADC reads between 2.95V and 3.05V (±1.67%)\n\n2. Apply 5.0V to the ADC input line\n   Expected: ADC reads between 4.95V and 5.05V (±1%)\n\n3. Apply 0V to the ADC input line\n   Expected: ADC reads between -0.05V and 0.05V\n\n4. Apply voltage just above maximum rated input (e.g., 5.5V if max is 5.0V)\n   Expected: ADC indicates out-of-range or saturated value\n\nEXPECTED RESULT:\nADC successfully converts input voltage to digital representation within specified tolerance for all test ranges.\n\nTEST DATA:\n- Nominal voltage: 3.0V, 5.0V\n- Minimum voltage: 0V\n- Maximum voltage: 5.0V (device limit)\n- Over-voltage test: 5.5V\n- Accuracy tolerance: ±2%",
  "Generated_At": "2024-10-20T12:34:56.789012"
}
```

---

### 4. Generate Multiple Test Cases (Batch)

**Endpoint:** `POST /generate/batch`

Generate test cases for multiple requirements in a single request.

**Request Body:**
```json
{
  "requirements": [
    {
      "REQUIREMENTS_ID": "REQ-001-01",
      "DESCRIPTION": "The input voltage shall be sensed by the MCU with a dedicated ADC line.",
      "CATEGORY": "Functional",
      "PARAMETER_CATEGORY": "INPUT VOLTAGE"
    },
    {
      "REQUIREMENTS_ID": "REQ-002-01",
      "DESCRIPTION": "The system shall detect battery disconnection within 100ms.",
      "CATEGORY": "Functional",
      "PARAMETER_CATEGORY": "POWER DETECTION"
    }
  ],
  "model": "llama2"
}
```

**Example with curl:**
```bash
curl -X POST http://localhost:5000/generate/batch \
  -H "Content-Type: application/json" \
  -d @batch_requirements.json | jq
```

**Response:**
```json
{
  "total": 2,
  "successful": 2,
  "failed": 0,
  "results": [
    {
      "index": 0,
      "status": "success",
      "data": { ... }
    },
    {
      "index": 1,
      "status": "success",
      "data": { ... }
    }
  ]
}
```

---

### 5. Generate from File

**Endpoint:** `POST /generate/file`

Generate test cases from an uploaded JSON file.

**Supported File Formats:**

**Format 1: Array of requirements**
```json
[
  { "REQUIREMENTS_ID": "REQ-001-01", ... },
  { "REQUIREMENTS_ID": "REQ-002-01", ... }
]
```

**Format 2: Object with requirements key**
```json
{
  "requirements": [
    { "REQUIREMENTS_ID": "REQ-001-01", ... },
    { "REQUIREMENTS_ID": "REQ-002-01", ... }
  ]
}
```

**Format 3: Single requirement object**
```json
{
  "REQUIREMENTS_ID": "REQ-001-01",
  "DESCRIPTION": "...",
  ...
}
```

**Example with curl:**
```bash
curl -X POST http://localhost:5000/generate/file \
  -F "file=@requirements.json" \
  -F "model=llama2" | jq
```

**Response:**
```json
{
  "filename": "requirements.json",
  "total": 2,
  "successful": 2,
  "failed": 0,
  "results": [
    {
      "index": 0,
      "status": "success",
      "data": { ... }
    },
    {
      "index": 1,
      "status": "success",
      "data": { ... }
    }
  ]
}
```

---

### 6. Get System Instructions

**Endpoint:** `GET /instructions`

Retrieve the current system instructions used for test case generation.

```bash
curl http://localhost:5000/instructions | jq
```

**Response:**
```json
{
  "instructions": "# System-Level Integration & Black-Box Test Case Generation\n\n## Role & Context\n...",
  "file_path": "/Users/emersonsolahd/EMR_SOLAHD/00_DCUPS/sdu_ups/01_plan/test_case_api/instructions/system_instructions.md",
  "file_exists": true
}
```

---

### 7. Update System Instructions

**Endpoint:** `POST /instructions`

Update the system instructions to customize test case generation behavior.

**Request Body:**
```json
{
  "instructions": "You are a QA expert. Generate test cases for embedded systems testing...\n\nGuidelines:\n- Focus on black-box testing\n- Include edge cases\n- Specify exact values and tolerances"
}
```

**Example with curl:**
```bash
curl -X POST http://localhost:5000/instructions \
  -H "Content-Type: application/json" \
  -d '{
    "instructions": "You are an expert QA engineer specializing in embedded systems black-box testing...\n..."
  }'
```

**Response:**
```json
{
  "status": "success",
  "message": "System instructions updated",
  "file_path": "/Users/emersonsolahd/EMR_SOLAHD/00_DCUPS/sdu_ups/01_plan/test_case_api/instructions/system_instructions.md"
}
```

---

## Complete Workflow Examples

### Example 1: Single Requirement to Test Case

**Step 1: Create a requirement JSON file** (`single_req.json`):
```json
{
  "PARAMETER_CATEGORY": "POWER TRANSFER",
  "PARENT_ID": "REQ-002",
  "REQUIREMENTS_ID": "REQ-002-01",
  "DESCRIPTION": "Battery-backed 24V DC UPS shall transfer to battery within 4 milliseconds of AC loss.",
  "CATEGORY": "Functional",
  "VERIFICATION_PLAN": "Test (Functional)",
  "VALIDATION_CRITERIA": "Measure time from AC loss signal to battery voltage on output.",
  "Test_Case": ""
}
```

**Step 2: Send to API**:
```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d @single_req.json > test_case_output.json

cat test_case_output.json
```

**Output:** The same file with `Test_Case` field populated with detailed test case.

---

### Example 2: Batch Processing Multiple Requirements

**Step 1: Create batch file** (`batch_reqs.json`):
```json
{
  "requirements": [
    {
      "REQUIREMENTS_ID": "REQ-001-01",
      "DESCRIPTION": "The input voltage shall be sensed by the MCU with a dedicated ADC line.",
      "CATEGORY": "Functional"
    },
    {
      "REQUIREMENTS_ID": "REQ-002-01",
      "DESCRIPTION": "Battery-backed 24V DC UPS shall transfer to battery within 4 milliseconds of AC loss.",
      "CATEGORY": "Functional"
    },
    {
      "REQUIREMENTS_ID": "REQ-003-01",
      "DESCRIPTION": "System shall detect low battery condition and initiate graceful shutdown.",
      "CATEGORY": "Functional"
    }
  ]
}
```

**Step 2: Process batch**:
```bash
curl -X POST http://localhost:5000/generate/batch \
  -H "Content-Type: application/json" \
  -d @batch_reqs.json > batch_results.json

cat batch_results.json | jq '.results | length'
```

**Output:** JSON file with results for each requirement.

---

### Example 3: Upload and Process File

```bash
curl -X POST http://localhost:5000/generate/file \
  -F "file=@requirements.json" \
  -F "model=mistral" > processed_requirements.json

# Extract only successful results
cat processed_requirements.json | jq '.results[] | select(.status=="success") | .data'
```

---

## Customizing Test Case Generation

### Modify System Instructions

The API loads system instructions from:
```
/Users/emersonsolahd/EMR_SOLAHD/00_DCUPS/sdu_ups/01_plan/test_case_api/instructions/system_instructions.md
```

**To customize test case generation:**

```bash
# Get current instructions
curl http://localhost:5000/instructions > current_instructions.json

# Edit the instructions as needed (using your preferred editor)
vim new_instructions.txt

# Update the instructions
curl -X POST http://localhost:5000/instructions \
  -H "Content-Type: application/json" \
  -d '{
    "instructions": "'$(cat new_instructions.txt)'"
  }'
```

**Instruction Tips:**
- Focus on the testing approach (black-box, integration, etc.)
- Specify required test case structure
- Include domain-specific guidelines (embedded systems, firmware, etc.)
- Mention required detail levels and edge cases

---

## Configuration

### Environment Variables

Create or edit `.env` file:

```bash
# Ollama connection
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
OLLAMA_TIMEOUT=180

# Flask server
HOST=0.0.0.0
PORT=5000
FLASK_DEBUG=False

# File handling
MAX_FILE_SIZE_MB=10
```

### Choosing the Right Model

| Model | Best For | Speed | Quality |
|-------|----------|-------|---------|
| `llama2` | General purpose | Medium | Good |
| `mistral` | Fast inference | Fast | Very Good |
| `neural-chat` | Conversational tasks | Medium | Good |
| `dolphin-mixtral` | Complex reasoning | Slow | Excellent |

For test case generation, **mistral** or **neural-chat** are recommended for faster generation without sacrificing quality.

---

## Troubleshooting

### Issue: Connection refused to Ollama

**Solution:**
1. Verify Ollama is running: `curl http://localhost:11434/api/tags`
2. Check `OLLAMA_BASE_URL` in `.env` file
3. If using Docker, update URL to: `http://host.docker.internal:11434`

### Issue: Model not found

**Solution:**
1. List available models: `curl http://localhost:5000/models`
2. Pull the desired model: `ollama pull mistral`
3. Restart the API

### Issue: Generation timeout

**Solution:**
1. Increase `OLLAMA_TIMEOUT` in `.env` (default: 180 seconds)
2. Use a faster model (mistral instead of dolphin-mixtral)
3. Reduce requirement complexity or add more specific instructions

### Issue: Poor quality test cases

**Solution:**
1. Update system instructions: `POST /instructions`
2. Add more examples or specific guidelines
3. Try a different model with better reasoning capability
4. Include more context in the requirement description

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

## API Response Format

All responses include:
- `status`: "success" or "failed"
- `data`: Generated test case (inherits all input fields + `Test_Case` field)
- `Generated_At`: ISO timestamp of generation
- Error responses include `error` field with details

---

## Performance Notes

- **Single test case generation:** ~5-30 seconds (depends on model and requirement complexity)
- **Batch processing:** Processed sequentially, total time = number of requirements × time per requirement
- **File upload:** Maximum 10MB by default (configurable)
- **Concurrent requests:** Served by Flask, but Ollama processes requests sequentially

---

## Support & Development

For issues or feature requests, refer to the workspace documentation in the root directory.

---

## License

See LICENSE file in the repository root.
