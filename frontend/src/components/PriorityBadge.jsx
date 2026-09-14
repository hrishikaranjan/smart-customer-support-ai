const CLASS_MAP = {
  Low: "priority-low",
  Medium: "priority-medium",
  High: "priority-high",
};

export default function PriorityBadge({ priority }) {
  const cls = CLASS_MAP[priority] || "priority-medium";
  return <span className={`badge ${cls}`}>{priority}</span>;
}
