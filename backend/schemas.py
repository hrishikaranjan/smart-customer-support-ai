"""
schemas.py

Pydantic models for API request/response validation. Keeping these
separate from the SQLAlchemy models (models.py) is intentional — the
API shape and the DB shape are allowed to evolve independently.
"""

from typing import Optional, List, Literal
from datetime import datetime
from pydantic import BaseModel, Field


# ---------- /chat --------------------------------------------------------

class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1, description="Client-generated session id")
    message: str = Field(..., min_length=1, max_length=2000)


class ChatCard(BaseModel):
    """Optional structured data the frontend renders as a rich card."""
    type: Literal["order", "refund", "ticket"]
    data: dict


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    sentiment: str
    cards: List[ChatCard] = []
    escalated: bool = False
    ticket_id: Optional[str] = None


# ---------- /tickets -------------------------------------------------------

class TicketCreateRequest(BaseModel):
    session_id: str
    issue: str = Field(..., min_length=1)
    sentiment: str = "neutral"
    priority: str = "Medium"
    summary: Optional[str] = None


class TicketResponse(BaseModel):
    ticket_id: str
    session_id: str
    issue: str
    sentiment: str
    priority: str
    status: str
    summary: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class TicketStatusUpdate(BaseModel):
    status: Literal["Open", "In Progress", "Resolved"]


# ---------- /conversations -------------------------------------------------

class MessageResponse(BaseModel):
    role: str
    content: str
    sentiment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationSummary(BaseModel):
    session_id: str
    message_count: int
    last_message_at: datetime
    last_sentiment: Optional[str] = None


# ---------- /dashboard -----------------------------------------------------

class DashboardStats(BaseModel):
    total_conversations: int
    active_conversations: int
    escalated_tickets: int
    open_tickets: int
    resolved_tickets: int
    frustrated_customers: int
