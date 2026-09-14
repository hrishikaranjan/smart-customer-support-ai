import { useEffect, useRef } from "react";
import ChatMessage from "./ChatMessage.jsx";
import TypingIndicator from "./TypingIndicator.jsx";
import SuggestedQuestions from "./SuggestedQuestions.jsx";

export default function ChatWindow({ messages, isTyping, onPickSuggestion }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  if (messages.length === 0) {
    return (
      <div className="chat-scroll">
        <div className="chat-empty">
          <div className="chat-empty-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
              <path d="M4 5h16v11H8l-4 4V5z" stroke="currentColor" strokeWidth="1.7" strokeLinejoin="round" />
            </svg>
          </div>
          <h2>Hi, I'm Ava 👋</h2>
          <p>Your ShopEase support assistant. Ask about an order, a refund, or shipping — or try one of these:</p>
          <SuggestedQuestions onPick={onPickSuggestion} />
        </div>
      </div>
    );
  }

  return (
    <div className="chat-scroll">
      <div className="chat-thread">
        {messages.map((m) => (
          <ChatMessage
            key={m.id}
            role={m.role}
            content={m.content}
            cards={m.cards}
            isError={m.isError}
            timestamp={m.timestamp}
          />
        ))}
        {isTyping && (
          <div className="chat-row ai">
            <div className="avatar ai">Ava</div>
            <div className="bubble-col">
              <div className="bubble ai">
                <TypingIndicator />
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
