import { useEffect, useState } from "react";
import Header from "../components/Header.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import TicketTable from "../components/TicketTable.jsx";
import TicketDetails from "../components/TicketDetails.jsx";
import { api } from "../services/api.js";

const FILTERS = ["All", "Open", "In Progress", "Resolved"];

export default function TicketsPage({ onMenuClick }) {
  const [tickets, setTickets] = useState([]);
  const [filter, setFilter] = useState("All");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedTicket, setSelectedTicket] = useState(null);

  async function load(status) {
    setLoading(true);
    setError("");
    try {
      const res = await api.listTickets(status === "All" ? undefined : status);
      setTickets(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load(filter);
  }, [filter]);

  function handleTicketUpdated(updated) {
    setTickets((prev) => prev.map((t) => (t.ticket_id === updated.ticket_id ? updated : t)));
    setSelectedTicket(updated);
  }

  return (
    <div className="page-shell">
      <Header title="Tickets" subtitle="All human-escalation tickets" onMenuClick={onMenuClick} />
      <div className="page-scroll">
        <div className="page-inner">
          <div className="page-heading">
            <div>
              <h2>Ticket queue</h2>
              <p>{tickets.length} ticket{tickets.length === 1 ? "" : "s"} shown</p>
            </div>
            <div style={{ display: "flex", gap: 6 }}>
              {FILTERS.map((f) => (
                <button
                  key={f}
                  className={`btn ${filter === f ? "btn-primary" : "btn-outline"}`}
                  onClick={() => setFilter(f)}
                >
                  {f}
                </button>
              ))}
            </div>
          </div>

          {error && <div className="error-banner">{error}</div>}

          {loading ? (
            <LoadingSpinner label="Loading tickets..." />
          ) : tickets.length === 0 ? (
            <div className="empty-state">
              <h3>No tickets found</h3>
              <p>Try a different filter, or wait for a customer to be escalated.</p>
            </div>
          ) : (
            <TicketTable tickets={tickets} onSelect={setSelectedTicket} />
          )}
        </div>
      </div>

      {selectedTicket && (
        <TicketDetails
          ticket={selectedTicket}
          onClose={() => setSelectedTicket(null)}
          onUpdated={handleTicketUpdated}
        />
      )}
    </div>
  );
}
