#!/usr/bin/env python3
"""
Pylint Test Runner for Test Case API Project
Automated code quality analysis and reporting system
"""

import os
import sys
import subprocess
import json
import html
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import argparse


class PylintTestRunner:
    """Comprehensive pylint testing framework for the Test Case API project"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent
        self.pylint_config = Path(__file__).parent / ".pylintrc"
        self.results_dir = Path(__file__).parent / "results"
        self.results_dir.mkdir(exist_ok=True)
        
        # Directories to exclude from analysis
        self.exclude_dirs = {
            "__pycache__", 
            ".git", 
            ".pytest_cache", 
            "venv", 
            "env", 
            ".env",
            "node_modules",
            ".vscode",
            "results",  # Our own results directory
            "converted",  # Project-specific converted directory
            ".local"  # Project-specific local directory
        }
        
        # File patterns to exclude
        self.exclude_patterns = {
            "test_*.py",      # Test files (if you want to exclude them)
            "*_test.py",      # Alternative test naming
            "setup.py",       # Setup scripts (optional)
        }
        
    def get_python_files(self) -> List[Path]:
        """Dynamically discover all Python files to analyze"""
        print(f"🔍 Scanning for Python files in: {self.project_root}")
        
        python_files = []
        
        # Walk through the project directory
        for root, dirs, files in os.walk(self.project_root):
            root_path = Path(root)
            
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            # Skip if current directory is excluded
            if any(exclude_dir in root_path.parts for exclude_dir in self.exclude_dirs):
                continue
            
            # Find Python files
            for file in files:
                if file.endswith('.py'):
                    file_path = root_path / file
                    
                    # Skip files matching exclude patterns
                    if any(file_path.match(pattern) for pattern in self.exclude_patterns):
                        continue
                    
                    # Skip our own pylint test files
                    if file_path.parent.name == "pylint_tests":
                        continue
                    
                    python_files.append(file_path)
        
        # Sort files for consistent ordering
        python_files.sort()
        
        if python_files:
            print(f"📄 Found {len(python_files)} Python files:")
            for file in python_files:
                relative_path = file.relative_to(self.project_root)
                print(f"   • {relative_path}")
        else:
            print("⚠️  No Python files found to analyze!")
        
        return python_files
    
    def add_exclude_pattern(self, pattern: str):
        """Add a custom exclude pattern"""
        self.exclude_patterns.add(pattern)
        print(f"➕ Added exclude pattern: {pattern}")
    
    def add_exclude_directory(self, directory: str):
        """Add a custom exclude directory"""
        self.exclude_dirs.add(directory)
        print(f"➕ Added exclude directory: {directory}")
    
    def filter_files_by_pattern(self, files: List[Path], include_pattern: str = None) -> List[Path]:
        """Filter files by include pattern (e.g., 'app*.py', 'client*')"""
        if not include_pattern:
            return files
        
        filtered_files = [f for f in files if f.match(include_pattern)]
        print(f"🔍 Filtered to {len(filtered_files)} files matching pattern: {include_pattern}")
        return filtered_files
    
    def run_pylint_on_file(self, file_path: Path) -> Dict:
        """Run pylint on a single file and return results"""
        print(f"🔍 Analyzing: {file_path.name}")
        
        cmd = [
            sys.executable, "-m", "pylint",
            "--rcfile", str(self.pylint_config),
            "--output-format=json",
            "--reports=yes",
            str(file_path)
        ]
        
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                cwd=self.project_root,
                timeout=120
            )
            
            # Parse JSON output
            messages = []
            if result.stdout.strip():
                try:
                    messages = json.loads(result.stdout)
                except json.JSONDecodeError:
                    # Fallback for non-JSON output
                    messages = [{"message": result.stdout}]
            
            return {
                "file": str(file_path),
                "exit_code": result.returncode,
                "messages": messages,
                "stderr": result.stderr,
                "success": result.returncode in [0, 4, 8, 16]  # Pylint exit codes
            }
            
        except subprocess.TimeoutExpired:
            return {
                "file": str(file_path),
                "exit_code": -1,
                "messages": [{"message": "Pylint timeout expired"}],
                "stderr": "Process timed out",
                "success": False
            }
        except Exception as e:
            return {
                "file": str(file_path),
                "exit_code": -1,
                "messages": [{"message": f"Error running pylint: {str(e)}"}],
                "stderr": str(e),
                "success": False
            }
    
    def categorize_messages(self, messages: List[Dict]) -> Dict[str, List]:
        """Categorize pylint messages by type"""
        categories = {
            "errors": [],      # E - Error
            "warnings": [],    # W - Warning  
            "refactoring": [], # R - Refactoring
            "conventions": [], # C - Convention
            "info": []         # I - Info
        }
        
        for msg in messages:
            if isinstance(msg, dict) and "type" in msg:
                msg_type = msg["type"].lower()
                if msg_type.startswith("error"):
                    categories["errors"].append(msg)
                elif msg_type.startswith("warning"):
                    categories["warnings"].append(msg)
                elif msg_type.startswith("refactor"):
                    categories["refactoring"].append(msg)
                elif msg_type.startswith("convention"):
                    categories["conventions"].append(msg)
                else:
                    categories["info"].append(msg)
            else:
                categories["info"].append(msg)
        
        return categories
    
    def generate_report(self, results: List[Dict]) -> str:
        """Generate comprehensive HTML report"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Calculate summary statistics
        total_files = len(results)
        successful_files = sum(1 for r in results if r["success"])
        total_messages = sum(len(r["messages"]) for r in results)
        
        # Count message types across all files
        all_errors = []
        all_warnings = []
        all_refactoring = []
        all_conventions = []
        
        for result in results:
            categories = self.categorize_messages(result["messages"])
            all_errors.extend(categories["errors"])
            all_warnings.extend(categories["warnings"])
            all_refactoring.extend(categories["refactoring"])
            all_conventions.extend(categories["conventions"])
        
        html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Pylint Analysis Report - Test Case API</title>
        <style>
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6; margin: 0; padding: 20px; background-color: #f8f9fa; 
        }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin: -30px -30px 30px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0; }}
        .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border-left: 4px solid #007bff; }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #007bff; }}
        .file-result {{ margin: 20px 0; padding: 20px; border: 1px solid #dee2e6; border-radius: 8px; }}
        .file-header {{ 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            margin-bottom: 15px; 
            cursor: pointer; 
            user-select: none; 
            padding: 8px; 
            border-radius: 5px;
            transition: background-color 0.2s ease;
        }}
        .file-header:hover {{ background-color: #f8f9fa; }}
        .file-name {{ 
            font-size: 1.2em; 
            font-weight: bold; 
            display: flex; 
            align-items: center;
        }}
        .status {{ 
            padding: 4px 12px; 
            border-radius: 20px; 
            font-size: 0.9em; 
            font-weight: bold; 
        }}
        .success {{ background-color: #d4edda; color: #155724; }}
        .failure {{ background-color: #f8d7da; color: #721c24; }}
        .message-category {{ margin: 15px 0; }}
        .message-list {{ 
            background: #f8f9fa; 
            padding: 15px; 
            border-radius: 5px; 
            margin-top: 5px; 
            border-left: 3px solid #dee2e6;
        }}
        .message-item {{ 
            margin: 8px 0; 
            padding: 10px; 
            background: white; 
            border-radius: 4px; 
            font-family: 'Courier New', monospace; 
            font-size: 0.9em; 
            line-height: 1.4;
            word-wrap: break-word;
        }}
        .error {{ border-left: 4px solid #dc3545; }}
        .warning {{ border-left: 4px solid #ffc107; }}
        .refactor {{ border-left: 4px solid #17a2b8; }}
        .convention {{ border-left: 4px solid #6c757d; }}
        .category-header {{ 
            font-weight: bold; 
            color: #495057; 
            cursor: pointer; 
            user-select: none; 
            padding: 8px; 
            border-radius: 3px;
            display: flex;
            align-items: center;
            transition: background-color 0.2s ease;
        }}
        .category-header:hover {{ background-color: #e9ecef; }}
        .timestamp {{ text-align: center; color: #6c757d; margin-top: 30px; }}
        .collapsible-content {{ 
            display: block; 
            transition: all 0.3s ease;
            overflow: hidden;
        }}
        .collapsed {{ 
            display: none !important; 
        }}
        .toggle-icon {{ 
            margin-right: 8px; 
            transition: transform 0.2s ease; 
            font-size: 0.8em;
            width: 16px;
            display: inline-block;
        }}
        .collapsed-icon {{ transform: rotate(-90deg); }}
        </style>
        <script>
        function toggleCollapse(element) {{
            const content = element.nextElementSibling;
            const icon = element.querySelector('.toggle-icon');
            
            if (content && icon) {{
                if (content.classList.contains('collapsed')) {{
                    content.classList.remove('collapsed');
                    icon.classList.remove('collapsed-icon');
                    icon.textContent = '▼';
                }} else {{
                    content.classList.add('collapsed');
                    icon.classList.add('collapsed-icon');
                    icon.textContent = '▶';
                }}
            }}
        }}
        
        function toggleFileContent(element) {{
            const fileResult = element.parentElement;
            const content = fileResult.querySelector('.file-content');
            const icon = element.querySelector('.toggle-icon');
            
            if (content && icon) {{
                if (content.classList.contains('collapsed')) {{
                    content.classList.remove('collapsed');
                    icon.classList.remove('collapsed-icon');
                    icon.textContent = '▼';
                }} else {{
                    content.classList.add('collapsed');
                    icon.classList.add('collapsed-icon');
                    icon.textContent = '▶';
                }}
            }}
        }}
        
        // Initialize all sections as expanded by default
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('Pylint Report loaded successfully');
        }});
        </script>
    </head>
    <body>
        <div class="container">
        <div class="header">
            <h1>🔍 Pylint Analysis Report</h1>
            <p>Test Case API Project - Code Quality Assessment</p>
            <p>Generated: {timestamp}</p>
        </div>
        
        <div class="summary">
            <div class="stat-card">
            <div class="stat-number">{total_files}</div>
            <div>Files Analyzed</div>
            </div>
            <div class="stat-card">
            <div class="stat-number">{successful_files}</div>
            <div>Successful</div>
            </div>
            <div class="stat-card">
            <div class="stat-number">{len(all_errors)}</div>
            <div>Errors</div>
            </div>
            <div class="stat-card">
            <div class="stat-number">{len(all_warnings)}</div>
            <div>Warnings</div>
            </div>
            <div class="stat-card">
            <div class="stat-number">{len(all_refactoring)}</div>
            <div>Refactoring</div>
            </div>
            <div class="stat-card">
            <div class="stat-number">{len(all_conventions)}</div>
            <div>Conventions</div>
            </div>
        </div>
        
        <h2>📋 Detailed Results</h2>
    """
        
        # Add individual file results
        for result in results:
            file_name = Path(result["file"]).name
            status_class = "success" if result["success"] else "failure"
            status_text = "✅ Passed" if result["success"] else "❌ Failed"
            
            categories = self.categorize_messages(result["messages"])
            total_messages = len(result["messages"])
            
            html_content += f"""
        <div class="file-result">
            <div class="file-header" onclick="toggleFileContent(this)">
                <div class="file-name"><span class="toggle-icon">▼</span>📄 {file_name} ({total_messages} issues)</div>
                <div class="status {status_class}">{status_text}</div>
            </div>
            <div class="file-content collapsible-content">
"""
            
            # Add messages by category
            for category, messages in categories.items():
                if messages:
                    category_icons = {
                        "errors": "🚨", "warnings": "⚠️", 
                        "refactoring": "🔧", "conventions": "📏", "info": "ℹ️"
                    }
                    icon = category_icons.get(category, "📝")
                    
                    html_content += f"""
                <div class="message-category">
                    <div class="category-header" onclick="toggleCollapse(this)">
                        <span class="toggle-icon">▼</span>{icon} {category.title()} ({len(messages)})
                    </div>
                    <div class="message-list collapsible-content">
"""
                    
                    for msg in messages:
                        if isinstance(msg, dict):
                            message_text = msg.get("message", str(msg))
                            line = msg.get("line", "")
                            column = msg.get("column", "")
                            location = f"Line {line}:{column} - " if line else ""
                        else:
                            message_text = str(msg)
                            location = ""
                        
                        # Escape HTML characters in message text
                        import html
                        message_text = html.escape(message_text)
                        
                        html_content += f'                        <div class="message-item {category[:-1] if category.endswith("s") else category}">{location}{message_text}</div>\n'
                    
                    html_content += """                    </div>
                </div>
"""
            
            # If no messages, show clean status
            if total_messages == 0:
                html_content += """
                <div class="message-category">
                    <div style="text-align: center; color: #28a745; font-weight: bold; padding: 20px;">
                        ✅ No issues found - Code quality looks good!
                    </div>
                </div>
"""
            
            html_content += """            </div>
        </div>
"""
        
        html_content += """
        <div class="timestamp">
            Report generated by Pylint Test Runner for Test Case API Project
        </div>
        </div>
    </body>
    </html>
    """
        return html_content
    
    def save_results(self, results: List[Dict], format_type: str = "html") -> Path:
        """Save results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_type == "html":
            report_content = self.generate_report(results)
            file_path = self.results_dir / f"pylint_report_{timestamp}.html"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(report_content)
        
        elif format_type == "json":
            file_path = self.results_dir / f"pylint_results_{timestamp}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, default=str)
        
        return file_path
    
    def run_all_tests(self, save_format: str = "html") -> Tuple[List[Dict], Path]:
        """Run pylint on all Python files"""
        print("🚀 Starting Pylint Analysis for Test Case API Project")
        print(f"📁 Project Root: {self.project_root}")
        print(f"⚙️  Pylint Config: {self.pylint_config}")
        print("=" * 60)
        
        # Use discovered files if available, otherwise discover them
        python_files = getattr(self, '_discovered_files', None) or self.get_python_files()
        if not python_files:
            print("❌ No Python files found to analyze!")
            return [], None
        
        results = []
        for file_path in python_files:
            result = self.run_pylint_on_file(file_path)
            results.append(result)
            
            # Show immediate feedback
            status = "✅" if result["success"] else "❌"
            message_count = len(result["messages"])
            print(f"{status} {file_path.name}: {message_count} messages")
        
        print("=" * 60)
        print(f"📊 Analysis complete! Processed {len(results)} files")
        
        # Save results
        report_path = self.save_results(results, save_format)
        print(f"💾 Report saved: {report_path}")
        
        return results, report_path


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Pylint Test Runner for Test Case API")
    parser.add_argument("--project-root", help="Project root directory")
    parser.add_argument("--format", choices=["html", "json"], default="html", 
                       help="Output format (default: html)")
    parser.add_argument("--file", help="Analyze specific file only")
    parser.add_argument("--pattern", help="Include only files matching pattern (e.g., 'app*.py')")
    parser.add_argument("--exclude-dir", action="append", help="Additional directories to exclude")
    parser.add_argument("--exclude-file", action="append", help="Additional file patterns to exclude")
    parser.add_argument("--include-tests", action="store_true", help="Include test files in analysis")
    parser.add_argument("--list-files", action="store_true", help="List all Python files and exit")
    
    args = parser.parse_args()
    
    runner = PylintTestRunner(args.project_root)
    
    # Apply custom exclusions
    if args.exclude_dir:
        for exclude_dir in args.exclude_dir:
            runner.add_exclude_directory(exclude_dir)
    
    if args.exclude_file:
        for exclude_pattern in args.exclude_file:
            runner.add_exclude_pattern(exclude_pattern)
    
    # Include test files if requested
    if args.include_tests:
        runner.exclude_patterns.discard("test_*.py")
        runner.exclude_patterns.discard("*_test.py")
        print("📋 Including test files in analysis")
    
    # List files mode
    if args.list_files:
        python_files = runner.get_python_files()
        if args.pattern:
            python_files = runner.filter_files_by_pattern(python_files, args.pattern)
        
        print(f"\n📊 Summary: {len(python_files)} Python files found")
        return
    
    if args.file:
        # Analyze single file
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            sys.exit(1)
        
        result = runner.run_pylint_on_file(file_path)
        results = [result]
        report_path = runner.save_results(results, args.format)
    else:
        # Get all Python files
        python_files = runner.get_python_files()
        
        # Apply pattern filtering if specified
        if args.pattern:
            python_files = runner.filter_files_by_pattern(python_files, args.pattern)
        
        # Update runner's file list for analysis
        runner._discovered_files = python_files
        
        # Analyze all files
        results, report_path = runner.run_all_tests(args.format)
    
    # Print summary
    if results:
        successful = sum(1 for r in results if r["success"])
        total_messages = sum(len(r["messages"]) for r in results)
        
        print(f"\n📈 Summary:")
        print(f"   Files analyzed: {len(results)}")
        print(f"   Successful: {successful}")
        print(f"   Total messages: {total_messages}")
        print(f"   Report: {report_path}")
        
        if args.format == "html":
            print(f"\n🌐 Open in browser: file://{report_path.absolute()}")


if __name__ == "__main__":
    main()