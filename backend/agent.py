"""
agent.py

The heart of the assistant. For every incoming chat message this module:

  1. Classifies sentiment (sentiment.py).
  2. Retrieves relevant knowledge-base context (rag.py -> vector_store.py).
  3. Sends the conversation + retrieved context + tool declarations to
     Gemini, using MANUAL function calling: we inspect response.function_calls
     ourselves, execute the matching Python function, and send the result
     back to Gemini for a follow-up turn. This is done in a loop so the
     model can chain more than one tool call if it needs to.
  4. Builds "cards" (structured JSON) for any tool results the frontend
     should render richly (order card, refund card, ticket card).
  5. If a support ticket was created, generates a short AI summary of the
     conversation and stores it on the ticket for the human agent.

No automatic function calling is used, per project requirements — this
file *is* the tool-calling loop.
"""

import os
from typing import List, Tuple

from google import genai
from google.genai import types
from sqlalchemy.orm import Session

import models
import memory
import rag
import tools
from sentiment import analyze_sentiment

CHAT_MODEL = os.getenv("GEMINI_CHAT_MODEL", "gemini-3.6-flash")
MAX_TOOL_ITERATIONS = 4

_client = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Copy backend/.env.example to "
                "backend/.env and fill in your key."
            )
        _client = genai.Client(api_key=api_key)
    return _client


SYSTEM_INSTRUCTION_TEMPLATE = """You are Ava, the AI customer support agent for ShopEase,
a fictional online store. Be warm, concise, and helpful.

Ground policy questions (refunds, shipping, cancellations, warranty, booking)
in the CONTEXT block below when it is provided — do not invent policy details
that aren't in the context. If the context is empty, answer generally and
briefly say you're not 100% sure, or offer to escalate.

Use tools whenever the customer asks about a specific order, refund, product
availability, or product details, instead of guessing.

Escalate to a human by calling create_support_ticket when:
- the customer explicitly asks for a human agent, or
- the customer's sentiment is "frustrated" or "angry" and their issue is not
  yet resolved, or
- none of the available tools can resolve their issue.

The customer's current message sentiment has been pre-classified as: {sentiment}

CONTEXT:
{context}
"""


def _history_to_contents(history: List[models.Message]) -> List[types.Content]:
    """Convert stored Message rows into Gemini Content objects.
    Gemini uses role "model" for the assistant, not "assistant"."""
    contents = []
    for msg in history:
        role = "model" if msg.role == "assistant" else "user"
        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=msg.content)]))
    return contents


def _execute_tool(db: Session, session_id: str, sentiment: str, name: str, args: dict) -> dict:
    """Run the Python implementation matching a Gemini function call."""
    if name in tools.SIMPLE_TOOL_IMPL:
        return tools.SIMPLE_TOOL_IMPL[name](**args)

    if name == "create_support_ticket":
        return tools.create_support_ticket(
            db=db,
            session_id=session_id,
            issue=args.get("issue", "Unspecified issue"),
            priority=args.get("priority", "Medium"),
            sentiment=sentiment,
        )

    return {"found": False, "message": f"Unknown tool '{name}'."}


def _build_cards(tool_calls_log: List[Tuple[str, dict, dict]]) -> List[dict]:
    """Turn executed tool calls into frontend-renderable cards."""
    cards = []
    for name, _args, result in tool_calls_log:
        if not result.get("found"):
            continue
        if name == "get_order_status":
            cards.append({"type": "order", "data": result})
        elif name == "get_refund_status":
            cards.append({"type": "refund", "data": result})
        elif name == "create_support_ticket":
            cards.append({"type": "ticket", "data": result})
    return cards


def _generate_ticket_summary(db: Session, session_id: str, issue: str) -> str:
    """Generate a short AI summary of the conversation for a human agent."""
    history = memory.get_recent_history(db, session_id, limit=20)
    transcript = "\n".join(f"{m.role}: {m.content}" for m in history)
    prompt = (
        "Summarize this customer support conversation in 2-3 sentences for a "
        "human support agent who has not read it. Mention the core issue, "
        "customer's emotional state, and what the human should verify or do "
        f"next.\n\nEscalation reason: {issue}\n\nConversation:\n{transcript}"
    )
    try:
        client = _get_client()
        response = client.models.generate_content(model=CHAT_MODEL, contents=prompt)
        return (response.text or "").strip() or issue
    except Exception:
        return issue


def handle_chat_message(db: Session, session_id: str, user_message: str) -> dict:
    """Main entry point called by the /chat route."""
    client = _get_client()

    # 1. Sentiment
    sentiment = analyze_sentiment(user_message)

    # 2. Save user message to memory
    memory.add_message(db, session_id, "user", user_message, sentiment=sentiment)

    # 3. RAG context
    context = rag.retrieve_context(user_message)

    # 4. Build conversation contents from history (includes the message we
    #    just saved, so Gemini sees it as part of the turn sequence)
    history = memory.get_recent_history(db, session_id)
    contents = _history_to_contents(history)

    system_instruction = SYSTEM_INSTRUCTION_TEMPLATE.format(
        sentiment=sentiment, context=context or "(no relevant policy context found)"
    )

    tool = types.Tool(function_declarations=tools.ALL_DECLARATIONS)
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        tools=[tool],
        temperature=0.4,
    )

    tool_calls_log: List[Tuple[str, dict, dict]] = []
    escalated = False
    ticket_id = None

    response = client.models.generate_content(model=CHAT_MODEL, contents=contents, config=config)

    iterations = 0
    while getattr(response, "function_calls", None) and iterations < MAX_TOOL_ITERATIONS:
        iterations += 1

        # The model's turn (containing the function call parts) must be
        # appended to the conversation before we can reply with results.
        model_content = response.candidates[0].content
        contents.append(model_content)

        function_response_parts = []
        for call in response.function_calls:
            args = dict(call.args or {})
            result = _execute_tool(db, session_id, sentiment, call.name, args)
            tool_calls_log.append((call.name, args, result))

            if call.name == "create_support_ticket" and result.get("found"):
                escalated = True
                ticket_id = result.get("ticket_id")

            function_response_parts.append(
                types.Part.from_function_response(name=call.name, response=result)
            )

        contents.append(types.Content(role="tool", parts=function_response_parts))

        response = client.models.generate_content(model=CHAT_MODEL, contents=contents, config=config)

    reply_text = (response.text or "").strip()
    if not reply_text:
        reply_text = "Sorry, I couldn't generate a response just now. Could you rephrase that?"

    # 5. Save assistant reply
    memory.add_message(db, session_id, "assistant", reply_text)

    # 6. If a ticket was created, backfill its AI summary
    if escalated and ticket_id:
        summary = _generate_ticket_summary(db, session_id, issue=tool_calls_log[-1][2].get("issue", user_message))
        ticket_row = db.query(models.Ticket).filter(models.Ticket.ticket_id == ticket_id).first()
        if ticket_row:
            ticket_row.summary = summary
            db.commit()

    cards = _build_cards(tool_calls_log)

    return {
        "session_id": session_id,
        "reply": reply_text,
        "sentiment": sentiment,
        "cards": cards,
        "escalated": escalated,
        "ticket_id": ticket_id,
    }
