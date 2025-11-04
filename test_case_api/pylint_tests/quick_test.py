#!/usr/bin/env python3
"""
Pylint Quick Test - Simplified runner for fast analysis
"""

import os
import sys
import subprocess
from pathlib import Path


def quick_pylint_test(file_path: str = None):
    """Run a quick pylint test on specified file or all files"""
    
    project_root = Path(__file__).parent.parent
    pylint_config = Path(__file__).parent / ".pylintrc"
    
    if file_path:
        # Test specific file
        target = project_root / file_path
        if not target.exists():
            print(f"❌ File not found: {target}")
            return False
        files_to_test = [target]
    else:
        # Dynamically find main Python files (excluding test files and pylint directory)
        files_to_test = []
        exclude_dirs = {"__pycache__", ".git", "pylint_tests", "results", "converted", ".local"}
        
        for root, dirs, files in os.walk(project_root):
            root_path = Path(root)
            
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            # Skip if current directory should be excluded
            if any(exclude_dir in root_path.parts for exclude_dir in exclude_dirs):
                continue
            
            # Find main Python files (prioritize common ones)
            for file in files:
                if file.endswith('.py') and not file.startswith('test_'):
                    file_path = root_path / file
                    files_to_test.append(file_path)
        
        # Sort and limit to top files for quick testing
        files_to_test.sort(key=lambda f: f.name)
        # Prioritize main application files
        priority_files = []
        other_files = []
        
        for file in files_to_test:
            if file.name in ["app.py", "client.py", "convert_results.py"]:
                priority_files.append(file)
            else:
                other_files.append(file)
        
        # Use priority files first, then others (limit to 5 total for quick test)
        files_to_test = priority_files + other_files[:5-len(priority_files)]
    
    if not files_to_test:
        print("❌ No files found to test")
        return False
    
    print("🔍 Quick Pylint Test - Test Case API Project")
    print("=" * 50)
    
    all_passed = True
    
    for file_path in files_to_test:
        print(f"\n📄 Testing: {file_path.name}")
        
        cmd = [
            sys.executable, "-m", "pylint",
            "--rcfile", str(pylint_config),
            "--score=yes",
            "--reports=no",
            str(file_path)
        ]
        
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True,
                cwd=project_root,
                timeout=60
            )
            
            # Extract score from output
            score = "N/A"
            for line in result.stdout.split('\n'):
                if "Your code has been rated at" in line:
                    score = line.split("rated at ")[1].split("/10")[0]
                    break
            
            if result.returncode == 0:
                print(f"✅ PASSED - Score: {score}/10")
            elif result.returncode <= 16:  # Pylint warning codes
                print(f"⚠️  WARNINGS - Score: {score}/10")
                if result.stdout:
                    # Show first few warnings
                    lines = result.stdout.split('\n')
                    warning_lines = [l for l in lines if l.strip() and not l.startswith('*')][:5]
                    for line in warning_lines[:3]:
                        if line.strip():
                            print(f"   {line}")
                    if len(warning_lines) > 3:
                        print(f"   ... and {len(warning_lines)-3} more")
                all_passed = False
            else:
                print(f"❌ FAILED - Score: {score}/10")
                if result.stdout:
                    # Show errors
                    lines = result.stdout.split('\n')
                    error_lines = [l for l in lines if l.strip() and not l.startswith('*')][:5]
                    for line in error_lines[:3]:
                        if line.strip():
                            print(f"   {line}")
                all_passed = False
                
        except subprocess.TimeoutExpired:
            print("⏱️  TIMEOUT - Analysis took too long")
            all_passed = False
        except Exception as e:
            print(f"❌ ERROR - {str(e)}")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests PASSED! Code quality looks good.")
    else:
        print("⚠️  Some issues found. Run full analysis for details:")
        print("   python run_pylint_tests.py")
    
    return all_passed


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Test specific file
        quick_pylint_test(sys.argv[1])
    else:
        # Test all files
        quick_pylint_test()