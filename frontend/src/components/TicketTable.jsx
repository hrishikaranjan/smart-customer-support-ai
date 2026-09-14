import StatusBadge from "./StatusBadge.jsx";
import SentimentBadge from "./SentimentBadge.jsx";
import PriorityBadge from "./PriorityBadge.jsx";

function formatDate(iso) {
  return new Date(iso).toLocaleString([], {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function TicketTable({ tickets, onSelect }) {
  return (
    <div className="data-table-wrap table-scroll">
      <table className="data-table">
        <thead>
          <tr>
            <th>Ticket ID</th>
            <th>Session</th>
            <th>Issue</th>
            <th>Sentiment</th>
            <th>Priority</th>
            <th>Status</th>
            <th>Created</th>
          </tr>
        </thead>
        <tbody>
          {tickets.map((t) => (
            <tr key={t.ticket_id} onClick={() => onSelect(t)}>
              <td className="mono">{t.ticket_id}</td>
              <td className="mono">{t.session_id}</td>
              <td>{t.issue.length > 48 ? `${t.issue.slice(0, 48)}…` : t.issue}</td>
              <td><SentimentBadge sentiment={t.sentiment} /></td>
              <td><PriorityBadge priority={t.priority} /></td>
              <td><StatusBadge status={t.status} /></td>
              <td className="mono">{formatDate(t.created_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
