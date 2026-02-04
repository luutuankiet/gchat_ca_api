# Google Chat Conversational Analytics Demo

> **Ask data questions in Google Chat, get answers powered by Google Cloud's Conversational Analytics API**

This project replicates the Google Workspace Chat integration demo showcased in the [Conversational Analytics API launch blog post](https://cloud.google.com/blog/products/data-analytics/understanding-lookers-conversational-analytics-api).

## What This Does

Users can ask natural language questions about their data directly in Google Chat:

```
User: "What were sales last quarter?"
Bot:  [Returns chart + data from BigQuery/Looker]

User: "Show me top customers by region"
Bot:  [Returns table with analysis]
```

No context switching. No SQL. Just questions and answers.

## Architecture

```
┌─────────────────┐
│  Google Chat    │  ← Users ask questions here
│  (Chat App)     │
└────────┬────────┘
         │
         │ HTTP Webhook
         ▼
┌─────────────────┐
│ gchat_connector │  ← Flask app on Cloud Run
│  (Middleware)   │     Translates Chat ↔ Vertex AI
└────────┬────────┘
         │
         │ Vertex AI SDK
         ▼
┌─────────────────┐
│  ca_api_agent   │  ← ADK Agent on Vertex AI
│  (ADK Agent)    │     Handles NL queries
└────────┬────────┘
         │
         │ Streaming HTTP
         ▼
┌─────────────────┐
│   CA API        │  ← Conversational Analytics API
│ (Gemini + Data) │     Processes questions
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ BigQuery/Looker │  ← Your data
│  (Data Source)  │
└─────────────────┘
```

## Project Structure

```
gchat_ca_api/
├── ca_api_agent/           # Vertex AI Agent (The "Brain")
│   ├── agent.py            # ADK agent with nlq tool
│   ├── requirements.txt    # Python dependencies
│   └── README.md           # Agent documentation
│
├── gchat_connector/        # Cloud Run Service (The "Telephone")
│   ├── app.py              # Flask webhook handler
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile          # Container definition
│   └── README.md           # Connector documentation
│
├── deployment/             # Deployment automation
│   ├── deploy-agent.sh     # Deploy to Vertex AI
│   ├── deploy-connector.sh # Deploy to Cloud Run
│   └── DEPLOYMENT_GUIDE.md # Step-by-step instructions
│
├── docs/                   # Additional documentation
├── gsd-lite/               # Project planning documents
│   ├── PROJECT.md          # Vision and goals
│   └── WORK.md             # Research and decisions
│
├── ref/                    # Reference materials
│   └── blog.md             # Original Google blog post
│
├── .env.example            # Environment variable template
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## Quick Start

### Prerequisites

1. **Google Cloud Project** with billing enabled
2. **Conversational Analytics Agent** (create in BigQuery or Looker)
3. **gcloud CLI** installed and authenticated

### 5-Minute Setup

```bash
# 1. Clone and configure
git clone <your-repo>
cd gchat_ca_api
cp .env.example .env
# Edit .env with your project details

# 2. Load environment variables
source .env

# 3. Deploy the agent to Vertex AI
cd deployment
./deploy-agent.sh
# Copy the REASONING_ENGINE_ID from output

# 4. Update .env with REASONING_ENGINE_ID
echo "export REASONING_ENGINE_ID=<your-id>" >> .env
source .env

# 5. Deploy the connector to Cloud Run
./deploy-connector.sh
# Copy the Service URL from output

# 6. Configure Google Chat
# - Go to Cloud Console → Google Chat API → Configuration
# - Set App URL to your Cloud Run URL
# - Publish the app

# 7. Test in Google Chat!
```

Detailed instructions: [deployment/DEPLOYMENT_GUIDE.md](deployment/DEPLOYMENT_GUIDE.md)

## Implementation Status

This is a **working skeleton with TODOs**. The architecture is deployed and connected, but needs implementation completion:

### ✅ Complete
- [x] Project structure
- [x] ADK Agent skeleton
- [x] Flask connector skeleton
- [x] Deployment scripts
- [x] Documentation
- [x] Environment configuration

### 🚧 TODO (Implementation Needed)

**In `ca_api_agent/agent.py`:**
- [ ] Parse Server-Sent Events (SSE) from CA API
- [ ] Separate `systemMessage` (thinking) from `data` (results)
- [ ] Error handling and retry logic
- [ ] Token refresh for long-running queries

**In `gchat_connector/app.py`:**
- [ ] JWT verification for Google Chat webhooks
- [ ] ReasoningEngine client initialization
- [ ] Google Chat Cards for rich responses
- [ ] Error handling and user-friendly messages

See TODO comments in source files for details.

## Key Concepts

### The "Hub-and-Spoke" Pattern

This project uses a proven integration pattern:

1. **Google Chat** (Frontend) - Where users interact
2. **Cloud Run** (Connector) - Protocol translator
3. **Vertex AI** (Brain) - Intelligent agent
4. **CA API** (Intelligence) - Data processing
5. **BigQuery/Looker** (Data) - Source of truth

Each component is independent, testable, and replaceable.

### Why Streaming?

Data queries can take 10+ seconds. Instead of blocking, the CA API streams responses:
- **systemMessage**: Shows the agent's "thinking" process
- **data**: Returns results as they're ready

This creates a better UX - users see progress, not just a loading spinner.

### Why ADK?

The Agent Development Kit (ADK) provides:
- Standard interface for agent tools
- Automatic deployment to Vertex AI
- Integration with Google's AI services
- Built-in orchestration and error handling

## Reference Implementation

This skeleton is based on:
- **Repository**: [looker-open-source/ca-demos-and-tools](https://github.com/looker-open-source/ca-demos-and-tools)
- **Specific code**: `ca-api-adk-streaming/ca_api_agent/agent.py`
- **Commit**: `6eed78e512638cbcbfcec101f34a24234d5607b5`
- **Blog post**: [Understanding Looker's Conversational Analytics API](https://cloud.google.com/blog/products/data-analytics/understanding-lookers-conversational-analytics-api)

## Component Documentation

- **Agent**: [ca_api_agent/README.md](ca_api_agent/README.md)
- **Connector**: [gchat_connector/README.md](gchat_connector/README.md)
- **Deployment**: [deployment/DEPLOYMENT_GUIDE.md](deployment/DEPLOYMENT_GUIDE.md)

## Development

### Local Testing

```bash
# Test the agent locally
cd ca_api_agent
pip install -r requirements.txt
python agent.py

# Test the connector locally
cd gchat_connector
pip install -r requirements.txt
export $(cat ../.env | xargs)
python app.py
```

### Testing Flow

1. **Unit test components** separately
2. **Deploy to dev project** first
3. **Test with sample Chat messages** via curl
4. **Deploy to production** once verified

### Monitoring

```bash
# View Cloud Run logs
gcloud run services logs read gchat-connector --region=us-central1

# View Vertex AI logs
gcloud logging read "resource.type=aiplatform.googleapis.com/ReasoningEngine"
```

## Cost Estimates

Typical monthly costs (varies by usage):
- **Vertex AI Agent Engine**: ~$0.002 per request
- **Cloud Run**: First 2M requests free
- **CA API**: Based on Gemini API pricing
- **Networking**: Minimal

Set up [budget alerts](https://cloud.google.com/billing/docs/how-to/budgets) to track spending.

## Security

### Authentication Flow

```
Google Chat → JWT Token → Cloud Run verifies → Vertex AI (ADC) → CA API (OAuth)
```

- **Google Chat → Cloud Run**: JWT signed by `chat@system.gserviceaccount.com`
- **Cloud Run → Vertex AI**: Application Default Credentials
- **Vertex AI → CA API**: OAuth 2.0 token

### Best Practices

- ✅ Verify JWT tokens on every request
- ✅ Use least-privilege service accounts
- ✅ Enable Cloud Armor for DDoS protection
- ✅ Monitor logs for suspicious activity
- ✅ Keep dependencies updated

## Troubleshooting

### Common Issues

**"Permission denied" when deploying**
→ Check IAM roles: Vertex AI Admin, Cloud Run Admin

**Google Chat doesn't respond**
→ Check Cloud Run logs, verify App URL in Chat config

**CA API returns errors**
→ Verify CA_AGENT_ID, check agent is published

**Deployment hangs**
→ Check quotas: Cloud Console → IAM & Admin → Quotas

See [deployment/DEPLOYMENT_GUIDE.md](deployment/DEPLOYMENT_GUIDE.md) for detailed troubleshooting.

## Resources

### Documentation
- [Conversational Analytics API](https://cloud.google.com/gemini/docs/conversational-analytics-api/overview)
- [Agent Development Kit](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-development-kit/quickstart)
- [Google Chat API](https://developers.google.com/chat)
- [Cloud Run](https://cloud.google.com/run/docs)

### Examples
- [CA API Colab Notebooks](https://cloud.google.com/gemini/docs/conversational-analytics-api/overview#interactive-colab-notebooks)
- [Streamlit Reference App](https://github.com/looker-open-source/ca-api-quickstarts)
- [TypeScript Reference](https://github.com/looker-open-source/ca-demos-and-tools)

## Contributing

To complete the implementation:
1. Fork this repository
2. Complete the TODOs in `ca_api_agent/agent.py`
3. Complete the TODOs in `gchat_connector/app.py`
4. Test thoroughly
5. Update documentation
6. Submit a pull request

## License

This project skeleton is provided as-is for demonstration purposes.

## Support

For questions:
- Check component README files
- Review [DEPLOYMENT_GUIDE.md](deployment/DEPLOYMENT_GUIDE.md)
- File an issue in this repository

---

**Built with**
- Google Cloud Platform
- Vertex AI Agent Engine
- Conversational Analytics API
- Cloud Run
- Flask
- Python ADK

**Inspired by**
- [Understanding Looker's Conversational Analytics API](https://cloud.google.com/blog/products/data-analytics/understanding-lookers-conversational-analytics-api)
- [looker-open-source/ca-demos-and-tools](https://github.com/looker-open-source/ca-demos-and-tools)
