#!/usr/bin/env python3
"""
Test Case API Client
Simple Python client for interacting with the Test Case Generator API
"""

import requests
import json
import argparse
from typing import Dict, List, Optional, Any
from pathlib import Path


class TestCaseAPIClient:
    """Client for Test Case Generator API"""
    
    def __init__(self, base_url: str = "http://localhost:5009"):
        """
        Initialize the API client
        
        Args:
            base_url: Base URL of the API server
        """
        self.base_url = base_url.rstrip('/')
        
    def health_check(self) -> Dict[str, Any]:
        """Check API health status"""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def list_models(self) -> Dict[str, Any]:
        """List available Ollama models"""
        response = requests.get(f"{self.base_url}/models")
        response.raise_for_status()
        return response.json()
    
    def generate_single(self, 
                       requirement_id: str,
                       description: str,
                       category: str,
                       parameter_category: Optional[str] = None,
                       verification_plan: Optional[str] = None,
                       model: Optional[str] = None,
                       use_instructions: bool = True) -> Dict[str, Any]:
        """
        Generate test case for a single requirement
        
        Args:
            requirement_id: Unique requirement identifier
            description: Requirement description
            category: Requirement category
            parameter_category: Optional parameter category
            verification_plan: Optional verification plan
            model: Optional model name to use
            use_instructions: Whether to use system instructions (default: True)
                             If False, LLM decides response format independently
        
        Returns:
            Generated test case data
        """
        payload = {
            "REQUIREMENTS_ID": requirement_id,
            "DESCRIPTION": description,
            "CATEGORY": category,
            "use_instructions": use_instructions
        }
        
        if parameter_category:
            payload["PARAMETER_CATEGORY"] = parameter_category
        
        if verification_plan:
            payload["VERIFICATION_PLAN"] = verification_plan
        
        if model:
            payload["model"] = model
        
        response = requests.post(
            f"{self.base_url}/generate",
            json=payload,
            timeout=300
        )
        response.raise_for_status()
        return response.json()
    
    def generate_batch(self,
                      requirements: List[Dict[str, Any]],
                      model: Optional[str] = None,
                      use_instructions: bool = True) -> Dict[str, Any]:
        """
        Generate test cases for multiple requirements
        
        Args:
            requirements: List of requirement dictionaries
            model: Optional model name to use
            use_instructions: Whether to use system instructions (default: True)
                             If False, LLM decides response format independently
        
        Returns:
            Batch generation results
        """
        payload = {
            "requirements": requirements,
            "use_instructions": use_instructions
        }
        
        if model:
            payload["model"] = model
        
        response = requests.post(
            f"{self.base_url}/generate/batch",
            json=payload,
            timeout=600
        )
        response.raise_for_status()
        return response.json()
    
    def generate_from_file(self,
                          file_path: str,
                          model: Optional[str] = None,
                          use_instructions: bool = True) -> Dict[str, Any]:
        """
        Generate test cases from a JSON file
        
        Args:
            file_path: Path to JSON file containing requirements
            model: Optional model name to use
            use_instructions: Whether to use system instructions (default: True)
                             If False, LLM decides response format independently
        
        Returns:
            File generation results
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not path.suffix == '.json':
            raise ValueError("File must be a JSON file")
        
        with open(path, 'rb') as f:
            files = {'file': (path.name, f, 'application/json')}
            data = {'use_instructions': str(use_instructions).lower()}
            
            if model:
                data['model'] = model
            
            response = requests.post(
                f"{self.base_url}/generate/file",
                files=files,
                data=data,
                timeout=600
            )
        
        response.raise_for_status()
        return response.json()
    
    def get_instructions(self) -> Dict[str, Any]:
        """Get current system instructions"""
        response = requests.get(f"{self.base_url}/instructions")
        response.raise_for_status()
        return response.json()
    
    def update_instructions(self, instructions: str) -> Dict[str, Any]:
        """Update system instructions"""
        response = requests.post(
            f"{self.base_url}/instructions",
            json={"instructions": instructions}
        )
        response.raise_for_status()
        return response.json()


def main():
    """Example usage of the Test Case API Client"""
    parser = argparse.ArgumentParser(description='Test Case API Client')
    parser.add_argument('--url', default='http://localhost:5009', 
                       help='API base URL (default: http://localhost:5009)')
    parser.add_argument('--model', help='Model name to use (optional)')
    parser.add_argument('--no-instructions', action='store_true',
                       help='Disable system instructions (let LLM decide format)')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Health check command
    subparsers.add_parser('health', help='Check API health')
    
    # List models command
    subparsers.add_parser('models', help='List available models')
    
    # Generate single command
    single_parser = subparsers.add_parser('generate', help='Generate single test case')
    single_parser.add_argument('--id', required=True, help='Requirement ID')
    single_parser.add_argument('--description', required=True, help='Requirement description')
    single_parser.add_argument('--category', required=True, help='Requirement category')
    single_parser.add_argument('--param-category', help='Parameter category')
    single_parser.add_argument('--verification', help='Verification plan')
    
    # Generate from file command
    file_parser = subparsers.add_parser('file', help='Generate from JSON file')
    file_parser.add_argument('path', help='Path to JSON file')
    file_parser.add_argument('--output', help='Output file path (optional)')
    
    args = parser.parse_args()
    
    # Create client
    client = TestCaseAPIClient(args.url)
    use_instructions = not args.no_instructions  # Default is True
    
    try:
        if args.command == 'health':
            result = client.health_check()
            print(json.dumps(result, indent=2))
        
        elif args.command == 'models':
            result = client.list_models()
            print(json.dumps(result, indent=2))
        
        elif args.command == 'generate':
            print(f"Generating test case (use_instructions={use_instructions})...")
            result = client.generate_single(
                requirement_id=args.id,
                description=args.description,
                category=args.category,
                parameter_category=args.param_category,
                verification_plan=args.verification,
                model=args.model,
                use_instructions=use_instructions
            )
            print(json.dumps(result, indent=2))
        
        elif args.command == 'file':
            print(f"Processing file (use_instructions={use_instructions})...")
            result = client.generate_from_file(
                file_path=args.path,
                model=args.model,
                use_instructions=use_instructions
            )
            
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2)
                print(f"Results saved to: {args.output}")
            else:
                print(json.dumps(result, indent=2))
        
        else:
            parser.print_help()
    
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
