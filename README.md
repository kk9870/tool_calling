# Code Review Implementation Examples

This repository demonstrates different approaches to implementing code review functionality using the Gemini API, highlighting the differences between function calling and non-function calling implementations.

## Overview

The repository contains three main implementations:

1. `code_review_without_function.py`: Traditional approach without function calling
2. `code_review_with_function.py`: Implementation using function calling
3. `multi_function_calling.py`: Advanced implementation supporting both code review and explanation with automatic intent detection

## Features

### Code Review Without Function Calling
- Uses direct prompt engineering
- Requires manual JSON parsing and validation
- Handles various edge cases and parsing errors
- More complex error handling for malformed responses
- Provides detailed code review covering:
  - Code Issues
  - Security Vulnerabilities
  - Engineering Practices
  - Documentation Issues
  - Review Score
  - Refactored Code

### Code Review With Function Calling
- Uses structured function calling
- Guaranteed JSON response format
- No manual parsing required
- Built-in type safety
- Consistent response format
- Automatic error handling
- Same comprehensive review coverage as non-function version

### Multi-Function Calling
- Supports both code review and explanation
- Automatic intent detection
- Multiple function handling
- Flexible response format
- Additional features:
  - Code explanation with purpose, components, algorithm details
  - Complexity analysis
  - Edge case identification
  - Performance optimization suggestions
  - Scalability analysis

## Setup

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your Gemini API key:
```
GEMINI_API_KEY=your_api_key_here
```

## Usage

### Basic Code Review
```python
from code_review_with_function import review_code
# or
from code_review_without_function import get_code_review

# Your code to review
code = """
def example_function():
    return "Hello World"
"""

# Using function calling approach
result = await review_code(code)

# Using non-function calling approach
result = get_code_review(code)
```

### Multi-Function Analysis
```python
from multi_function_calling import analyze_code_auto

code = """
def example_function():
    return "Hello World"
"""

# The function will automatically determine whether to review, explain, or do both
result = await analyze_code_auto(code, "Please review this code")
```

## Response Format

### Function Calling Response
```json
{
  "response": {
    "codeIssues": [...],
    "securityVulnerabilityIssues": [...],
    "engineeringPracticesIssues": [...],
    "documentationIssues": [...],
    "reviewScore": 85,
    "refactoredCode": "..."
  }
}
```

### Non-Function Calling Response
```json
{
  "response": {
    "codeIssues": [...],
    "securityVulnerabilityIssues": [...],
    "engineeringPracticesIssues": [...],
    "documentationIssues": [...],
    "reviewScore": 85,
    "refactoredCode": "..."
  },
  "parsing_required": true
}
```

## Advantages of Function Calling

1. **Reliability**: Guaranteed structured response format
2. **Simplicity**: No manual JSON parsing required
3. **Type Safety**: Built-in schema validation
4. **Consistency**: Uniform response format
5. **Error Handling**: Automatic handling of malformed responses

## Logging

All implementations include comprehensive logging:
- DEBUG level for detailed information
- INFO level for general progress
- WARNING level for potential issues
- ERROR level for failures

## Error Handling

- API key validation
- Response parsing errors
- Malformed JSON handling
- API call failures
- Invalid response format handling

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the LICENSE file for details. 