# 10-Minute Quickstart Guide

Get your Google Chat data assistant running in 10 minutes.

## Prerequisites Checklist

Before starting, ensure you have:

- [ ] Google Cloud account with billing enabled
- [ ] `gcloud` CLI installed ([Download](https://cloud.google.com/sdk/docs/install))
- [ ] A Conversational Analytics agent (BigQuery or Looker)
- [ ] 10 minutes of focused time

## Step 1: Setup (2 minutes)

```bash
# Clone the repository
git clone <your-repo-url>
cd gchat_ca_api

# Copy environment template
cp .env.example .env
```

Edit `.env` and fill in:
```bash
GOOGLE_CLOUD_PROJECT=your-project-id        # Your GCP project
GOOGLE_CLOUD_LOCATION=us-central1           # Region
CA_AGENT_ID=your-ca-agent-id                # From BigQuery/Looker
```

## Step 2: Deploy Agent (3 minutes)

```bash
# Load environment
source .env

# Deploy to Vertex AI
cd deployment
./deploy-agent.sh
```

**Expected output:**
```
Created reasoning engine: projects/.../reasoningEngines/123456
                                                        ^^^^^^
```

**Action:** Copy the number (e.g., `123456`) and add to `.env`:
```bash
echo "export REASONING_ENGINE_ID=123456" >> .env
source .env
```

## Step 3: Deploy Connector (2 minutes)

```bash
# Still in deployment/
./deploy-connector.sh
```

**Expected output:**
```
Service URL: https://gchat-connector-xyz-uc.a.run.app
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
```

**Action:** Copy this entire URL

## Step 4: Configure Google Chat (2 minutes)

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to **APIs & Services** → **Library**
3. Enable **Google Chat API**
4. Go to **Google Chat API** → **Configuration**
5. Fill in:
   - **App name**: Data Assistant
   - **App URL**: `https://gchat-connector-xyz-uc.a.run.app` (from Step 3)
   - **Authentication**: App-provided authentication
   - ✅ Enable "Receive 1:1 messages"
6. Click **Save**
7. Click **Publish app**

## Step 5: Test (1 minute)

1. Open [Google Chat](https://chat.google.com)
2. Click **+** → **Find apps**
3. Search for "Data Assistant"
4. Send: `Hello!`

**Expected response:**
```
TODO: Query CA API with question: 'Hello!'
```

**Success!** The plumbing works. You now have:
- ✅ Agent deployed to Vertex AI
- ✅ Connector deployed to Cloud Run
- ✅ Google Chat connected

## Next Steps

The skeleton responds with placeholders. To get real data answers:

### Complete the Implementation

**In `ca_api_agent/agent.py`:**
1. Uncomment and complete the SSE parsing logic
2. Add error handling

**In `gchat_connector/app.py`:**
1. Implement JWT verification
2. Uncomment the ReasoningEngine client code
3. Add rich response formatting

See TODO comments in each file.

### Test with Real Questions

Once implemented, try:
```
What were sales last month?
Show me top customers by region
Compare Q1 vs Q2 revenue
```

## Troubleshooting

### "Permission denied"
→ Run: `gcloud auth application-default login`

### "API not enabled"
→ Wait 2-3 minutes after enabling APIs, then retry

### Chat app doesn't respond
→ Check logs: `gcloud run services logs read gchat-connector`

### "Invalid agent ID"
→ Verify `CA_AGENT_ID` in `.env` matches your BigQuery/Looker agent

## Architecture Recap

What you just deployed:

```
Google Chat (your test message)
    ↓
Cloud Run (gchat-connector - Flask app)
    ↓
Vertex AI (ca_api_agent - ADK agent)
    ↓
CA API (Conversational Analytics)
    ↓
Your Data (BigQuery/Looker)
```

## Useful Commands

```bash
# View connector logs
gcloud run services logs read gchat-connector --region=us-central1

# View agent logs
gcloud logging read "resource.type=aiplatform.googleapis.com/ReasoningEngine"

# Test connector health
curl https://YOUR_CLOUD_RUN_URL/health

# Redeploy after changes
cd deployment
./deploy-connector.sh  # Updates Cloud Run
```

## What's Next?

1. **Complete TODOs** in source code
2. **Test with data questions** once implemented
3. **Deploy to production** project
4. **Add monitoring** and alerting
5. **Share with team** in Google Chat

## Need Help?

- Full guide: [../deployment/DEPLOYMENT_GUIDE.md](../deployment/DEPLOYMENT_GUIDE.md)
- Agent docs: [../ca_api_agent/README.md](../ca_api_agent/README.md)
- Connector docs: [../gchat_connector/README.md](../gchat_connector/README.md)
- Main README: [../README.md](../README.md)

---

**Total time:** ~10 minutes
**Result:** Working skeleton ready for implementation
