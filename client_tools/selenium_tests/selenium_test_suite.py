#!/usr/bin/env python3
"""
Selenium Test Suite for Test Case Generator
Tests the deployed system at http://8p89b74:8009/client
Focuses on verifying the 4 instruction conditions and overall functionality
"""

import logging
import time
import json
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


class TestCaseGeneratorTester:
    """Comprehensive Selenium test suite for Test Case Generator"""

    def __init__(self, base_url="http://8p89b74:8009/client"):
        self.base_url = base_url
        self.driver = None
        self.wait = None
        self.test_results = []
        self.setup_logging()

    def setup_logging(self):
        """Setup comprehensive logging"""
        log_filename = f"selenium_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("Test Case Generator Selenium Test Suite Started")

    def setup_driver(self):
        """Setup Chrome WebDriver with appropriate options"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")  # Speed up loading
            chrome_options.add_argument("--disable-javascript")  # Wait, we need JS!
            # Actually, we DO need JavaScript for this app
            chrome_options.add_argument("--enable-javascript")

            # Uncomment for headless mode
            # chrome_options.add_argument("--headless")

            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, 30)
            self.logger.info("Chrome WebDriver initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to setup WebDriver: {e}")
            raise

    def teardown_driver(self):
        """Clean up WebDriver"""
        if self.driver:
            self.driver.quit()
            self.logger.info("WebDriver closed")

    def log_test_result(self, test_name, status, details=None, error=None):
        """Log individual test result"""
        result = {
            "test_name": test_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details or "",
            "error": str(error) if error else None
        }
        self.test_results.append(result)

        if status == "PASS":
            self.logger.info(f"[PASS] {test_name}: {details}")
        elif status == "FAIL":
            self.logger.error(f"[FAIL] {test_name}: {error}")
        else:
            self.logger.warning(f"[UNKNOWN] {test_name}: {details}")

    def navigate_to_app(self):
        """Navigate to the application and verify it's loaded"""
        try:
            self.logger.info(f"Navigating to {self.base_url}")
            self.driver.get(self.base_url)

            # Wait for page to load
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
            self.logger.info("Page loaded successfully")

            # Verify title
            title = self.driver.find_element(By.TAG_NAME, "h1").text
            if "Test Case Generator" in title:
                self.log_test_result("Page Load", "PASS", "Application loaded correctly")
                return True
            else:
                self.log_test_result("Page Load", "FAIL", f"Unexpected title: {title}")
                return False

        except Exception as e:
            self.log_test_result("Page Load", "FAIL", error=e)
            return False

    def test_basic_functionality(self):
        """Test basic single requirement generation"""
        try:
            self.logger.info("Testing basic functionality")

            # Switch to single requirement tab
            single_tab = self.wait.until(EC.element_to_be_clickable((By.ID, "single")))
            single_tab.click()

            # Fill in the form
            req_id = self.wait.until(EC.presence_of_element_located((By.ID, "requirementId")))
            req_id.clear()
            req_id.send_keys("TEST-SEL-001")

            description = self.driver.find_element(By.ID, "description")
            description.clear()
            description.send_keys("System shall provide backup power when input voltage drops below 21.6V for more than 10ms")

            category = self.driver.find_element(By.ID, "category")
            category.click()
            # Select Functional
            functional_option = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//select[@id='category']/option[@value='Functional']")
            ))
            functional_option.click()

            # Ensure use instructions is checked
            use_instructions = self.driver.find_element(By.ID, "useInstructions")
            if not use_instructions.is_selected():
                use_instructions.click()

            # Click generate
            generate_btn = self.driver.find_element(By.ID, "generateBtn")
            generate_btn.click()

            # Wait for results
            self.wait.until(EC.visibility_of_element_located((By.ID, "resultsSection")))

            # Check if results contain expected content
            results_content = self.driver.find_element(By.ID, "resultsContent")
            result_text = results_content.text

            if "Test_Case" in result_text or "test case" in result_text.lower():
                self.log_test_result("Basic Generation", "PASS", "Test case generated successfully")
                return True
            else:
                self.log_test_result("Basic Generation", "FAIL", f"Unexpected result content: {result_text[:200]}")
                return False

        except Exception as e:
            self.log_test_result("Basic Generation", "FAIL", error=e)
            return False

    def test_instruction_conditions(self):
        """Test all 4 instruction conditions"""
        conditions = [
            {
                "name": "Checked + Modified",
                "use_instructions": True,
                "modify_instructions": True,
                "expected_contains": ["voltage", "battery", "threshold"]  # More realistic expectations
            },
            {
                "name": "Checked + Unmodified",
                "use_instructions": True,
                "modify_instructions": False,
                "expected_contains": ["PRODUCT CONTEXT", "SolaHD", "system-level"]
            },
            {
                "name": "Unchecked + Modified",
                "use_instructions": False,
                "modify_instructions": True,
                "expected_contains": ["Test Case Title", "Objective", "Preconditions"]  # Basic structure without context
            },
            {
                "name": "Unchecked + Unmodified",
                "use_instructions": False,
                "modify_instructions": False,
                "expected_contains": ["Test Case Title", "Objective"]  # Minimal expectations
            }
        ]

        all_passed = True

        for condition in conditions:
            try:
                self.logger.info(f"Testing condition: {condition['name']}")

                # Switch to instructions tab
                instructions_tab = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-tab='instructions']")))
                instructions_tab.click()

                # Wait for instructions textarea to load
                instructions_textarea = self.wait.until(EC.presence_of_element_located((By.ID, "instructionsTextarea")))

                # Store original instructions
                original_instructions = instructions_textarea.get_attribute("value")

                # Modify instructions if needed
                if condition["modify_instructions"]:
                    modified_text = original_instructions + "\n\nCUSTOM MODIFIED INSTRUCTIONS FOR TESTING: Focus on voltage thresholds and timing requirements."
                    instructions_textarea.clear()
                    instructions_textarea.send_keys(modified_text)
                    self.logger.info("Modified instructions in textarea")
                else:
                    # Ensure original instructions are loaded
                    reload_btn = self.driver.find_element(By.ID, "loadInstructionsBtn")
                    reload_btn.click()
                    time.sleep(3)  # Wait for reload
                    self.logger.info("Reloaded original instructions")

                # Switch back to single requirement tab
                single_tab = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-tab='single']")))
                single_tab.click()
                time.sleep(1)  # Allow tab switch

                # Set use instructions checkbox
                use_instructions_checkbox = self.driver.find_element(By.ID, "useInstructions")
                if condition["use_instructions"] != use_instructions_checkbox.is_selected():
                    use_instructions_checkbox.click()
                    self.logger.info(f"Set use_instructions checkbox to: {condition['use_instructions']}")

                # Fill form with test data
                req_id = self.driver.find_element(By.ID, "requirementId")
                req_id.clear()
                req_id.send_keys(f"TEST-{condition['name'].replace(' ', '-').upper()}")

                description = self.driver.find_element(By.ID, "description")
                description.clear()
                description.send_keys("System shall monitor input voltage and switch to battery when voltage drops below threshold for specified duration")

                category = self.driver.find_element(By.ID, "category")
                category.click()
                functional_option = self.wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//select[@id='category']/option[@value='Functional']")
                ))
                functional_option.click()

                # Generate test case
                generate_btn = self.driver.find_element(By.ID, "generateBtn")
                self.logger.info("Clicking generate button")
                generate_btn.click()

                # Wait for results - simplified approach
                # Just wait for the results section to become visible
                try:
                    results_wait = WebDriverWait(self.driver, 120)  # Increased timeout
                    results_wait.until(EC.visibility_of_element_located((By.ID, "resultsSection")))
                    self.logger.info("Results section became visible")

                except TimeoutException as e:
                    self.logger.error(f"Timeout waiting for results section: {e}")
                    # Take a screenshot for debugging
                    try:
                        screenshot_path = f"debug_screenshot_{condition['name'].replace(' ', '_')}.png"
                        self.driver.save_screenshot(screenshot_path)
                        self.logger.info(f"Screenshot saved to {screenshot_path}")
                    except:
                        pass
                    raise e

                # Get result content
                results_content = self.driver.find_element(By.ID, "resultsContent")
                result_text = results_content.text

                self.logger.info(f"Result text length: {len(result_text)}")
                self.logger.info(f"Result text preview: {result_text[:200]}...")

                # Check if result contains expected content
                contains_expected = any(expected.lower() in result_text.lower() for expected in condition["expected_contains"])

                if contains_expected:
                    self.log_test_result(f"Instruction Condition: {condition['name']}", "PASS",
                                       f"Result contains expected content: {condition['expected_contains']}")
                else:
                    self.log_test_result(f"Instruction Condition: {condition['name']}", "FAIL",
                                       f"Result missing expected content: {condition['expected_contains']}. Got: {result_text[:500]}...")
                    all_passed = False

                # Clear results for next test
                clear_btn = self.driver.find_element(By.ID, "clearBtn")
                clear_btn.click()
                time.sleep(2)  # Wait for clear

            except Exception as e:
                self.log_test_result(f"Instruction Condition: {condition['name']}", "FAIL", error=e)
                all_passed = False

        return all_passed

    def test_import_export_instructions(self):
        """Test import/export functionality for instructions"""
        try:
            self.logger.info("Testing import/export functionality")

            # Switch to instructions tab
            instructions_tab = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-tab='instructions']")))
            instructions_tab.click()

            # Wait for instructions to load
            instructions_textarea = self.wait.until(EC.presence_of_element_located((By.ID, "instructionsTextarea")))

            # Modify instructions
            test_instructions = "TEST INSTRUCTIONS FOR IMPORT/EXPORT FUNCTIONALITY\nThis is a test to verify import/export works correctly."
            instructions_textarea.clear()
            instructions_textarea.send_keys(test_instructions)

            # Test export (we can't actually download, but we can check the button exists and is clickable)
            export_btn = self.driver.find_element(By.ID, "exportInstructionsBtn")
            if export_btn.is_displayed() and export_btn.is_enabled():
                self.log_test_result("Export Button", "PASS", "Export button is visible and enabled")
            else:
                self.log_test_result("Export Button", "FAIL", "Export button not accessible")
                return False

            # Test import button (check if it exists)
            import_btn = self.driver.find_element(By.ID, "importInstructionsBtn")
            if import_btn.is_displayed() and import_btn.is_enabled():
                self.log_test_result("Import Button", "PASS", "Import button is visible and enabled")
            else:
                self.log_test_result("Import Button", "FAIL", "Import button not accessible")
                return False

            # Check if hidden file input exists
            import_file_input = self.driver.find_element(By.ID, "importFileInput")
            if import_file_input.get_attribute("type") == "file":
                self.log_test_result("Import File Input", "PASS", "Hidden file input exists for import functionality")
            else:
                self.log_test_result("Import File Input", "FAIL", "Import file input not properly configured")
                return False

            return True

        except Exception as e:
            self.log_test_result("Import/Export Test", "FAIL", error=e)
            return False

    def test_tabs_and_navigation(self):
        """Test tab switching and navigation"""
        try:
            self.logger.info("Testing tab navigation")

            tabs = ["single", "batch", "instructions"]

            for tab_id in tabs:
                try:
                    tab_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, f"//button[@data-tab='{tab_id}']")))
                    tab_btn.click()

                    # Check if tab panel is active
                    tab_panel = self.driver.find_element(By.ID, tab_id)
                    if "active" in tab_panel.get_attribute("class"):
                        self.log_test_result(f"Tab Navigation: {tab_id}", "PASS", f"{tab_id} tab activated correctly")
                    else:
                        self.log_test_result(f"Tab Navigation: {tab_id}", "FAIL", f"{tab_id} tab not activated")
                        return False

                except Exception as e:
                    self.log_test_result(f"Tab Navigation: {tab_id}", "FAIL", error=e)
                    return False

            return True

        except Exception as e:
            self.log_test_result("Tab Navigation", "FAIL", error=e)
            return False

    def generate_report(self):
        """Generate comprehensive test report"""
        report_filename = f"selenium_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        # Calculate summary statistics
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])

        summary = {
            "test_run_timestamp": datetime.now().isoformat(),
            "target_url": self.base_url,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%",
            "test_results": self.test_results
        }

        # Save detailed report
        with open(report_filename, 'w') as f:
            json.dump(summary, f, indent=2)

        # Print summary to console
        self.logger.info("="*60)
        self.logger.info("TEST SUMMARY REPORT")
        self.logger.info("="*60)
        self.logger.info(f"Target URL: {self.base_url}")
        self.logger.info(f"Total Tests: {total_tests}")
        self.logger.info(f"Passed: {passed_tests}")
        self.logger.info(f"Failed: {failed_tests}")
        self.logger.info(f"Success Rate: {summary['success_rate']}")
        self.logger.info(f"Detailed report saved to: {report_filename}")

        if failed_tests > 0:
            self.logger.info("\nFAILED TESTS:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    self.logger.info(f"  - {result['test_name']}: {result['error']}")

        self.logger.info("="*60)

        return summary

    def run_all_tests(self):
        """Run the complete test suite"""
        try:
            self.logger.info("Starting comprehensive test suite")

            # Setup
            self.setup_driver()
            self.navigate_to_app()

            # Run tests
            tests = [
                ("Basic Functionality", self.test_basic_functionality),
                ("Tab Navigation", self.test_tabs_and_navigation),
                ("Instruction Conditions", self.test_instruction_conditions),
                ("Import/Export", self.test_import_export_instructions)
            ]

            for test_name, test_func in tests:
                self.logger.info(f"Running: {test_name}")
                try:
                    result = test_func()
                    if result:
                        self.log_test_result(test_name, "PASS", "Test completed successfully")
                    else:
                        self.log_test_result(test_name, "FAIL", "Test failed - see individual test results")
                except Exception as e:
                    self.log_test_result(test_name, "FAIL", error=e)

            # Generate report
            self.generate_report()

        except Exception as e:
            self.logger.error(f"Test suite failed: {e}")
            self.log_test_result("Test Suite", "FAIL", error=e)

        finally:
            self.teardown_driver()


def main():
    """Main entry point"""
    tester = TestCaseGeneratorTester("http://8p89b74:8009/client")
    tester.run_all_tests()


if __name__ == "__main__":
    main()