"""
models.py

SQLAlchemy ORM models: conversation messages and support tickets.
These are the two things that must survive a server restart, so they
live in SQLite instead of an in-memory dict.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func

from database import Base


class Message(Base):
    """A single chat turn (user or assistant) inside a session."""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=False)
    role = Column(String, nullable=False)  # "user" | "assistant"
    content = Column(Text, nullable=False)
    sentiment = Column(String, nullable=True)  # only set for user messages
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Ticket(Base):
    """A human-escalation support ticket created by the agent."""

    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String, unique=True, index=True, nullable=False)
    session_id = Column(String, index=True, nullable=False)
    issue = Column(Text, nullable=False)
    sentiment = Column(String, nullable=False, default="neutral")
    priority = Column(String, nullable=False, default="Medium")
    status = Column(String, nullable=False, default="Open")
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
