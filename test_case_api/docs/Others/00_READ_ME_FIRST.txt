╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║              🎉 TEST CASE GENERATOR API - READY TO USE! 🎉                ║
║                                                                            ║
║                         Flask + Ollama LLM                                ║
║                  System-Level Integration Black-Box Testing               ║
║                                                                            ║
║                       (Direct Python Execution)                           ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝


📍 PROJECT LOCATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

/Users/emersonsolahd/EMR_SOLAHD/00_DCUPS/sdu_ups/01_plan/test_case_api/


⚡ QUICK START (5 MINUTES)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Step 1: Install
  $ cd /Users/emersonsolahd/EMR_SOLAHD/00_DCUPS/sdu_ups/01_plan/test_case_api
  $ python3 -m venv venv
  $ source venv/bin/activate
  $ pip install -r requirements.txt

Step 2: Run
  $ python app.py

Step 3: Test (in another terminal)
  $ curl http://localhost:5000/health

Step 4: Generate
  $ curl -X POST http://localhost:5000/generate \
    -H "Content-Type: application/json" \
    -d @samples/single_requirement.json | jq '.Test_Case'

✅ DONE!


📚 DOCUMENTATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👉 START HERE:
   • START_HERE.md        - Complete setup summary (READ THIS FIRST!)
   • QUICKSTART.md        - 5-minute setup guide
   • WELCOME.md           - Overview & features

FULL DOCS:
   • README.md            - Complete documentation
   • API_SPECIFICATION.md - All endpoints
   • PROJECT_OVERVIEW.md  - Architecture

ADVANCED:
   • CUSTOMIZATION_GUIDE.md - Customize test generation
   • INDEX.md             - File navigation guide


📦 WHAT'S INCLUDED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ app.py                     - Flask REST API server
✓ client.py                  - Python client library
✓ requirements.txt           - Dependencies (4 packages)
✓ .env.example              - Configuration template
✓ test_api.sh               - Test script
✓ instructions/             - Customizable system prompt
✓ samples/                  - Example requirements
✓ 10 documentation files    - Complete guides


🎯 WHAT IT DOES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

INPUT:  Software requirements in JSON format
        {
          "REQUIREMENTS_ID": "REQ-001-01",
          "DESCRIPTION": "System shall...",
          "CATEGORY": "Functional"
        }

PROCESS: Uses Ollama LLM to understand requirement
         Generates detailed test case using system instructions
         Focuses on system-level, black-box testing approach

OUTPUT: JSON with populated Test_Case field
        {
          "REQUIREMENTS_ID": "REQ-001-01",
          "DESCRIPTION": "...",
          "Test_Case": "OBJECTIVE: ...\nPRECONDITIONS: ...\n..."
        }


🚀 KEY FEATURES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Single test case generation    - Via REST API or Python client
✅ Batch processing               - Multiple requirements at once
✅ File upload                    - Process bulk JSON files
✅ Customizable instructions      - Control test generation style
✅ Multiple Ollama models         - Speed vs quality tradeoff
✅ Python client library          - Easy programmatic access
✅ System-level focus             - Black-box testing emphasis
✅ Hardware/embedded support      - Power systems, firmware, etc.
✅ No authentication              - Perfect for internal use
✅ Production-ready               - Error handling, validation


🎯 API ENDPOINTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

GET  /health                       - Check API & Ollama status
GET  /models                       - List available models
GET  /instructions                 - Get system instructions
POST /instructions                 - Update system instructions
POST /generate                     - Single test case
POST /generate/batch               - Multiple test cases
POST /generate/file                - Upload & process file


💻 USAGE EXAMPLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Single:
  curl -X POST http://localhost:5000/generate \
    -H "Content-Type: application/json" \
    -d @samples/single_requirement.json

Batch:
  curl -X POST http://localhost:5000/generate/batch \
    -H "Content-Type: application/json" \
    -d @samples/batch_requirements.json

Upload:
  curl -X POST http://localhost:5000/generate/file \
    -F "file=@requirements.json"

Python:
  from client import TestCaseGeneratorClient
  client = TestCaseGeneratorClient()
  result = client.generate(requirement)


⚙️ CONFIGURATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

File: .env (copy from .env.example)

Key settings:
  OLLAMA_BASE_URL=http://localhost:11434
  OLLAMA_MODEL=llama2
  PORT=5000

Most defaults work for local Ollama - no changes needed!


🆘 TROUBLESHOOTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Problem: "Connection refused"
Fix:     Verify Ollama: curl http://localhost:11434/api/tags

Problem: "Model not found"
Fix:     Pull model: ollama pull llama2

Problem: "Timeout"
Fix:     Increase OLLAMA_TIMEOUT in .env or use mistral model

Problem: "Poor test quality"
Fix:     Edit instructions/system_instructions.md

See QUICKSTART.md for more troubleshooting.


🎓 LEARNING PATHS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🟢 FAST (15 min):
   1. Read QUICKSTART.md
   2. Run 4 commands
   3. Test with curl

🟡 FULL (2 hours):
   1. Read WELCOME.md
   2. Install and test
   3. Read README.md
   4. Try Python client

🔴 ADVANCED (2-3 hours):
   1. Read PROJECT_OVERVIEW.md
   2. Read CUSTOMIZATION_GUIDE.md
   3. Customize instructions
   4. Integrate into workflow


✨ WHAT CHANGED (REVISED)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

REMOVED:
  ✗ Dockerfile          (No Docker needed)
  ✗ docker-compose.yml  (Running directly with Python)

WHY:
  Direct Python execution is simpler and better for your use case.
  Easier to debug, customize, and integrate.


🌟 NEXT STEPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 👉 Read START_HERE.md (complete overview)
   OR read QUICKSTART.md (fast track)

2. Install dependencies (4 commands, 1 minute)

3. Run: python app.py

4. Test: curl http://localhost:5000/health

5. Generate: curl -X POST ... (see examples above)


🎉 YOU'RE READY!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Everything is set up and ready to go:

✓ Complete API (app.py)
✓ Python client (client.py)
✓ All dependencies (requirements.txt)
✓ Comprehensive docs (10 files)
✓ Examples (samples/)
✓ Customizable (instructions/)

👉 Start with START_HERE.md or QUICKSTART.md

Questions? Check the documentation or see INDEX.md

Good luck! 🚀

═══════════════════════════════════════════════════════════════════════════════

Version: 1.0 Revised (October 2024)
Status: Production Ready ✅
Execution: Direct Python (No Docker)
