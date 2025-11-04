
#####################################################################
#                       E M E R S O N   S O L A H D                 #
#                         Test Case API Server                      #
#####################################################################
"""
Test Case Generator API - Python Client
Simple client for programmatic access to the API
"""

import requests, sys, json, time, os, shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from dotenv import load_dotenv                  # Load environment variables from .env file 

#check if .env file exist in current directory
if not Path('.env').exists():
    try:
        shutil.copy('.env.example', '.env')
    except FileNotFoundError:
        print("ERROR: .env.example not found; cannot create .env")
        sys.exit(1)
    if not Path('.env').exists():
        print("ERROR: Failed to create .env file")
        sys.exit(1)

load_dotenv()

@dataclass
class GenerationResult:
    """Result of a test case generation request"""
    requirement_id: str
    status: str
    test_case: Optional[str] = None
    error: Optional[str] = None
    timestamp: Optional[str] = None

# ================== configuration ==================
debug_mode              = os.getenv("DEBUG_MODE", False)
tgt_model               = os.getenv("OLLAMA_MODEL", "llama3:latest")


# Test Case Generator Object
class TestCaseGeneratorClient:
    """Client for interacting with Test Case Generator API"""
    
    def __init__(self, base_url: str = "http://localhost:5000", timeout: int = 300):
        """
        Initialize the client
        
        Args:
            base_url: Base URL of the API (default: http://localhost:5000)
            timeout: Request timeout in seconds (default: 300)
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
    
    def health_check(self) -> bool:
        """Check if API and Ollama are healthy"""
        try:
            response = self.session.get(
                f"{self.base_url}/health",
                timeout=10
            )
            if debug_mode:
                print(f"Health check response: {response.status_code}")
            return response.status_code == 200
        except Exception as e:
            if debug_mode:
                print(f"Health check failed: {e}")
            return False
    
    def list_models(self) -> List[str]:
        """Get list of available Ollama models"""
        try:
            response = self.session.get(f"{self.base_url}/models")
            response.raise_for_status()
            data = response.json()
            models = data.get("models", [])
            if debug_mode:
                print(f"List models response: {response.status_code}, models: {models}")
            return models
        except Exception as e:
            if debug_mode:
                print(f"List models failed: {e}")
            raise
    
    def get_instructions(self) -> str:
        """Get current system instructions"""
        try:
            response = self.session.get(f"{self.base_url}/instructions")
            response.raise_for_status()
            data = response.json()
            instructions = data.get("instructions", "")
            if debug_mode:
                print(f"Get instructions response: {response.status_code}, instructions length: {len(instructions)}")
            return instructions
        except Exception as e:
            if debug_mode:
                print(f"Get instructions failed: {e}")
            raise
    
    def update_instructions(self, instructions: str) -> bool:
        """Update system instructions"""
        try:
            response = self.session.post(
                f"{self.base_url}/instructions",
                json={"instructions": instructions}
            )
            response.raise_for_status()
            success = response.status_code == 200
            if debug_mode:
                print(f"Update instructions response: {response.status_code}, success: {success}")
            return success
        except Exception as e:
            if debug_mode:
                print(f"Update instructions failed: {e}")
            raise
    
    def generate(
        self,
        requirement: Dict[str, Any],
        model: Optional[str] = None
    ) -> GenerationResult:
        """
        Generate a test case for a single requirement
        
        Args:
            requirement: Requirement dictionary with REQUIREMENTS_ID, DESCRIPTION, CATEGORY
            model: Optional model name to override default
        
        Returns:
            GenerationResult object
        """
        payload = requirement.copy()
        if model:
            payload["model"] = model
        
        try:
            response = self.session.post(
                f"{self.base_url}/generate",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            return GenerationResult(
                requirement_id=data.get("REQUIREMENTS_ID", "UNKNOWN"),
                status="success",
                test_case=data.get("Test_Case", ""),
                timestamp=data.get("Generated_At")
            )
        except requests.exceptions.RequestException as e:
            return GenerationResult(
                requirement_id=requirement.get("REQUIREMENTS_ID", "UNKNOWN"),
                status="failed",
                error=str(e)
            )
    
    def generate_batch(
        self,
        requirements: List[Dict[str, Any]],
        model: Optional[str] = None
    ) -> List[GenerationResult]:
        """
        Generate test cases for multiple requirements
        
        Args:
            requirements: List of requirement dictionaries
            model: Optional model name to override default
        
        Returns:
            List of GenerationResult objects
        """
        payload = {"requirements": requirements}
        if model:
            payload["model"] = model
        
        try:
            response = self.session.post(
                f"{self.base_url}/generate/batch",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            results = []
            for result in data.get("results", []):
                req_data = result.get("data", {})
                results.append(GenerationResult(
                    requirement_id=req_data.get("REQUIREMENTS_ID", "UNKNOWN"),
                    status=result.get("status", "unknown"),
                    test_case=req_data.get("Test_Case", "") if result.get("status") == "success" else None,
                    timestamp=req_data.get("Generated_At") if result.get("status") == "success" else None
                ))
            
            return results
        except requests.exceptions.RequestException as e:
            return [GenerationResult(
                requirement_id="BATCH",
                status="failed",
                error=str(e)
            )]
    
    def generate_from_file(
        self,
        file_path: str,
        model: Optional[str] = None
    ) -> List[GenerationResult]:
        """
        Generate test cases from a JSON file
        
        Args:
            file_path: Path to JSON file containing requirements
            model: Optional model name to override default
        
        Returns:
            List of GenerationResult objects
        """
        file_path = Path(file_path)
        if debug_mode:
            print(f"Generating from file: {file_path}")
            print(f"model: {model}")

        if not file_path.exists():
            return [GenerationResult(
                requirement_id="FILE",
                status="failed",
                error=f"File not found: {file_path}"
            )]
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = {'model': model} if model else {}
                
                response = self.session.post(
                    f"{self.base_url}/generate/file",
                    files=files,
                    data=data,
                    timeout=self.timeout
                )
                if debug_mode:
                    print(f"File upload response status: {response.status_code}")
                    response_data = response.json()
                    formatted = json.dumps(response_data, indent=2)
                    lines = formatted.split('\n')
                    print("File upload response body (first 10 lines):")
                    for line in lines[:10]:
                        print(line)
                    
                response.raise_for_status()
                api_data = response.json()
                
                results = []
                for result in api_data.get("results", []):
                    req_data = result.get("data", {})
                    results.append(GenerationResult(
                        requirement_id=req_data.get("REQUIREMENTS_ID", "UNKNOWN"),
                        status=result.get("status", "unknown"),
                        test_case=req_data.get("Test_Case", "") if result.get("status") == "success" else None,
                        timestamp=req_data.get("Generated_At") if result.get("status") == "success" else None
                    ))
                
                return results
        except requests.exceptions.RequestException as e:
            return [GenerationResult(
                requirement_id="FILE",
                status="failed",
                error=str(e)
            )]
    
    def save_results(
        self,
        results: List[GenerationResult],
        output_file: str,
        format: str = "json"
    ) -> bool:
        """
        Save generation results to file
        
        Args:
            results: List of GenerationResult objects
            output_file: Output file path
            format: Output format ('json' or 'txt')
        
        Returns:
            True if successful, False otherwise
        """
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if format.lower() == "json":
                data = [
                    {
                        "requirement_id": r.requirement_id,
                        "status": r.status,
                        "test_case": r.test_case,
                        "error": r.error,
                        "timestamp": r.timestamp
                    }
                    for r in results
                ]
                with open(output_path, 'w') as f:
                    json.dump(data, f, indent=2)
            else:  # text format
                with open(output_path, 'w') as f:
                    for r in results:
                        f.write(f"\n{'='*80}\n")
                        f.write(f"Requirement ID: {r.requirement_id}\n")
                        f.write(f"Status: {r.status}\n")
                        if r.timestamp:
                            f.write(f"Generated: {r.timestamp}\n")
                        f.write(f"{'='*80}\n")
                        if r.test_case:
                            f.write(f"{r.test_case}\n")
                        elif r.error:
                            f.write(f"ERROR: {r.error}\n")
            return True
        except Exception as e:
            print(f"Error saving results: {e}")
            return False


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = TestCaseGeneratorClient()
    
    # Check health
    print("Checking API health...")
    if not client.health_check():
        print("ERROR: API is not healthy!")
        exit(1)
    
    print("✓ API is healthy\n")
    
    # List models
    print("Available models:")
    models = client.list_models()
    for model in models:
        print(f"  - {model}")
    print()

    """
    # # Single requirement
    # print("Generating single test case...")
    # requirement = {
    #     "REQUIREMENTS_ID": "REQ-EXAMPLE-001",
    #     "DESCRIPTION": "The system shall measure input voltage with ADC accuracy of ±2%.",
    #     "CATEGORY": "Functional",
    #     "PARAMETER_CATEGORY": "VOLTAGE SENSING"
    # }
    # 
    # result = client.generate(requirement)
    # print(f"Status: {result.status}")
    # if result.test_case:
    #     print(f"Test Case Preview:\n{result.test_case[:500]}...\n")
    # if result.error:
    #     print(f"Error: {result.error}\n")
    # 
    # # Save single result
    # client.save_results([result], "output/single_result.json")
    # print("✓ Saved to output/single_result.json\n")
    # 
    # # Batch generation
    # print("Generating batch test cases...")
    # requirements = [
    #     {
    #         "REQUIREMENTS_ID": "REQ-BATCH-001",
    #         "DESCRIPTION": "Input voltage shall be sensed by MCU with dedicated ADC line.",
    #         "CATEGORY": "Functional"
    #     },
    #     {
    #         "REQUIREMENTS_ID": "REQ-BATCH-002",
    #         "DESCRIPTION": "System shall transfer to battery within 4ms of AC loss.",
    #         "CATEGORY": "Functional"
    #     }
    # ]
    # 
    # 
    # 
    # batch_results = client.generate_batch(requirements)
    # print(f"Generated {len(batch_results)} test cases")
    # successful = sum(1 for r in batch_results if r.status == "success")
    # print(f"Successful: {successful}/{len(batch_results)}\n")
    # 
    # # Save batch results
    # client.save_results(batch_results, "output/batch_results.json")
    # print("✓ Saved to output/batch_results.json")
    # 
    # # Save as text
    # client.save_results(batch_results, "output/batch_results.txt", format="txt")
    # print("✓ Saved to output/batch_results.txt")
    # 
    # 
    # # Generate from file
    # print("Generating test cases from file...")
    # file_results = client.generate_from_file("samples/single_requirement.json")
    # print(f"Generated {len(file_results)} test cases from file")
    # successful = sum(1 for r in file_results if r.status == "success")
    # print(f"Successful: {successful}/{len(file_results)}\n")
    # 
    # # Save file results
    # client.save_results(file_results, "output/file_results.json")
    # print("✓ Saved to output/file_results.json")

    """
    
    # Generate from file #2
    tgt_file        = os.getenv("TARGET_FILE", "samples/batch_requirements.json")
    tgt_file_name   = os.getenv("TARGET_FILE_NAME", "batch_requirements.json")

    tgt_file_name = str(tgt_file_name).replace(".json", f"_{str(tgt_model).replace(':', '')}.json")
    out_file_name   = f"output/{tgt_file_name}"

    print("Generating test cases from file...")
    file_results = client.generate_from_file(tgt_file, model=tgt_model)
    
    print(f"Generated {len(file_results)} test cases from file")
    successful = sum(1 for r in file_results if r.status == "success")
    print(f"Successful: {successful}/{len(file_results)}\n")
    
    # Save file results
    client.save_results(file_results, out_file_name)
    print(f"✓ Saved to {out_file_name}")
