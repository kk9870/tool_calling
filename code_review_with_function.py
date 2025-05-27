import json
import os
from typing import Dict, Any
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Load the API key from the environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set. Please check your .env file.")


def code_review_function():
    return {
        "name": "code_review",
        "description": "Review code and provide detailed analysis",
        "parameters": {
            "type": "object",
            "properties": {
                "codeIssues": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "issueType": {
                                "type": "string",
                                "description": "Type of the code issue (e.g., logic error, redundancy, performance bottleneck)"
                            },
                            "description": {
                                "type": "string",
                                "description": "Detailed description of the issue"
                            },
                            "criticalityLevel": {
                                "type": "integer",
                                "description": "Criticality level of the issue (0 - low, 5 - high)"
                            }
                        },
                        "required": ["issueType", "description", "criticalityLevel"]
                    }
                },
                "securityVulnerabilityIssues": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "issueType": {
                                "type": "string",
                                "description": "Type of security vulnerability (e.g., SQL injection, XSS, hardcoded credentials)"
                            },
                            "description": {
                                "type": "string",
                                "description": "Description of the vulnerability"
                            },
                            "criticalityLevel": {
                                "type": "integer",
                                "description": "Criticality level (0-5)"
                            }
                        },
                        "required": ["issueType", "description", "criticalityLevel"]
                    }
                },
                "engineeringPracticesIssues": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "issueType": {
                                "type": "string",
                                "description": "Type of engineering practice issue (e.g., naming conventions, meaningful function names)"
                            },
                            "description": {
                                "type": "string",
                                "description": "Detailed description of the issue along with relevant code context"
                            },
                            "criticalityLevel": {
                                "type": "integer",
                                "description": "Criticality level (0 = low, 5 = high)"
                            }
                        },
                        "required": ["issueType", "description", "criticalityLevel"]
                    }
                },
                "documentationIssues": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "issueDescription": {
                                "type": "string",
                                "description": "Description of documentation issue (e.g., missing class-level comments, lack of function docstrings, unclear inline comments)"
                            }
                        },
                        "required": ["issueDescription"]
                    }
                },
                "reviewScore": {
                    "type": "number",
                    "description": "Overall code review score in percentage (0-100)"
                },
                "refactoredCode": {
                    "type": "string",
                    "description": "Refactored version of the input code with improvements applied"
                }
            },
            "required": [
                "codeIssues",
                "securityVulnerabilityIssues",
                "engineeringPracticesIssues",
                "documentationIssues",
                "reviewScore",
                "refactoredCode"
            ]
        }
    }


def create_code_review_prompt(code: str) -> str:
    return (
        f"You are an expert code reviewer.\n"
        f"Analyze the following code and respond using the function 'code_review_function'.\n"
        f"Only use function calling to return your result. Do not include plain text.\n"
        f"Code to review:\n\n{code}"
    )


def format_response(response: Dict[str, Any]) -> str:
    return json.dumps(response, indent=2)


async def review_code(code: str) -> str:
    """
    Main function to review code using function calling approach.

    Args:
        code (str): The code to be reviewed

    Returns:
        str: JSON formatted review results
    """
    try:
        logger.info("=== Code Review With Function Calling ===")
        logger.info("This approach uses structured function calling")
        logger.info("The response is guaranteed to be in the expected JSON format")
        logger.info("No manual parsing required")

        prompt = create_code_review_prompt(code)
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=GEMINI_API_KEY,
            streaming=True
        )

        functions = [code_review_function()]
        llm = llm.bind(functions=functions)

        messages = [
            {"role": "system", "content": "You are an expert code reviewer."},
            {"role": "user", "content": prompt}
        ]

        logger.info("Sending request to LLM with function calling...")
        response = await llm.ainvoke(messages)

        logger.info("Raw response: {response}")
        if response.additional_kwargs.get("function_call"):
            function_call = response.additional_kwargs["function_call"]
            if function_call["name"] == "code_review":
                logger.info("Received structured function call response")
                review_result = json.loads(function_call["arguments"])
                return format_response({
                    "response": review_result
                })

        logger.warning("No valid function call response received")
        return format_response({
            "error": "No valid review result found",
        })

    except Exception as e:
        logger.error(f"Error in code review: {str(e)}")
        return format_response({
            "error": f"Error in code review: {str(e)}",
        })


# Example usage
if __name__ == "__main__":
    import asyncio

    with open("sample_code.txt", "r") as file:
        sample_code = file.read()


    async def main():
        review_result = await review_code(sample_code)
        logger.info("Final Result:")
        logger.info(review_result)


    asyncio.run(main())
