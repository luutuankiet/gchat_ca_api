# CA API Agent - ADK Streaming Implementation

This is the "Brain" of the Google Chat conversational analytics demo. It implements an Agent Development Kit (ADK) agent that queries the Conversational Analytics API.

## Architecture Role

```
Google Chat → gchat_connector → [CA API Agent] → CA API → Looker/BigQuery
                                  ^^^^^^^^^^^^
                                  YOU ARE HERE
```

## What This Agent Does

1. **Receives** natural language questions (e.g., "What were sales last quarter?")
2. **Streams** the question to the Conversational Analytics API
3. **Returns** both thinking process and final results (data, charts, text)

## Key Implementation: The `nlq` Tool

The `nlq` (Natural Language Query) function is the core tool:

```python
async def nlq(question: str, token: str, ctx: InvocationContext) -> AsyncGenerator
```

### Why Streaming?

The CA API uses a streaming architecture because data queries can take 10+ seconds. Instead of making users wait for a complete answer, the API streams:
- **systemMessage**: The agent's "thinking" steps (optional to display)
- **data**: Query results as they're ready (SQL, charts, text answers)

This is like a "ticker tape" - results arrive character-by-character, not all at once.

## Setup Instructions

### 1. Prerequisites

- Google Cloud Project with Conversational Analytics API enabled
- A configured CA agent (created in BigQuery or Looker Studio)
- Vertex AI enabled in your project

### 2. Environment Variables

Create a `.env` file:

```bash
# Your Google Cloud project
GOOGLE_CLOUD_PROJECT=your-project-id

# Region where CA API is available (usually us-central1)
GOOGLE_CLOUD_LOCATION=us-central1

# Your Conversational Analytics agent ID
# Find this in: Cloud Console → Conversational Analytics → Your Agent
CA_AGENT_ID=your-agent-id-here
```

### 3. Install Dependencies

```bash
cd ca_api_agent
pip install -r requirements.txt
```

### 4. Deploy to Vertex AI Agent Engine

This agent must run on Vertex AI Agent Engine (not locally for production):

```bash
# Authenticate
gcloud auth application-default login

# Deploy the agent
gcloud vertex-ai reasoning-engines create \
  --agent-file=agent.py \
  --requirements-file=requirements.txt \
  --region=us-central1 \
  --display-name="ca-api-agent"
```

### 5. Get the Reasoning Engine ID

After deployment, note the Reasoning Engine ID from the output:

```
Created reasoning engine: projects/123/locations/us-central1/reasoningEngines/456
                                                                            ^^^
                                                                            This is your ID
```

You'll need this ID for the `gchat_connector`.

## Testing Locally (Optional)

While the agent must be deployed to Vertex AI for production, you can test the core logic locally:

```bash
python agent.py
```

This will show you the setup instructions.

## Implementation TODOs

The skeleton includes placeholder comments marked with `TODO:`. Complete these to finish the implementation:

1. **Parse SSE format** in `nlq()`: The CA API returns Server-Sent Events. Parse the `data:` lines.
2. **Filter message types**: Separate `systemMessage` (thinking) from `data` (results).
3. **Error handling**: Add try/catch for network errors, auth failures, etc.
4. **Token refresh**: Implement OAuth token refresh if needed.

## Reference Implementation

This skeleton is based on:
- **Repository**: `looker-open-source/ca-demos-and-tools`
- **File**: `ca-api-adk-streaming/ca_api_agent/agent.py`
- **Commit**: `6eed78e512638cbcbfcec101f34a24234d5607b5`

## Next Steps

After deploying this agent:
1. Go to `../gchat_connector` to build the Google Chat webhook
2. Configure the connector to call this agent via Vertex AI SDK
3. Deploy the connector to Cloud Run
4. Connect Google Chat to the Cloud Run endpoint

---

**Questions?** See the main project README or check the Google Cloud documentation:
- [Conversational Analytics API Overview](https://cloud.google.com/gemini/docs/conversational-analytics-api/overview)
- [Agent Development Kit Quickstart](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-development-kit/quickstart)
