export default function RefundCard({ data }) {
  return (
    <div className="info-card">
      <div className="info-card-title">
        <span>💸 Refund</span>
        <span className="info-card-id">{data.order_id}</span>
      </div>
      <Row label="Status" value={data.refund_status} />
      <Row label="Amount" value={`${data.currency} ${data.refund_amount?.toFixed?.(2) ?? data.refund_amount}`} />
      <Row label="Requested" value={data.requested_date} />
      <Row label="Completed" value={data.completed_date || "Pending"} />
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
