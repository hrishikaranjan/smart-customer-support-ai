const QUESTIONS = [
  "Where is my order?",
  "What is your refund policy?",
  "Can I cancel my order?",
  "How long does shipping take?",
  "Talk to a human agent",
];

export default function SuggestedQuestions({ onPick }) {
  return (
    <div className="suggested-grid">
      {QUESTIONS.map((q) => (
        <button key={q} className="suggested-chip" onClick={() => onPick(q)}>
          {q}
        </button>
      ))}
    </div>
  );
}
