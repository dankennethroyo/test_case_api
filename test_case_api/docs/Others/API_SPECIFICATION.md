# API Specification

## Base URL
```
http://localhost:5000
```

## Request/Response Format
- **Content-Type**: `application/json` (for JSON endpoints)
- **Content-Type**: `multipart/form-data` (for file uploads)
- **Character Encoding**: UTF-8

---

## Endpoints

### 1. Health Check

**GET** `/health`

Check API and Ollama connectivity status.

**Response (200):**
```json
{
  "status": "healthy",
  "ollama": "connected",
  "timestamp": "2024-10-20T12:34:56.789012"
}
```

**Response (503):**
```json
{
  "status": "unhealthy",
  "ollama": "disconnected",
  "timestamp": "2024-10-20T12:34:56.789012"
}
```

---

### 2. List Models

**GET** `/models`

List all available Ollama models.

**Response (200):**
```json
{
  "models": ["llama2", "mistral", "neural-chat"],
  "default_model": "llama2"
}
```

**Response (503):**
```json
{
  "error": "Connection error message",
  "default_model": "llama2"
}
```

---

### 3. Generate Single Test Case

**POST** `/generate`

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

**Required Fields:**
- `REQUIREMENTS_ID`: Unique identifier for requirement
- `DESCRIPTION`: Requirement description
- `CATEGORY`: Requirement category (e.g., "Functional", "Performance")

**Optional Fields:**
- `PARAMETER_CATEGORY`: Functional category
- `PARENT_ID`: Parent requirement ID
- `VERIFICATION_PLAN`: How verification will be performed
- `VALIDATION_CRITERIA`: Acceptance criteria
- `model`: Override default Ollama model

**Response (200):**
```json
{
  "PARAMETER_CATEGORY": "INPUT VOLTAGE",
  "PARENT_ID": "REQ-001",
  "REQUIREMENTS_ID": "REQ-001-01",
  "DESCRIPTION": "The input voltage shall be sensed by the MCU with a dedicated ADC line.",
  "CATEGORY": "Functional",
  "VERIFICATION_PLAN": "Test (Functional)",
  "VALIDATION_CRITERIA": "Measure ADC input voltage reading vs applied voltage.",
  "Test_Case": "OBJECTIVE:\nVerify that the MCU correctly senses input voltage through a dedicated ADC line...",
  "Generated_At": "2024-10-20T12:34:56.789012"
}
```

**Response (400):**
```json
{
  "error": "Requirement missing required fields",
  "required": ["REQUIREMENTS_ID", "DESCRIPTION", "CATEGORY"]
}
```

**Response (500):**
```json
{
  "error": "Ollama API error: Connection refused"
}
```

---

### 4. Generate Batch Test Cases

**POST** `/generate/batch`

Generate test cases for multiple requirements.

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
      "DESCRIPTION": "Battery-backed 24V DC UPS shall transfer to battery within 4 milliseconds.",
      "CATEGORY": "Functional",
      "PARAMETER_CATEGORY": "POWER TRANSFER"
    }
  ],
  "model": "llama2"
}
```

**Required Fields:**
- `requirements`: Array of requirement objects (minimum 1 element)
  - Each requirement must have: `REQUIREMENTS_ID`, `DESCRIPTION`, `CATEGORY`

**Optional Fields:**
- `model`: Override default Ollama model

**Response (200):**
```json
{
  "total": 2,
  "successful": 2,
  "failed": 0,
  "results": [
    {
      "index": 0,
      "status": "success",
      "data": {
        "REQUIREMENTS_ID": "REQ-001-01",
        "DESCRIPTION": "...",
        "CATEGORY": "Functional",
        "Test_Case": "...",
        "Generated_At": "2024-10-20T12:34:56.789012"
      }
    },
    {
      "index": 1,
      "status": "success",
      "data": { ... }
    }
  ]
}
```

**Response (207 - Partial Success):**
```json
{
  "total": 2,
  "successful": 1,
  "failed": 1,
  "results": [ ... ],
  "errors": [
    {
      "index": 1,
      "status": "failed",
      "error": "Error message"
    }
  ]
}
```

**Response (400):**
```json
{
  "error": "'requirements' must be an array"
}
```

---

### 5. Generate from File

**POST** `/generate/file`

Generate test cases from an uploaded JSON file.

**Request:**
```
Content-Type: multipart/form-data

file=@requirements.json (required)
model=llama2 (optional)
```

**Supported File Formats:**

**Format 1: Array**
```json
[
  { "REQUIREMENTS_ID": "REQ-001-01", "DESCRIPTION": "...", "CATEGORY": "Functional" },
  { "REQUIREMENTS_ID": "REQ-002-01", "DESCRIPTION": "...", "CATEGORY": "Functional" }
]
```

**Format 2: Object with requirements key**
```json
{
  "requirements": [
    { "REQUIREMENTS_ID": "REQ-001-01", "DESCRIPTION": "...", "CATEGORY": "Functional" },
    { "REQUIREMENTS_ID": "REQ-002-01", "DESCRIPTION": "...", "CATEGORY": "Functional" }
  ]
}
```

**Format 3: Single requirement**
```json
{
  "REQUIREMENTS_ID": "REQ-001-01",
  "DESCRIPTION": "...",
  "CATEGORY": "Functional"
}
```

**Response (200):**
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

**Response (400):**
```json
{
  "error": "File must be a JSON file"
}
```

**Response (413):**
```json
{
  "error": "File too large (max 10MB)"
}
```

---

### 6. Get System Instructions

**GET** `/instructions`

Retrieve the current system instructions used for test case generation.

**Response (200):**
```json
{
  "instructions": "# System-Level Integration & Black-Box Test Case Generation\n\n## Role & Context\nYou are an expert QA engineer...",
  "file_path": "/path/to/instructions/system_instructions.md",
  "file_exists": true
}
```

---

### 7. Update System Instructions

**POST** `/instructions`

Update system instructions to customize test case generation.

**Request Body:**
```json
{
  "instructions": "You are an expert QA engineer specializing in embedded systems testing.\n\nGenerate detailed black-box test cases that focus on:\n- System-level integration\n- Hardware interfaces\n- Error handling\n- Edge cases"
}
```

**Response (200):**
```json
{
  "status": "success",
  "message": "System instructions updated",
  "file_path": "/path/to/instructions/system_instructions.md"
}
```

**Response (400):**
```json
{
  "error": "Instructions cannot be empty"
}
```

---

## Error Responses

### 400 Bad Request
Client error - missing or invalid fields.

```json
{
  "error": "Error description"
}
```

### 404 Not Found
Endpoint does not exist.

```json
{
  "error": "Endpoint not found"
}
```

### 413 Payload Too Large
File size exceeds limit.

```json
{
  "error": "File too large (max 10MB)"
}
```

### 500 Internal Server Error
Server error - typically Ollama connection issue.

```json
{
  "error": "Error description"
}
```

### 503 Service Unavailable
Ollama is not accessible.

```json
{
  "error": "Could not connect to Ollama at http://localhost:11434"
}
```

---

## Rate Limiting

No built-in rate limiting. Ollama processes requests sequentially.

---

## Timeout

Default timeout: 180 seconds per request. Configurable via `OLLAMA_TIMEOUT` environment variable.

---

## Authentication

No authentication required (suitable for local/internal use).

---

## CORS

Cross-Origin Resource Sharing (CORS) is enabled. All origins are allowed.

---

## Data Types

### Requirement Object

```typescript
{
  REQUIREMENTS_ID: string,        // Unique requirement ID (required)
  DESCRIPTION: string,            // Requirement description (required)
  CATEGORY: string,              // Requirement category (required)
  PARAMETER_CATEGORY?: string,   // Functional parameter category
  PARENT_ID?: string,            // Parent requirement ID
  VERIFICATION_PLAN?: string,    // Verification approach
  VALIDATION_CRITERIA?: string,  // Acceptance criteria
  Test_Case?: string,            // Generated test case (output)
  Generated_At?: string          // ISO timestamp (output)
}
```

### Generation Result Object

```typescript
{
  index: number,                 // Index in batch
  status: "success" | "failed",  // Generation status
  data?: object,                 // Requirement with Test_Case (if success)
  error?: string                 // Error message (if failed)
}
```

---

## Example cURL Commands

### Health Check
```bash
curl http://localhost:5000/health
```

### List Models
```bash
curl http://localhost:5000/models
```

### Generate Single
```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "REQUIREMENTS_ID": "REQ-001-01",
    "DESCRIPTION": "...",
    "CATEGORY": "Functional"
  }'
```

### Generate Batch
```bash
curl -X POST http://localhost:5000/generate/batch \
  -H "Content-Type: application/json" \
  -d @batch.json
```

### Upload File
```bash
curl -X POST http://localhost:5000/generate/file \
  -F "file=@requirements.json" \
  -F "model=mistral"
```

### Get Instructions
```bash
curl http://localhost:5000/instructions
```

### Update Instructions
```bash
curl -X POST http://localhost:5000/instructions \
  -H "Content-Type: application/json" \
  -d '{
    "instructions": "Your custom instructions here"
  }'
```
