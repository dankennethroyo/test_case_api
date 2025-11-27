#!/usr/bin/env python3
#####################################################################
#                       E M E R S O N   S O L A H D                 #
#                  Excel Requirements Transformer                   #
#####################################################################
"""
Transform requirements from Excel format to CSV/JSON for API consumption.
Reads Excel requirement documents and exports to standardized formats.
"""

import pandas as pd
import sys
import argparse
import os
from pathlib import Path

debug = True

def read_excel_to_dataframe(file_path):
    """
    Reads an Excel file and returns its content as a pandas DataFrame.
    
    Args:
        file_path (str): Path to the Excel file.
    
    Returns:
        pd.DataFrame: DataFrame containing the Excel data.
    """
    try:
        df = pd.read_excel(file_path)
        return df
    except FileNotFoundError:
        print(f"ERROR: File not found: {file_path}")
        return None
    except Exception as e:
        print(f"ERROR: Failed to read Excel file: {e}")
        return None


def transform_to_json_format(df):
    """
    Transform DataFrame to JSON format expected by the API.
    Wraps the list of requirements in {"requirements": [...]} structure.
    
    Args:
        df (pd.DataFrame): DataFrame containing requirements
        
    Returns:
        dict: JSON structure with requirements array
    """
    # Convert to list of dictionaries
    requirements_list = df.to_dict(orient='records')
    
    # Wrap in the expected format
    return {"requirements": requirements_list}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Transform Excel requirements to CSV/JSON format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview data only
  python transform_requirements.py --file Requirement_Document.xlsx
  
  # Generate output files
  python transform_requirements.py --file Requirement_Document.xlsx --output
  
  # Generate with custom output names
  python transform_requirements.py --file Requirement_Document.xlsx --output --csv custom.csv --json custom.json
        """
    )
    parser.add_argument("--file", default="Requirement_Document.xlsx", help="Path to the input Excel file")
    parser.add_argument("--output", action="store_true", help="Save to CSV and JSON files")
    parser.add_argument("--csv", help="Custom CSV output filename")
    parser.add_argument("--json", help="Custom JSON output filename")
    args = parser.parse_args()
    
    # Read Excel file
    print(f"\nReading Excel file: {args.file}")
    df = read_excel_to_dataframe(args.file)
    
    if df is None:
        sys.exit(1)
    
    print(f"✓ Loaded {len(df)} rows from Excel file\n")
    
    if debug: 
        print("DataFrame preview:")
        print(df.head())
        print()
    
    # Define required columns for the API
    selected_columns = [
        'PARAMETER_CATEGORY', 
        'PARENT_ID', 
        'REQUIREMENTS_ID', 
        'DESCRIPTION', 
        'CATEGORY', 
        'VERIFICATION_PLAN', 
        'VALIDATION_CRITERIA', 
        'Test_Case'
    ]
    
    # Create missing columns if they don't exist
    missing_columns = [col for col in selected_columns if col not in df.columns]
    if missing_columns:
        print(f"Adding missing columns: {', '.join(missing_columns)}")
        for col in missing_columns:
            df[col] = ''
    
    # Select only the required columns
    df_selected = df[selected_columns]
    
    # Remove commas from string columns to avoid CSV formatting issues
    df_selected = df_selected.apply(lambda x: x.str.replace(',', '') if x.dtype == 'object' else x)
    
    print("\nSelected columns for transformation:")
    for col in selected_columns:
        print(f"  - {col}")
    print()
    
    if debug: 
        print("Transformed DataFrame preview:")
        print(df_selected.head())
        print()
    
    if args.output:
        # Determine output filenames
        base_name = os.path.splitext(args.file)[0]
        csv_file = args.csv if args.csv else f"{base_name}.csv"
        json_file = args.json if args.json else f"{base_name}.json"
        
        # Save to CSV
        df_selected.to_csv(csv_file, index=False)
        print(f"✓ CSV saved to: {csv_file}")
        
        # Save to JSON with proper structure
        json_data = transform_to_json_format(df_selected)
        import json
        with open(json_file, 'w') as f:
            json.dump(json_data, f, indent=4)
        print(f"✓ JSON saved to: {json_file}")
        
        print(f"\n{'='*80}")
        print("TRANSFORMATION COMPLETE")
        print(f"{'='*80}")
        print(f"\nSummary:")
        print(f"  Input file: {args.file}")
        print(f"  Requirements processed: {len(df_selected)}")
        print(f"  CSV output: {csv_file}")
        print(f"  JSON output: {json_file}")
        print(f"\nReady for API consumption!")
        print(f"Use the JSON file with client.py for test case generation.\n")
    else:
        print("=" * 80)
        print("PREVIEW MODE")
        print("=" * 80)
        print("\nNo output files generated. Use --output flag to save files.")
        print("Example: python transform_requirements.py --file your_file.xlsx --output\n")
