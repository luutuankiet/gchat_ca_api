# Architecture Overview

This document explains the technical architecture of the Google Chat Conversational Analytics demo.

## High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        User Layer                            │
│                                                              │
│  ┌────────────┐         ┌────────────┐                      │
│  │   Mobile   │         │    Web     │                      │
│  │ Google Chat│         │Google Chat │                      │
│  └─────┬──────┘         └─────┬──────┘                      │
│        └────────────┬──────────┘                            │
└─────────────────────┼───────────────────────────────────────┘
                      │
                      │ HTTPS Webhook
                      │ JSON Payload
                      ▼
┌──────────────────────────────────────────────────────────────┐
│                   Integration Layer                          │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │          gchat_connector (Cloud Run)               │    │
│  │                                                    │    │
│  │  ┌──────────────┐  ┌──────────────┐              │    │
│  │  │   Webhook    │  │   Security   │              │    │
│  │  │   Handler    │→ │ Verification │              │    │
│  │  └──────────────┘  └──────────────┘              │    │
│  │         │                                          │    │
│  │         ▼                                          │    │
│  │  ┌──────────────┐  ┌──────────────┐              │    │
│  │  │   Message    │  │   Vertex AI  │              │    │
│  │  │   Parser     │→ │  SDK Client  │              │    │
│  │  └──────────────┘  └──────┬───────┘              │    │
│  └────────────────────────────┼────────────────────────┘    │
└───────────────────────────────┼─────────────────────────────┘
                                │
                                │ Vertex AI SDK
                                │ ReasoningEngine.query()
                                ▼
┌──────────────────────────────────────────────────────────────┐
│                      Agent Layer                             │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │       ca_api_agent (Vertex AI Agent Engine)        │    │
│  │                                                    │    │
│  │  ┌──────────────┐  ┌──────────────┐              │    │
│  │  │  ADK Agent   │  │  nlq() Tool  │              │    │
│  │  │   Runtime    │→ │              │              │    │
│  │  └──────────────┘  └──────┬───────┘              │    │
│  │                            │                       │    │
│  │  ┌──────────────┐         │                       │    │
│  │  │   Streaming  │←────────┘                       │    │
│  │  │    Parser    │                                 │    │
│  │  └──────┬───────┘                                 │    │
│  └─────────┼────────────────────────────────────────────┘    │
└────────────┼─────────────────────────────────────────────────┘
             │
             │ HTTPS Streaming (SSE)
             │ Server-Sent Events
             ▼
┌──────────────────────────────────────────────────────────────┐
│                  Intelligence Layer                          │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │    Conversational Analytics API                    │    │
│  │                                                    │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐        │    │
│  │  │  Gemini  │  │   NLU    │  │  Query   │        │    │
│  │  │  Models  │→ │ Pipeline │→ │ Generator│        │    │
│  │  └──────────┘  └──────────┘  └─────┬────┘        │    │
│  │                                     │             │    │
│  │  ┌──────────┐  ┌──────────┐       │             │    │
│  │  │  Charts  │  │   Code   │←──────┘             │    │
│  │  │ Generator│  │Interpreter│                     │    │
│  │  └──────────┘  └──────────┘                     │    │
│  └─────────────────────────┬────────────────────────────┘    │
└────────────────────────────┼─────────────────────────────────┘
                             │
                             │ SQL / API Queries
                             ▼
┌──────────────────────────────────────────────────────────────┐
│                      Data Layer                              │
│                                                              │
│  ┌─────────────────┐      ┌─────────────────┐              │
│  │    BigQuery     │      │     Looker      │              │
│  │  Data Warehouse │      │  Semantic Layer │              │
│  └─────────────────┘      └─────────────────┘              │
└──────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

### 1. Google Chat (User Interface)
**Technology:** Google Workspace Chat
**Role:** Frontend

**Responsibilities:**
- Display conversational interface to users
- Capture user messages
- Send webhook events to Cloud Run
- Display bot responses

**Data Flow:**
- **Input:** User types message
- **Output:** JSON webhook to gchat_connector

**Example Payload:**
```json
{
  "type": "MESSAGE",
  "message": {
    "name": "spaces/.../messages/...",
    "sender": {
      "name": "users/123",
      "displayName": "John Doe"
    },
    "text": "What were sales last quarter?"
  }
}
```

### 2. gchat_connector (Integration Middleware)
**Technology:** Flask on Cloud Run
**Role:** Protocol Translator

**Responsibilities:**
- Receive Google Chat webhooks (HTTP POST)
- Verify JWT tokens for security
- Extract message text from JSON
- Call Vertex AI Agent Engine via SDK
- Format responses for Google Chat
- Handle errors and retries

**Data Flow:**
- **Input:** Google Chat webhook (JSON)
- **Output:** Vertex AI SDK call (Python object)

**Key Functions:**
- `verify_chat_token()`: Security check
- `extract_message_text()`: Parse webhook
- `query_ca_agent()`: Call Vertex AI
- `handle_chat_event()`: Main orchestrator

**Why Needed:**
Google Chat speaks "webhooks" (JSON events), but Vertex AI speaks "SDK calls" (Python objects). This connector translates between them.

### 3. ca_api_agent (AI Agent)
**Technology:** ADK (Agent Development Kit) on Vertex AI
**Role:** Intelligent Query Processor

**Responsibilities:**
- Receive natural language questions
- Stream queries to CA API
- Parse Server-Sent Events responses
- Separate "thinking" from "results"
- Return structured answers

**Data Flow:**
- **Input:** String question from connector
- **Output:** Streaming JSON responses

**Key Tool:**
```python
async def nlq(question: str, token: str) -> AsyncGenerator:
    # Streams responses from CA API
```

**Why Streaming:**
Data queries can take 10+ seconds. Streaming provides:
1. Immediate feedback ("I'm thinking...")
2. Partial results as they arrive
3. Better user experience

### 4. Conversational Analytics API (Intelligence)
**Technology:** Google Cloud Gemini + Data Services
**Role:** Natural Language to Data Pipeline

**Responsibilities:**
- Parse natural language questions
- Generate SQL/Looker queries
- Execute queries on data sources
- Create visualizations (charts)
- Run code for advanced analysis
- Generate text explanations

**Data Flow:**
- **Input:** Natural language question
- **Output:** Streaming response with:
  - `systemMessage`: Agent's thinking process
  - `data`: Query results, charts, text

**Example Response Stream:**
```
data: {"systemMessage": "Analyzing question..."}
data: {"systemMessage": "Querying sales database..."}
data: {"data": {"sql": "SELECT SUM(amount) FROM sales..."}}
data: {"data": {"chart": {...}, "text": "Total sales were $1.2M"}}
```

### 5. Data Layer (Source of Truth)
**Technology:** BigQuery and/or Looker
**Role:** Data Storage and Modeling

**Responsibilities:**
- Store raw data (BigQuery)
- Define semantic models (Looker)
- Execute SQL queries
- Apply access controls
- Return query results

**BigQuery:**
- Stores tables and datasets
- Executes SQL from CA API
- Applies row/column-level security

**Looker:**
- Provides semantic layer (business logic)
- Defines metrics and dimensions
- Translates business terms to SQL

## Request Flow Example

Let's trace a sample question through the system:

**User asks:** "What were sales last quarter?"

### 1. Google Chat → gchat_connector
```
POST https://gchat-connector-xyz.a.run.app
Headers:
  Authorization: Bearer eyJhbGc...  (JWT from Google)
Body:
{
  "message": {
    "text": "What were sales last quarter?"
  }
}
```

### 2. gchat_connector Processing
```python
# Security check
verify_chat_token(request.headers['Authorization'])

# Extract question
question = "What were sales last quarter?"

# Call Vertex AI
agent = ReasoningEngine(
    f"projects/{PROJECT}/locations/us-central1/reasoningEngines/{ID}"
)
response = agent.query(input=question)
```

### 3. gchat_connector → ca_api_agent
```python
# Vertex AI SDK serializes and sends:
{
  "input": "What were sales last quarter?",
  "agent_id": "ca-api-agent"
}
```

### 4. ca_api_agent → CA API
```python
# Agent streams request to CA API
POST https://geminidataanalytics.googleapis.com/.../chat
{
  "agentId": "your-ca-agent-id",
  "messages": [
    {
      "role": "user",
      "content": "What were sales last quarter?"
    }
  ]
}
```

### 5. CA API Processing
```
data: {"systemMessage": "Understanding question..."}
data: {"systemMessage": "Identifying relevant data..."}
data: {"systemMessage": "Generating SQL query..."}
data: {"data": {"sql": "SELECT SUM(revenue) FROM sales WHERE quarter = 'Q4'"}}
data: {"systemMessage": "Executing query..."}
data: {"data": {"table": [[1234567]], "columns": ["Total Revenue"]}}
data: {"data": {"text": "Sales last quarter were $1,234,567"}}
```

### 6. ca_api_agent Parsing
```python
# Agent parses SSE stream
async for chunk in response.aiter_bytes():
    if "systemMessage" in chunk:
        # Optional: Log or skip
        continue
    elif "data" in chunk:
        # Extract actual results
        yield parse_data(chunk)
```

### 7. gchat_connector → Google Chat
```python
# Format for Chat
return jsonify({
    "text": "Sales last quarter were $1,234,567",
    "cards": [...]  # Optional: rich formatting
})
```

### 8. Google Chat → User
```
Bot: Sales last quarter were $1,234,567
     [Chart showing trend]
```

**Total time:** 2-5 seconds

## Security Architecture

### Authentication Flow

```
┌─────────────┐
│ Google Chat │
└──────┬──────┘
       │
       │ 1. Signs request with JWT
       │    Issuer: chat@system.gserviceaccount.com
       ▼
┌──────────────────┐
│ gchat_connector  │
│                  │
│ verify_token()   │ 2. Verifies JWT signature
│                  │    Checks audience, expiry
└──────┬───────────┘
       │
       │ 3. Uses ADC (Application Default Credentials)
       ▼
┌──────────────────┐
│  Vertex AI       │
│                  │
│ Service Account  │ 4. Vertex AI service account
│                  │    calls CA API with OAuth
└──────┬───────────┘
       │
       │ 5. OAuth 2.0 token
       ▼
┌──────────────────┐
│      CA API      │
└──────────────────┘
```

### Security Layers

1. **Google Chat → Cloud Run:**
   - JWT token verification
   - Signed by Google service account
   - Validates audience and expiry

2. **Cloud Run → Vertex AI:**
   - Application Default Credentials
   - Service account with least privilege
   - IAM role: `roles/aiplatform.user`

3. **Vertex AI → CA API:**
   - OAuth 2.0 access token
   - Scoped to CA API only
   - Auto-refreshed by Google libraries

4. **CA API → Data:**
   - Looker/BigQuery access controls
   - Row-level security
   - Column-level security
   - Audit logging

## Performance Considerations

### Latency Budget

| Component | Typical Latency |
|-----------|----------------|
| Google Chat → Cloud Run | 50-100ms |
| Cloud Run processing | 10-50ms |
| Cloud Run → Vertex AI | 100-200ms |
| Vertex AI → CA API | 50-100ms |
| CA API processing | 2-10 seconds |
| Data query execution | 1-5 seconds |
| **Total** | **3-15 seconds** |

### Optimization Strategies

**Streaming:**
- Start showing results after 500ms
- Stream "thinking" messages
- Display partial results

**Caching:**
- Cache common queries in CA API
- Use Looker's query cache
- Cache BigQuery results

**Scaling:**
- Cloud Run auto-scales 0→1000 instances
- Vertex AI handles concurrent requests
- CA API has built-in rate limiting

## Error Handling

### Error Flow

```
User Question
     │
     ▼
┌─────────────────┐
│ gchat_connector │
└────────┬────────┘
         │
         ├─ Network Error? → Retry 3x with backoff
         │
         ▼
┌─────────────────┐
│  ca_api_agent   │
└────────┬────────┘
         │
         ├─ Parsing Error? → Log and return placeholder
         │
         ▼
┌─────────────────┐
│     CA API      │
└────────┬────────┘
         │
         ├─ Query Error? → Return error message to user
         │
         ▼
User sees: "Sorry, I couldn't process that question."
```

### Error Types

1. **Network Errors:** Retry with exponential backoff
2. **Auth Errors:** Refresh tokens automatically
3. **Query Errors:** User-friendly error messages
4. **Timeout Errors:** Cancel and notify user

## Monitoring

### Key Metrics

**Cloud Run (gchat_connector):**
- Request count
- Error rate (4xx, 5xx)
- Latency (p50, p95, p99)
- Instance count

**Vertex AI (ca_api_agent):**
- Request count
- Success rate
- Average processing time
- Token usage

**CA API:**
- Query count
- Query errors
- Average query time
- Cost per query

### Logging Strategy

```python
# Structured logging
logger.info("Query received", extra={
    "user_id": user_id,
    "question": question,
    "timestamp": datetime.now()
})

logger.info("CA API response", extra={
    "query_time_ms": duration,
    "result_rows": len(results),
    "chart_type": chart_type
})
```

## Scalability

### Current Limits

- **Cloud Run:** 1000 concurrent instances
- **Vertex AI:** Project quotas apply
- **CA API:** Rate limits per project

### Scaling Strategy

1. **Horizontal:** Cloud Run auto-scales
2. **Vertical:** Increase memory/CPU per instance
3. **Regional:** Deploy to multiple regions
4. **Caching:** Reduce API calls for common queries

## Next Steps

For implementation details, see:
- [gchat_connector/app.py](../gchat_connector/app.py) - Connector code
- [ca_api_agent/agent.py](../ca_api_agent/agent.py) - Agent code
- [DEPLOYMENT_GUIDE.md](../deployment/DEPLOYMENT_GUIDE.md) - Deployment
