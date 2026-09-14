"""
sentiment.py

Classifies a user message into one of: positive, neutral, frustrated, angry.

We use a very small, cheap Gemini call with a constrained prompt instead
of a separate ML model — good enough accuracy for a support-chat demo
without adding a whole new dependency (e.g. a HuggingFace classifier).
"""

import os
from google import genai

CHAT_MODEL = os.getenv("GEMINI_CHAT_MODEL", "gemini-3.6-flash")

_client = None

VALID_LABELS = {"positive", "neutral", "frustrated", "angry"}

SENTIMENT_PROMPT = """Classify the sentiment of this customer support message
into exactly one word from this list: positive, neutral, frustrated, angry.

Rules:
- "angry" = explicit hostility, all-caps shouting, insults, threats to leave.
- "frustrated" = repeated complaints, "still not fixed", visible annoyance.
- "positive" = thanks, satisfaction, compliments.
- "neutral" = plain questions or statements with no strong emotion.

Reply with ONLY the single word, nothing else.

Message: "{message}"
"""


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set.")
        _client = genai.Client(api_key=api_key)
    return _client


def analyze_sentiment(message: str) -> str:
    """Return one of: positive, neutral, frustrated, angry.

    Falls back to "neutral" if the model returns something unexpected,
    so a sentiment-classification hiccup never breaks the chat flow.
    """
    try:
        client = _get_client()
        response = client.models.generate_content(
            model=CHAT_MODEL,
            contents=SENTIMENT_PROMPT.format(message=message),
        )
        label = (response.text or "").strip().lower()
        label = label.strip(".").split()[0] if label else "neutral"
        if label not in VALID_LABELS:
            return "neutral"
        return label
    except Exception:
        return "neutral"
