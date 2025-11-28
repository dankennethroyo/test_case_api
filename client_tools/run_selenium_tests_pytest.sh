#!/bin/bash
# Test Case Generator Selenium Test Runner using pytest
# Runs the Selenium test suite against the deployed application

echo "🚀 Starting Selenium Test Suite for Test Case Generator"
echo "============================================================"

# Change to the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment if it exists
if [ -f ".venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
else
    echo "No virtual environment found, using system Python"
fi

# Run pytest with the selenium tests
echo "Running pytest..."
pytest selenium_tests/test_selenium_pytest.py

# Check the exit code
if [ $? -eq 0 ]; then
    echo "✅ Test suite completed successfully"
else
    echo "❌ Test suite failed with exit code $?"
fi

echo "============================================================"
echo "Test reports generated:"
echo "- HTML Report: selenium_test_report.html"
echo "============================================================"