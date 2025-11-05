
#####################################################################
#                       E M E R S O N   S O L A H D                 #
#                         Test Case API Server                      #
#####################################################################

"""
Test Case Generator API - Flask Application
Generates detailed system-level integration/black-box test cases using Ollama
"""


import requests, os, logging, json
from flask import Flask, request, jsonify, Response, send_from_directory
from flask_cors import CORS
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv                  # Load environment variables from .env file  

#load_dotenv()                                   # Load .env file

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app initialization
app = Flask(__name__)
CORS(app)

# ==================== Configuration ====================
OLLAMA_BASE_URL         = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
DEFAULT_MODEL           = os.getenv("OLLAMA_MODEL", "llama3:latest")
OLLAMA_TIMEOUT          = int(os.getenv("OLLAMA_TIMEOUT", "180"))
SYSTEM_INSTRUCTION_FILE = Path(__file__).parent / "instructions" / "system_instructions.md"
MAX_FILE_SIZE_MB        = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
MAX_FILE_BYTES          = MAX_FILE_SIZE_MB * 1024 * 1024
debug_mode              = os.getenv("DEBUG_MODE", False)
ENVIRONMENT             = os.getenv("ENVIRONMENT", "development")  # development or production
ADMIN_GUI_PATH          = Path(__file__).parent / "admin_gui"
PUBLIC_GUI_PATH         = Path(__file__).parent / "public_gui"

if debug_mode == True:
    print(f"          OLLAMA_BASE_URL: {OLLAMA_BASE_URL}")
    print(f".           DEFAULT_MODEL: {DEFAULT_MODEL}")
    print(f".          OLLAMA_TIMEOUT: {OLLAMA_TIMEOUT}")
    print(f".        MAX_FILE_SIZE_MB: {MAX_FILE_SIZE_MB}")  
    print(f"  SYSTEM_INSTRUCTION_FILE: {SYSTEM_INSTRUCTION_FILE}")
    print(f"Current Working Directory: {Path.cwd()}")

# Load system instructions from file
# ==================== Helper Functions ====================
def load_system_instructions() -> str:
    """Load system instructions for test case generation"""
    if SYSTEM_INSTRUCTION_FILE.exists():
        try:
            with open(SYSTEM_INSTRUCTION_FILE, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.warning(f"Failed to load system instructions: {e}")
    
    # Default instructions if file not found
    return """You are an expert QA engineer specializing in system-level integration and black-box testing.
Your task is to generate comprehensive, detailed test cases based on requirements.

Guidelines:
- Focus on system-level integration testing (black-box approach)
- Each test case should be independent and executable
- Include clear preconditions, steps, and expected results
- Test both normal operation and edge cases
- Use clear, unambiguous language
- Include data values and specific parameters
- Consider boundary conditions and error scenarios
- Test case should verify the requirement is met from end-user perspective"""

#SYSTEM prompt from the instruction file
def build_system_prompt() -> str:
    """Build the system prompt for Ollama"""
    return load_system_instructions()

    ### #generic prompt to generate test cases from requirement
    ### #this is including the actual requirement details [DESCRIPTION, CATEGORY, etc]
    ### def build_generation_prompt(requirement: Dict[str, Any]) -> str:
    ###     """Build the prompt for test case generation from a requirement"""
    ###     
    ###     prompt = """Based on the following requirement specification, generate a detailed system-level integration test case (black-box testing approach).
    ### 
    ### REQUIREMENT DETAILS:
    ### """
    ###     
    ###     # Add all requirement fields to the prompt
    ###     for key, value in requirement.items():
    ###         if key != "Test_Case" and value:
    ###             prompt += f"\n{key}: {value}"
    ###     
    ###         if debug_mode:
    ###             print(f". Added to prompt: {key}: {value}")
    ###             print(f"Current prompt state:\n{prompt}")   
    ### 
    ###     prompt += """
    ### 
    ### Please generate a comprehensive test case that includes:
    ### 1. Test Case Title: A clear, concise title
    ### 2. Objective: What this test case verifies
    ### 3. Preconditions: Any setup required before test execution
    ### 4. Test Steps: Detailed numbered steps with actions and expected results
    ### 5. Expected Result: The final expected state/output
    ### 6. Postconditions: Any cleanup or state verification after test
    ### 7. Test Data: Specific values, ranges, or parameters used
    ### 8. Edge Cases: Any edge cases or boundary conditions tested
    ### 
    ### Format the response as a clear, structured text that describes the test case in detail.
    ### Do NOT use markdown formatting or code blocks.
    ### Do NOT include any explanation or preamble - just the test case content."""
    ###
    ###    return prompt


def build_generation_prompt(requirement: Dict[str, Any]) -> str:
    """Build the prompt for test case generation from a requirement (SolaHD DC UPS B Series context)"""

    prompt = """Based on the following requirement specification, generate a detailed system-level integration test case (black-box testing approach).

PRODUCT CONTEXT:
- SolaHD SDU DC UPS “B” Series (Models: SDU1024B-EIP, SDU2024B-EIP, SDU1024B-MBUS, SDU2024B-MBUS)
- Output: 24V DC, 10A or 20A (model dependent)
- Communications: EtherNet/IP, Modbus, GUI/webserver; telemetry includes input/output voltage/current, battery voltage, SoC, SoH, temperature, event logs, alarms; remote ON/OFF; LED indicators; PC safe shutdown/restart
- Battery Management: VRLA and LiFePO4 (auto-detect/user-select), hot-swappable, external battery modules; charging stops at 28V; auto-recharge; dead battery detection (<10V); auto/manual self-test
- Protections & Thresholds: Input undervoltage (<21.6V for 10ms), input overvoltage (>29V for 10ms), battery undervoltage (<21.6V for 100ms), battery overvoltage (>28.4V for 500ms), battery dead (<10V for 100ms), output overcurrent (>150% rated for 5ms), PowerBoost (140% rated for 6s), overtemperature (shutdown/auto-recovery)
- Environmental: –15°C to +50°C (ordinary), –15°C to +40°C (hazardous), 0–95% RH, altitude ≤3000m
- QA Alignment: Requirement-driven, traceable black-box validation per SQAV; entry/exit criteria, defect management, traceability
REQUIREMENT DETAILS:
"""

    # Add all requirement fields to the prompt
    for key, value in requirement.items():
        if key != "Test_Case" and value:
            prompt += f"\n{key}: {value}"

        # Optional debug output (if you use debug_mode)
        if 'debug_mode' in globals() and debug_mode:
            print(f". Added to prompt: {key}: {value}")
            print(f"Current prompt state:\n{prompt}")

    prompt += """

Please generate a comprehensive test case that includes:
1. Test Case Title: A clear, concise title
2. Objective: What this test case verifies
3. References: Requirement ID/Title; related SRS/TRD/QA Manual sections
4. Preconditions: Any setup required before test execution (equipment, configuration, model, battery type, protocol, safety)
5. Test Steps: Detailed numbered steps with actions and expected results (use observable outputs, telemetry, indicators, logs)
6. Expected Result: The final expected state/output with specific pass/fail criteria
7. Postconditions: Any cleanup or state verification after test
8. Test Data: Specific values, ranges, or parameters used (cover both 10A/20A, VRLA/LiFePO4 if relevant)
9. Edge Cases: Any edge cases, boundary conditions, or negative scenarios tested (e.g., transient events, comms loss, hot-swap, self-test timing)
10. Observability: What to check via GUI/EtherNet/IP/Modbus, LED states, event logs, alarms, PC shutdown sequencing
11. Traceability: Requirement-to-Test mapping notes

Format the response as a clear, structured text that describes the test case in detail.
Do NOT use markdown formatting or code blocks.
Do NOT include any explanation or preamble - just the test case content."""

    return prompt

#call the ollama api to generate the test case and return the generated text 
def call_ollama_generate(prompt: str, system_prompt: str, model: str = None) -> str:
    """Call Ollama API to generate test case"""
    model = model or DEFAULT_MODEL
    
    try:
        url = f"{OLLAMA_BASE_URL}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_k": 40,
                "top_p": 0.9
            }
        }
        if debug_mode:
            print(f"Calling Ollama API with model: {model}")
            print(f"Payload: {json.dumps(payload, indent=2)}")
        logger.info(f"Calling Ollama API with model: {model}")
        response = requests.post(url, json=payload, timeout=OLLAMA_TIMEOUT)
        response.raise_for_status()
        
        data = response.json()
        generated_text = data.get("response", "").strip()
        
        if debug_mode:
            print(f"Generated text: {generated_text}")
        logger.info("Test case generated successfully")
        return generated_text
        
    except requests.exceptions.Timeout:
        raise Exception(f"Ollama API timeout after {OLLAMA_TIMEOUT} seconds")
    except requests.exceptions.ConnectionError:
        raise Exception(f"Could not connect to Ollama at {OLLAMA_BASE_URL}")
    except Exception as e:
        raise Exception(f"Ollama API error: {str(e)}")

def validate_requirement(data: Dict[str, Any]) -> bool:
    """Validate that the requirement has required fields"""
    required_fields = ["REQUIREMENTS_ID", "DESCRIPTION", "CATEGORY"]
    return all(field in data for field in required_fields)

#consolidate the prompt, call to ollama, and return the test case
#output is an array or results with test cases
def generate_test_case_for_requirement(requirement: Dict[str, Any], model: str = None) -> Dict[str, Any]:
    """Generate a test case for a single requirement"""
    
    if not validate_requirement(requirement):
        raise ValueError("Requirement missing required fields: REQUIREMENTS_ID, DESCRIPTION, CATEGORY")
    
    # Build prompts
    system_prompt       = build_system_prompt()
    generation_prompt   = build_generation_prompt(requirement)
    
    # Generate test case using Ollama
    test_case_content = call_ollama_generate(generation_prompt, system_prompt, model)
    
    # Create output with test case
    output = requirement.copy()
    output["Test_Case"] = test_case_content
    output["Generated_At"] = datetime.now().isoformat()
    
    return output


# ==================== API Endpoints ====================

# ==================== GUI Routes ====================
@app.route('/admin')
def admin_dashboard():
    """Serve admin dashboard - only in development mode"""
    if ENVIRONMENT.lower() != "development":
        return jsonify({"error": "Admin interface not available in production"}), 403
    return send_from_directory(ADMIN_GUI_PATH, 'index.html')

@app.route('/admin/<path:filename>')
def admin_static(filename):
    """Serve admin static files - only in development mode"""
    if ENVIRONMENT.lower() != "development":
        return jsonify({"error": "Admin interface not available in production"}), 403
    return send_from_directory(ADMIN_GUI_PATH, filename)

@app.route('/client')
def client_interface():
    """Serve public client interface"""
    return send_from_directory(PUBLIC_GUI_PATH, 'index.html')

@app.route('/client/<path:filename>')
def client_static(filename):
    """Serve client static files"""
    return send_from_directory(PUBLIC_GUI_PATH, filename)

# ==================== API Endpoints ====================
#just show the local OLLAMA API is active
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            return jsonify({
                "status": "healthy",
                "ollama": "connected",
                "timestamp": datetime.now().isoformat()
            }), 200
    except:
        return jsonify({
            "status": "unhealthy",
            "ollama": "disconnected",
            "timestamp": datetime.now().isoformat()
        }), 503
    
    return jsonify({
        "status": "unhealthy",
        "ollama": "disconnected",
        "timestamp": datetime.now().isoformat()
    }), 503

#list all the models of ollama available on the system server
@app.route('/models', methods=['GET'])
def list_models():
    """List available Ollama models"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=10)
        response.raise_for_status()
        data = response.json()
        models = [model['name'] for model in data.get('models', [])]
        return jsonify({
            "models": models,
            "default_model": DEFAULT_MODEL
        }), 200
    except Exception as e:
        return jsonify({
            "error": str(e),
            "default_model": DEFAULT_MODEL
        }), 503

#create an automatic route to home page as a list of available models
@app.route('/', methods=['GET'])
def home():
    """Home page"""

    #get list of models from ollama
    response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=10)
    data = response.json()
    models = [model['name'] for model in data.get('models', [])]

    return jsonify({
        "message": "Welcome to the Test Case API",
        "available_routes": [
            {"route": "/health", "method": "GET"},
            {"route": "/models", "method": "GET"},
            {"route": "/generate", "method": "POST"},
            {"route": "/generate/batch", "method": "POST"},
            {"route": f"/{models}", "method": "GET"},
        ],
    }), 200

@app.route('/generate', methods=['POST'])
def generate_single():
    """
    Generate test case for a single requirement
    
    Expected JSON body:
    {
        "PARAMETER_CATEGORY": "...",
        "PARENT_ID": "...",
        "REQUIREMENTS_ID": "...",
        "DESCRIPTION": "...",
        "CATEGORY": "...",
        "VERIFICATION_PLAN": "...",
        "VALIDATION_CRITERIA": "...",
        "Test_Case": "",
        "model": "optional-model-name"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON body provided"}), 400
        
        # Extract optional model parameter
        model = data.pop("model", None)
        
        # Validate requirement
        if not validate_requirement(data):
            return jsonify({
                "error": "Requirement missing required fields",
                "required": ["REQUIREMENTS_ID", "DESCRIPTION", "CATEGORY"]
            }), 400
        
        # Generate test case
        result = generate_test_case_for_requirement(data, model)
        
        return jsonify(result), 200
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error generating test case: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/generate/batch', methods=['POST'])
def generate_batch():
    """
    Generate test cases for multiple requirements
    
    Expected JSON body:
    {
        "requirements": [
            {requirement object 1},
            {requirement object 2},
            ...
        ],
        "model": "optional-model-name"
    }
    """
    try:
        data = request.get_json()
        
        if not data or "requirements" not in data:
            return jsonify({"error": "No 'requirements' array in JSON body"}), 400
        
        requirements = data.get("requirements", [])
        model = data.get("model", None)
        
        if not isinstance(requirements, list):
            return jsonify({"error": "'requirements' must be an array"}), 400
        
        if len(requirements) == 0:
            return jsonify({"error": "requirements array is empty"}), 400
        
        # Generate test cases for each requirement
        results = []
        errors = []
        
        for idx, requirement in enumerate(requirements):
            try:
                result = generate_test_case_for_requirement(requirement, model)
                results.append({
                    "index": idx,
                    "status": "success",
                    "data": result
                })
            except Exception as e:
                logger.error(f"Error processing requirement {idx}: {e}")
                errors.append({
                    "index": idx,
                    "status": "failed",
                    "error": str(e)
                })
        
        return jsonify({
            "total": len(requirements),
            "successful": len(results),
            "failed": len(errors),
            "results": results,
            "errors": errors
        }), 200 if len(errors) == 0 else 207
        
    except Exception as e:
        logger.error(f"Error in batch generation: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/generate/stream', methods=['POST'])
def generate_stream():
    """
    Generate test cases with streaming response (Server-Sent Events)
    
    Expected JSON body:
    {
        "requirements": [
            {requirement object 1},
            {requirement object 2},
            ...
        ],
        "model": "optional-model-name"
    }
    """
    
    # Get request data before the generator function
    try:
        data = request.get_json()
        
        if not data or "requirements" not in data:
            return Response(
                f"data: {json.dumps({'error': 'No requirements array in JSON body'})}\n\n",
                mimetype='text/event-stream'
            )
        
        requirements = data.get("requirements", [])
        model = data.get("model", None)
        
        if not isinstance(requirements, list):
            return Response(
                f"data: {json.dumps({'error': 'requirements must be an array'})}\n\n",
                mimetype='text/event-stream'
            )
        
        if len(requirements) == 0:
            return Response(
                f"data: {json.dumps({'error': 'requirements array is empty'})}\n\n",
                mimetype='text/event-stream'
            )
    except Exception as e:
        return Response(
            f"data: {json.dumps({'error': str(e)})}\n\n",
            mimetype='text/event-stream'
        )

    def generate_events():
        try:
            # Send initial status
            yield f"data: {json.dumps({'type': 'start', 'total': len(requirements)})}\n\n"
            
            successful = 0
            failed = 0
            
            for idx, requirement in enumerate(requirements):
                req_id = requirement.get("REQUIREMENTS_ID", f"index_{idx}")
                
                try:
                    # Send progress update
                    yield f"data: {json.dumps({'type': 'progress', 'index': idx, 'requirement_id': req_id, 'status': 'processing'})}\n\n"
                    
                    # Generate test case
                    result = generate_test_case_for_requirement(requirement, model)
                    successful += 1
                    
                    # Send result
                    yield f"data: {json.dumps({'type': 'result', 'index': idx, 'status': 'success', 'data': result})}\n\n"
                    
                except Exception as e:
                    failed += 1
                    error_result = {
                        'type': 'result',
                        'index': idx,
                        'status': 'failed',
                        'requirement_id': req_id,
                        'error': str(e)
                    }
                    yield f"data: {json.dumps(error_result)}\n\n"
            
            # Send completion status
            yield f"data: {json.dumps({'type': 'complete', 'total': len(requirements), 'successful': successful, 'failed': failed})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
    
    return Response(
        generate_events(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Cache-Control'
        }
    )

@app.route('/generate/file', methods=['POST'])
def generate_from_file():
    logger.info("Received request to /generate/file endpoint")
    
    if debug_mode:
        print("Received request to /generate/file")
        print(f"Request data: {request.form.to_dict()}")
        print(f"Request files: {request.files.to_dict()}")
        print(f"Request args: {request.args.to_dict()}")
        print(f"Request headers: {request.headers.to_dict()}")

    """
    Generate test cases from an uploaded JSON file
    
    The file should contain either:
    1. A single requirement object
    2. An array of requirement objects
    3. An object with a "requirements" key containing an array
    """
    try:
        if 'file' not in request.files:
            logger.warning("File upload request missing 'file' part")
            return jsonify({"error": "No file part in request"}), 400
        
        file = request.files['file']
        model = request.form.get('model', None)

        logger.info(f"Processing file upload: {file.filename}, model: {model or 'default'}")

        if debug_mode:
            print(f"Using model: {model}")
            print(f"Uploaded file name: {file.filename}")
         # Check if a file was selected
        
        if file.filename == '':
            logger.warning("Empty filename in file upload")
            return jsonify({"error": "No selected file"}), 400
        
        if not file.filename.endswith('.json'):
            logger.warning(f"Invalid file type uploaded: {file.filename}")
            return jsonify({"error": "File must be a JSON file"}), 400
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        logger.info(f"File size: {file_size} bytes")
        if file_size > MAX_FILE_BYTES:
            logger.warning(f"File too large: {file_size} bytes (max: {MAX_FILE_BYTES})")
            return jsonify({
                "error": f"File too large (max {MAX_FILE_SIZE_MB}MB)"
            }), 413
        
        file.seek(0)
        
        # Read and parse JSON
        try:
            content = file.read().decode('utf-8')
            file_data = json.loads(content)
            logger.info("Successfully parsed JSON file")
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            return jsonify({"error": f"Invalid JSON file: {str(e)}"}), 400
        
        # Handle different JSON structures
        requirements = []
        
        if isinstance(file_data, list):
            requirements = file_data
            logger.info(f"Found {len(requirements)} requirements in array format")
        elif isinstance(file_data, dict):
            if "requirements" in file_data:
                requirements = file_data["requirements"]
                if not isinstance(requirements, list):
                    logger.error("'requirements' field is not an array")
                    return jsonify({
                        "error": "'requirements' field must be an array"
                    }), 400
                logger.info(f"Found {len(requirements)} requirements in object.requirements format")
            else:
                # Single requirement object
                requirements = [file_data]
                logger.info("Found single requirement object")
        else:
            logger.error("JSON file is neither array nor object")
            return jsonify({"error": "JSON must be an object or array"}), 400
        
        if len(requirements) == 0:
            logger.warning("No requirements found in uploaded file")
            return jsonify({"error": "No requirements found in file"}), 400
        
        # Generate test cases
        results = []
        errors = []

        logger.info(f"Starting test case generation for {len(requirements)} requirements")
        
        if debug_mode:
            print(f"Processing {len(requirements)} requirements from file")
        
        for idx, requirement in enumerate(requirements):
            req_id = requirement.get('REQUIREMENTS_ID', f'index_{idx}')
            logger.info(f"Processing requirement {idx}: {req_id}")
            
            if debug_mode:
                print(f"Processing requirement {idx}: {requirement.get('REQUIREMENTS_ID', 'N/A')}")
            try:
                result = generate_test_case_for_requirement(requirement, model)
                logger.info(f"Successfully generated test case for requirement {idx}: {req_id}")
                
                if debug_mode:
                    print(f"Generated test case for requirement {idx}")
                    print(f"Generated test case: {result}")
                results.append({
                    "index": idx,
                    "status": "success",
                    "data": result
                })
                if debug_mode:
                    print(f"Successfully processed requirement {idx}")  

            except Exception as e:
                logger.error(f"Failed to generate test case for requirement {idx} ({req_id}): {str(e)}")
                errors.append({
                    "index": idx,
                    "status": "failed",
                    "error": str(e)
                })
        
        logger.info(f"Completed processing {len(requirements)} requirements. Success: {len(results)}, Failed: {len(errors)}")
        
        response_data = {
            "filename": file.filename,
            "total": len(requirements),
            "successful": len(results),
            "failed": len(errors),
            "results": results
        }
        
        if errors:
            response_data["errors"] = errors
        
        status_code = 200 if len(errors) == 0 else 207
        logger.info(f"Returning response with status code {status_code}")
        return jsonify(response_data), status_code
        
    except Exception as e:
        logger.error(f"Unexpected error in generate_from_file: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/generate/file/stream', methods=['POST'])
def generate_from_file_stream():
    """
    Generate test cases from an uploaded JSON file with streaming response
    """
    
    # Get request data before the generator function
    try:
        if 'file' not in request.files:
            return Response(
                f"data: {json.dumps({'type': 'error', 'error': 'No file part in request'})}\n\n",
                mimetype='text/event-stream'
            )
        
        file = request.files['file']
        model = request.form.get('model', None)
        
        if file.filename == '':
            return Response(
                f"data: {json.dumps({'type': 'error', 'error': 'No selected file'})}\n\n",
                mimetype='text/event-stream'
            )
        
        if not file.filename.endswith('.json'):
            return Response(
                f"data: {json.dumps({'type': 'error', 'error': 'File must be a JSON file'})}\n\n",
                mimetype='text/event-stream'
            )

        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        if file_size > MAX_FILE_BYTES:
            return Response(
                f"data: {json.dumps({'type': 'error', 'error': f'File too large (max {MAX_FILE_SIZE_MB}MB)'})}\n\n",
                mimetype='text/event-stream'
            )
        
        file.seek(0)
        
        # Read and parse JSON
        try:
            content = file.read().decode('utf-8')
            file_data = json.loads(content)
        except json.JSONDecodeError as e:
            return Response(
                f"data: {json.dumps({'type': 'error', 'error': f'Invalid JSON file: {str(e)}'})}\n\n",
                mimetype='text/event-stream'
            )
        
        # Handle different JSON structures
        requirements = []
        if isinstance(file_data, list):
            requirements = file_data
        elif isinstance(file_data, dict):
            if "requirements" in file_data:
                requirements = file_data["requirements"]
                if not isinstance(requirements, list):
                    return Response(
                        f"data: {json.dumps({'type': 'error', 'error': 'requirements field must be an array'})}\n\n",
                        mimetype='text/event-stream'
                    )
            else:
                requirements = [file_data]
        else:
            return Response(
                f"data: {json.dumps({'type': 'error', 'error': 'JSON must be an object or array'})}\n\n",
                mimetype='text/event-stream'
            )
        
        if len(requirements) == 0:
            return Response(
                f"data: {json.dumps({'type': 'error', 'error': 'No requirements found in file'})}\n\n",
                mimetype='text/event-stream'
            )
        
        # Store filename for use in generator
        filename = file.filename

    except Exception as e:
        return Response(
            f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n",
            mimetype='text/event-stream'
        )

    def generate_file_events():
        try:
            # Send initial status
            yield f"data: {json.dumps({'type': 'start', 'filename': filename, 'total': len(requirements)})}\n\n"
            
            successful = 0
            failed = 0
            
            for idx, requirement in enumerate(requirements):
                req_id = requirement.get('REQUIREMENTS_ID', f'index_{idx}')
                
                try:
                    # Send progress update
                    yield f"data: {json.dumps({'type': 'progress', 'index': idx, 'requirement_id': req_id, 'status': 'processing'})}\n\n"
                    
                    # Generate test case
                    result = generate_test_case_for_requirement(requirement, model)
                    successful += 1
                    
                    # Send result
                    yield f"data: {json.dumps({'type': 'result', 'index': idx, 'status': 'success', 'data': result})}\n\n"
                    
                except Exception as e:
                    failed += 1
                    error_result = {
                        'type': 'result',
                        'index': idx,
                        'status': 'failed',
                        'requirement_id': req_id,
                        'error': str(e)
                    }
                    yield f"data: {json.dumps(error_result)}\n\n"
            
            # Send completion status
            yield f"data: {json.dumps({'type': 'complete', 'filename': filename, 'total': len(requirements), 'successful': successful, 'failed': failed})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
    
    return Response(
        generate_file_events(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Cache-Control'
        }
    )


@app.route('/instructions', methods=['GET'])
def get_instructions():
    """Get current system instructions"""
    try:
        instructions = load_system_instructions()
        return jsonify({
            "instructions": instructions,
            "file_path": str(SYSTEM_INSTRUCTION_FILE),
            "file_exists": SYSTEM_INSTRUCTION_FILE.exists()
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/instructions', methods=['POST'])
def update_instructions():
    """Update system instructions"""
    try:
        data = request.get_json()
        
        if not data or "instructions" not in data:
            return jsonify({"error": "No 'instructions' field in JSON body"}), 400
        
        instructions = data.get("instructions", "").strip()
        
        if not instructions:
            return jsonify({"error": "Instructions cannot be empty"}), 400
        
        # Create instructions directory if it doesn't exist
        SYSTEM_INSTRUCTION_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        # Write instructions to file
        with open(SYSTEM_INSTRUCTION_FILE, 'w', encoding='utf-8') as f:
            f.write(instructions)
        
        logger.info(f"System instructions updated: {SYSTEM_INSTRUCTION_FILE}")
        
        return jsonify({
            "status": "success",
            "message": "System instructions updated",
            "file_path": str(SYSTEM_INSTRUCTION_FILE)
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating instructions: {e}")
        return jsonify({"error": str(e)}), 500


# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


# ==================== Main ====================

if __name__ == '__main__':
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    port = int(os.getenv("PORT", 5000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print("🚀 Starting Test Case Generator API")
    print(f"📡 Ollama Base URL: {OLLAMA_BASE_URL}")
    print(f"🤖 Default Model: {DEFAULT_MODEL}")
    print(f"📄 System Instructions File: {SYSTEM_INSTRUCTION_FILE}")
    print(f"🌐 Server will run on http://{host}:{port}")
    
    logger.info(f"Starting Test Case Generator API")
    logger.info(f"Ollama Base URL: {OLLAMA_BASE_URL}")
    logger.info(f"Default Model: {DEFAULT_MODEL}")
    logger.info(f"System Instructions File: {SYSTEM_INSTRUCTION_FILE}")

    # Run Flask app
    app.run(host=host, port=port, debug=debug_mode)
