"""
Cloud Function to handle chat with a Gemini model.
"""

import logging
import os
from typing import Any, Dict, Tuple, Optional

import google.generativeai as genai
from flask import Request
from functions_framework import http
from google.generativeai.types import GenerateContentResponse

# Configure logging
logging.basicConfig(level=logging.INFO)

# --- Configuration ---
try:
    GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
except KeyError:
    logging.critical("GEMINI_API_KEY environment variable not set.")
    raise

# Comma-separated list of allowed origins
ALLOWED_ORIGINS_STR = os.environ.get("ALLOWED_ORIGINS", "https://bencsbalazs.github.io")
ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS_STR.split(",")]

GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")

# --- System Instructions ---
try:
    with open("instructions.md", "r", encoding="utf-8") as f:
        SYSTEM_INSTRUCTIONS = f.read()
except FileNotFoundError:
    logging.warning("instructions.md not found. System instructions will be empty.")
    SYSTEM_INSTRUCTIONS = ""


def _get_cors_headers(origin: Optional[str]) -> Dict[str, str]:
    """
    Returns CORS headers if the origin is allowed.
    """
    if origin and origin in ALLOWED_ORIGINS:
        return {"Access-Control-Allow-Origin": origin}
    return {}


@http
def gemini_api_call(request: Request) -> Tuple[Dict[str, Any], int, Dict[str, str]]:
    """
    HTTP Cloud Function to accept a POST request and communicate with a Gemini model.
    Handles CORS preflight requests and validates incoming requests.
    """
    request_origin = request.headers.get("Origin")
    headers = _get_cors_headers(request_origin)

    # Handle CORS preflight requests
    if request.method == "OPTIONS":
        if headers:
            preflight_headers = {
                **headers,
                "Access-Control-Allow-Methods": "POST",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Max-Age": "3600",
            }
            return {}, 204, preflight_headers
        # If origin is not allowed, return a simple 204 without CORS headers
        return {}, 204, {}

    # Reject requests from non-allowed origins
    if not headers:
        logging.warning(f"Security violation: Forbidden origin: {request_origin}")
        return {"error": "Forbidden"}, 403, {}

    if request.method != "POST":
        return {"error": "Method not allowed"}, 405, headers

    # --- Request Validation ---
    try:
        request_json = request.get_json()
        prompt = request_json.get("prompt")
        if not prompt or not isinstance(prompt, str):
            return {"error": "Missing or invalid 'prompt' in request body"}, 400, headers
    except Exception:
        return {"error": "Invalid JSON in request body"}, 400, headers

    # --- Gemini API Call ---
    try:
        model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            system_instruction=SYSTEM_INSTRUCTIONS,
        )
        result: GenerateContentResponse = model.generate_content([{"role": "user", "parts": [{"text": prompt}]}])
        return {"text": result.text}, 200, headers

    except Exception as e:
        logging.error(f"Error calling Gemini model: {e}", exc_info=True)
        return {"error": "An error occurred while processing your request."}, 500, headers
