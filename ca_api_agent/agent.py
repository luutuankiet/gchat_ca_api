"""
Conversational Analytics ADK Agent
Based on: looker-open-source/ca-demos-and-tools/ca-api-adk-streaming
Commit SHA: 6eed78e512638cbcbfcec101f34a24234d5607b5

This agent implements the Natural Language Query (nlq) tool that streams
responses from the Google Cloud Conversational Analytics API.
"""

import os
import json
import httpx
from typing import AsyncGenerator
from adk import agent, InvocationContext

# TODO: Replace with your Conversational Analytics agent ID
# Find this in Google Cloud Console > Conversational Analytics
CA_AGENT_ID = os.getenv("CA_AGENT_ID", "YOUR_AGENT_ID_HERE")


@agent(
    name="ca_api_agent",
    description="A conversational analytics agent that answers data questions using natural language"
)
class CaApiAgent:
    """
    The main agent that processes natural language questions about data.

    Architecture:
    - Receives questions from the connector (gchat_connector)
    - Streams responses from the Conversational Analytics API
    - Returns both "thinking" process and final data results
    """

    @agent.tool
    async def nlq(self, question: str, token: str, ctx: InvocationContext) -> AsyncGenerator:
        """
        Natural Language Query tool - sends questions to the CA API and streams responses.

        Args:
            question: The natural language question to ask about the data
            token: Authentication token for CA API access
            ctx: Invocation context from ADK

        Yields:
            Streaming responses from CA API including:
            - systemMessage: "Thinking" steps the agent takes
            - data: Query results, charts, and final answers

        Implementation Notes:
        - Uses httpx.AsyncClient for streaming HTTP
        - Parses Server-Sent Events (SSE) format
        - Handles both thinking process and result data
        """

        # TODO: Configure your Google Cloud project details
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "YOUR_PROJECT_ID")
        location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

        # CA API endpoint (streaming chat)
        url = (
            f"https://geminidataanalytics.googleapis.com/v1beta/"
            f"projects/{project_id}/locations/{location}:chat"
        )

        # Request payload
        payload = {
            "agentId": CA_AGENT_ID,
            "messages": [
                {
                    "role": "user",
                    "content": question
                }
            ]
        }

        # Headers with authentication
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        # TODO: Implement streaming logic
        # This is where the "ticker tape" streaming happens
        # The API sends chunks of data as they're processed, not all at once

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                url,
                json=payload,
                headers=headers,
                timeout=None
            ) as response:

                # TODO: Check response status
                response.raise_for_status()

                # Stream the response byte by byte
                # CA API uses Server-Sent Events (SSE) format
                async for chunk in response.aiter_bytes():

                    # TODO: Parse the SSE format
                    # Expected format: "data: {json}\n\n"
                    # Two types of messages:
                    # 1. systemMessage: The agent's "thinking" (optional to show)
                    # 2. data: The actual results (charts, SQL, answers)

                    # Placeholder: Just yield raw chunks for now
                    # IMPLEMENTATION NEEDED: Parse JSON, filter message types
                    yield {"raw_chunk": chunk.decode("utf-8")}

                # TODO: Handle end of stream
                # Send a completion marker or final summary


# Entry point for local testing
if __name__ == "__main__":
    print("=" * 60)
    print("CA API Agent - ADK Streaming Implementation")
    print("=" * 60)
    print("\nTODO: This agent needs to be deployed to Vertex AI Agent Engine")
    print("\nSteps:")
    print("1. Set environment variables:")
    print("   - GOOGLE_CLOUD_PROJECT")
    print("   - GOOGLE_CLOUD_LOCATION")
    print("   - CA_AGENT_ID")
    print("\n2. Deploy to Vertex AI:")
    print("   gcloud vertex-ai reasoning-engines create \\")
    print("     --agent-file=agent.py \\")
    print("     --region=us-central1")
    print("\n3. Connect to gchat_connector")
    print("=" * 60)
