# Complete Deployment Guide

This guide walks you through deploying the entire Google Chat Conversational Analytics demo from scratch.

## Overview

You'll deploy two components:
1. **CA API Agent** (Vertex AI Agent Engine) - The "Brain"
2. **Google Chat Connector** (Cloud Run) - The "Telephone"

Then configure Google Chat to connect to them.

## Prerequisites

### 1. Google Cloud Project Setup

- Create a new Google Cloud project (or use existing)
- Enable billing (required for Vertex AI and Cloud Run)
- Install [gcloud CLI](https://cloud.google.com/sdk/docs/install)

### 2. Required APIs

These will be enabled automatically by the deployment scripts, but you can enable them manually:

```bash
gcloud services enable aiplatform.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable chat.googleapis.com
gcloud services enable storage.googleapis.com
```

### 3. Create a Conversational Analytics Agent

Before deploying, you need a CA agent:

**Option A: BigQuery Agent**
1. Go to [BigQuery Studio](https://console.cloud.google.com/bigquery)
2. Click "Gemini" → "Create Agent"
3. Select your dataset
4. Configure and save
5. Note the **Agent ID**

**Option B: Looker Agent**
1. Go to Looker Studio
2. Create a Conversational Analytics agent
3. Note the **Agent ID**

**Finding your Agent ID:**
- In BigQuery: It's in the agent URL or agent settings
- Format: Usually a UUID like `a1b2c3d4-e5f6-...`

## Step-by-Step Deployment

### Step 1: Set Environment Variables

Create a file `deployment/.env` with your configuration:

```bash
# Your Google Cloud project ID
export GOOGLE_CLOUD_PROJECT="your-project-id"

# Region (must support Vertex AI and Cloud Run)
export GOOGLE_CLOUD_LOCATION="us-central1"

# Your Conversational Analytics agent ID (from prerequisites)
export CA_AGENT_ID="your-ca-agent-id"
```

Load the variables:

```bash
cd deployment
source .env
```

### Step 2: Deploy the CA API Agent to Vertex AI

This is the "Brain" that processes data questions.

```bash
./deploy-agent.sh
```

**What this does:**
- Authenticates with Google Cloud
- Enables required APIs
- Uploads your agent code to Vertex AI
- Creates a Reasoning Engine instance
- Returns a **Reasoning Engine ID**

**Expected output:**
```
Created reasoning engine: projects/123/locations/us-central1/reasoningEngines/456789
```

**IMPORTANT:** Copy the Reasoning Engine ID (the number at the end: `456789`)

Save it:
```bash
export REASONING_ENGINE_ID="456789"
```

**Troubleshooting:**
- If deployment fails with "API not enabled", wait 2-3 minutes and retry
- If you get permission errors, ensure your account has Vertex AI Admin role
- Check logs: `gcloud logging read --limit 50`

### Step 3: Deploy the Google Chat Connector to Cloud Run

This is the "Telephone" that connects Google Chat to your agent.

```bash
./deploy-connector.sh
```

**What this does:**
- Builds a Docker container with your Flask app
- Deploys to Cloud Run
- Sets environment variables
- Returns a **Service URL**

**Expected output:**
```
Service URL: https://gchat-connector-abc123-uc.a.run.app
```

**IMPORTANT:** Copy the Service URL

**Troubleshooting:**
- If build fails, check Docker is running
- If deployment hangs, check Cloud Run quotas
- Test the health endpoint: `curl https://YOUR_URL/health`

### Step 4: Configure Google Chat App

Now we connect Google Chat to your deployed connector.

#### A. Enable Google Chat API

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to **APIs & Services** → **Library**
3. Search for "Google Chat API"
4. Click **Enable**

#### B. Configure the Chat App

1. Go to **APIs & Services** → **Enabled APIs** → **Google Chat API**
2. Click **Configuration** tab
3. Fill in the form:

**App name:** Data Assistant

**Avatar:** (optional) Upload an icon

**Description:** Ask questions about your data in natural language

**Connection settings:**
- **App URL:** `https://gchat-connector-abc123-uc.a.run.app` (your Cloud Run URL from Step 3)
- **Authentication:** Select "App-provided authentication"

**Functionality:**
- ✅ Enable "Receive 1:1 messages"
- ✅ Enable "Join spaces and group conversations"

**Slash commands:** (optional)
- Name: `/ask`
- Description: "Ask a data question"
- Command ID: `1`

**Permissions:**
- Select "Specific people and groups in your domain"
- Add yourself as a tester

4. Click **Save**

#### C. Publish the App

1. Under **Configuration**, click **Publish app**
2. Choose visibility (e.g., "Available to domain")
3. Confirm publication

### Step 5: Test the Integration

1. **Open Google Chat** (web or mobile)
2. **Find your app:**
   - Click "+" to start a chat
   - Search for "Data Assistant" (or your app name)
3. **Send a test message:**
   ```
   What were sales last quarter?
   ```
4. **Expected response:**
   ```
   TODO: Query CA API with question: 'What were sales last quarter?'
   ```

This confirms the plumbing works! The placeholder response means you need to complete the TODOs in the code.

## Architecture Verification

If everything is deployed correctly:

```
┌──────────────┐
│ Google Chat  │ ← You tested this in Step 5
└──────┬───────┘
       ▼
┌──────────────────────┐
│  gchat-connector     │ ← Deployed in Step 3
│  (Cloud Run)         │
└──────┬───────────────┘
       ▼
┌──────────────────────┐
│  ca-api-agent        │ ← Deployed in Step 2
│  (Vertex AI)         │
└──────┬───────────────┘
       ▼
┌──────────────────────┐
│  CA API              │ ← Your CA_AGENT_ID from Step 1
│  (BigQuery/Looker)   │
└──────────────────────┘
```

## Next Steps: Complete the Implementation

The skeleton is deployed, but has placeholder TODOs. To make it fully functional:

### In `ca_api_agent/agent.py`:
1. Complete the streaming SSE parser in the `nlq()` function
2. Add proper error handling for CA API failures
3. Implement token refresh logic

### In `gchat_connector/app.py`:
1. Implement real JWT verification in `verify_chat_token()`
2. Uncomment and configure the `ReasoningEngine` client
3. Add Google Chat Cards for rich responses (charts, tables)

See the TODO comments in each file for details.

## Monitoring and Debugging

### Check Cloud Run Logs
```bash
gcloud run services logs read gchat-connector \
  --region=us-central1 \
  --limit=50
```

### Check Vertex AI Logs
```bash
gcloud logging read "resource.type=aiplatform.googleapis.com/ReasoningEngine" \
  --limit=50
```

### Test Directly
```bash
# Test Cloud Run health
curl https://YOUR_CLOUD_RUN_URL/health

# Test with a sample payload
curl -X POST https://YOUR_CLOUD_RUN_URL \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test-token" \
  -d '{"message": {"text": "test question"}}'
```

## Costs

Estimated costs (varies by usage):
- **Vertex AI Agent Engine**: ~$0.002 per request
- **Cloud Run**: First 2 million requests free, then $0.40/million
- **CA API**: Based on Gemini API pricing
- **BigQuery/Looker**: Depends on your data setup

Set up [budget alerts](https://cloud.google.com/billing/docs/how-to/budgets) to monitor spending.

## Updating the Deployment

To redeploy after code changes:

```bash
# Redeploy agent
cd deployment
./deploy-agent.sh

# Redeploy connector
./deploy-connector.sh
```

Cloud Run auto-builds from source, so changes to `gchat_connector/app.py` take effect immediately.

## Cleanup

To delete all resources:

```bash
# Delete Cloud Run service
gcloud run services delete gchat-connector --region=us-central1

# Delete Vertex AI Reasoning Engine
gcloud vertex-ai reasoning-engines delete REASONING_ENGINE_ID \
  --region=us-central1

# Delete Google Chat app
# (Manual: Go to Console → Chat API → Configuration → Delete)
```

## Troubleshooting

### "Permission denied" errors
- Ensure your user has these roles:
  - Vertex AI Admin
  - Cloud Run Admin
  - Service Account User

### "Quota exceeded"
- Check [Quotas page](https://console.cloud.google.com/iam-admin/quotas)
- Request increases if needed

### Google Chat doesn't respond
1. Check Cloud Run logs for incoming requests
2. Verify the App URL is correct in Chat configuration
3. Test the endpoint with curl
4. Check "allow-unauthenticated" is set on Cloud Run

### Agent returns errors
1. Verify `CA_AGENT_ID` is correct
2. Check the CA agent is published and accessible
3. Verify your project has CA API enabled

## Support Resources

- [Conversational Analytics API Docs](https://cloud.google.com/gemini/docs/conversational-analytics-api/overview)
- [Google Chat API Docs](https://developers.google.com/chat)
- [Vertex AI Agent Engine Docs](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-development-kit/quickstart)
- [Cloud Run Docs](https://cloud.google.com/run/docs)

---

**Need help?** Check the main README or file an issue in the project repository.
