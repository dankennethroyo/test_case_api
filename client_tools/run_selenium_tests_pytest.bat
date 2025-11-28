@echo off
REM Test Case Generator Selenium Test Runner using pytest
REM Runs the Selenium test suite against the deployed application

echo 🚀 Starting Selenium Test Suite for Test Case Generator
echo ============================================================

REM Change to the script directory
cd /d "%~dp0"

REM Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo No virtual environment found, using system Python
)

REM Run pytest with the selenium tests
echo Running pytest...
pytest selenium_tests/test_selenium_pytest.py

REM Check the exit code
if %ERRORLEVEL% EQU 0 (
    echo ✅ Test suite completed successfully
) else (
    echo ❌ Test suite failed with exit code %ERRORLEVEL%
)

echo ============================================================
echo Test reports generated:
echo - HTML Report: selenium_test_report.html
echo ============================================================

pause