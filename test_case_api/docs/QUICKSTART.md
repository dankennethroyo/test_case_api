# Quick Start Guide

Get the Test Case Generator API up and running in 5 minutes.

## Prerequisites

- Python 3.8+
- Ollama installed and running on your machine
- At least one Ollama model pulled (e.g., `llama2`)

## 1. Prepare Ollama

Make sure Ollama is running with a model:

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not installed, download from https://ollama.ai
# Once installed, run:
ollama pull llama2

# Or try these faster models:
ollama pull mistral
ollama pull neural-chat
```

## 2. Setup Python Environment

```bash
cd /Users/emersonsolahd/EMR_SOLAHD/00_DCUPS/sdu_ups/01_plan/test_case_api

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## 3. Configure API (Optional)

```bash
# Copy default configuration
cp .env.example .env

# Edit if needed (most defaults work for local Ollama)
# Recommended: change OLLAMA_MODEL to "mistral" for faster generation
```

## 4. Start the API

```bash
python app.py
```

You should see:
```
 * Running on http://0.0.0.0:5000
 * Press CTRL+C to quit
```

## 5. Test the API

Open a new terminal and run:

```bash
# Check health
curl http://localhost:5000/health

# Generate a single test case
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d @samples/single_requirement.json | jq

# Or generate multiple at once
curl -X POST http://localhost:5000/generate/batch \
  -H "Content-Type: application/json" \
  -d @samples/batch_requirements.json | jq '.results[] | .data | {REQUIREMENTS_ID, Test_Case}' | head -50
```

## 6. Generate Test Cases

Choose your method:

### Method A: Single Requirement (REST)

```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "REQUIREMENTS_ID": "REQ-001-01",
    "DESCRIPTION": "The input voltage shall be sensed by the MCU with a dedicated ADC line.",
    "CATEGORY": "Functional",
    "PARAMETER_CATEGORY": "INPUT VOLTAGE"
  }' | jq '.Test_Case'
```

### Method B: Batch Processing (JSON Body)

```bash
curl -X POST http://localhost:5000/generate/batch \
  -H "Content-Type: application/json" \
  -d @samples/batch_requirements.json > results.json

# View results
cat results.json | jq '.successful'
```

### Method C: File Upload

```bash
curl -X POST http://localhost:5000/generate/file \
  -F "file=@samples/batch_requirements.json" > results.json
```

## 7. Save Generated Test Cases

```bash
# Save batch results to file with test cases
cat results.json | jq '.results[].data' > test_cases_with_content.json

# Extract test cases only
cat results.json | jq '.results[] | select(.status=="success") | .data | {REQUIREMENTS_ID, Test_Case}' > test_cases_only.json
```

## 8. Customize Test Case Generation

Modify the system instructions to improve output quality:

```bash
# View current instructions
curl http://localhost:5000/instructions | jq '.instructions'

# Update instructions
curl -X POST http://localhost:5000/instructions \
  -H "Content-Type: application/json" \
  -d '{
    "instructions": "Generate detailed black-box test cases for embedded UPS systems focusing on power transitions, voltage sensing, and fault conditions..."
  }'
```

## Useful Commands

```bash
# List available models
curl http://localhost:5000/models | jq

# Generate with specific model
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "REQUIREMENTS_ID": "REQ-001-01",
    "DESCRIPTION": "...",
    "CATEGORY": "Functional",
    "model": "mistral"
  }' | jq

# Process file with custom model
curl -X POST http://localhost:5000/generate/file \
  -F "file=@requirements.json" \
  -F "model=neural-chat" | jq

# Pretty print batch results
curl -X POST http://localhost:5000/generate/batch \
  -H "Content-Type: application/json" \
  -d @samples/batch_requirements.json | jq '.results[] | {id: .data.REQUIREMENTS_ID, status: .status}'
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Connection refused | Verify Ollama running: `curl http://localhost:11434/api/tags` |
| Model not found | List models: `curl http://localhost:5000/models` and pull: `ollama pull llama2` |
| Timeout errors | Increase `OLLAMA_TIMEOUT` in `.env` (default 180s) or use faster model |
| Slow generation | Switch to `mistral` or `neural-chat` in `.env` (faster than `llama2`) |
| Poor quality | Update system instructions via `POST /instructions` |

## Next Steps

1. **Explore Endpoints**: Read full API documentation in `README.md`
2. **Customize Instructions**: Edit `instructions/system_instructions.md` or use the API endpoint
3. **Batch Processing**: Use `samples/batch_requirements.json` as a template
4. **Integrate**: Use the API endpoints in your test management workflow

## Performance Tips

- **Single requirement**: ~5-15 seconds (with mistral)
- **Batch of 5**: ~25-75 seconds
- **Faster results**: Use `mistral` model (change in `.env`)
- **Better quality**: Use `dolphin-mixtral` (slower but more detailed)
- **Concurrent requests**: Handled by Flask but Ollama processes sequentially

---

For detailed documentation, see `README.md`
