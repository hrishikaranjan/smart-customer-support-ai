const LABELS = {
  positive: "Positive",
  neutral: "Neutral",
  frustrated: "Frustrated",
  angry: "Angry",
};

export default function SentimentBadge({ sentiment }) {
  if (!sentiment) return null;
  const key = sentiment.toLowerCase();
  return (
    <span className={`badge sentiment-${key}`}>
      <span className="badge-dot" />
      {LABELS[key] || sentiment}
    </span>
  );
}
