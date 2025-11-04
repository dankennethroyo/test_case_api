# Test Case Results Converter

## Overview

The `convert_results.py` script converts test case generation results from JSON format into multiple output formats for easy review and integration:

- **Individual TXT files** - Plain text files for each test case
- **Individual MD files** - Markdown files for each test case (formatted, version control friendly)
- **Tabulated CSV file** - Spreadsheet-compatible format with parsed fields

## Usage

### Basic Usage (Default Input File)

```bash
python convert_results.py
```

This will process the default file: `output/batch_requirements.json`

### Specify Input File

```bash
python convert_results.py path/to/your/results.json
```

## Output Structure

The script creates a timestamped directory structure:

```
converted/
└── batch_requirements_20251020_153000/
    ├── txt/
    │   ├── REQ-001-01.txt
    │   ├── REQ-001-02.txt
    │   └── REQ-001-03.txt
    ├── md/
    │   ├── REQ-001-01.md
    │   ├── REQ-001-02.md
    │   └── REQ-001-03.md
    └── csv/
        └── batch_requirements.csv
```

## Output Formats

### 1. TXT Files

Plain text format with clear sections:

```
================================================================================
REQUIREMENT ID: REQ-001-01
================================================================================

Status: success
Generated: 2025-10-20T15:39:38.926120

--------------------------------------------------------------------------------
TEST CASE
--------------------------------------------------------------------------------

Test Case Title: Input Voltage Sensing Test
Objective: To verify that the MCU correctly senses...
[... full test case content ...]
```

### 2. Markdown Files

GitHub-friendly markdown format:

```markdown
# Test Case: REQ-001-01

## Metadata

- **Requirement ID**: REQ-001-01
- **Status**: success
- **Generated**: 2025-10-20T15:39:38.926120

---

## Test Case Details

Test Case Title: Input Voltage Sensing Test
Objective: To verify that the MCU correctly senses...
[... full test case content ...]
```

### 3. CSV File

Spreadsheet format with parsed fields:

| Requirement_ID | Status | Timestamp | Test_Case_Title | Objective | Preconditions | Test_Steps | Expected_Result | Postconditions | Test_Data | Edge_Cases | Full_Test_Case | Error |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| REQ-001-01 | success | 2025-10-20... | Input Voltage... | To verify... | The system is... | 1. Apply... | The MCU... | The system... | Input voltages... | The test... | [full text] | |

## CSV Columns

The CSV file includes the following columns:

1. **Requirement_ID** - Unique requirement identifier
2. **Status** - success/failed
3. **Timestamp** - When the test case was generated
4. **Test_Case_Title** - Parsed title from test case
5. **Objective** - What the test verifies
6. **Preconditions** - Setup required before testing
7. **Test_Steps** - Detailed test procedure
8. **Expected_Result** - Expected outcome
9. **Postconditions** - Cleanup/verification after test
10. **Test_Data** - Test values and parameters
11. **Edge_Cases** - Boundary conditions tested
12. **Full_Test_Case** - Complete unmodified test case text
13. **Error** - Error message (if status is failed)

## Features

- **Automatic parsing** - Extracts structured fields from test case text
- **Timestamped output** - Each conversion run creates a new timestamped directory
- **Error handling** - Gracefully handles missing or malformed data
- **Progress reporting** - Shows conversion progress and summary

## Requirements

- Python 3.6+
- No external dependencies (uses standard library only)

## Examples

### Convert Default File

```bash
python convert_results.py
```

Output:
```
================================================================================
Test Case Results Converter
================================================================================

✓ Loaded 3 test cases from output/batch_requirements.json

Output directory: converted/batch_requirements_20251020_153000

Creating TXT files...
  Created: REQ-001-01.txt
  Created: REQ-001-02.txt
  Created: REQ-001-03.txt
✓ Created 3 TXT files in converted/batch_requirements_20251020_153000/txt

Creating Markdown files...
  Created: REQ-001-01.md
  Created: REQ-001-02.md
  Created: REQ-001-03.md
✓ Created 3 MD files in converted/batch_requirements_20251020_153000/md

Creating CSV file...
✓ Created CSV file: batch_requirements.csv
  Total rows: 4 (including header)

================================================================================
CONVERSION COMPLETE
================================================================================

Summary:
  Input file: output/batch_requirements.json
  Test cases processed: 3
  TXT files: converted/batch_requirements_20251020_153000/txt
  MD files: converted/batch_requirements_20251020_153000/md
  CSV file: converted/batch_requirements_20251020_153000/csv/batch_requirements.csv

✓ All conversions completed successfully!
```

### Convert Custom File

```bash
python convert_results.py custom_results/my_test_cases.json
```

## Use Cases

1. **Documentation** - Export to TXT/MD for documentation systems
2. **Spreadsheet Analysis** - Import CSV into Excel/Google Sheets for analysis
3. **Version Control** - Track MD files in Git for test case history
4. **Archiving** - Save TXT files for long-term storage
5. **Integration** - Import CSV into test management tools

## Notes

- The script creates a new timestamped directory for each run to prevent overwrites
- Failed test cases will have their error messages in the CSV Error column
- The parser works best with test cases following the standard format
- All output files use UTF-8 encoding
