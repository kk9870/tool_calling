# Code Review Implementation Examples

This repository demonstrates different approaches to implementing code review functionality using the Azure OpenAI API, highlighting the differences between function calling and non-function calling implementations.

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

2. Create a `.env` file with your Azure OpenAI credentials:
```
AZURE_OPENAI_API_KEY
AZURE_OPENAI_ENDPOINT
AZURE_OPENAI_DEPLOYMENT_NAME
AZURE_OPENAI_API_VERSION
```


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
