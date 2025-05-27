import json
import os
from typing import Dict, Any, List, Optional
from enum import Enum
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Load the API key from the environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set. Please check your .env file.")


class AnalysisType(Enum):
    REVIEW = "review"
    EXPLANATION = "explanation"
    BOTH = "both"


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
                            "issueType": {"type": "string"},
                            "description": {"type": "string"},
                            "criticalityLevel": {"type": "integer"}
                        }
                    }
                },
                "performanceOptimizationIssues": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "issueType": {"type": "string"},
                            "description": {"type": "string"},
                            "criticalityLevel": {"type": "integer"}
                        }
                    }
                },
                "securityVulnerabilityIssues": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "issueType": {"type": "string"},
                            "description": {"type": "string"},
                            "criticalityLevel": {"type": "integer"}
                        }
                    }
                },
                "scalabilityIssues": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "issueType": {"type": "string"},
                            "description": {"type": "string"},
                            "criticalityLevel": {"type": "integer"}
                        }
                    }
                },
                "engineeringPracticesIssues": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "issueType": {"type": "string"},
                            "description": {"type": "string"},
                            "criticalityLevel": {"type": "integer"}
                        }
                    }
                },
                "refactoredCode": {"type": "string"}
            }
        }
    }


def code_explanation_function():
    return {
        "name": "code_explanation",
        "description": "Explain code in detail",
        "parameters": {
            "type": "object",
            "properties": {
                "purpose": {"type": "string"},
                "components": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "algorithm": {"type": "string"},
                "complexity": {
                    "type": "object",
                    "properties": {
                        "time": {"type": "string"},
                        "space": {"type": "string"}
                    }
                },
                "edgeCases": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            }
        }
    }

def format_response(response: Dict[str, Any], analysis_type: AnalysisType) -> str:
    return json.dumps(response, indent=2)


async def analyze_code_auto(code: str, user_instruction: str) -> str:
    """
    Analyze code based on user instruction using function calling.
    Automatically determines if review, explanation or both are needed.
    """
    try:
        logger.info("=== Auto Code Analysis with LLM Decision Making ===")
        logger.info("The LLM will determine whether to review, explain, or do both.")
        logger.info("=" * 50)

        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=GEMINI_API_KEY,
            streaming=True
        )

        full_prompt = (
            f"You are an expert code reviewer and programmer.\n\n"
            f"User request: {user_instruction}\n\n"
            f"Code:\n{code}\n\n"
            "Based on the user request, either:\n"
            "- Review the code and return issues\n"
            "- Explain the code in detail\n"
            "- Or do both\n"
            "Use only structured function calling to respond appropriately. Response must follow JSON format using the defined functions."
        )

        functions = [code_review_function(), code_explanation_function()]
        llm = llm.bind(functions=functions)

        messages = [
            {"role": "system", "content": "You are an expert code reviewer and explainer. Use function calling based on user's intent."},
            {"role": "user", "content": full_prompt}
        ]

        logger.debug("Sending request to LLM with function calling...")
        response = await llm.ainvoke(messages)
        logger.debug(f"Raw response received: {response}")

        if response.additional_kwargs.get("function_call"):
            function_call = response.additional_kwargs["function_call"]
            logger.info(f"Received structured function call response for: {function_call['name']}")
            result = json.loads(function_call["arguments"])
            return format_response({
                "response": result,
                "function_called": function_call["name"],
                "parsing_required": False,
                "automatic_intent_detection": True
            }, AnalysisType.BOTH)

        elif hasattr(response, "tool_calls") and response.tool_calls:
            review_result = None
            explanation_result = None

            for tool_call in response.tool_calls:
                name = tool_call.get("name")
                args = tool_call.get("args")
                if name == "code_review":
                    review_result = args
                elif name == "code_explanation":
                    explanation_result = args

            logger.info("Received multiple tool call responses.")
            return format_response({
                "response": {
                    "review": review_result,
                    "explanation": explanation_result
                },
                "function_called": "both",
                "parsing_required": False,
                "automatic_intent_detection": True
            }, AnalysisType.BOTH)

        logger.warning("No valid function call response received")
        return format_response({
            "error": "No valid analysis result found",
            "automatic_intent_detection": True,
            "parsing_failed": True
        }, AnalysisType.BOTH)

    except Exception as e:
        logger.error(f"Error in code analysis: {str(e)}")
        return format_response({
            "error": f"Error in code analysis: {str(e)}",
            "automatic_intent_detection": True,
            "parsing_failed": True
        }, AnalysisType.BOTH)


# Example usage
if __name__ == "__main__":
    import asyncio
    async def main():
        sample_code = """
            def calculate_sum(numbers):
                total = 0
                for i in range(len(numbers)):
                    total += numbers[i]
                return total
            """

        user_inputs = [
            "Please review this code for potential issues",
            "Can you explain how this code works?",
            "Give both a review and an explanation of this code"
        ]

        for i, user_input in enumerate(user_inputs, start=1):
            logger.info(f"\n=== Example {i}: {user_input} ===")
            result = await analyze_code_auto(sample_code, user_input)
            logger.info("\nFinal Result:")
            logger.info(result)

    asyncio.run(main())
