# Cost Estimate Report: Gemini 2.5 Flash Stack

**Date:** February 06, 2026
**Model:** Gemini 2.5 Flash (GA)
**Region:** us-central1 (Tier 1)

## Executive Summary

Using **Gemini 2.5 Flash** significantly optimizes cost-to-performance. The stack remains extremely affordable for development and pilot phases, with production costs scaling linearly with usage.

| Phase | Monthly Queries | Estimated Cost | Main Cost Driver |
|:---|:---:|:---:|:---|
| **Development** | 100 | **< $0.20** | Negligible |
| **Pilot** | 10,000 | **~ $16.00** | Model Tokens |
| **Production** | 100,000 | **~ $220.00** | Model Tokens + Data Scanning |

---

## 1. Pricing Breakdown by Component

### A. Intelligence: Gemini 2.5 Flash
This model offers a balance of speed and reasoning capability.
*   **Input Cost:** $0.30 per 1 million tokens
*   **Output Cost:** $2.50 per 1 million tokens
*   **Estimated Per-Query Cost:** **$0.0014**
    *   *Assumption:* 500 input tokens (Context + Question) + 500 output tokens (Reasoning + Answer).

### B. Brain: Vertex AI Agent Engine
Orchestrates the agent and tools.
*   **Active Runtime:** ~$0.11 per hour (vCPU + Memory)
*   **Billing:** Pay only when the agent is processing a request.

### C. Connector: Cloud Run
Handles the webhooks from Google Chat.
*   **Tier 1 Pricing:** Pay per vCPU-second.
*   **Free Tier:** First 180,000 vCPU-seconds & 2 million requests per month are **FREE**.

### D. Data: BigQuery
Storage and analysis.
*   **Analysis:** $6.25 per TiB scanned.
*   **Free Tier:** First 1 TiB per month is **FREE**.

---

## 2. Detailed Scenario Analysis

### Scenario 1: Development / Demo
*Usage: 100 queries/month (Single developer testing)*

| Component | Usage Estimate | Cost Calculation | Total |
|-----------|----------------|------------------|-------|
| **Gemini 2.5 Flash** | 100k tokens | 100 * $0.0014 | $0.14 |
| **Vertex Agent** | ~10 mins active | Negligible | $0.00 |
| **Cloud Run** | 100 requests | Fully covered by Free Tier | $0.00 |
| **BigQuery** | < 1 GB scanned | Fully covered by Free Tier | $0.00 |
| **TOTAL** | | | **$0.14** |

### Scenario 2: Pilot
*Usage: 10,000 queries/month (Small team internal tool)*

| Component | Usage Estimate | Cost Calculation | Total |
|-----------|----------------|------------------|-------|
| **Gemini 2.5 Flash** | 10M tokens | 10,000 * $0.0014 | $14.00 |
| **Vertex Agent** | ~14 hours active | 14 hrs * $0.11 | $1.54 |
| **Cloud Run** | 10k requests | Fully covered by Free Tier | $0.00 |
| **BigQuery** | ~100 GB scanned | Fully covered by Free Tier | $0.00 |
| **TOTAL** | | | **$15.54** |

### Scenario 3: Production
*Usage: 100,000 queries/month (Enterprise deployment)*

| Component | Usage Estimate | Cost Calculation | Total |
|-----------|----------------|------------------|-------|
| **Gemini 2.5 Flash** | 100M tokens | 100,000 * $0.0014 | $140.00 |
| **Vertex Agent** | ~140 hours active | 140 hrs * $0.11 | $15.40 |
| **Cloud Run** | 500k vCPU-sec | (500k - 180k free) * $0.000024 | $7.68 |
| **BigQuery** | 10 TB scanned | (10 TiB - 1 TiB free) * $6.25 | $56.25 |
| **TOTAL** | | | **$219.33** |

---

## 3. Risk Factors & Recommendations

### ⚠️ BigQuery Scanning Costs (Highest Volatility)
*   **Risk:** A poorly written query (e.g., `SELECT *`) can scan TBs of data in seconds, costing $6.25 per query immediately.
*   **Mitigation:**
    1.  Partition and Cluster tables by Date/Region.
    2.  Set a **Maximum Bytes Billed** limit per query in BigQuery settings.
    3.  Ensure the Agent prompt is instructed to write optimized SQL (select only needed columns).

### ⚠️ Infinite Loops
*   **Risk:** Agent getting stuck in a tool-calling loop.
*   **Mitigation:** Vertex AI Agent Engine has built-in recursion limits, but setting a timeout on the Cloud Run connector (e.g., 60s) is a good safety net.

### ⚠️ Idle Instances
*   **Risk:** Setting `min-instances > 0` on Cloud Run to improve speed.
*   **Cost Impact:** One always-on instance costs ~$25/month regardless of traffic.
*   **Recommendation:** Keep `min-instances=0` unless sub-second latency is critical.

---

## 4. Conclusion
For the proposed use case, **Gemini 2.5 Flash is the optimal choice**. It provides sophisticated reasoning capabilities at ~1/4th the cost of older Pro models, making the project viable even at high scale. The primary cost control focus should be on **BigQuery optimization**, not the AI model tokens.