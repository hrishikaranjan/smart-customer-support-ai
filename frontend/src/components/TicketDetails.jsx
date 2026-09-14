import { useState } from "react";
import StatusBadge from "./StatusBadge.jsx";
import SentimentBadge from "./SentimentBadge.jsx";
import PriorityBadge from "./PriorityBadge.jsx";
import { api } from "../services/api.js";

const STATUS_OPTIONS = ["Open", "In Progress", "Resolved"];

export default function TicketDetails({ ticket, onClose, onUpdated }) {
  const [status, setStatus] = useState(ticket.status);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  async function handleStatusChange(e) {
    const newStatus = e.target.value;
    setStatus(newStatus);
    setSaving(true);
    setError("");
    try {
      const updated = await api.updateTicketStatus(ticket.ticket_id, newStatus);
      onUpdated(updated);
    } catch (err) {
      setError(err.message);
      setStatus(ticket.status);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="drawer-backdrop" onClick={onClose}>
      <div className="drawer-panel" onClick={(e) => e.stopPropagation()}>
        <div className="drawer-header">
          <div>
            <h3 className="mono">{ticket.ticket_id}</h3>
            <StatusBadge status={ticket.status} />
          </div>
          <button className="drawer-close" onClick={onClose} aria-label="Close">
            ✕
          </button>
        </div>

        <div className="drawer-section">
          <div className="label">Customer session</div>
          <div className="value mono">{ticket.session_id}</div>
        </div>

        <div className="drawer-section">
          <div className="label">Issue</div>
          <div className="value">{ticket.issue}</div>
        </div>

        <div className="drawer-section">
          <div className="label">Sentiment / Priority</div>
          <div className="value" style={{ display: "flex", gap: 8 }}>
            <SentimentBadge sentiment={ticket.sentiment} />
            <PriorityBadge priority={ticket.priority} />
          </div>
        </div>

        {ticket.summary && (
          <div className="drawer-section">
            <div className="label">AI conversation summary</div>
            <div className="value">{ticket.summary}</div>
          </div>
        )}

        <div className="drawer-section">
          <div className="label">Update status</div>
          <select className="status-select" value={status} onChange={handleStatusChange} disabled={saving}>
            {STATUS_OPTIONS.map((opt) => (
              <option key={opt} value={opt}>{opt}</option>
            ))}
          </select>
          {error && <div className="error-banner" style={{ marginTop: 10 }}>{error}</div>}
        </div>

        <div className="drawer-section">
          <div className="label">Created</div>
          <div className="value mono">{new Date(ticket.created_at).toLocaleString()}</div>
        </div>
      </div>
    </div>
  );
}
