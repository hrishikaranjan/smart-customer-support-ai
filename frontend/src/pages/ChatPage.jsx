import { useState } from "react";
import ChatWindow from "../components/ChatWindow.jsx";
import MessageInput from "../components/MessageInput.jsx";
import Header from "../components/Header.jsx";
import { useSessionId } from "../hooks/useSessionId.js";
import { api } from "../services/api.js";

let idCounter = 0;
function nextId() {
  idCounter += 1;
  return idCounter;
}

export default function ChatPage({ onMenuClick }) {
  const sessionId = useSessionId();
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);

  async function sendMessage(text) {
    const userMsg = {
      id: nextId(),
      role: "user",
      content: text,
      cards: [],
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsTyping(true);

    try {
      const res = await api.sendMessage(sessionId, text);
      const aiMsg = {
        id: nextId(),
        role: "assistant",
        content: res.reply,
        cards: res.cards || [],
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch (err) {
      const errorMsg = {
        id: nextId(),
        role: "assistant",
        content: err.message || "Something went wrong. Please try again.",
        cards: [],
        isError: true,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsTyping(false);
    }
  }

  return (
    <div className="chat-page">
      <Header title="Support Chat" subtitle="Ask Ava about orders, refunds, or policies" onMenuClick={onMenuClick} />
      <ChatWindow messages={messages} isTyping={isTyping} onPickSuggestion={sendMessage} />
      <MessageInput onSend={sendMessage} disabled={isTyping} />
    </div>
  );
}
