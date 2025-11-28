"""
Test Case Generator Selenium Test Suite using pytest
Tests the deployed web application at http://8p89b74:8009/client
"""

import pytest
import json
import time
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# Setup logging for pytest compatibility
import os
from datetime import datetime

log_file = os.path.join(os.path.dirname(__file__), 'test_results.log')

def log_message(message, level="INFO"):
    """Custom logging function that works with pytest"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"{timestamp} - {level} - {message}\n"

    # Write to file
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(log_entry)

    # Also print to console for pytest -s
    print(f"{timestamp} - {level} - {message}")

logger = log_message


@pytest.fixture(scope="session")
def driver():
    """Setup Chrome WebDriver for the test session"""
    log_message("Setting up Chrome WebDriver for test session")
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Commented out to show browser window
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    log_message("Chrome WebDriver initialized successfully")

    yield driver

    log_message("Closing Chrome WebDriver")
    driver.quit()


@pytest.fixture
def base_url():
    """Base URL for the test case generator application"""
    return "http://8p89b74:8009/client"


@pytest.fixture
def wait(driver):
    """WebDriverWait instance with default timeout"""
    return WebDriverWait(driver, 30)


def navigate_to_app(driver, base_url, wait):
    """Navigate to the application and verify it's loaded"""
    log_message(f"Navigating to application at {base_url}")
    driver.get(base_url)

    # Wait for page to load
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
    log_message("Page loaded successfully")

    # Verify title
    title = driver.find_element(By.TAG_NAME, "h1").text
    assert "Test Case Generator" in title, f"Unexpected title: {title}"
    log_message(f"Page title verified: {title}")


def test_page_load(driver, base_url, wait):
    """Test that the application loads correctly"""
    log_message("Starting test_page_load")
    navigate_to_app(driver, base_url, wait)

    # Verify title
    title = driver.find_element(By.TAG_NAME, "h1").text
    assert "Test Case Generator" in title
    log_message("test_page_load passed")


def test_basic_functionality(driver, base_url, wait):
    """Test basic single requirement generation"""
    log_message("Starting test_basic_functionality")
    navigate_to_app(driver, base_url, wait)

    # Switch to single requirement tab
    single_tab = wait.until(EC.element_to_be_clickable((By.ID, "single")))
    single_tab.click()
    log_message("Switched to single requirement tab")

    # Fill in the form
    req_id = wait.until(EC.presence_of_element_located((By.ID, "requirementId")))
    req_id.clear()
    req_id.send_keys("TEST-SEL-001")
    log_message("Filled requirement ID")

    description = driver.find_element(By.ID, "description")
    description.clear()
    description.send_keys("System shall provide backup power when input voltage drops below 21.6V for more than 10ms")
    log_message("Filled description")

    category = driver.find_element(By.ID, "category")
    category.click()
    # Select Functional
    functional_option = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//select[@id='category']/option[@value='Functional']")
    ))
    functional_option.click()
    log_message("Selected Functional category")

    # Ensure use instructions is checked
    use_instructions = driver.find_element(By.ID, "useInstructions")
    if not use_instructions.is_selected():
        use_instructions.click()
        log_message("Checked use instructions")

    # Click generate
    generate_btn = driver.find_element(By.ID, "generateBtn")
    generate_btn.click()
    log_message("Clicked generate button")

    # Wait for results
    wait.until(EC.visibility_of_element_located((By.ID, "resultsSection")))
    log_message("Results section appeared")

    # Check if results contain expected content
    results_content = driver.find_element(By.ID, "resultsContent")
    result_text = results_content.text

    assert "Test_Case" in result_text or "test case" in result_text.lower(), f"Unexpected result content: {result_text[:200]}"
    log_message("test_basic_functionality passed")


def test_tabs_and_navigation(driver, base_url, wait):
    """Test tab switching and navigation"""
    log_message("Starting test_tabs_and_navigation")
    navigate_to_app(driver, base_url, wait)

    tabs = ["single", "batch", "instructions"]

    for tab_id in tabs:
        tab_btn = wait.until(EC.element_to_be_clickable((By.XPATH, f"//button[@data-tab='{tab_id}']")))
        tab_btn.click()
        log_message(f"Clicked {tab_id} tab")

        # Check if tab panel is active
        tab_panel = driver.find_element(By.ID, tab_id)
        assert "active" in tab_panel.get_attribute("class"), f"{tab_id} tab not activated"
        log_message(f"{tab_id} tab activated successfully")

    log_message("test_tabs_and_navigation passed")


@pytest.mark.parametrize("condition_name,use_instructions,modify_instructions,expected_contains", [
    ("Checked + Modified", True, True, ["voltage", "battery", "threshold", "Test Case Title", "Objective"]),
    ("Checked + Unmodified", True, False, ["Test Case Title", "Objective", "References", "Preconditions"]),
    ("Unchecked + Modified", False, True, ["Test Case Title", "Objective", "Preconditions"]),
    ("Unchecked + Unmodified", False, False, ["Test Case", "Requirement", "Test Steps"]),
])
def test_instruction_conditions(driver, base_url, wait, condition_name, use_instructions, modify_instructions, expected_contains):
    """Test all 4 instruction conditions"""
    log_message(f"Starting test_instruction_conditions for {condition_name}")
    navigate_to_app(driver, base_url, wait)

    # Switch to instructions tab
    instructions_tab = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-tab='instructions']")))
    instructions_tab.click()
    log_message("Switched to instructions tab")

    # Wait for instructions textarea to load
    instructions_textarea = wait.until(EC.presence_of_element_located((By.ID, "instructionsTextarea")))
    log_message("Instructions textarea loaded")

    # Store original instructions
    original_instructions = instructions_textarea.get_attribute("value")

    # Modify instructions if needed
    if modify_instructions:
        modified_text = original_instructions + "\n\nCUSTOM MODIFIED INSTRUCTIONS FOR TESTING: Focus on voltage thresholds and timing requirements."
        instructions_textarea.clear()
        instructions_textarea.send_keys(modified_text)
        log_message("Modified instructions")
    else:
        log_message("Using unmodified instructions")

    # Switch back to single requirement tab
    single_tab = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-tab='single']")))
    single_tab.click()
    time.sleep(1)  # Allow tab switch
    log_message("Switched back to single requirement tab")

    # Set use instructions checkbox
    use_instructions_checkbox = driver.find_element(By.ID, "useInstructions")
    if use_instructions != use_instructions_checkbox.is_selected():
        use_instructions_checkbox.click()
        log_message(f"Set use_instructions to {use_instructions}")

    # Fill form with test data
    req_id = driver.find_element(By.ID, "requirementId")
    req_id.clear()
    req_id.send_keys(f"TEST-{condition_name.replace(' ', '-').upper()}")
    log_message("Filled requirement ID")

    description = driver.find_element(By.ID, "description")
    description.clear()
    description.send_keys("System shall monitor input voltage and switch to battery when voltage drops below threshold for specified duration")
    log_message("Filled description")

    category = driver.find_element(By.ID, "category")
    category.click()
    functional_option = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//select[@id='category']/option[@value='Functional']")
    ))
    functional_option.click()
    log_message("Selected Functional category")

    # Generate test case - try calling the JavaScript handler directly
    driver.execute_script("""
        const form = document.getElementById('singleForm');
        const event = new Event('submit', { bubbles: true, cancelable: true });
        form.dispatchEvent(event);
    """)
    log_message("Dispatched form submit event")

    # Wait for progress overlay to appear (indicating generation started)
    progress_wait = WebDriverWait(driver, 10)
    try:
        progress_wait.until(EC.visibility_of_element_located((By.ID, "progressOverlay")))
        log_message(f"Progress overlay appeared for {condition_name}")
    except TimeoutException:
        log_message(f"Progress overlay did not appear for {condition_name}", "WARNING")

    # Wait for progress overlay to disappear (indicating generation completed)
    try:
        progress_wait.until(EC.invisibility_of_element_located((By.ID, "progressOverlay")))
        log_message(f"Progress overlay disappeared for {condition_name}")
    except TimeoutException:
        log_message(f"Progress overlay did not disappear for {condition_name}", "WARNING")

    # Wait for results - with shorter timeout first
    results_wait = WebDriverWait(driver, 60)  # Reduced timeout
    results_wait.until(EC.visibility_of_element_located((By.ID, "resultsSection")))

    # Get result content
    results_content = driver.find_element(By.ID, "resultsContent")
    result_text = results_content.text

    # Log the actual result for debugging
    log_message(f"Generated result for {condition_name}: {result_text[:500]}...")

    # Check if result contains expected content
    contains_expected = any(expected.lower() in result_text.lower() for expected in expected_contains)
    assert contains_expected, f"Result missing expected content: {expected_contains}. Got: {result_text[:500]}..."
    log_message(f"test_instruction_conditions passed for {condition_name}")


def test_import_export_instructions(driver, base_url, wait):
    """Test import/export functionality for instructions"""
    log_message("Starting test_import_export_instructions")
    navigate_to_app(driver, base_url, wait)

    # Switch to instructions tab
    instructions_tab = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-tab='instructions']")))
    instructions_tab.click()
    log_message("Switched to instructions tab")

    # Wait for instructions to load
    instructions_textarea = wait.until(EC.presence_of_element_located((By.ID, "instructionsTextarea")))
    log_message("Instructions textarea loaded")

    # Wait for export button to be visible
    export_btn = wait.until(EC.visibility_of_element_located((By.ID, "exportInstructionsBtn")))
    assert export_btn.is_displayed() and export_btn.is_enabled(), "Export button not accessible"
    log_message("Export button is accessible")

    # Test import button exists and is accessible
    import_btn = driver.find_element(By.ID, "importInstructionsBtn")
    assert import_btn.is_displayed() and import_btn.is_enabled(), "Import button not accessible"
    log_message("Import button is accessible")

    # Check if hidden file input exists
    import_file_input = driver.find_element(By.ID, "importFileInput")
    assert import_file_input.get_attribute("type") == "file", "Import file input not properly configured"
    log_message("Import file input is properly configured")

    log_message("test_import_export_instructions passed")