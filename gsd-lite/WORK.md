# GSD-Lite Work Log

<!--
PERPETUAL SESSION WORK LOG - captures all work during project execution.
Tracks vision, planning, execution, decisions, and blockers across multiple tasks.
-->

---

## 1. Current Understanding

<current_mode>
discuss (architectural definition complete, evidence gathered)
</current_mode>

<active_task>
Task: PHASE-01 - Foundation & Data Setup
</active_task>

<vision>
User wants a "Hub-and-Spoke" demo: Google Chat -> Connector -> Agent Engine -> CA API -> Data.
Goal: Demo chatting with business data in Google Workspace.
</vision>

<decisions>
[DECISION-001] Architecture: ADK Agent (Vertex AI) + Flask Connector (Cloud Run).
[DECISION-002] Source of Truth: `looker-open-source/ca-demos-and-tools` (Commit: `ec333f4`).
</decisions>

---

## 2. Key Events Index

| Log ID | Type | Task | Summary |
|--------|------|------|---------|
| LOG-001 | DISCOVERY | ARCH-DEF | Located exact ADK Agent implementation (SHA: 6eed78e) |
| LOG-002 | DISCOVERY | ARCH-DEF | Verified Flask/Vertex integration pattern via Google Docs |
| LOG-003 | DECISION | ARCH-DEF | Defined 4-layer architecture based on verified components |
| LOG-004 | ESTIMATION | PHASE-01 | Cost Analysis for Gemini 2.5 Flash Stack |

---

## 3. Atomic Session Log (Evidence & Citations)

### [LOG-001] - [DISCOVERY] - Located Definitive ADK Agent Source Code - Task: ARCH-DEF
**Timestamp:** 2026-02-04 10:30
**Source of Truth (Citations):**
- **Repository:** `looker-open-source/ca-demos-and-tools`
- **File:** `ca-api-adk-streaming/ca_api_agent/agent.py`
- **Commit SHA:** `6eed78e512638cbcbfcec101f34a24234d5607b5` (Verified via `github_get_file_contents`)
- **Primary Source:** [Google Cloud Blog: Understanding Looker's Conversational Analytics API](https://cloud.google.com/blog/products/data-analytics/understanding-lookers-conversational-analytics-api) (Ref: `ref/blog.md`)

**Investigation Trace (Debug Verbose):**
1.  **Input:** Read `ref/blog.md` -> Identified key terms "Conversational Analytics API", "Agent Development Kit", "Slack/Chat".
2.  **Search:** Tool `github__get_file_contents` on repo `looker-open-source/ca-demos-and-tools`.
3.  **Drill-down:**
    *   List root -> Found `ca-api-adk` and `ca-api-adk-streaming`.
    *   Read `ca-api-adk-streaming/README.md` (SHA: `978b178`) -> Confirmed it "can be run locally or deployed to Agent Engine".
    *   **CRITICAL HIT:** Read `ca-api-adk-streaming/ca_api_agent/agent.py` -> Found the `nlq` tool implementation.

**The "Smoking Gun" Code (Line 42, `agent.py`):**
This code proves the API requires a specific streaming implementation (`AsyncGenerator`) to handle the "thinking" process, not just a simple REST call.
```python
# Sourced from looker-open-source/ca-demos-and-tools @ 6eed78e
async def nlq(question: str, token: str, ctx: InvocationContext) -> AsyncGenerator:
    # ...
    url = f"https://geminidataanalytics.googleapis.com/v1beta/projects/{os.getenv("GOOGLE_CLOUD_PROJECT")}/locations/{os.getenv("GOOGLE_CLOUD_LOCATION")}:chat"
    # ...
    async with httpx.AsyncClient() as client:
        async with client.stream("POST", url, json=payload, headers=headers, timeout=None) as response:
            # ...
            async for chunk in response.aiter_bytes():
                # Logic to parse "systemMessage" (Thinking) vs "data" (Results)
```

**Cherry on Top (Concept Explainer):**
*   **The Artifact:** The `nlq` function acts like a "ticker tape" reader. Instead of waiting for the full report, it reads the data character-by-character as it arrives from Google.
*   **Why it matters:** If we built this with a standard request/response (like a normal website), the chat would hang for 10+ seconds while the data crunching happens. This code proves we *must* build a streaming connector.

---

### [LOG-002] - [DISCOVERY] - Verified Google Chat <-> Vertex AI Integration Pattern - Task: ARCH-DEF
**Timestamp:** 2026-02-04 10:45
**Source of Truth (Citations):**
- **Documentation:** Google Chat API "Receive messages from Google Chat"
- **Documentation:** Vertex AI Agent Engine "Query a deployed agent"
- **Search Query:** `python google chat app http endpoint call vertex ai agent engine`
- **Result ID:** `tools_mmcp_google_grounding__search_documentation` (Result #1 & #2)

**Investigation Trace (Debug Verbose):**
1.  **Hypothesis:** We need a "middleman" because Google Chat webhooks (HTTP POST) cannot talk directly to Vertex AI Agent Engine (gRPC/Specialized REST).
2.  **Verification:** Ran `google_grounding__search_documentation`.
3.  **Findings:**
    *   **Chat Side:** Requires an HTTP endpoint that verifies `Bearer` tokens signed by `chat@system.gserviceaccount.com`.
    *   **Vertex Side:** Requires the `vertexai.agent_engines.ReasoningEngine` SDK class.
    *   **Integration:** Validated that a Python Flask app on Cloud Run is the standard "Glue" pattern.

**The "Glue" Pattern (Synthesized from Documentation):**
```python
# Validated against Google Chat API docs & Vertex AI SDK
from vertexai.agent_engines import ReasoningEngine

# 1. The "Brain" Connection (Vertex AI SDK)
agent = ReasoningEngine("projects/123/locations/us-central1/reasoningEngines/456")

# 2. The "Ear" (Google Chat Webhook)
@app.route('/', methods=['POST'])
def receive_chat_event():
    # Verify token from chat@system.gserviceaccount.com (Critical Security Step)
    # ... verification logic ...
    
    # Forward to Brain
    response = agent.query(input=request.json['message']['text'])
    return {"text": response.output['text']}
```

**Cherry on Top (Concept Explainer):**
*   **The Concept:** Protocol Translation.
*   **The Reality:** Google Chat yells in "Events" (JSON blobs). The Agent Brain listens in "Questions" (Strings).
*   **The Fix:** This Connector code is the "Interpreter" standing in the middle. It takes the JSON blob, pulls out the question, hands it to the Brain, and hands the answer back. Without this specific Flask code, the two systems remain deaf to each other.

---

### [LOG-003] - [DECISION] - Confirmed "Hub-and-Spoke" Architecture - Task: ARCH-DEF
**Timestamp:** 2026-02-04 11:00
**Basis of Decision:**
- **Evidence A:** `LOG-001` proves we have a working Agent implementation (`CaApiAgent`).
- **Evidence B:** `LOG-002` proves we have a valid connectivity pattern (Flask Connector).
- **Constraint:** User requested a "clean slate" project, so we must assemble these proven components from scratch, not fork the repo directly.

**The Blueprint (Derived from Evidence):**
1.  **Frontend:** Google Chat (The interface).
2.  **Connector:** Cloud Run Service (The Python Flask code from LOG-002).
3.  **Brain:** Vertex AI Agent Engine (The `CaApiAgent` code from LOG-001).
4.  **Intelligence:** Conversational Analytics API (The streaming HTTP call from LOG-001).
5.  **Data:** Looker/BigQuery (The source).

**Cherry on Top (Concept Explainer):**
*   **The Analogy:**
    *   **Looker:** The Library (Contains all the books/data).
    *   **CA API:** The Librarian (Knows how to find the answer in the books).
    *   **Agent Engine:** The Research Assistant (Takes your question, asks the Librarian, and summarizes the answer).
    *   **Connector:** The Telephone (Connects you to the Research Assistant).
    *   **Google Chat:** You (Asking the question).
*   **Why this works:** We aren't reinventing the wheel. We are simply connecting the Telephone (Chat) to the Researcher (Agent).

---

### [LOG-004] - [ESTIMATION] - Cost Analysis for Gemini 2.5 Flash Stack - Task: PHASE-01
**Timestamp:** 2026-02-06 12:00
**Summary:**
Generated detailed cost estimate for the proposed stack using Gemini 2.5 Flash.
- **Development:** < $0.20/month
- **Pilot:** ~ $16.00/month
- **Production:** ~ $220.00/month

**Key Findings:**
- **Gemini 2.5 Flash** is highly cost-effective ($0.30/M input, $2.50/M output).
- **BigQuery** scanning is the highest volatility risk factor in production.
- **Cloud Run/Vertex Runtime** costs are negligible for dev/pilot due to free tiers.

**Artifact:** `estimate.md` created with full breakdown.
