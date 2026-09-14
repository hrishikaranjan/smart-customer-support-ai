import OrderCard from "./OrderCard.jsx";
import RefundCard from "./RefundCard.jsx";
import TicketCard from "./TicketCard.jsx";

const CARD_COMPONENTS = {
  order: OrderCard,
  refund: RefundCard,
  ticket: TicketCard,
};

function formatTime(date) {
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

export default function ChatMessage({ role, content, cards = [], isError, timestamp }) {
  const isUser = role === "user";
  return (
    <div className={`chat-row ${isUser ? "user" : "ai"}`}>
      <div className={`avatar ${isUser ? "user" : "ai"}`}>{isUser ? "You" : "Ava"}</div>
      <div className="bubble-col">
        <div className={`bubble ${isUser ? "user" : "ai"} ${isError ? "error" : ""}`}>{content}</div>
        {cards.map((card, i) => {
          const Card = CARD_COMPONENTS[card.type];
          return Card ? <Card key={i} data={card.data} /> : null;
        })}
        <div className="msg-meta">{formatTime(timestamp)}</div>
      </div>
    </div>
  );
}
