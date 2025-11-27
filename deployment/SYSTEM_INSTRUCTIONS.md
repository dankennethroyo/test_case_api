# System Instructions Control

## What It Does

Controls whether the AI uses predefined system instructions or decides response format independently.

## Usage

### Web Interface
- Open `http://localhost:5009/client`
- Check/uncheck: **"Use System Instructions (recommended)"**
- Checked = structured output (default)
- Unchecked = LLM decides format

### API
```bash
# With instructions (default)
curl -X POST http://localhost:5009/generate \
  -H "Content-Type: application/json" \
  -d '{"REQUIREMENTS_ID":"REQ-001", "DESCRIPTION":"...", "CATEGORY":"Functional"}'

# Without instructions
curl -X POST http://localhost:5009/generate \
  -H "Content-Type: application/json" \
  -d '{"REQUIREMENTS_ID":"REQ-001", "DESCRIPTION":"...", "CATEGORY":"Functional", "use_instructions":false}'
```

### Environment Variable
```bash
# In .env file
USE_SYSTEM_INSTRUCTIONS=true  # Default: true
```

## When to Use

### ✅ With Instructions (Default)
- Production test cases
- Consistent format needed
- Team collaboration

### 🔬 Without Instructions
- Creative approaches
- Model comparison
- Research

## Backward Compatible
- Default behavior unchanged
- Existing code works as-is
- New parameter is optional