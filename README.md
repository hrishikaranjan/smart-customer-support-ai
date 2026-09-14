# AI Customer Support Agent — ShopEase

An AI-powered customer support platform for **ShopEase**, a fictional
e-commerce store. Built as a final-year B.Tech CSE capstone project to
demonstrate a realistic, resume-worthy full-stack GenAI application:
RAG, LLM tool calling, an AI agent loop, conversation memory, sentiment
analysis, and automated human escalation — wrapped in a SaaS-style UI.

> **Disclaimer:** ShopEase, its policies, orders, and products are entirely
> fictional and exist only to give the AI something concrete to reason about.

---

## Table of contents

1. [Problem statement](#problem-statement)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Tech stack](#tech-stack)
5. [RAG pipeline](#rag-pipeline)
6. [Agent / tool-calling architecture](#agent--tool-calling-architecture)
7. [Folder structure](#folder-structure)
8. [Installation](#installation)
9. [Environment variables](#environment-variables)
10. [Running the backend](#running-the-backend)
11. [Running the frontend](#running-the-frontend)
12. [API endpoints](#api-endpoints)
13. [Example queries](#example-queries)
14. [Testing checklist](#testing-checklist)
15. [Common errors and fixes](#common-errors-and-fixes)
16. [Screenshots](#screenshots)
17. [Future improvements](#future-improvements)
18. [Resume description](#resume-description)

---

## Problem statement

Most customer-support chatbots either (a) do plain keyword matching with
no real understanding, or (b) hallucinate policy answers with no grounding.
This project builds a support agent that:

- Answers policy questions **grounded** in an actual knowledge base (RAG),
  instead of hallucinating.
- **Decides for itself** when it needs to look something up (an order, a
  refund, a product) using real LLM tool calling, instead of a Python
  if/else keyword router pretending to be an agent.
- Understands **follow-up questions** ("when will *it* arrive?") using
  conversation memory.
- Detects **frustration/anger** and escalates to a human with an
  AI-written summary, instead of leaving upset customers stuck in a loop.

## Features

- 💬 AI chatbot with natural follow-up understanding (session memory)
- 📚 Real RAG: chunking → Gemini embeddings → FAISS → grounded generation
- 🛠️ Gemini **manual** function/tool calling (5 tools) — not keyword faking
- 🧠 Sentiment detection (positive / neutral / frustrated / angry)
- 🚨 Automatic human escalation + AI-generated conversation summary
- 🎫 Support ticket system with status workflow (Open → In Progress → Resolved)
- 📊 Live support dashboard (conversation & ticket stats)
- 🕘 Conversation history browser
- 💻 Professional, responsive SaaS-style chat UI (desktop/tablet/mobile)

## Architecture

```
┌────────────────────┐        HTTP/JSON        ┌──────────────────────────┐
│   React (Vite) UI   │ ───────────────────────▶ │      FastAPI backend     │
│  Chat / Dashboard /  │ ◀─────────────────────── │  main.py (REST routes)   │
│  Tickets / History   │                          └───────────┬──────────────┘
└────────────────────┘                                      │
                                                              ▼
                                      ┌───────────────────────────────────┐
                                      │            agent.py                │
                                      │  (sentiment + RAG + tool-call loop) │
                                      └───┬───────────┬───────────┬────────┘
                                          │           │           │
                                          ▼           ▼           ▼
                                 ┌──────────────┐ ┌─────────┐ ┌────────────┐
                                 │  rag.py /    │ │tools.py │ │ memory.py /│
                                 │vector_store.py│ │(5 tools)│ │ SQLite DB  │
                                 └──────┬───────┘ └────┬────┘ └────────────┘
                                        │              │
                                        ▼              ▼
                                 ┌────────────┐  ┌──────────────┐
                                 │FAISS index │  │ mock_data.py │
                                 │(kb.index)  │  │ (orders etc) │
                                 └────────────┘  └──────────────┘
                                        ▲
                                        │
                              ┌───────────────────┐
                              │ Gemini API          │
                              │ (chat + embeddings) │
                              └───────────────────┘
```

## Tech stack

| Layer      | Technology                                             |
|------------|---------------------------------------------------------|
| Frontend   | React 18, Vite, JavaScript (no TypeScript), plain CSS   |
| Backend    | Python 3.10+, FastAPI, Uvicorn                          |
| GenAI      | Google Gemini (`google-genai` SDK) — `gemini-3.6-flash` |
| Embeddings | Gemini `gemini-embedding-001`                           |
| Vector DB  | FAISS (`faiss-cpu`)                                     |
| Database   | SQLite (via SQLAlchemy) — messages & tickets            |

## RAG pipeline

```
knowledge_base/*.txt
        │  (read + normalize whitespace)
        ▼
   chunk_text()            700-char chunks, 100-char overlap
        │
        ▼
 embed_documents()         Gemini gemini-embedding-001 (RETRIEVAL_DOCUMENT)
        │
        ▼
  FAISS IndexFlatIP        cosine similarity via normalized vectors
        │   (cached to backend/index_store/ — built ONCE, not per message)
        ▼
    embed_query()          user question → RETRIEVAL_QUERY embedding
        │
        ▼
   index.search()          top-k most similar chunks (score-filtered)
        │
        ▼
  injected into Gemini's system_instruction as CONTEXT
        │
        ▼
  grounded, policy-accurate response
```

The index is built once on server startup (or on first request) and
cached to disk (`backend/index_store/kb.index` + `chunks.json`). Restarting
the server does **not** re-embed the knowledge base unless you delete that
folder or call `vector_store.build_index(force=True)`.

## Agent / tool-calling architecture

`agent.py` implements **manual** Gemini function calling (no automatic
function calling), so the app has full control over side effects like
writing a ticket to the database:

```
User message
     │
     ▼
generate_content(contents, tools=[5 declarations], system_instruction=RAG context)
     │
     ▼
Does response.function_calls exist?
     │
   ┌─┴─── no ──▶ return response.text as final reply
   │
  yes
   │
   ▼
Execute the matching Python function in tools.py
   │
   ▼
Append the model's function-call turn + our function-response turn
to `contents`, then call generate_content() again
   │
   └── loop (max 4 iterations) until the model returns plain text
```

### Available tools

| Tool                          | Purpose                                    |
|--------------------------------|---------------------------------------------|
| `get_order_status(order_id)`  | Look up shipping status / delivery date      |
| `get_refund_status(order_id)` | Look up refund status                        |
| `get_product_information(product_name)` | Price/description lookup           |
| `check_product_availability(product_name)` | Stock check                     |
| `create_support_ticket(issue, priority)`  | Escalate to a human agent        |

## Folder structure

```
ai-customer-support-agent/
├── README.md
├── .gitignore
│
├── backend/
│   ├── main.py                # FastAPI app + all routes
│   ├── agent.py                # RAG + manual tool-calling loop
│   ├── rag.py                  # Context retrieval helper
│   ├── embeddings.py           # Gemini embeddings wrapper
│   ├── vector_store.py         # FAISS build/load/search
│   ├── tools.py                # Tool declarations + implementations
│   ├── memory.py                # SQLite-backed conversation memory
│   ├── sentiment.py            # Gemini-based sentiment classifier
│   ├── database.py             # SQLAlchemy engine/session
│   ├── models.py                # SQLAlchemy ORM models
│   ├── schemas.py               # Pydantic request/response models
│   ├── mock_data.py             # Fictional ShopEase orders/refunds/products
│   ├── requirements.txt
│   ├── .env.example
│   └── knowledge_base/
│       ├── booking_policy.txt
│       ├── cancellation_policy.txt
│       ├── refund_policy.txt
│       ├── shipping_policy.txt
│       ├── warranty_policy.txt
│       └── faq.txt
│
└── frontend/
    ├── package.json
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── main.jsx
        ├── App.jsx
        ├── components/   (17 reusable UI components)
        ├── pages/         (ChatPage, DashboardPage, TicketsPage, HistoryPage)
        ├── services/api.js
        ├── hooks/useSessionId.js
        └── styles/        (global, sidebar, chat, components, dashboard CSS)
```

## Installation

Requires **Python 3.10+** and **Node.js 18+**. Commands below are for
**Windows PowerShell**; macOS/Linux users can drop `.\venv\Scripts\` in
favor of `venv/bin/` and `python3`.

### Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
copy .env.example .env
# now edit .env and paste your real GEMINI_API_KEY
```

### Frontend

```powershell
cd frontend
npm install
```

## Environment variables

Copy `backend/.env.example` to `backend/.env` and fill in your key:

```
GEMINI_API_KEY=your_key_here
GEMINI_CHAT_MODEL=gemini-3.6-flash
GEMINI_EMBEDDING_MODEL=gemini-embedding-001
FRONTEND_ORIGIN=http://localhost:5173
```

Get a free Gemini API key at **https://aistudio.google.com/app/apikey**.
`.env` is git-ignored — never commit it.

## Running the backend

```powershell
cd backend
.\venv\Scripts\python.exe -m uvicorn main:app --reload
```

On first startup the server builds the FAISS index from
`knowledge_base/*.txt` (one-time Gemini embedding calls) and creates
`support.db` (SQLite) automatically. The API is live at
`http://localhost:8000` — interactive docs at `http://localhost:8000/docs`.

## Running the frontend

```powershell
cd frontend
npm run dev
```

Open `http://localhost:5173`. The app talks to the backend at
`http://localhost:8000` by default (override with a `VITE_API_URL` env
var in a `frontend/.env` file if needed).

## API endpoints

| Method | Path                          | Description                              |
|--------|-------------------------------|-------------------------------------------|
| GET    | `/health`                     | Health check                              |
| POST   | `/chat`                       | Send a chat message, get AI reply + cards |
| POST   | `/tickets`                    | Manually create a ticket                  |
| GET    | `/tickets`                    | List tickets (optional `?status=` filter) |
| GET    | `/tickets/{ticket_id}`        | Get one ticket                            |
| PATCH  | `/tickets/{ticket_id}`        | Update ticket status                      |
| GET    | `/conversations`              | List all conversation sessions            |
| GET    | `/conversations/{session_id}` | Full message history for a session        |
| GET    | `/dashboard/stats`            | Aggregate stats for the dashboard         |

### Example `/chat` request

```json
POST /chat
{
  "session_id": "session_abc123",
  "message": "What is the status of ORD1001?"
}
```

```json
{
  "session_id": "session_abc123",
  "reply": "Your order ORD1001 (Wireless Headphones) has shipped and is expected to arrive on 2026-08-30.",
  "sentiment": "neutral",
  "cards": [{ "type": "order", "data": { "order_id": "ORD1001", "...": "..." } }],
  "escalated": false,
  "ticket_id": null
}
```

## Example queries

1. `"What is your refund policy?"` → RAG-grounded answer from `refund_policy.txt`
2. `"What is the status of ORD1001?"` → `get_order_status` tool call
3. `"When will it arrive?"` (follow-up) → memory resolves "it" = ORD1001
4. `"Is the USB-C Hub in stock?"` → `check_product_availability` tool call
5. `"I've contacted support three times and nobody helped me!"` → sentiment: angry → auto-escalation
6. `"I want to talk to a human"` → `create_support_ticket` tool call

## Testing checklist

| # | Scenario                    | How to test                                                   |
|---|------------------------------|----------------------------------------------------------------|
| 1 | General FAQ                  | Ask "Do you offer gift wrapping?"                              |
| 2 | RAG question                 | Ask "What is your shipping policy?"                             |
| 3 | Semantic (no exact keyword)  | Ask "Can I get my money back?" (should hit refund policy)       |
| 4 | Order lookup                 | Ask "Where is ORD1002?"                                          |
| 5 | Refund lookup                | Ask "What's the refund status for ORD1004?"                     |
| 6 | Invalid order                | Ask "Where is ORD9999?" → should say not found, not hallucinate |
| 7 | Follow-up question           | Ask about ORD1001, then "when will it arrive?"                  |
| 8 | Angry customer               | Send an angry message → check sentiment badge = "Angry"         |
| 9 | Human escalation             | Ask "I want to talk to a human" → ticket appears in `/tickets`   |
| 10| Ticket creation end-to-end   | Escalate → check Dashboard/Tickets page shows the new ticket with AI summary |

## Common errors and fixes

| Error                                              | Fix                                                                 |
|-----------------------------------------------------|----------------------------------------------------------------------|
| `RuntimeError: GEMINI_API_KEY is not set`           | Copy `.env.example` to `.env` and add your real key                 |
| `Can't reach the support server`                    | Make sure `uvicorn main:app --reload` is running on port 8000       |
| CORS error in browser console                       | Check `FRONTEND_ORIGIN` in `.env` matches your Vite dev URL exactly |
| `No knowledge base documents found`                  | Run the backend from inside `backend/` so relative paths resolve    |
| FAISS dimension mismatch after switching embedding model | Delete `backend/index_store/` and restart to rebuild the index |
| `429` errors from Gemini                            | You've hit a rate limit — wait a few seconds and retry              |

## Screenshots

_Add screenshots here after running the app locally, e.g.:_
- `docs/screenshot-chat.png`
- `docs/screenshot-dashboard.png`
- `docs/screenshot-tickets.png`

## Future improvements

- Streaming responses (token-by-token) instead of waiting for the full reply
- Multi-language support
- Real authentication for the support-agent dashboard
- Swap SQLite for PostgreSQL for multi-instance deployments
- Add automated evaluation of RAG answer quality

## Resume description

> **AI Customer Support Agent (ShopEase)** — Full-stack GenAI support
> platform (React + FastAPI + Gemini). Implemented a RAG pipeline
> (chunking, Gemini embeddings, FAISS similarity search) for
> policy-grounded answers, and a manual LLM tool-calling agent loop with
> 5 tools for order/refund/product lookups and human escalation.
> Added session-based conversation memory, Gemini-based sentiment
> detection, automatic ticket creation with AI-generated summaries, and
> a responsive support-agent dashboard.
