"""
tools.py

Defines the tools the Gemini agent can call, using the google-genai SDK's
manual function-calling primitives (types.FunctionDeclaration / types.Tool).
We deliberately do NOT use automatic function calling: agent.py inspects
each function call, executes the matching Python function itself, and
sends the result back to Gemini. This keeps full control over side effects
like writing a support ticket to the database.

Each tool has:
  1. A FunctionDeclaration (the JSON schema Gemini sees).
  2. A plain Python implementation with the same name, called via TOOL_IMPL.
"""

import random
from datetime import datetime, timezone
from typing import Optional

from google.genai import types
from sqlalchemy.orm import Session

import mock_data
import models


# ---------------------------------------------------------------------------
# 1. get_order_status
# ---------------------------------------------------------------------------

get_order_status_decl = types.FunctionDeclaration(
    name="get_order_status",
    description=(
        "Look up the shipping status and estimated delivery date of a "
        "ShopEase order. Use this whenever the customer asks 'where is my "
        "order', gives an order ID, or asks about delivery/shipping status."
    ),
    parameters={
        "type": "object",
        "properties": {
            "order_id": {
                "type": "string",
                "description": "The order ID, e.g. 'ORD1001'.",
            }
        },
        "required": ["order_id"],
    },
)


def get_order_status(order_id: str) -> dict:
    order = mock_data.ORDERS.get(order_id.strip().upper())
    if not order:
        return {"found": False, "message": f"No order found with ID '{order_id}'."}
    return {"found": True, **order}


# ---------------------------------------------------------------------------
# 2. get_refund_status
# ---------------------------------------------------------------------------

get_refund_status_decl = types.FunctionDeclaration(
    name="get_refund_status",
    description=(
        "Look up the refund status for a ShopEase order. Use this when the "
        "customer asks about a refund, money back, or a return they filed."
    ),
    parameters={
        "type": "object",
        "properties": {
            "order_id": {
                "type": "string",
                "description": "The order ID the refund belongs to, e.g. 'ORD1004'.",
            }
        },
        "required": ["order_id"],
    },
)


def get_refund_status(order_id: str) -> dict:
    refund = mock_data.REFUNDS.get(order_id.strip().upper())
    if not refund:
        return {"found": False, "message": f"No refund on file for order '{order_id}'."}
    return {"found": True, **refund}


# ---------------------------------------------------------------------------
# 3. get_product_information
# ---------------------------------------------------------------------------

get_product_information_decl = types.FunctionDeclaration(
    name="get_product_information",
    description="Get price and description details for a ShopEase product by name.",
    parameters={
        "type": "object",
        "properties": {
            "product_name": {
                "type": "string",
                "description": "Product name, e.g. 'Wireless Headphones'.",
            }
        },
        "required": ["product_name"],
    },
)


def get_product_information(product_name: str) -> dict:
    product = mock_data.PRODUCTS.get(product_name.strip().lower())
    if not product:
        return {"found": False, "message": f"No product found matching '{product_name}'."}
    return {"found": True, **product}


# ---------------------------------------------------------------------------
# 4. check_product_availability
# ---------------------------------------------------------------------------

check_product_availability_decl = types.FunctionDeclaration(
    name="check_product_availability",
    description="Check whether a ShopEase product is currently in stock.",
    parameters={
        "type": "object",
        "properties": {
            "product_name": {
                "type": "string",
                "description": "Product name, e.g. 'USB-C Hub'.",
            }
        },
        "required": ["product_name"],
    },
)


def check_product_availability(product_name: str) -> dict:
    product = mock_data.PRODUCTS.get(product_name.strip().lower())
    if not product:
        return {"found": False, "message": f"No product found matching '{product_name}'."}
    return {
        "found": True,
        "name": product["name"],
        "in_stock": product["in_stock"],
        "stock_count": product["stock_count"],
    }


# ---------------------------------------------------------------------------
# 5. create_support_ticket
# ---------------------------------------------------------------------------
# NOTE: this tool needs a DB session, which Gemini obviously can't provide.
# agent.py passes `db` and `session_id` in separately when it detects this
# specific tool name (see EXTRA_CONTEXT_TOOLS in agent.py).

create_support_ticket_decl = types.FunctionDeclaration(
    name="create_support_ticket",
    description=(
        "Create a human support ticket. Use this when the customer explicitly "
        "asks for a human agent, when their issue cannot be resolved with the "
        "other tools, or when they are clearly very frustrated or angry."
    ),
    parameters={
        "type": "object",
        "properties": {
            "issue": {
                "type": "string",
                "description": "A short description of the customer's problem.",
            },
            "priority": {
                "type": "string",
                "enum": ["Low", "Medium", "High"],
                "description": "Ticket priority based on urgency/severity.",
            },
        },
        "required": ["issue"],
    },
)


def _generate_ticket_id() -> str:
    return f"TKT-{random.randint(10000, 99999)}"


def create_support_ticket(
    db: Session,
    session_id: str,
    issue: str,
    priority: str = "Medium",
    sentiment: str = "neutral",
    summary: Optional[str] = None,
) -> dict:
    ticket = models.Ticket(
        ticket_id=_generate_ticket_id(),
        session_id=session_id,
        issue=issue,
        sentiment=sentiment,
        priority=priority,
        status="Open",
        summary=summary,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return {
        "found": True,
        "ticket_id": ticket.ticket_id,
        "status": ticket.status,
        "priority": ticket.priority,
        "issue": ticket.issue,
        "created_at": ticket.created_at.isoformat() if ticket.created_at else datetime.now(timezone.utc).isoformat(),
    }


# ---------------------------------------------------------------------------
# Registry used by agent.py
# ---------------------------------------------------------------------------

ALL_DECLARATIONS = [
    get_order_status_decl,
    get_refund_status_decl,
    get_product_information_decl,
    check_product_availability_decl,
    create_support_ticket_decl,
]

# Tools that only need the args Gemini provides.
SIMPLE_TOOL_IMPL = {
    "get_order_status": get_order_status,
    "get_refund_status": get_refund_status,
    "get_product_information": get_product_information,
    "check_product_availability": check_product_availability,
}

# Tools that need extra server-side context (db session, session_id, sentiment)
# injected by agent.py in addition to the model-provided arguments.
CONTEXT_TOOL_NAMES = {"create_support_ticket"}
