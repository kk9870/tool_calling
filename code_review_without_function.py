import json
import os
import re
import logging
import asyncio
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

# Set up logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Load the API key from the environment variable
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

async def get_code_review(code):
    try:
        prompt = (
            f"Act as an expert code reviewer. Analyze the following code:\n\n{code}\n\n"
            "Evaluate the code based on the following parameters in detail:\n"
            "1. Code Issues: Identify logical errors, type errors, runtime errors, and syntax errors. Explain each issue and assign a criticality level from 0 (low) to 5 (high).\n"
            "2. Security Vulnerabilities: Identify OWASP Top 10 issues like injection, broken access control, hardcoded credentials, missing input validation, insecure deserialization, and other vulnerabilities. Include a description and criticality level for each.\n"
            "3. Engineering Practices: Evaluate adherence to software engineering best practices including proper naming conventions, modularity, separation of concerns, design pattern usage, and error handling. Include detailed descriptions with code context and criticality level.\n"
            "4. Documentation Issues: Report missing or unclear documentation, such as absent class/function docstrings, poor inline comments, or missing usage instructions.\n"
            "5. Review Score: Provide an overall code review score (0-100) in percentage representing the code's quality.\n"
            "6. Refactored Code: If issues are found, return the improved version of the code. Only return code (no markdown or explanation).\n"
            "For each issue, provide a description and criticality level (1-5).\n"
            "Return the result in this JSON format:\n"
            "{\n"
            '  "codeIssues": [\n'
            '    {"issueType": "Logical error", "description": "Explain the issue here", "criticalityLevel": 3}\n'
            "  ],\n"
            '  "securityVulnerabilityIssues": [\n'
            '    {"issueType": "Hardcoded credentials", "description": "Sensitive info hardcoded", "criticalityLevel": 4}\n'
            "  ],\n"
            '  "engineeringPracticesIssues": [\n'
            '    {"issueType": "Poor naming conventions", "description": "Variable names are unclear", "criticalityLevel": 2}\n'
            "  ],\n"
            '  "documentationIssues": [\n'
            '    {"issueDescription": "Missing docstrings for public functions"}\n'
            "  ],\n"
            '  "reviewScore": 72.5,\n'
            '  "refactoredCode": "Only the refactored code here. No markdown, no explanation."\n'
            "}\n"
            "If no issues are found in a section, return an empty array for that parameter."
        )


        llm = AzureChatOpenAI(
            openai_api_version=AZURE_OPENAI_API_VERSION,
            azure_deployment=AZURE_OPENAI_DEPLOYMENT_NAME,
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY,
            temperature=0.9,  # Higher temperature for more creative problem generation
        )

        messages = [
            {"role": "system", "content": "You are an expert code reviewer."},
            {"role": "user", "content": prompt}
        ]

        logger.info("Sending request to LLM...")
        response = await llm.ainvoke(messages)

        logger.info("Raw Response from LLM:")
        logger.info(response)

        if response and hasattr(response, 'content'):
            try:
                # Extract JSON from the response content
                content = response.content.strip()
                # Remove any markdown code block markers if present
                if content.startswith('```json'):
                    content = content[7:-3]  # Remove ```json and ``` markers
                elif content.startswith('```'):
                    content = content[3:-3]  # Remove ``` markers
                
                # Parse the JSON response
                review_dict = json.loads(content)
                logger.info("Successfully parsed JSON response!")
                return {
                    "response": review_dict
                }
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {str(e)}")
                return {
                    "error": "Error decoding JSON response",
                    "raw_response": content
                }
        else:
            logger.error("Invalid response format")
            return {
                "error": "Invalid response format",
                "raw_response": str(response)
            }

    except Exception as e:
        logger.exception(f"Exception occurred: {str(e)}")
        return {
            "error": f"Error generating review: {e}"
        }

# Example usage
if __name__ == "__main__":
    async def main():
        with open("sample_code.txt", "r") as file:
            sample_code = file.read()

        logger.info("=== Code Review Without Function Calling ===")
        logger.info("This approach requires manual JSON parsing and handling")
        logger.info("The response might not always be in the expected format")
        logger.info("We need to handle various edge cases and parsing errors")
        logger.info("=" * 50)

        review_result = await get_code_review(sample_code)
        logger.info("Final Result:")
        logger.info(json.dumps(review_result, indent=2))

    # Run the async main function
    asyncio.run(main())
