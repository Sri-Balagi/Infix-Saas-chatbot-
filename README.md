# Infix: Social-to-Lead AI Agent

Infix is a human-like, context-aware AI agent designed to bridge the gap between social inquiries and lead qualification. Built on a robust state-machine architecture, Infix handles product clarification, context-aware RAG querying, and natural entity extraction to capture leads seamlessly.

## 🚀 How to Run Locally

### 1. Prerequisites
- Python 3.9+
- An OpenRouter API Key (or OpenAI API Key)

### 2. Setup
Clone the repository and navigate to the project directory:
```bash
# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root directory and add your API key:
```env
OPENROUTER_API_KEY=your_api_key_here
```

### 4. Application Launch
To launch the chat interface:
```bash
streamlit run app.py
```

---

## 🏗️ Architecture Explanation

For Infix, I chose **LangGraph** over alternatives like AutoGen due to its superior capability in managing structured conversational state machines. While AutoGen excels at multi-agent collaboration, LangGraph provides granular control over the "Flow" — enabling explicit transitions between an "Inquiry Phase" (RAG) and a "Qualification Phase" (Lead Capture).

**State Management:**
The system's state is managed using a centralized `AppState` TypedDict. This state tracks:
- **Conversation History:** Maintains context across multiple turns.
- **User Data:** A structured object (Name, Email, Platform) populated via natural extraction.
- **Workflow Stage:** Tracks exactly where the user is in the qualification funnel to prevent redundant questioning.

Using LangGraph's `MemorySaver`, the agent implements thread-based persistence. This allows the system to remember previous interactions even if the user interrupts a lead capture to ask a general product question. The state-routing logic detects these "Interruptions," services the inquiry using a FAISS-backed Vector Store (RAG), and then gracefully loops the user back to the exact pending signup step.

---

## 📱 WhatsApp Deployment Strategy

To deploy Infix to WhatsApp, I would implement a **Webhook-based Architecture** using the Meta WhatsApp Business Cloud API.

### Integration Steps:
1. **Webhook Endpoint:** Develop a lightweight server (using Flask or FastAPI) to host a POST endpoint. This endpoint will receive real-time JSON payloads from Meta whenever a user sends a message to the business number.
2. **Message Identification:** Extract the `from` phone number from the payload to serve as the unique `thread_id` in the LangGraph memory system. This ensures each WhatsApp user has their own persistent session.
3. **Async Processing:** Route user messages to the `graph.invoke()` method. Given WhatsApp's asynchronous nature, the agent can process complex RAG queries and use the Cloud API to "POST" the response back to the user's phone number as a template or text message.
4. **Data Webhooks:** On successful lead capture, the system can trigger an additional webhook to push the structured lead data into a CRM like Salesforce or a Google Sheet via Zapier/Make.
