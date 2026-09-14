"""
main.py

FastAPI application entrypoint for the AI Customer Support Agent backend.
Run with:  uvicorn main:app --reload
"""

import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from sqlalchemy import func

load_dotenv()  # must run before any module reads GEMINI_API_KEY

import database
import models
import memory
import agent
import tools
import vector_store
from schemas import (
    ChatRequest, ChatResponse,
    TicketCreateRequest, TicketResponse, TicketStatusUpdate,
    MessageResponse, ConversationSummary,
    DashboardStats,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai-support-agent")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables and build/load the FAISS index once.
    database.init_db()
    try:
        vector_store.build_index()
        logger.info("Knowledge base index ready.")
    except RuntimeError as e:
        # Missing API key at startup shouldn't crash the whole server —
        # /chat will raise a clear error instead when actually called.
        logger.warning("Could not build vector index at startup: %s", e)
    yield


app = FastAPI(title="AI Customer Support Agent API", version="1.0.0", lifespan=lifespan)

FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/health")
def health_check():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(database.get_db)):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    if not req.session_id.strip():
        raise HTTPException(status_code=400, detail="session_id is required.")

    try:
        result = agent.handle_chat_message(db, req.session_id, req.message.strip())
    except RuntimeError as e:
        # e.g. missing GEMINI_API_KEY
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error in /chat")
        raise HTTPException(status_code=502, detail=f"AI service error: {e}")

    return ChatResponse(**result)


# ---------------------------------------------------------------------------
# Tickets
# ---------------------------------------------------------------------------

@app.post("/tickets", response_model=TicketResponse)
def create_ticket(req: TicketCreateRequest, db: Session = Depends(database.get_db)):
    result = tools.create_support_ticket(
        db=db,
        session_id=req.session_id,
        issue=req.issue,
        priority=req.priority,
        sentiment=req.sentiment,
        summary=req.summary,
    )
    ticket = db.query(models.Ticket).filter(models.Ticket.ticket_id == result["ticket_id"]).first()
    return ticket


@app.get("/tickets", response_model=list[TicketResponse])
def list_tickets(status: str | None = None, db: Session = Depends(database.get_db)):
    query = db.query(models.Ticket)
    if status:
        query = query.filter(models.Ticket.status == status)
    return query.order_by(models.Ticket.created_at.desc()).all()


@app.get("/tickets/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: str, db: Session = Depends(database.get_db)):
    ticket = db.query(models.Ticket).filter(models.Ticket.ticket_id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Ticket '{ticket_id}' not found.")
    return ticket


@app.patch("/tickets/{ticket_id}", response_model=TicketResponse)
def update_ticket_status(ticket_id: str, req: TicketStatusUpdate, db: Session = Depends(database.get_db)):
    ticket = db.query(models.Ticket).filter(models.Ticket.ticket_id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Ticket '{ticket_id}' not found.")
    ticket.status = req.status
    db.commit()
    db.refresh(ticket)
    return ticket


# ---------------------------------------------------------------------------
# Conversations
# ---------------------------------------------------------------------------

@app.get("/conversations", response_model=list[ConversationSummary])
def list_conversations(db: Session = Depends(database.get_db)):
    rows = memory.get_all_sessions_summary(db)
    summaries = []
    for row in rows:
        last_sentiment = memory.get_last_sentiment(db, row.session_id)
        summaries.append(ConversationSummary(
            session_id=row.session_id,
            message_count=row.message_count,
            last_message_at=row.last_message_at,
            last_sentiment=last_sentiment,
        ))
    return summaries


@app.get("/conversations/{session_id}", response_model=list[MessageResponse])
def get_conversation(session_id: str, db: Session = Depends(database.get_db)):
    history = memory.get_recent_history(db, session_id, limit=200)
    if not history:
        raise HTTPException(status_code=404, detail=f"No conversation found for session '{session_id}'.")
    return history


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@app.get("/dashboard/stats", response_model=DashboardStats)
def dashboard_stats(db: Session = Depends(database.get_db)):
    total_conversations = db.query(func.count(func.distinct(models.Message.session_id))).scalar() or 0

    # "active" = had a message in the last hour, using SQLite text-based comparison
    recent_cutoff = func.datetime("now", "-1 hour")
    active_conversations = (
        db.query(func.count(func.distinct(models.Message.session_id)))
        .filter(models.Message.created_at >= recent_cutoff)
        .scalar() or 0
    )

    escalated_tickets = db.query(func.count(models.Ticket.id)).scalar() or 0
    open_tickets = db.query(func.count(models.Ticket.id)).filter(models.Ticket.status == "Open").scalar() or 0
    resolved_tickets = db.query(func.count(models.Ticket.id)).filter(models.Ticket.status == "Resolved").scalar() or 0
    frustrated_customers = (
        db.query(func.count(func.distinct(models.Message.session_id)))
        .filter(models.Message.sentiment.in_(["frustrated", "angry"]))
        .scalar() or 0
    )

    return DashboardStats(
        total_conversations=total_conversations,
        active_conversations=active_conversations,
        escalated_tickets=escalated_tickets,
        open_tickets=open_tickets,
        resolved_tickets=resolved_tickets,
        frustrated_customers=frustrated_customers,
    )
