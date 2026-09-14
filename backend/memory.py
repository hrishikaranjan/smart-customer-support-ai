"""
memory.py

Session-based conversation memory backed by SQLite (via models.Message),
instead of a plain Python dict, so history survives a server restart and
multiple worker processes could in principle share it.

Each function takes a SQLAlchemy `Session` (db) passed in by the caller
(the FastAPI route), following the standard dependency-injection pattern.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

import models

MAX_HISTORY_MESSAGES = 12  # how many recent turns we feed back to Gemini


def add_message(db: Session, session_id: str, role: str, content: str,
                 sentiment: Optional[str] = None) -> models.Message:
    msg = models.Message(
        session_id=session_id, role=role, content=content, sentiment=sentiment
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def get_recent_history(db: Session, session_id: str, limit: int = MAX_HISTORY_MESSAGES) -> List[models.Message]:
    """Return the most recent messages for a session, oldest first."""
    rows = (
        db.query(models.Message)
        .filter(models.Message.session_id == session_id)
        .order_by(models.Message.created_at.desc())
        .limit(limit)
        .all()
    )
    return list(reversed(rows))


def get_all_sessions_summary(db: Session):
    """Aggregate per-session stats for the /conversations and dashboard endpoints."""
    rows = (
        db.query(
            models.Message.session_id,
            func.count(models.Message.id).label("message_count"),
            func.max(models.Message.created_at).label("last_message_at"),
        )
        .group_by(models.Message.session_id)
        .order_by(func.max(models.Message.created_at).desc())
        .all()
    )
    return rows


def get_last_sentiment(db: Session, session_id: str) -> Optional[str]:
    row = (
        db.query(models.Message)
        .filter(models.Message.session_id == session_id, models.Message.role == "user")
        .order_by(models.Message.created_at.desc())
        .first()
    )
    return row.sentiment if row else None
