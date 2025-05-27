import json
import os
import re
import logging
import google.generativeai as genai
from dotenv import load_dotenv
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Set up logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Load the API key from the environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

def get_code_review(code):
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
            '  "reviewScore": 72.5%,\n'
            '  "refactoredCode": "Only the refactored code here. No markdown, no explanation."\n'
            "}\n"
            "If no issues are found in a section, return an empty array for that parameter."
        )

        response = model.generate_content(
            prompt,
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            },
        )

        logger.info("Raw Response from LLM:")
        logger.info(response.text)
        logger.info("Trying to parse JSON response...")

        if response and response.parts:
            generated_review = response.parts[0].text

            json_match = re.search(
                r'\{.*"refactoredCode":', generated_review, re.DOTALL
            )

            if json_match:
                json_str = json_match.group() + '""}'


                try:
                    review_dict = json.loads(json_str)
                    refactored_code_match = re.search(
                        r'"refactoredCode":(.*)$', generated_review, re.DOTALL
                    )
                    if refactored_code_match:
                        refactored_code = refactored_code_match.group(1).strip()[1:-1]
                        review_dict["refactoredCode"] = refactored_code.replace("\\n", "\n")

                    logger.info("Successfully parsed JSON response!")
                    return {
                        "response": review_dict
                    }
                except json.JSONDecodeError as e:
                    logger.error(f"JSON parsing error: {str(e)}")
                    return {
                        "error": "Error decoding JSON response",
                        "raw_response": json_str
                    }
            else:
                logger.warning("No JSON structure found in response")
                return {
                    "error": "No JSON found in response",
                    "raw_response": generated_review
                }
        else:
            logger.error("No response parts found")
            return {
                "error": "Unexpected response format",
                "raw_response": str(response)
            }

    except Exception as e:
        logger.exception(f"Exception occurred: {str(e)}")
        return {
            "error": f"Error generating review: {e}"
        }

# Example usage
if __name__ == "__main__":
    with open("sample_code.txt", "r") as file:
        sample_code = file.read()

    logger.info("=== Code Review Without Function Calling ===")
    logger.info("This approach requires manual JSON parsing and handling")
    logger.info("The response might not always be in the expected format")
    logger.info("We need to handle various edge cases and parsing errors")
    logger.info("=" * 50)

    review_result = get_code_review(sample_code)
    logger.info("Final Result:")
    logger.info(json.dumps(review_result, indent=2))
