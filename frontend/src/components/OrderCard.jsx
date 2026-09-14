export default function OrderCard({ data }) {
  return (
    <div className="info-card">
      <div className="info-card-title">
        <span>📦 Order</span>
        <span className="info-card-id">{data.order_id}</span>
      </div>
      <Row label="Product" value={data.product} />
      <Row label="Status" value={data.status} />
      <Row label="Order date" value={data.order_date} />
      <Row label="Est. delivery" value={data.estimated_delivery || "—"} />
      <Row label="Amount" value={`${data.currency} ${data.amount?.toFixed?.(2) ?? data.amount}`} />
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
