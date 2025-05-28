import json
import os
from typing import Dict, Any, List, Optional
from enum import Enum
from dotenv import load_dotenv
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from langchain_openai import AzureChatOpenAI
# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Load the API key from the environment variable
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

if not AZURE_OPENAI_API_KEY :
    raise ValueError("AZURE_OPENAI_API_KEY environment variable is not set. Please check your .env file.")

app = FastAPI()

class CodeAnalysisRequest(BaseModel):
    user_instruction: str

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
                }
            },
            "required": ["codeIssues", "securityVulnerabilityIssues", "engineeringPracticesIssues"]
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
            },
            "required": ["purpose", "components", "algorithm", "complexity", "edgeCases"]
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

        llm = AzureChatOpenAI(
            openai_api_version=AZURE_OPENAI_API_VERSION,
            azure_deployment=AZURE_OPENAI_DEPLOYMENT_NAME,
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY,
            temperature=0.9,  # Higher temperature for more creative problem generation
        )

        full_prompt = (
            f"You are an expert code reviewer and programmer.\n\n"
            f"User request: {user_instruction}\n\n"
            f"Code:\n{code}\n\n"
            "Based on the user request, you MUST use function calling to respond. "
            "Do not return any other format. Use either code_review or code_explanation function "
            "based on the user's intent."
        )

        functions = [code_review_function(), code_explanation_function()]
        
        # Configure the model with function calling
        llm = llm.bind(
            functions=functions
        )

        messages = [
            {"role": "system", "content": "You are an expert code reviewer and explainer. You MUST use function calling to respond."},
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
            }, AnalysisType.BOTH)

        logger.warning("No valid function call response received")
        return format_response({
            "error": "No valid analysis result found"
        }, AnalysisType.BOTH)

    except Exception as e:
        logger.error(f"Error in code analysis: {str(e)}")
        return format_response({
            "error": f"Error in code analysis: {str(e)}"
        }, AnalysisType.BOTH)

@app.post("/analyze-code")
async def analyze_code_endpoint(request: CodeAnalysisRequest):
    try:
        with open("sample_code.txt", "r") as file:
            sample_code = file.read()
        result = await analyze_code_auto(sample_code, request.user_instruction)
        return json.loads(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
