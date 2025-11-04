# 🎯 Test Case Generator API - Welcome!

Welcome to the **Test Case Generator API** - a Flask-based REST API that generates detailed system-level integration and black-box test cases using Ollama LLM.

---

## ⚡ Get Started in 5 Minutes

### 1. Prerequisites Check
```bash
# Verify Python
python3 --version  # Should be 3.8+

# Verify Ollama is running
curl http://localhost:11434/api/tags

# If Ollama not running, install from https://ollama.ai
# Then pull a model:
ollama pull llama2
```

### 2. Install
```bash
cd /Users/emersonsolahd/EMR_SOLAHD/00_DCUPS/sdu_ups/01_plan/test_case_api

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure
```bash
# Copy default configuration
cp .env.example .env

# If using local Ollama, no changes needed
# (default OLLAMA_BASE_URL is http://localhost:11434)
```

### 4. Run
```bash
python app.py

# You should see: "Running on http://0.0.0.0:5000"
```

### 5. Test
In another terminal:
```bash
# Check API is working
curl http://localhost:5000/health

# Generate your first test case
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "REQUIREMENTS_ID": "REQ-001-01",
    "DESCRIPTION": "The input voltage shall be sensed by the MCU with a dedicated ADC line.",
    "CATEGORY": "Functional"
  }' | jq '.Test_Case'
```

✅ **Done!** You now have a working test case generator.

---

## 📚 Documentation Quick Links

| Document | Purpose | Read Time |
|----------|---------|-----------|
| **QUICKSTART.md** | Step-by-step setup guide | 5 min |
| **README.md** | Full API documentation | 20 min |
| **API_SPECIFICATION.md** | Detailed endpoint reference | Reference |
| **PROJECT_OVERVIEW.md** | Architecture and features | 15 min |
| **CUSTOMIZATION_GUIDE.md** | Customize test generation | 15 min |
| **INDEX.md** | Navigation and file guide | 10 min |

**👉 Start with QUICKSTART.md for a guided walkthrough**

---

## 🎨 What This API Does

### Input
A software requirement in JSON format:
```json
{
  "REQUIREMENTS_ID": "REQ-001-01",
  "DESCRIPTION": "The input voltage shall be sensed by the MCU with a dedicated ADC line.",
  "CATEGORY": "Functional",
  "PARAMETER_CATEGORY": "INPUT VOLTAGE",
  "VERIFICATION_PLAN": "Test (Functional)",
  "VALIDATION_CRITERIA": "Measure ADC input voltage reading vs applied voltage."
}
```

### Processing
- Uses Ollama LLM to understand the requirement
- Generates detailed, executable test case
- Focuses on system-level, black-box testing approach
- Creates concrete test steps with specific values and tolerances

### Output
The same JSON with `Test_Case` field populated:
```json
{
  "REQUIREMENTS_ID": "REQ-001-01",
  "DESCRIPTION": "...",
  "CATEGORY": "Functional",
  "Test_Case": "OBJECTIVE:\nVerify that the MCU correctly senses input voltage through a dedicated ADC line.\n\nPRECONDITIONS:\n- MCU is powered on and configured\n- ADC is calibrated\n...",
  "Generated_At": "2024-10-20T12:34:56.789012"
}
```

---

## 🚀 Key Features

✅ **Single test case generation** via REST API  
✅ **Batch processing** - generate multiple test cases at once  
✅ **File upload** - bulk processing of requirements  
✅ **Customizable system instructions** - control test case style  
✅ **Multiple Ollama models** - choose speed vs quality  
✅ **Python client library** - easy programmatic access  
✅ **Docker support** - containerized deployment  
✅ **System-level focus** - black-box testing emphasis  
✅ **Hardware integration** - supports embedded systems testing  
✅ **No authentication** - perfect for internal use  

---

## 💻 Typical Use Cases

### 1. Generate Single Test Case
```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d @my_requirement.json
```

### 2. Batch Processing Multiple Requirements
```bash
curl -X POST http://localhost:5000/generate/batch \
  -H "Content-Type: application/json" \
  -d @batch_requirements.json
```

### 3. Upload and Process File
```bash
curl -X POST http://localhost:5000/generate/file \
  -F "file=@all_requirements.json"
```

### 4. Python Integration
```python
from client import TestCaseGeneratorClient

client = TestCaseGeneratorClient()
result = client.generate({
    "REQUIREMENTS_ID": "REQ-001-01",
    "DESCRIPTION": "...",
    "CATEGORY": "Functional"
})
print(result.test_case)
```

---

## 🎯 Test Case Features

Each generated test case includes:

- **Objective** - What is being tested
- **Preconditions** - Setup and initial state
- **Test Steps** - Numbered actions with expected results
- **Expected Result** - Final verification
- **Test Data** - Specific values and parameters
- **Edge Cases** - Boundary conditions and error scenarios

Example test case structure:
```
OBJECTIVE:
Verify input voltage sensing accuracy within ±2%.

PRECONDITIONS:
- MCU powered on
- ADC calibrated
- Multimeter connected

TEST STEPS:
1. Apply 3.3V to ADC input
   Expected: ADC reads 3.24-3.36V (±2%)

2. Apply 5.0V to ADC input
   Expected: ADC reads 4.90-5.10V (±2%)

EXPECTED RESULT:
ADC accurately converts all input voltages within ±2% tolerance.

TEST DATA:
- Nominal: 3.3V, 5.0V
- Tolerance: ±2%
- Equipment: Multimeter, power supply

EDGE CASES:
- Over-voltage (5.5V when max is 5.0V)
- Zero voltage
- Rapidly changing inputs
```

---

## 🔧 System-Level Integration Testing

This API is specifically designed for:

- **Black-box testing**: Test system behavior without knowing implementation
- **System integration**: Verify component interactions
- **End-to-end verification**: Test complete workflows
- **Hardware testing**: Support for firmware, sensors, communication
- **Real-world scenarios**: Focus on measurable, executable tests

**NOT** for:
- Unit testing (test individual functions)
- Implementation testing (test internal logic)
- Code coverage analysis

---

## 📦 What's Included

```
Core Files:
- app.py                    → Flask API server
- client.py                 → Python client library
- requirements.txt          → Python dependencies

Configuration:
- .env.example             → Environment template
- Dockerfile               → Container definition
- docker-compose.yml       → Multi-container setup

Documentation:
- INDEX.md                 → File guide (you are here)
- QUICKSTART.md            → 5-minute setup
- README.md                → Full documentation
- API_SPECIFICATION.md     → API reference
- PROJECT_OVERVIEW.md      → Project info
- CUSTOMIZATION_GUIDE.md   → Customization help

Testing & Examples:
- test_api.sh              → Test script
- samples/                 → Example JSON files
- instructions/            → System prompt (customizable)
```

---

## 🎓 Learning Path

### Beginner (30 minutes)
1. Read this welcome file ✓
2. Read QUICKSTART.md
3. Install and run
4. Test with samples

### Intermediate (2 hours)
1. Read README.md (full docs)
2. Try all API endpoints
3. Review API_SPECIFICATION.md
4. Try Python client

### Advanced (2-3 hours)
1. Read PROJECT_OVERVIEW.md
2. Read CUSTOMIZATION_GUIDE.md
3. Customize system instructions
4. Integrate into workflow

---

## ❓ Common Questions

### Q: Do I need to know how Ollama works?
**A:** No, the API handles all Ollama interaction. Just have it running.

### Q: Can I use this for unit testing?
**A:** Not recommended. This is for system-level, black-box testing.

### Q: How do I improve test case quality?
**A:** Customize system instructions. See CUSTOMIZATION_GUIDE.md.

### Q: Can I use different LLM models?
**A:** Yes! You can specify any Ollama model. See API_SPECIFICATION.md.

### Q: Does it work offline?
**A:** Ollama runs locally, so yes - no cloud dependency.

### Q: Can I deploy with Docker?
**A:** Yes! See docker-compose.yml and README.md.

### Q: What if Ollama is too slow?
**A:** Use a faster model like `mistral`. Adjust `OLLAMA_MODEL` in `.env`.

### Q: Can I customize the generated test cases?
**A:** Yes! Update `instructions/system_instructions.md` or use the API endpoint.

---

## 🚨 Troubleshooting Quick Fixes

| Issue | Quick Fix |
|-------|-----------|
| Connection refused | Verify: `curl http://localhost:11434/api/tags` |
| Model not found | Pull model: `ollama pull llama2` |
| API won't start | Check port 5000 is available |
| Timeout errors | Increase `OLLAMA_TIMEOUT` in `.env` |
| Poor quality | Update system instructions |

See QUICKSTART.md for detailed troubleshooting.

---

## 📞 Getting Help

1. **Setup questions**: Read QUICKSTART.md
2. **API usage**: See API_SPECIFICATION.md
3. **Integration**: See README.md examples
4. **Customization**: See CUSTOMIZATION_GUIDE.md
5. **Architecture**: See PROJECT_OVERVIEW.md

---

## 🎯 Next Steps

Choose your path:

### 🟢 **Fast Track** (15 min)
1. Read QUICKSTART.md
2. Run setup commands
3. Test with curl
4. Start generating!

### 🟡 **Full Understanding** (2 hours)
1. Read QUICKSTART.md
2. Install and test
3. Read README.md
4. Read API_SPECIFICATION.md
5. Try Python client

### 🔴 **Advanced Integration** (2-3 hours)
1. Read PROJECT_OVERVIEW.md
2. Read CUSTOMIZATION_GUIDE.md
3. Customize instructions
4. Integrate into workflow

---

## 💡 Tips for Best Results

1. **Be specific** in requirement descriptions
2. **Include measurable criteria** (voltages, timing, tolerances)
3. **Customize instructions** for your domain
4. **Test different models** to find best quality/speed balance
5. **Review and refine** generated test cases
6. **Keep requirements focused** on single behavior
7. **Use concrete values** not generic descriptions

---

## 🎉 Ready to Start?

**👉 Read QUICKSTART.md next for a guided setup walkthrough!**

Then you'll have your first test cases in minutes.

---

## 📋 Document Roadmap

```
START HERE
    ↓
    ├→ QUICKSTART.md (5 min setup)
    │   ↓
    │   └→ Running first test case ✓
    │
    ├→ README.md (Full docs)
    │   ↓
    │   ├→ API_SPECIFICATION.md (Reference)
    │   └→ Examples and workflows
    │
    ├→ PROJECT_OVERVIEW.md (Architecture)
    │   ↓
    │   └→ Deployment options
    │
    └→ CUSTOMIZATION_GUIDE.md (Advanced)
        ↓
        └→ Improving test quality
```

---

## 🌟 Key Takeaways

✨ **Easy Setup**: 5 commands to get running  
✨ **Powerful API**: REST endpoints for all use cases  
✨ **Flexible**: Works with Python, curl, or any HTTP client  
✨ **Customizable**: Control test generation quality  
✨ **Production Ready**: Docker, scaling, error handling  
✨ **Well Documented**: 6 comprehensive guides  

---

**Welcome aboard! Let's generate some great test cases! 🚀**

---

**Next**: Read **QUICKSTART.md** for a 5-minute setup guide.

**Questions?** Check the documentation links above or see INDEX.md for navigation.

**Good luck!** 🎉

---

**Version**: 1.0 (October 2024)  
**Status**: Production Ready  
**Maintenance**: Active  
