https://cloud.google.com/blog/products/data-analytics/understanding-lookers-conversational-analytics-api
  cloud.google.com uses cookies from Google to deliver and enhance the quality of its services and to analyze traffic. [Learn more](https://policies.google.com/technologies/cookies?hl=en)
Hide
Data Analytics
August 25, 2025
##### Richard Kuzma
Group Product Manager, Data Agents
##### Try Gemini 3
Our most intelligent model is now available on Vertex AI and Gemini Enterprise
[Try now ](https://console.cloud.google.com/vertex-ai/studio/multimodal)
Decision-makers, employees, and customers all need answers where they work: in the applications they use every day. In recent years, the rise of AI-powered BI has transformed our relationship with data, enabling us to ask questions in natural language and get answers fast. But even with support for natural language, the insights you receive are often confined to the data in your BI tool. At Google Cloud, our goal is to change this.
At Google Cloud Next 25, [we introduced the Conversational Analytics API](https://cloud.google.com/blog/products/data-analytics/looker-bi-platform-gets-ai-powered-data-exploration), which lets developers embed natural-language query functionality in custom applications, internal tools, or workflows, all backed by trusted data access and scalable, reliable data modeling. The API is already powering first-party Google Cloud conversational experiences including Looker and BigQuery data canvas, and is available for Google Cloud developers of all stripes to implement wherever their imagination takes them. **Today we release the Conversational Analytics API in public preview.**[ Start building with our documentation](https://cloud.google.com/gemini/docs/conversational-analytics-api/overview).
The Conversational Analytics API lets you build custom data experiences that provide data, chart, and text answers while leveraging Looker's trusted semantic model for accuracy or providing critical business and data context to agents in BigQuery. You can embed this functionality to create intuitive data experiences, enable complex analysis via natural language, and even orchestrate conversational analytics agents as ‘tools’ for an orchestrator agent using [Agent Development Kit](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-development-kit/quickstart).
The Google Health Population app is being developed with the Conversational Analytics API
### **Getting to know the Conversational Analytics API**
The Conversational Analytics API allows you to interact with your BigQuery or Looker data through chat, from anywhere. Embed side-panel chat next to your Looker dashboards, invoke agents in chat applications like Slack, customize your company’s web applications, or build multi-agent systems.
This API empowers your team to obtain answers precisely when and where they are needed, directly within their daily workflows. It achieves this by merging Google's advanced AI models and agentic capabilities with Looker's semantic layer and BigQuery's context engineering services. The result is natural language experiences that can be shared across your organization, making data-to-insight interaction seamless in your company's most frequently used applications.
Building with Google’s Analytics and AI stack comes with significant benefits in accurate question answering:
  * Best-in-class AI for data analytics
  * An agentic architecture that enables the system to perceive its environment and take actions
  * Access to Looker’s powerful semantic layer for trustworthy answers
  * [High-performance agent tools](https://cloud.google.com/blog/products/business-intelligence/use-conversational-analytics-api-for-natural-language-ai?e=48754805), including software functions, charts and APIs, supported by dedicated engineering teams
  * Python code interpreter for advanced analysis
  * Tune your agent’s knowledge with [structured context and prompts](https://cloud.google.com/gemini/docs/conversational-analytics-api/data-agent-system-instructions)


Flexibility to build the agentic applications that best suit your data needs:
  * Create, update, and share agents that let users chat with BigQuery or Looker data 
  * Lower maintenance burden via stateful APIs for agent and conversation management
  * Full control of your user experience via our stateless chat API
  * Build multi-agent architectures by wrapping APIs with [ADK](https://github.com/google/adk-python) and [MCP](https://github.com/googleapis/genai-toolbox)
  * Help agents understand your business and data with AI-Assisted context engineering
  * Version control your agents, updating prompts without affecting production use


And the [enterprise controls and security](https://cloud.google.com/blog/products/business-intelligence/understanding-looker-conversational-analytics-security?e=48754805) you expect from Google Cloud Platform:
  * Govern the use of agents using [role based access controls](https://cloud.google.com/gemini/docs/conversational-analytics-api/access-control)
  * Trust your data is secure with data with row and column level access controls by default
  * Guard against expensive queries with built-in query limitations


When pairing Conversational Analytics API with Looker, Looker’s semantic layer reduces data errors in gen AI natural language queries by as much as two thirds, so that queries are sourced in truth.
Looker’s semantic layer ensures your conversational analytics are grounded in data truth.
### **An agentic architecture powered by Google AI**
The Conversational Analytics API uses purpose-built models for querying and analyzing data to provide accurate answers, while its flexible agentic architecture lets you configure which capabilities the agent leverages to best provide users with answers to their questions.
Conversational Analytics leverages an agentic architecture to empower agent creators with the right tools.
As a developer, you can compose AI-powered agents with the following tools:
  * Text-to-SQL, trusted by customers using Gemini in BigQuery
  * Context retrieval, informed by personalized and organization usage
  * Looker's NL-to-Looker Query Engine, to leverage the analyst-curated semantic layer
  * Code Interpreter, for advanced analytics like forecasting and root-cause analysis
  * Charting, to create stunning visualizations and bring data to life
  * Insights, to explain answers in plain language 


These generative AI tools are built upon Google’s latest Gemini models and fine-tuned for specific data analysis tasks to deliver high levels of accuracy. There’s also the Code Interpreter for Conversational Analytics, which provides computations ranging from cohort analysis to period-over-period calculations. Currently in preview, Code Interpreter turns you into a data scientist without having to learn advanced coding or statistical methods. Sign up for early access [here](http://cloud.google.com/looker/docs/studio/conversational-analytics-code-interpreter).
### **Context retrieval and generation**
A good data analyst isn’t just smart, but also deeply knowledgeable about your business and your data. To provide the same kind of value, a “chat with your data” experience should be just as knowledgeable. That’s why the Conversational Analytics API prioritizes gathering context about your data and queries.
Thanks to retrieval augmented generation (RAG), our Conversational Analytics agents know you and your data well enough to know that when you’re asking for sales in “New York” or “NYC,” you mean “New York City.” The API understands your question’s meaning to match it to the most relevant fields to query, and learns from your organization, recognizing that, for example, “revenue_final_calc” may be queried more frequently than “revenue_intermediate” in your BigQuery project, and adjusts accordingly. Finally, the API learns from your past interactions; it will remember that you queried about “customer lifetime value” in BigQuery Studio on Tuesday when you ask about it again on Friday.
Not all datasets have the context an agent needs to do its work. Column descriptions, business glossaries, and question-query pairs can all improve an agent’s accuracy, but they can be hard to create manually— especially if you have 1,000 tables in your business, each with 500 fields. To speed up the process of teaching your agent, we are including AI-assisted context, using Gemini to suggest metadata that might be useful for your agent to know, while letting you approve or reject changes.
### **Low maintenance burden**
The Conversational Analytics API gives you access to the latest data agent tools from Google Cloud, so you can focus on building your business, not building more agents. You benefit from Google’s continued advancements in generative AI for coding and data analysis.
When you create an agent, we protect your data with Google’s security, best practices, and role-based access controls. Once you share your Looker or BigQuery agent, it can be used across Google Cloud products, such as [Agent Development Kit](https://developers.googleblog.com/en/agent-development-kit-easy-to-build-multi-agent-applications/), and in your own applications.
The Conversational Analytics API lets you interact with your data anywhere.
### **API powered chats from anywhere**
With agents consumable via API, you can surface insights anywhere decision makers need them—whether it’s when speaking with a customer over a support ticket, via a tablet when you’re in the field, or in your messaging apps.
The Conversational Analytics API is designed to bring benefits to all users, whether they be business users, data analysts building agents, or software developers. With Conversational Agents, when a user asks a question, answers are delivered rapidly alongside the agent’s thinking process, to ensure the right approach to gaining insights is used. Individual updates allow your developers to control what a user sees — like answers and charts — and what you want to log for later auditing by analysts — like SQL and Python code. 
To get started, you can use [our documentation](https://cloud.google.com/gemini/docs/conversational-analytics-api/overview) and [API references](https://cloud.google.com/gemini/docs/conversational-analytics-api/reference/rest) for REST APIs and SDKs, as well as code examples in [example Colab notebooks](https://cloud.google.com/gemini/docs/conversational-analytics-api/overview#interactive-colab-notebooks), [streamlit application on GitHub](https://github.com/looker-open-source/ca-api-quickstarts), and [typescript reference application](https://github.com/looker-open-source/ca-demos-and-tools).
Posted in
  * [Business Intelligence](https://cloud.google.com/blog/products/business-intelligence)


##### Related articles
[ Data Analytics What’s new with Google Data Cloud By The Google Cloud Data Analytics, BI, and Database teams • 3-minute read ](https://cloud.google.com/blog/products/data-analytics/whats-new-with-google-data-cloud)
[ Data Analytics Introducing Conversational Analytics in BigQuery By Vasiya Krishnan • 4-minute read ](https://cloud.google.com/blog/products/data-analytics/introducing-conversational-analytics-in-bigquery)
[ Data Analytics What's new with ML infrastructure for Dataflow By Efesa Origbo • 4-minute read ](https://cloud.google.com/blog/products/data-analytics/new-dataflow-features-to-enable-streaming-and-ml-workloads)
[ Data Analytics BigQuery AI supports Gemini 3.0, simplified embedding generation and new similarity function By Tianxiang Gao • 5-minute read ](https://cloud.google.com/blog/products/data-analytics/new-bigquery-gen-ai-functions-for-better-data-analysis)
