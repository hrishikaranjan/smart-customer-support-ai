import os
from dotenv import load_dotenv
from google import genai

from vector_store import search_similar_documents
from tools import (
    get_order_status,
    get_refund_status,
    create_support_ticket,
)

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is not set in the .env file")

client = genai.Client(api_key=api_key)


def generate_response(message: str) -> str:

    # Retrieve relevant knowledge
    documents = search_similar_documents(message)

    context = "\n\n".join(
        f"Source: {doc['filename']}\n{doc['content']}"
        for doc in documents
    )

    tools = [
        get_order_status,
        get_refund_status,
        create_support_ticket,
    ]

    prompt = f"""
You are an AI customer support agent for ShopEase.

You have access to the following knowledge base:

{context}

Customer message:
{message}

Use the knowledge base to answer policy-related questions.

Use the available tools when the customer asks for:
- Order status
- Refund status
- Creating a support ticket

Do not invent order information.

If an order ID is required, ask the customer for it.

Be helpful, professional, and concise.
"""

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
        config={
            "tools": tools
        },
    )

    return response.text    