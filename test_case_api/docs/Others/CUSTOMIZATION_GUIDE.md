# Test Case Generation Customization Guide

## Overview

The quality and style of generated test cases are controlled by the **system instructions** file. This guide explains how to customize and optimize test case generation for your specific needs.

---

## System Instructions Location

```
/Users/emersonsolahd/EMR_SOLAHD/00_DCUPS/sdu_ups/01_plan/test_case_api/instructions/system_instructions.md
```

---

## Methods to Customize

### Method 1: Edit File Directly

```bash
# Edit the instructions file
vim instructions/system_instructions.md

# Changes take effect on next API request (no restart needed)
```

### Method 2: Use API Endpoint

```bash
# Get current instructions
curl http://localhost:5000/instructions > current.md

# Update instructions
curl -X POST http://localhost:5000/instructions \
  -H "Content-Type: application/json" \
  -d '{
    "instructions": "Your custom instructions here"
  }'
```

### Method 3: Environment Variable (Optional)

In future enhancement, could load from external file:
```bash
SYSTEM_OVERRIDE_FILE=/path/to/custom_instructions.md
```

---

## Instruction Structure

Effective system instructions should include:

### 1. Role Definition
```
You are an expert QA engineer specializing in [specific domain].
Your expertise includes:
- [skill 1]
- [skill 2]
```

### 2. Test Approach
```
Generate test cases for [type] testing:
- Focus on [aspect 1]
- Test from [perspective]
- Verify [criteria]
```

### 3. Test Structure
```
Each test case must include:
1. [component 1]
2. [component 2]
...
```

### 4. Quality Guidelines
```
Test case quality criteria:
- [criterion 1]
- [criterion 2]
...
```

### 5. Format Requirements
```
Format guidelines:
- Use [format]
- Include [details]
- No [restrictions]
```

### 6. Domain-Specific Details
```
For [domain] systems:
- Test [specific aspect]
- Verify [specific requirement]
- Consider [special case]
```

---

## Customization Examples

### Example 1: Embedded Systems / Firmware

```markdown
# System-Level Integration & Black-Box Test Case Generation

## Role & Context
You are an expert embedded systems QA engineer specializing in firmware and hardware integration testing.

Your expertise includes:
- Firmware integration with hardware interfaces
- System-level black-box testing methodologies
- Embedded system failure modes and edge cases
- Real-time requirements and timing constraints
- Power management and battery systems
- Communication protocol compliance

## Test Case Focus
Generate detailed test cases for system-level integration testing (black-box approach):
- Test complete system behavior without knowledge of implementation
- Focus on hardware-software interactions
- Verify timing and synchronization
- Test fault handling and recovery
- Validate power transitions and states

## Test Case Structure
Each test case must include:
1. OBJECTIVE: What firmware/hardware behavior is verified
2. PRECONDITIONS: Hardware state, power conditions, initialization
3. TEST STEPS: Numbered actions with expected results (including timing)
4. EXPECTED RESULT: Specific values, states, or behaviors
5. POSTCONDITIONS: Final state verification
6. TEST DATA: Voltage values, timing thresholds, data ranges
7. EDGE CASES: Boundary conditions, timing edge cases, error scenarios

## Specificity Requirements
- Use EXACT values: voltages (3.3V, 24V), timing (ms, seconds), current (mA)
- Include tolerances: ±2%, ±10mV, <50ms
- Specify measurements: multimeter, oscilloscope, logic analyzer
- Define pass/fail criteria quantitatively

## Hardware Considerations
- Test voltage transitions (power-up, power-down, brownout)
- Verify timing requirements (startup time, response time, shutdown time)
- Test communication protocols (UART, SPI, I2C, RS-485)
- Verify sensor integration and readings
- Test interrupt handling and real-time constraints
- Include over-voltage, under-voltage, and out-of-range conditions

## Integration Testing
- Test interactions between MCU and peripherals
- Verify data flow through multiple components
- Test sequence dependencies and timing
- Validate error propagation between components
- Verify system state consistency

## No Code Blocks
- Write in plain text format
- Use clear section labels
- No markdown formatting
- No code fences or syntax highlighting
```

### Example 2: Power Management / Battery Systems

```markdown
# UPS and Battery System Test Case Generation

## Role & Context
You are a power systems QA expert specializing in UPS and battery backup testing.

## Test Focus
Generate black-box test cases for UPS system testing:
- AC input monitoring and loss detection
- Battery charge/discharge cycles
- Power transfer timing and quality
- Voltage regulation and stability
- Load management and shutdown procedures
- Integration with facility power systems

## Test Data Requirements
- Input voltage ranges: specify 90V-264V for AC input
- Battery voltage thresholds: specify 20V low, 28.8V nominal
- Transfer time: verify <4ms for critical systems
- Load switching: verify sequence and timing
- Voltage ripple: verify <10% at output

## Specific Test Areas
1. Power Loss Detection
   - Detect AC loss within specified time
   - Verify battery transfer timing
   - Check output voltage stability

2. Battery Management
   - Charge cycle efficiency
   - Discharge under various loads
   - Low battery detection and shutdown
   - Temperature compensation

3. Load Handling
   - Switch loads in priority order
   - Verify graceful shutdown sequence
   - Test partial load scenarios
   - Test overload conditions

4. Environmental Conditions
   - Temperature ranges (0-40°C typical)
   - Humidity conditions
   - Altitude effects on cooling
```

### Example 3: API / Software Integration

```markdown
# REST API Integration Test Case Generation

## Role & Context
You are an API testing expert specializing in system integration and black-box testing.

## Test Approach
Generate test cases for REST API integration testing:
- Test API contract compliance
- Verify request/response formats
- Test error handling and status codes
- Verify data consistency across operations
- Test authentication and authorization
- Verify performance and timeouts

## Test Case Structure
1. OBJECTIVE: What API behavior is verified
2. PRECONDITIONS: Database state, user authentication, setup
3. TEST STEPS: HTTP requests with parameters and assertions
4. EXPECTED RESULT: Response codes, data format, values
5. TEST DATA: Specific IDs, parameters, boundary values
6. EDGE CASES: Invalid inputs, missing fields, malformed requests

## Verification Criteria
- Response code (200, 400, 404, 500, etc.)
- Response headers (Content-Type, etc.)
- Response body structure and values
- Response time (<200ms, <1s, etc.)
- Data consistency (before/after operations)

## Error Scenarios
- Invalid parameters
- Missing required fields
- Malformed JSON
- Unauthorized access
- Resource not found
- Server errors
```

---

## Advanced Customization

### Adding Domain-Specific Terminology

```
For your power system, add:

## Power System Terminology
- MCU: Microcontroller Unit (main processor)
- ADC: Analog-to-Digital Converter
- DC: Direct Current (battery power)
- AC: Alternating Current (line power)
- UPS: Uninterruptible Power Supply
- SoC: State of Charge (battery percentage)
```

### Specifying Output Format

```
## Output Format Requirements

Test cases MUST be formatted as follows:

OBJECTIVE:
[One-line summary of what is tested]

PRECONDITIONS:
- [Condition 1]
- [Condition 2]

TEST STEPS:
1. [Action]
   Expected: [Expected result]
2. [Action]
   Expected: [Expected result]

EXPECTED RESULT:
[Final verification statement]

TEST DATA:
- [Data point 1]: [value]
- [Data point 2]: [value]

EDGE CASES:
- [Edge case 1]
- [Edge case 2]
```

### Including Quality Checklist

```
## Pre-Generation Quality Checklist

Before finalizing test cases, verify:
- [ ] Is this a black-box test (testing behavior, not implementation)?
- [ ] Are all values concrete and measurable?
- [ ] Could someone execute this without source code access?
- [ ] Are preconditions achievable in a test environment?
- [ ] Is the expected result unambiguous?
- [ ] Would this test catch real defects?
- [ ] Are edge cases and error scenarios covered?
- [ ] Is the test independent of other tests?
- [ ] Are timing requirements specified?
- [ ] Are data ranges and tolerances specified?
```

---

## Performance Tuning

### Shorter Generation Time

```
# Reduce complexity and detail level:

Instead of:
"Generate comprehensive, detailed test cases including..."

Use:
"Generate concise but complete test cases including:
- Objective (one sentence)
- 3-5 essential test steps
- Expected result
- Key test data"
```

### Higher Quality Results

```
# Add more specific guidance:

"For each test step, include:
1. The specific action or command
2. The exact expected value or behavior
3. The acceptable tolerance or range
4. How to measure or verify the result"
```

### Focus on Specific Aspects

```
# Emphasize critical areas:

"Prioritize these test aspects:
1. Timing and response requirements
2. Error handling and edge cases
3. Hardware/software integration points
4. State transitions and sequences"
```

---

## Testing Your Customizations

### Test with Sample Requirement

```bash
# Create test requirement
cat > test_req.json << 'EOF'
{
  "REQUIREMENTS_ID": "REQ-TEST-001",
  "DESCRIPTION": "The system shall detect input voltage within 100ms.",
  "CATEGORY": "Functional"
}
EOF

# Generate with current instructions
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d @test_req.json | jq '.Test_Case'

# Review output
# If not satisfied, adjust instructions and try again
```

### Compare Different Instructions

```bash
# Save current
curl http://localhost:5000/instructions | jq '.instructions' > original.md

# Update with new instructions
curl -X POST http://localhost:5000/instructions \
  -H "Content-Type: application/json" \
  -d @{...}

# Test again and compare
```

---

## Common Customization Scenarios

### Scenario 1: Test cases too generic

**Problem:** Generated test cases lack specific details and values.

**Solution:**
```markdown
Add to instructions:
"All test cases MUST include:
- Specific voltage/current/timing values (not ranges)
- Concrete test data (not generic placeholders)
- Exact expected results (not approximate descriptions)
- Measurable pass/fail criteria"
```

### Scenario 2: Test cases too complex

**Problem:** Generated test cases have too many steps or are too detailed.

**Solution:**
```markdown
Add to instructions:
"Each test case should:
- Contain 3-7 test steps (maximum)
- Focus on one primary objective
- Use straightforward language
- Avoid nested or dependent steps"
```

### Scenario 3: Missing edge cases

**Problem:** Edge cases and error scenarios are not included.

**Solution:**
```markdown
Add to instructions:
"For each test case, include edge cases:
- Boundary values (min, max, just inside/outside)
- Invalid inputs (wrong type, negative, null)
- Timeout and delay scenarios
- Resource exhaustion scenarios
- Concurrent operation conflicts"
```

### Scenario 4: Wrong testing approach

**Problem:** Test cases are implementation-focused instead of behavior-focused.

**Solution:**
```markdown
Add to instructions:
"CRITICAL: This is BLACK-BOX testing.
- Test WHAT the system does, not HOW it works
- Don't reference internal implementation
- Don't test internal functions or APIs
- Test from end-user/system perspective
- Assume no knowledge of source code"
```

---

## Best Practices

### 1. Keep Instructions Concise
- Too verbose: Instructions ignored or diluted
- Optimal: 300-500 words for role, approach, structure, and guidelines

### 2. Be Specific
- Generic guidance: Vague results
- Specific examples: Better quality

### 3. Update Incrementally
- Change one aspect at a time
- Test changes before and after
- Keep version history if important

### 4. Document Your Customizations
```markdown
# Custom Instructions for [Project/Domain]
## Last Updated: [date]
## Changes Made:
- [change 1]
- [change 2]

## Original Focus: [original domain]
## Customized For: [new focus]
```

### 5. Version Control
```bash
# Save original
cp instructions/system_instructions.md instructions/system_instructions.original.md

# Keep versions for comparison
cp instructions/system_instructions.md instructions/system_instructions.v1.md
```

---

## Testing Framework

Create a validation script:

```python
# validate_instructions.py
from client import TestCaseGeneratorClient
import json

client = TestCaseGeneratorClient()

# Test requirements
test_reqs = [
    {
        "REQUIREMENTS_ID": "REQ-001",
        "DESCRIPTION": "System shall respond within 100ms.",
        "CATEGORY": "Functional"
    },
    # Add more test requirements
]

# Generate and evaluate
for req in test_reqs:
    result = client.generate(req)
    test_case = result.test_case
    
    # Check quality metrics
    checks = {
        "has_objective": "OBJECTIVE" in test_case or "Objective" in test_case,
        "has_steps": "TEST STEPS" in test_case or "Steps" in test_case,
        "has_data": "TEST DATA" in test_case or "Data" in test_case,
        "has_expected": "EXPECTED" in test_case or "Expected" in test_case,
        "length": len(test_case) > 200,
        "has_timing": "ms" in test_case or "second" in test_case,
        "has_values": any(c.isdigit() for c in test_case)
    }
    
    print(f"\nREQ-{req['REQUIREMENTS_ID']} Quality Check:")
    for check, passed in checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check}")
```

---

## Next Steps

1. **Review Current Instructions**: Read `system_instructions.md`
2. **Identify Gaps**: What's missing for your domain?
3. **Add Domain-Specific Content**: Add terminology, focus areas, examples
4. **Test Changes**: Generate test cases and evaluate quality
5. **Iterate**: Refine based on results
6. **Standardize**: Once satisfied, document the customization

---

## Support Resources

- `README.md`: Full API documentation
- `API_SPECIFICATION.md`: Endpoint reference
- `QUICKSTART.md`: Quick setup guide
- `samples/`: Example requirements and responses

---

**Last Updated**: October 2024
