#!/usr/bin/env python3
"""
Quick runner for Selenium Test Suite
Run comprehensive tests on the deployed Test Case Generator
"""

import subprocess
import sys
import os

def run_selenium_tests():
    """Run the Selenium test suite"""
    print("🚀 Starting Selenium Test Suite for Test Case Generator")
    print("=" * 60)

    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Check if selenium_test_suite.py exists in the same directory
    test_suite_path = os.path.join(script_dir, "selenium_test_suite.py")
    if not os.path.exists(test_suite_path):
        print("❌ Error: selenium_test_suite.py not found in selenium_tests directory")
        print(f"Expected path: {test_suite_path}")
        sys.exit(1)

    # Run the test suite
    try:
        cmd = [sys.executable, test_suite_path]
        print(f"Running: {' '.join(cmd)}")
        print("-" * 60)

        result = subprocess.run(cmd, capture_output=False, text=True, cwd=script_dir)

        print("-" * 60)
        if result.returncode == 0:
            print("✅ Test suite completed successfully")
        else:
            print("❌ Test suite failed")

        return result.returncode

    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1

if __name__ == "__main__":
    exit_code = run_selenium_tests()
    sys.exit(exit_code)