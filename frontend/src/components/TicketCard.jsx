export default function TicketCard({ data }) {
  return (
    <div className="info-card">
      <div className="info-card-title">
        <span>🎫 Support Ticket Created</span>
        <span className="info-card-id">{data.ticket_id}</span>
      </div>
      <Row label="Priority" value={data.priority} />
      <Row label="Status" value={data.status} />
      <Row label="Issue" value={data.issue} />
    </div>
  );
}

function Row({ label, value }) {
  return (
    <div className="info-card-row">
      <span className="label">{label}</span>
      <span className="value">{value}</span>
    </div>
  );
}
