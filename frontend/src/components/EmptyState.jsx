export default function EmptyState({ icon, title, description }) {
  return (
    <div className="empty-state">
      {icon}
      <h3>{title}</h3>
      {description && <p>{description}</p>}
    </div>
  );
}
