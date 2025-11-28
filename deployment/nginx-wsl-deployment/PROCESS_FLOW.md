# Test Case Generation Process Flow

```mermaid
flowchart TD
    A[User clicks 'Generate Test Case' button] --> B{Is 'Use Instructions' checkbox checked?}
    
    B -->|Yes| C{Have instructions been modified?}
    B -->|No| D{Have instructions been modified?}
    
    C -->|Yes| E[Use modified instructions as prompt<br/>webpage_instructions]
    C -->|No| F[Use full prompt<br/>System instructions + Product context + Structured guidelines]
    
    D -->|Yes| G[Use modified instructions as prompt<br/>webpage_instructions<br/>No system prompt]
    D -->|No| H[Use minimal prompt<br/>No product context<br/>No system prompt]
    
    E --> I[Build generation prompt<br/>webpage_instructions]
    F --> J[Build generation prompt<br/>Full context with product details]
    G --> K[Build generation prompt<br/>webpage_instructions]
    H --> L[Build generation prompt<br/>Minimal context]
    
    I --> M[Send request to backend<br/>use_instructions: true<br/>webpage_instructions: modified text]
    J --> N[Send request to backend<br/>use_instructions: true<br/>webpage_instructions: none]
    K --> O[Send request to backend<br/>use_instructions: false<br/>webpage_instructions: modified text]
    L --> P[Send request to backend<br/>use_instructions: false<br/>webpage_instructions: none]
    
    M --> Q[Backend: build_generation_prompt<br/>Returns webpage_instructions]
    N --> R[Backend: build_generation_prompt<br/>Returns full prompt]
    O --> S[Backend: build_generation_prompt<br/>Returns webpage_instructions]
    P --> T[Backend: build_generation_prompt<br/>Returns minimal prompt]
    
    Q --> U[Call Ollama API<br/>with custom instructions as prompt<br/>System prompt: webpage_instructions]
    R --> V[Call Ollama API<br/>with full prompt<br/>System prompt: original instructions]
    S --> W[Call Ollama API<br/>with custom instructions as prompt<br/>System prompt: none]
    T --> X[Call Ollama API<br/>with minimal prompt<br/>System prompt: none]
    
    U --> Y[Generate test case]
    V --> Y
    W --> Y
    X --> Y
    
    Y --> Z[Return result to frontend]
    Z --> AA[Display generated test case<br/>Single session - no context awareness<br/>One-click operation - not threaded]
```

## Decision Table Matrix

### Grouped by Checkbox State

#### When "Use Instructions" is **Checked** (use_instructions = true)
| Instructions Modified | System Prompt | Generation Prompt | Description |
|----------------------|---------------|-------------------|-------------|
| Yes | Modified instructions (webpage_instructions) | Modified instructions (webpage_instructions) | Uses custom instructions for both system and generation prompts |
| No | Original system instructions | Full prompt with product context | Uses default system instructions + detailed generation prompt |

#### When "Use Instructions" is **Unchecked** (use_instructions = false)
| Instructions Modified | System Prompt | Generation Prompt | Description |
|----------------------|---------------|-------------------|-------------|
| Yes | None (empty string) | Modified instructions (webpage_instructions) | Uses custom instructions for generation prompt only, no system context |
| No | None (empty string) | Minimal prompt without context | Basic generation prompt without system instructions or product context |

## Process Explanation

This flowchart illustrates the complete process flow from the user's button click to displaying the generated test case result. The key decision points are:

1. **Checkbox State**: Whether "Use Instructions" is checked determines if system/product context is included
2. **Modification Check**: Whether the instructions textarea has been modified from the original system instructions
3. **Prompt Selection**: Based on the combination, one of four prompt types is used:
   - **Checked + Modified**: Custom instructions from webpage (both generation and system prompt)
   - **Checked + Unmodified**: Full system prompt with product context (generation and system)
   - **Unchecked + Modified**: Custom instructions from webpage (generation prompt only, no system prompt)
   - **Unchecked + Unmodified**: Minimal prompt without context (no system prompt)

The process is stateless (single session), one-click (immediate generation), and non-threaded (synchronous operation). The backend correctly handles all four conditions as implemented in the updated code.

The code changes ensure that:
- Client-side tracks original instructions and sends `webpage_instructions` when modified
- Backend's `build_generation_prompt` function selects the appropriate generation prompt based on both `use_instructions` flag and presence of `webpage_instructions`
- `build_system_prompt` provides system context only when `use_instructions` is True
- System prompt and generation prompt are handled separately for proper Ollama API usage

This implementation fully complies with the four conditional behaviors.