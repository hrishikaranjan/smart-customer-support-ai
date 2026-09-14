const STATUS_MAP = {
  Open: "status-open",
  "In Progress": "status-inprogress",
  Resolved: "status-resolved",
};

export default function StatusBadge({ status }) {
  const cls = STATUS_MAP[status] || "status-open";
  return (
    <span className={`badge ${cls}`}>
      <span className="badge-dot" />
      {status}
    </span>
  );
}
