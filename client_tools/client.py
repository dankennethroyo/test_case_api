#!/usr/bin/env python3
#####################################################################
#                       E M E R S O N   S O L A H D                 #
#                         Test Case API Client                      #
#####################################################################
"""
Test Case Generator API - Python Client
Simple client for programmatic access to the API
"""

import requests
import sys
import json
import time
import os
import shutil
import argparse
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
tgt_model               = os.getenv("OLLAMA_MODEL", "phi4:14b")
tgt_server              = os.getenv("API_SERVER", "http://localhost:8009")


# Test Case Generator Object
class TestCaseGeneratorClient:
    """Client for interacting with Test Case Generator API"""
    
    def __init__(self, base_url: str = f"{tgt_server}", timeout: int = 300):
        """
        Initialize the client
        
        Args:
            base_url: Base URL of the API (default: http://localhost:8009)
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
        model: Optional[str] = None,
        use_instructions: bool = True
    ) -> GenerationResult:
        """
        Generate a test case for a single requirement
        
        Args:
            requirement: Requirement dictionary with REQUIREMENTS_ID, DESCRIPTION, CATEGORY
            model: Optional model name to override default
            use_instructions: Whether to use system instructions (default: True)
        
        Returns:
            GenerationResult object
        """
        payload = requirement.copy()
        if model:
            payload["model"] = model
        payload["use_instructions"] = use_instructions
        
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
        model: Optional[str] = None,
        use_instructions: bool = True
    ) -> List[GenerationResult]:
        """
        Generate test cases for multiple requirements
        
        Args:
            requirements: List of requirement dictionaries
            model: Optional model name to override default
            use_instructions: Whether to use system instructions (default: True)
        
        Returns:
            List of GenerationResult objects
        """
        payload = {"requirements": requirements}
        if model:
            payload["model"] = model
        payload["use_instructions"] = use_instructions
        
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
        model: Optional[str] = None,
        use_instructions: bool = True,
        incremental_save: bool = False,
        output_file: Optional[str] = None
    ) -> List[GenerationResult]:
        """
        Generate test cases from a JSON file with incremental saving
        
        Args:
            file_path: Path to JSON file containing requirements
            model: Optional model name to override default
            use_instructions: Whether to use system instructions (default: True)
            incremental_save: If True, save each result as it's generated
            output_file: Output file for incremental saves
        
        Returns:
            List of GenerationResult objects
        """
        file_path = Path(file_path)
        if debug_mode:
            print(f"Generating from file: {file_path}")
            print(f"model: {model}")
            print(f"incremental_save: {incremental_save}")

        if not file_path.exists():
            return [GenerationResult(
                requirement_id="FILE",
                status="failed",
                error=f"File not found: {file_path}"
            )]
        
        # Load requirements from file
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Handle both {"requirements": [...]} and direct array formats
            if isinstance(data, dict) and "requirements" in data:
                requirements = data.get("requirements", [])
            elif isinstance(data, list):
                requirements = data
            else:
                requirements = []
        except Exception as e:
            return [GenerationResult(
                requirement_id="FILE",
                status="failed",
                error=f"Failed to load file: {e}"
            )]
        
        if not requirements:
            return [GenerationResult(
                requirement_id="FILE",
                status="failed",
                error="No requirements found in file"
            )]
        
        all_results = []
        
        # Process each requirement individually for incremental saving
        for i, requirement in enumerate(requirements):
            if debug_mode:
                req_id = requirement.get("REQUIREMENTS_ID", f"REQ-{i}")
                print(f"Processing requirement {i+1}/{len(requirements)}: {req_id}")
            
            # Generate test case for this requirement
            result = self.generate(requirement, model, use_instructions)
            all_results.append(result)
            
            # Save incrementally if requested
            if incremental_save and output_file:
                self.save_results([result], output_file, append=(i > 0))
                if debug_mode:
                    print(f"✓ Saved result for {result.requirement_id} to {output_file}")
        
        return all_results
    
    def save_results(
        self,
        results: List[GenerationResult],
        output_file: str,
        format: str = "json",
        append: bool = False
    ) -> bool:
        """
        Save generation results to file
        
        Args:
            results: List of GenerationResult objects
            output_file: Output file path
            format: Output format ('json' or 'txt')
            append: If True, append to existing file (for incremental saves)
        
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
                
                if append and output_path.exists():
                    # Load existing data and append new results
                    try:
                        with open(output_path, 'r') as f:
                            existing_data = json.load(f)
                        if isinstance(existing_data, list):
                            existing_data.extend(data)
                            data = existing_data
                    except (json.JSONDecodeError, TypeError):
                        # If existing file is corrupt, just overwrite
                        pass
                
                with open(output_path, 'w') as f:
                    json.dump(data, f, indent=2)
            else:  # text format
                mode = 'a' if append else 'w'
                with open(output_path, mode) as f:
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
    parser = argparse.ArgumentParser(description='Test Case Generator API Client')
    parser.add_argument('--model', help='Model name to use (overrides default)')
    parser.add_argument('--no-instructions', action='store_true', 
                       help='Disable system instructions (let LLM decide format)')
    parser.add_argument('--server', help='API server URL (overrides default)')
    
    args = parser.parse_args()
    
    # Override server if specified
    server_url = args.server or tgt_server
    
    # Initialize client
    client = TestCaseGeneratorClient(server_url)
    
    # Determine use_instructions setting
    use_instructions = not args.no_instructions
    
    # Override model if specified
    model = args.model or tgt_model
    
    # Check health
    print("Checking API health...")
    if not client.health_check():
        print("ERROR: API is not healthy!")
        exit(1)
    
    print("✓ API is healthy\n")
    
    # List models
    print("Available models:")
    models = client.list_models()
    for m in models:
        print(f"  - {m}")
    print()

    # Generate from file with incremental saving
    tgt_file        = os.getenv("TARGET_FILE", "samples/batch_requirements.json")
    tgt_file_name   = os.getenv("TARGET_FILE_NAME", "batch_requirements.json")

    tgt_file_name = str(tgt_file_name).replace(".json", f"_{str(model).replace(':', '')}.json")
    out_file_name   = f"output/{tgt_file_name}"

    print(f"Generating test cases (use_instructions={use_instructions})...")
    print(f"Model: {model}")
    print(f"Output will be saved to: {out_file_name}")
    print("-" * 60)
    
    file_results = client.generate_from_file(
        tgt_file, 
        model=model, 
        use_instructions=use_instructions,
        incremental_save=True, 
        output_file=out_file_name
    )
    
    print("-" * 60)
    print(f"Generated {len(file_results)} test cases from file")
    successful = sum(1 for r in file_results if r.status == "success")
    failed = len(file_results) - successful
    print(f"Successful: {successful}/{len(file_results)}")
    print(f"Failed: {failed}/{len(file_results)}")
    print(f"✓ All results saved incrementally to: {out_file_name}")
