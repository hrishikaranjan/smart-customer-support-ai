import { useEffect, useState } from "react";
import Header from "../components/Header.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import SentimentBadge from "../components/SentimentBadge.jsx";
import { api } from "../services/api.js";

export default function HistoryPage({ onMenuClick }) {
  const [conversations, setConversations] = useState([]);
  const [selected, setSelected] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingThread, setLoadingThread] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .listConversations()
      .then(setConversations)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  async function openConversation(sessionId) {
    setSelected(sessionId);
    setLoadingThread(true);
    try {
      const res = await api.getConversation(sessionId);
      setMessages(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingThread(false);
    }
  }

  return (
    <div className="page-shell">
      <Header title="History" subtitle="Browse past customer conversations" onMenuClick={onMenuClick} />
      <div className="page-scroll">
        <div className="page-inner">
          {error && <div className="error-banner">{error}</div>}

          {loading ? (
            <LoadingSpinner label="Loading conversations..." />
          ) : conversations.length === 0 ? (
            <div className="empty-state">
              <h3>No conversations yet</h3>
              <p>Chat with Ava on the Support Chat page to see history here.</p>
            </div>
          ) : (
            <div style={{ display: "grid", gridTemplateColumns: selected ? "320px 1fr" : "1fr", gap: 20 }}>
              <div className="conv-list">
                {conversations.map((c) => (
                  <div
                    key={c.session_id}
                    className="conv-row"
                    onClick={() => openConversation(c.session_id)}
                    style={{ borderColor: selected === c.session_id ? "var(--teal)" : undefined }}
                  >
                    <div className="conv-row-left">
                      <div className="conv-row-id">{c.session_id}</div>
                      <div className="conv-row-meta">
                        {c.message_count} messages · {new Date(c.last_message_at).toLocaleString()}
                      </div>
                    </div>
                    <SentimentBadge sentiment={c.last_sentiment} />
                  </div>
                ))}
              </div>

              {selected && (
                <div className="data-table-wrap" style={{ padding: 18 }}>
                  {loadingThread ? (
                    <LoadingSpinner label="Loading conversation..." />
                  ) : (
                    <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                      {messages.map((m, i) => (
                        <div key={i}>
                          <div className="conv-row-meta" style={{ marginBottom: 2 }}>
                            <strong>{m.role === "user" ? "Customer" : "Ava"}</strong>{" "}
                            {new Date(m.created_at).toLocaleTimeString()}
                          </div>
                          <div>{m.content}</div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
