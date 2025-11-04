#!/bin/bash

"""
Test script for Test Case Generator API
Tests all major endpoints and validates responses
"""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
API_URL="http://localhost:5000"
TIMEOUT=300

# Counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Test functions
test_endpoint() {
    local test_name=$1
    local method=$2
    local endpoint=$3
    local data=$4
    local expected_status=$5
    
    TESTS_RUN=$((TESTS_RUN + 1))
    
    echo -e "\n${YELLOW}Test ${TESTS_RUN}: ${test_name}${NC}"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" -X GET "$API_URL$endpoint")
    elif [ "$method" = "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    # Extract status code
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "$expected_status" ]; then
        echo -e "${GREEN}✓ PASSED${NC} (HTTP $http_code)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        
        # Show body snippet if available
        if [ -n "$body" ]; then
            echo "$body" | jq '.' 2>/dev/null | head -20 || echo "$body" | head -20
        fi
    else
        echo -e "${RED}✗ FAILED${NC} (Expected $expected_status, got $http_code)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        echo "Response: $body"
    fi
}

echo "=========================================="
echo "Test Case Generator API - Test Suite"
echo "=========================================="
echo "Target: $API_URL"
echo "Timeout: ${TIMEOUT}s"

# Test 1: Health Check
test_endpoint "Health Check" "GET" "/health" "" "200"

# Test 2: List Models
test_endpoint "List Models" "GET" "/models" "" "200"

# Test 3: Get Instructions
test_endpoint "Get Instructions" "GET" "/instructions" "" "200"

# Test 4: Single Requirement - Missing Fields
test_endpoint "Generate - Missing Required Fields" "POST" "/generate" \
    '{"PARAMETER_CATEGORY": "TEST"}' "400"

# Test 5: Single Requirement - Valid
test_endpoint "Generate - Single Requirement" "POST" "/generate" \
    '{
        "REQUIREMENTS_ID": "REQ-TEST-001",
        "DESCRIPTION": "Test requirement for system integration testing.",
        "CATEGORY": "Functional",
        "PARAMETER_CATEGORY": "TEST CATEGORY",
        "PARENT_ID": "REQ-TEST",
        "VERIFICATION_PLAN": "Test",
        "VALIDATION_CRITERIA": "Verify behavior"
    }' "200"

# Test 6: Batch - Invalid Format
test_endpoint "Batch Generate - Invalid Format" "POST" "/generate/batch" \
    '{"invalid": "data"}' "400"

# Test 7: Batch - Empty Array
test_endpoint "Batch Generate - Empty Array" "POST" "/generate/batch" \
    '{"requirements": []}' "400"

# Test 8: Batch - Valid Multiple Requirements
test_endpoint "Batch Generate - Multiple Requirements" "POST" "/generate/batch" \
    '{
        "requirements": [
            {
                "REQUIREMENTS_ID": "REQ-BATCH-001",
                "DESCRIPTION": "First test requirement",
                "CATEGORY": "Functional"
            },
            {
                "REQUIREMENTS_ID": "REQ-BATCH-002",
                "DESCRIPTION": "Second test requirement",
                "CATEGORY": "Functional"
            }
        ]
    }' "200"

# Test 9: Update Instructions
test_endpoint "Update Instructions" "POST" "/instructions" \
    '{
        "instructions": "You are a test case generator for embedded systems. Generate detailed black-box test cases."
    }' "200"

# Test 10: Invalid Endpoint
test_endpoint "Invalid Endpoint" "GET" "/invalid/endpoint" "" "404"

# Summary
echo -e "\n=========================================="
echo -e "Test Summary"
echo -e "=========================================="
echo -e "Total Tests: $TESTS_RUN"
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"
echo -e "==========================================${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
fi
