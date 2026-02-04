# Google Chat Connector

This is the "Telephone" of the conversational analytics demo. It translates between Google Chat webhooks and Vertex AI Agent Engine.

## Architecture Role

```
[Google Chat] → gchat_connector → ca_api_agent → CA API → Data
                ^^^^^^^^^^^^^^^^
                YOU ARE HERE
```

## What This Connector Does

1. **Receives** webhook events from Google Chat when users send messages
2. **Verifies** the request is legitimate (security check)
3. **Extracts** the user's question from the JSON payload
4. **Calls** the CA API Agent on Vertex AI using the ReasoningEngine SDK
5. **Returns** the answer back to Google Chat

## Why Do We Need This?

**Protocol Mismatch:** Google Chat and Vertex AI Agent Engine speak different languages:
- **Google Chat**: Sends HTTP webhooks with complex JSON events
- **Agent Engine**: Expects SDK calls with simple string inputs

This connector acts as an interpreter, translating between these two systems.

## Prerequisites

Before deploying this connector, you need:
1. The `ca_api_agent` deployed to Vertex AI (see `../ca_api_agent/README.md`)
2. The Reasoning Engine ID from that deployment
3. A Google Cloud project with Cloud Run enabled
4. A Google Chat app configured (we'll set this up below)

## Setup Instructions

### 1. Set Environment Variables

Create a `.env` file for local testing:

```bash
# Your Google Cloud project
GOOGLE_CLOUD_PROJECT=your-project-id

# Region where your agent is deployed
GOOGLE_CLOUD_LOCATION=us-central1

# The Reasoning Engine ID from ca_api_agent deployment
# Format: projects/123/locations/us-central1/reasoningEngines/456
#                                                            ^^^
REASONING_ENGINE_ID=456
```

### 2. Local Testing (Optional)

```bash
cd gchat_connector

# Install dependencies
pip install -r requirements.txt

# Load environment variables
export $(cat .env | xargs)

# Run locally
python app.py
```

Visit http://localhost:8080/health to verify it's running.

### 3. Deploy to Cloud Run

```bash
# Set your project
gcloud config set project YOUR_PROJECT_ID

# Build and deploy
gcloud run deploy gchat-connector \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID \
  --set-env-vars GOOGLE_CLOUD_LOCATION=us-central1 \
  --set-env-vars REASONING_ENGINE_ID=YOUR_REASONING_ENGINE_ID
```

**Note the Service URL** from the deployment output. You'll need this for Google Chat configuration.

Example: `https://gchat-connector-abc123-uc.a.run.app`

### 4. Configure Google Chat App

Now we need to tell Google Chat to send messages to your Cloud Run service:

#### A. Create a Google Chat App

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to **APIs & Services** → **Enabled APIs & Services**
3. Enable **Google Chat API**
4. Go to **Google Chat API** → **Configuration**

#### B. Configure the Chat App

Fill in these settings:

- **App name**: "Data Assistant" (or your choice)
- **Avatar URL**: (optional) Your logo
- **Description**: "Ask questions about your data in natural language"

**Connection settings**:
- **App URL**: Your Cloud Run service URL (from step 3)
  - Example: `https://gchat-connector-abc123-uc.a.run.app`
- **Authentication**: "App-provided authentication"

**Functionality**:
- ✅ Enable "Receive 1:1 messages"
- ✅ Enable "Join spaces and group conversations"

**Slash commands**: (optional)
- Command: `/ask`
- Description: "Ask a question about your data"

#### C. Permissions

Under **Visibility**:
- Set who can install the app (e.g., your domain, specific users)

#### D. Save and Publish

Click **Save** and then **Publish** your Chat app.

### 5. Test in Google Chat

1. Open Google Chat (chat.google.com or mobile app)
2. Find your app in the chat directory
3. Send a message: "What were sales last quarter?"
4. You should receive a response (currently a placeholder)

## Implementation TODOs

The skeleton includes placeholders marked with `TODO:`. Complete these for production:

### Security
- [ ] **Implement JWT verification** in `verify_chat_token()`:
  - Decode the bearer token
  - Verify signature from `chat@system.gserviceaccount.com`
  - Check audience matches your Cloud Run URL

### Agent Integration
- [ ] **Uncomment ReasoningEngine code** in `query_ca_agent()`:
  - Initialize the client with your Reasoning Engine ID
  - Handle streaming responses from the agent
  - Parse the agent output format

### Response Formatting
- [ ] **Add Google Chat Cards** for rich responses:
  - Display charts as card images
  - Show SQL queries in code blocks
  - Format data tables nicely

### Error Handling
- [ ] Add retry logic for transient failures
- [ ] Implement proper error messages for users
- [ ] Add monitoring/logging for debugging

## Project Structure

```
gchat_connector/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── Dockerfile          # Cloud Run container definition
└── README.md          # This file
```

## Key Functions

### `verify_chat_token(bearer_token)`
**Security Critical**: Ensures requests are from Google Chat, not attackers.

### `extract_message_text(chat_event)`
Parses Google Chat's JSON to get the user's question.

### `query_ca_agent(question)`
Calls the Vertex AI Agent Engine to get answers from the CA API.

### `handle_chat_event()`
Main webhook endpoint that orchestrates the entire flow.

## Debugging

### Check Cloud Run logs:
```bash
gcloud run services logs read gchat-connector --region=us-central1
```

### Test the health endpoint:
```bash
curl https://YOUR_CLOUD_RUN_URL/health
```

### Manually test with a sample payload:
```bash
curl -X POST https://YOUR_CLOUD_RUN_URL \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer fake-token-for-testing" \
  -d '{"message": {"text": "What were sales last month?"}}'
```

## Architecture Diagram

```
┌──────────────┐
│ Google Chat  │
│   (User)     │
└──────┬───────┘
       │ 1. User sends message
       │    "What were sales?"
       ▼
┌──────────────────────┐
│  gchat_connector     │
│  (Cloud Run)         │
│                      │
│ ┌─────────────────┐ │
│ │ verify_token()  │ │ 2. Security check
│ └─────────────────┘ │
│                      │
│ ┌─────────────────┐ │
│ │ extract_message()│ │ 3. Parse JSON
│ └─────────────────┘ │
│                      │
│ ┌─────────────────┐ │
│ │ query_ca_agent()│ │ 4. Call Vertex AI
│ └─────────────────┘ │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  ca_api_agent        │ 5. Process question
│  (Vertex AI)         │    with CA API
└──────────┬───────────┘
           │
           │ 6. Return answer
           ▼
     (back to user)
```

## Next Steps

After deploying this connector:
1. Complete the TODO items in `app.py`
2. Test with real questions in Google Chat
3. Monitor Cloud Run logs for errors
4. Implement rich card responses for better UX

---

**Questions?** Check the main project README or Google Cloud docs:
- [Google Chat API Overview](https://developers.google.com/chat)
- [Cloud Run Quickstart](https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-service)
