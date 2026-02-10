"""
Google Chat Connector for CA API Agent
The "Telephone" that connects Google Chat to the Vertex AI Agent Engine

Architecture Role:
Google Chat → [gchat_connector] → ca_api_agent → CA API → Data
              ^^^^^^^^^^^^^^^^
              YOU ARE HERE

This Flask app acts as protocol translator:
- Google Chat speaks in "Events" (JSON webhooks)
- Agent Engine speaks in "Questions" (SDK calls)
- This connector translates between them
"""

import os
import json
import logging
from flask import Flask, request, jsonify
from google.auth.transport import requests as auth_requests
from google.oauth2 import id_token
from vertexai.agent_engines import ReasoningEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# TODO: Set these environment variables
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "YOUR_PROJECT_ID")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
REASONING_ENGINE_ID = os.getenv("REASONING_ENGINE_ID", "YOUR_REASONING_ENGINE_ID")

# Google Chat verification
CHAT_ISSUER = "chat@system.gserviceaccount.com"


def verify_chat_token(bearer_token):
    """
    Verify that the request actually comes from Google Chat.

    Security Critical: Without this check, anyone could send fake messages
    to your endpoint and trigger expensive CA API queries.

    Args:
        bearer_token: The Authorization header value (format: "Bearer <token>")

    Returns:
        True if valid, False otherwise
    """
    try:
        # Remove "Bearer " prefix
        token = bearer_token.split(" ")[1] if " " in bearer_token else bearer_token

        # TODO: Implement actual verification
        # This is a placeholder - you must implement real JWT verification

        # Real implementation should:
        # 1. Decode the JWT token
        # 2. Verify it's signed by chat@system.gserviceaccount.com
        # 3. Check the audience matches your Cloud Run service URL

        # For now, just check if token exists
        if not token:
            logger.error("No bearer token provided")
            return False

        # PLACEHOLDER: Replace with actual verification
        logger.warning("TODO: Implement real JWT verification!")
        return True

    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        return False


def extract_message_text(chat_event):
    """
    Extract the actual message text from Google Chat's JSON payload.

    Google Chat sends complex JSON with lots of metadata. We just need
    the user's actual question.

    Args:
        chat_event: The full JSON payload from Google Chat

    Returns:
        The message text string, or None if not found
    """
    try:
        # Google Chat structure: event.message.text
        return chat_event.get("message", {}).get("text", "").strip()
    except Exception as e:
        logger.error(f"Failed to extract message text: {e}")
        return None


def query_ca_agent(question):
    """
    Call the Vertex AI Agent Engine with the user's question.

    This is the bridge to the "Brain" (ca_api_agent).

    Args:
        question: Natural language question from the user

    Returns:
        dict: Response from the agent with answers/charts/data
    """
    try:
        # TODO: Initialize the ReasoningEngine client
        # This connects to the deployed ca_api_agent on Vertex AI

        # PLACEHOLDER: This is where we'd call the agent
        logger.info(f"Would query agent with question: {question}")

        # Real implementation:
        # agent = ReasoningEngine(
        #     f"projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{REASONING_ENGINE_ID}"
        # )
        # response = agent.query(input=question)
        # return response.output

        # For now, return a placeholder
        return {
            "text": f"TODO: Query CA API with question: '{question}'",
            "status": "placeholder"
        }

    except Exception as e:
        logger.error(f"Failed to query CA agent: {e}")
        return {
            "text": f"Error querying data agent: {str(e)}",
            "status": "error"
        }


@app.route("/", methods=["POST"])
def handle_chat_event():
    """
    Main webhook endpoint that receives Google Chat events.

    Flow:
    1. Verify the request is from Google Chat (security)
    2. Extract the user's message
    3. Query the CA API Agent via Vertex AI
    4. Return the response to Google Chat
    """

    # Step 1: Verify this is a legitimate Google Chat request
    auth_header = request.headers.get("Authorization", "")
    if not verify_chat_token(auth_header):
        logger.warning("Unauthorized request rejected")
        return jsonify({"error": "Unauthorized"}), 401

    # Step 2: Parse the incoming event
    try:
        chat_event = request.get_json()
        logger.info(f"Received chat event: {json.dumps(chat_event, indent=2)}")
    except Exception as e:
        logger.error(f"Failed to parse request JSON: {e}")
        return jsonify({"error": "Invalid JSON"}), 400

    # Step 3: Extract the user's message
    message_text = extract_message_text(chat_event)
    if not message_text:
        logger.warning("No message text found in event")
        return jsonify({"text": "I didn't receive a message. Please try again."}), 200

    # Step 4: Query the CA API Agent
    logger.info(f"Processing question: {message_text}")
    agent_response = query_ca_agent(message_text)

    # Step 5: Format response for Google Chat
    # Google Chat expects JSON with a "text" field
    response_payload = {
        "text": agent_response.get("text", "No response from agent")
    }

    # TODO: Add support for rich responses (cards, charts, etc.)
    # Google Chat supports card-based UI for displaying charts and structured data

    logger.info(f"Sending response: {response_payload}")
    return jsonify(response_payload), 200


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for Cloud Run"""
    return jsonify({"status": "healthy", "service": "gchat-connector"}), 200


# Local development server
if __name__ == "__main__":
    print("=" * 60)
    print("Google Chat Connector - Starting Development Server")
    print("=" * 60)
    print("\nWARNING: This is for local testing only!")
    print("For production, deploy to Cloud Run.\n")
    print(f"Project: {PROJECT_ID}")
    print(f"Location: {LOCATION}")
    print(f"Reasoning Engine: {REASONING_ENGINE_ID}")
    print("\nListening on http://localhost:8080")
    print("=" * 60)

    app.run(host="0.0.0.0", port=8080, debug=True)
