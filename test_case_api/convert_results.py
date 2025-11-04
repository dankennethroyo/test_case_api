#!/usr/bin/env python3
#####################################################################
#                       E M E R S O N   S O L A H D                 #
#                   Test Case Results Converter                     #
#####################################################################
"""
Convert test case generation results from JSON to various formats:
- Individual TXT files per requirement
- Individual MD (Markdown) files per requirement
- Single CSV file with all test cases
"""

import json, csv, os, sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Load/import JSON results
def load_json_results(json_file: str) -> List[Dict[str, Any]]:
    """Load test case results from JSON file"""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✓ Loaded {len(data)} test cases from {json_file}")
        return data
    except FileNotFoundError:
        print(f"ERROR: File not found: {json_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON file: {e}")
        sys.exit(1)

# Create individual TXT file
def create_txt_file(result: Dict[str, Any], output_dir: Path) -> None:
    """
    Create individual TXT file for a test case
    -------------------------------------------------
    result: Dict[str, Any] - Test case result data
    output_dir: Path - Directory to save the TXT file
    """
    req_id = result.get('requirement_id', 'UNKNOWN')
    filename = f"{req_id}.txt"
    filepath = output_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write(f"REQUIREMENT ID: {req_id}\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"Status: {result.get('status', 'unknown')}\n")
        if result.get('timestamp'):
            f.write(f"Generated: {result.get('timestamp')}\n")
        f.write("\n")
        
        if result.get('status') == 'success' and result.get('test_case'):
            f.write("-" * 80 + "\n")
            f.write("TEST CASE\n")
            f.write("-" * 80 + "\n\n")
            f.write(result.get('test_case'))
            f.write("\n\n")
        elif result.get('error'):
            f.write("-" * 80 + "\n")
            f.write("ERROR\n")
            f.write("-" * 80 + "\n\n")
            f.write(result.get('error'))
            f.write("\n\n")
        
        f.write("=" * 80 + "\n")
    
    print(f"  Created: {filename}")

# Create individual MD file
def create_md_file(result: Dict[str, Any], output_dir: Path) -> None:
    """
    Create individual Markdown file for a test case
    -------------------------------------------------
    result: Dict[str, Any] - Test case result data
    output_dir: Path - Directory to save the MD file
    """
    
    req_id = result.get('requirement_id', 'UNKNOWN')
    filename = f"{req_id}.md"
    filepath = output_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# Test Case: {req_id}\n\n")
        
        # Metadata section
        f.write("## Metadata\n\n")
        f.write(f"- **Requirement ID**: {req_id}\n")
        f.write(f"- **Status**: {result.get('status', 'unknown')}\n")
        if result.get('timestamp'):
            f.write(f"- **Generated**: {result.get('timestamp')}\n")
        f.write("\n---\n\n")
        
        # Test case or error section
        if result.get('status') == 'success' and result.get('test_case'):
            f.write("## Test Case Details\n\n")
            f.write(result.get('test_case'))
            f.write("\n\n")
        elif result.get('error'):
            f.write("## Error\n\n")
            f.write(f"```\n{result.get('error')}\n```\n\n")
        
        # Footer
        f.write("---\n")
        f.write(f"*Generated on {result.get('timestamp', 'N/A')}*\n")
    
    print(f"  Created: {filename}")

# Parse structured fields from test case text
def parse_test_case_fields(test_case: str) -> Dict[str, str]:
    """
    Parse structured fields from test case text
    --------------------------------------------------
    test_case: str - Full test case text
    returns: Dict[str, str] - Parsed fields
    """
    fields = {
        'title': '',
        'objective': '',
        'preconditions': '',
        'test_steps': '',
        'expected_result': '',
        'postconditions': '',
        'test_data': '',
        'edge_cases': ''
    }
    
    if not test_case:
        return fields
    
    # Enhanced parsing to handle various formats
    lines = test_case.split('\n')
    current_field = None
    current_content = []
    
    # Extract title from first line if it doesn't have "Test Case Title:" prefix
    first_line = lines[0].strip() if lines else ''
    if first_line and not first_line.lower().startswith('test case title:'):
        # Check if first line looks like a title (not starting with number or common section words)
        if not any(first_line.lower().startswith(word) for word in ['objective:', 'references:', '1.', '2.', 'preconditions:']):
            fields['title'] = first_line
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        line_lower = line_stripped.lower()
        
        # Skip empty lines
        if not line_stripped:
            if current_field:
                current_content.append('')
            continue
        
        # Title patterns
        if (line_lower.startswith('test case title:') or
            line_lower.startswith('title:')):
            if current_field:
                fields[current_field] = '\n'.join(current_content).strip()
            current_field = 'title'
            current_content = [line.split(':', 1)[1].strip() if ':' in line else '']
            
        # Objective patterns (including numbered sections)
        elif (line_lower.startswith('objective:') or
              line_lower.startswith('1. objective:') or
              line_lower.startswith('1.objective:')):
            if current_field:
                fields[current_field] = '\n'.join(current_content).strip()
            current_field = 'objective'
            # Extract content after colon
            if ':' in line:
                content = line.split(':', 1)[1].strip()
                current_content = [content] if content else []
            else:
                current_content = []
                
        # Preconditions patterns
        elif (line_lower.startswith('preconditions:') or
              line_lower.startswith('3. preconditions:') or
              line_lower.startswith('4. preconditions:')):
            if current_field:
                fields[current_field] = '\n'.join(current_content).strip()
            current_field = 'preconditions'
            # Extract content after colon if present
            if ':' in line:
                content = line.split(':', 1)[1].strip()
                current_content = [content] if content else []
            else:
                current_content = []
            
        # Test Steps patterns
        elif (line_lower.startswith('test steps:') or
              line_lower.startswith('4. test steps:') or
              line_lower.startswith('5. test steps:')):
            if current_field:
                fields[current_field] = '\n'.join(current_content).strip()
            current_field = 'test_steps'
            # Extract content after colon if present
            if ':' in line:
                content = line.split(':', 1)[1].strip()
                current_content = [content] if content else []
            else:
                current_content = []
            
        # Expected Result patterns
        elif (line_lower.startswith('expected result:') or
              line_lower.startswith('5. expected result:') or
              line_lower.startswith('6. expected result:')):
            if current_field:
                fields[current_field] = '\n'.join(current_content).strip()
            current_field = 'expected_result'
            # Extract content after colon
            if ':' in line:
                content = line.split(':', 1)[1].strip()
                current_content = [content] if content else []
            else:
                current_content = []
                
        # Postconditions patterns
        elif (line_lower.startswith('postconditions:') or
              line_lower.startswith('6. postconditions:') or
              line_lower.startswith('7. postconditions:')):
            if current_field:
                fields[current_field] = '\n'.join(current_content).strip()
            current_field = 'postconditions'
            # Extract content after colon if present
            if ':' in line:
                content = line.split(':', 1)[1].strip()
                current_content = [content] if content else []
            else:
                current_content = []
            
        # Test Data patterns
        elif (line_lower.startswith('test data:') or
              line_lower.startswith('7. test data:') or
              line_lower.startswith('8. test data:')):
            if current_field:
                fields[current_field] = '\n'.join(current_content).strip()
            current_field = 'test_data'
            # Extract content after colon if present
            if ':' in line:
                content = line.split(':', 1)[1].strip()
                current_content = [content] if content else []
            else:
                current_content = []
            
        # Edge Cases patterns
        elif (line_lower.startswith('edge cases:') or
              line_lower.startswith('8. edge cases:') or
              line_lower.startswith('9. edge cases:')):
            if current_field:
                fields[current_field] = '\n'.join(current_content).strip()
            current_field = 'edge_cases'
            # Extract content after colon if present
            if ':' in line:
                content = line.split(':', 1)[1].strip()
                current_content = [content] if content else []
            else:
                current_content = []
            
        # Skip References, Observability, Traceability sections (not in our fields)
        elif (line_lower.startswith('references:') or
              line_lower.startswith('2. references:') or
              line_lower.startswith('observability:') or
              line_lower.startswith('9. observability:') or
              line_lower.startswith('10. observability:') or
              line_lower.startswith('traceability:') or
              line_lower.startswith('10. traceability:') or
              line_lower.startswith('11. traceability:')):
            # These sections are not captured in our fields, skip them
            if current_field:
                fields[current_field] = '\n'.join(current_content).strip()
            current_field = None
            current_content = []
            
        else:
            # Add content to current field
            if current_field:
                current_content.append(line)
    
    # Save last field
    if current_field:
        fields[current_field] = '\n'.join(current_content).strip()
    
    # Clean up fields and provide defaults for empty ones
    for key, value in fields.items():
        if not value or value.isspace():
            fields[key] = 'N/A'
        else:
            fields[key] = value.strip()
    
    return fields

# Sanitize text for CSV
def sanitize_csv_text(text: str) -> str:
    """
    Sanitize text for proper CSV formatting
    --------------------------------------------------
    text: str - Raw text that may contain newlines, quotes, etc.
    returns: str - Sanitized text safe for CSV
    """
    if not text:
        return ''
    
    # Replace actual newlines with literal \n for better readability
    # This keeps the structure visible but prevents CSV corruption
    sanitized = text.replace('\n', ' | ').replace('\r', '')
    
    # Remove excessive whitespace and clean up
    sanitized = ' '.join(sanitized.split())
    
    # Replace multiple pipe separators with single ones
    while ' |  | ' in sanitized:
        sanitized = sanitized.replace(' |  | ', ' | ')
    
    return sanitized.strip()

# Create CSV file with all test cases
def create_csv_file(results: List[Dict[str, Any]], output_file: Path) -> None:
    """
    Create CSV file with all test cases
    --------------------------------------------------
    results: List[Dict[str, Any]] - List of test case results
    output_file: Path - Path to save the CSV file
    """
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        # Define CSV columns
        fieldnames = [
            'Requirement_ID',
            'Status',
            'Timestamp',
            'Test_Case_Title',
            'Objective',
            'Preconditions',
            'Test_Steps',
            'Expected_Result',
            'Postconditions',
            'Test_Data',
            'Edge_Cases',
            'Full_Test_Case',
            'Error'
        ]
        
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        
        for result in results:
            req_id = result.get('requirement_id', 'UNKNOWN')
            status = result.get('status', 'unknown')
            timestamp = result.get('timestamp', '')
            test_case = result.get('test_case', '')
            error = result.get('error', '')
            
            # Parse test case fields
            parsed = parse_test_case_fields(test_case)
            
            row = {
                'Requirement_ID': sanitize_csv_text(req_id),
                'Status': sanitize_csv_text(status),
                'Timestamp': sanitize_csv_text(timestamp),
                'Test_Case_Title': sanitize_csv_text(parsed['title']),
                'Objective': sanitize_csv_text(parsed['objective']),
                'Preconditions': sanitize_csv_text(parsed['preconditions']),
                'Test_Steps': sanitize_csv_text(parsed['test_steps']),
                'Expected_Result': sanitize_csv_text(parsed['expected_result']),
                'Postconditions': sanitize_csv_text(parsed['postconditions']),
                'Test_Data': sanitize_csv_text(parsed['test_data']),
                'Edge_Cases': sanitize_csv_text(parsed['edge_cases']),
                'Full_Test_Case': sanitize_csv_text(test_case),
                'Error': sanitize_csv_text(error)
            }
            
            writer.writerow(row)
    
    print(f"✓ Created CSV file: {output_file.name}")

# Main conversion function
def main():
    """Main conversion function"""
    print("\n" + "=" * 80)
    print("Test Case Results Converter")
    print("=" * 80 + "\n")
    

    # Get input file from command line or use default
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        
        input_file = "output/batch_requirements.json"
        filename_checkpoint = input(f"No File Name Provided. Press Enter to use default '{input_file}': ")
        # Check if user provided a new file name
        if filename_checkpoint:
            input_file = filename_checkpoint

    # Load results
    results = load_json_results(input_file)
    
    # Create output directories
    base_name = Path(input_file).stem
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    output_base = Path("converted") / f"{base_name}_{timestamp}"
    txt_dir = output_base / "txt"
    md_dir = output_base / "md"
    csv_dir = output_base / "csv"
    
    txt_dir.mkdir(parents=True, exist_ok=True)
    md_dir.mkdir(parents=True, exist_ok=True)
    csv_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\nOutput directory: {output_base}\n")
    
    # Generate TXT files
    print("Creating TXT files...")
    for result in results:
        create_txt_file(result, txt_dir)
    
    print(f"✓ Created {len(results)} TXT files in {txt_dir}\n")
    
    # Generate MD files
    print("Creating Markdown files...")
    for result in results:
        create_md_file(result, md_dir)
    
    print(f"✓ Created {len(results)} MD files in {md_dir}\n")
    
    # Generate CSV file
    print("Creating CSV file...")
    csv_file = csv_dir / f"{base_name}.csv"
    create_csv_file(results, csv_file)
    print(f"  Total rows: {len(results) + 1} (including header)\n")
    
    # Summary
    print("=" * 80)
    print("CONVERSION COMPLETE")
    print("=" * 80)
    print(f"\nSummary:")
    print(f"  Input file: {input_file}")
    print(f"  Test cases processed: {len(results)}")
    print(f"  TXT files: {txt_dir}")
    print(f"  MD files: {md_dir}")
    print(f"  CSV file: {csv_file}")
    print(f"\n✓ All conversions completed successfully!\n")


if __name__ == "__main__":
    main()
