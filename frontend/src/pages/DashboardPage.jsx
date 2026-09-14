import { useEffect, useState } from "react";
import Header from "../components/Header.jsx";
import DashboardCard from "../components/DashboardCard.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import TicketTable from "../components/TicketTable.jsx";
import TicketDetails from "../components/TicketDetails.jsx";
import { api } from "../services/api.js";

export default function DashboardPage({ onMenuClick }) {
  const [stats, setStats] = useState(null);
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedTicket, setSelectedTicket] = useState(null);

  async function load() {
    setLoading(true);
    setError("");
    try {
      const [statsRes, ticketsRes] = await Promise.all([
        api.getDashboardStats(),
        api.listTickets(),
      ]);
      setStats(statsRes);
      setTickets(ticketsRes.slice(0, 8));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  function handleTicketUpdated(updated) {
    setTickets((prev) => prev.map((t) => (t.ticket_id === updated.ticket_id ? updated : t)));
    setSelectedTicket(updated);
  }

  return (
    <div className="page-shell">
      <Header title="Dashboard" subtitle="Live overview of conversations and escalations" onMenuClick={onMenuClick} />
      <div className="page-scroll">
        <div className="page-inner">
          {error && <div className="error-banner">{error}</div>}
          {loading ? (
            <LoadingSpinner label="Loading dashboard..." />
          ) : (
            <>
              <div className="stat-grid">
                <DashboardCard label="Total Conversations" value={stats.total_conversations} />
                <DashboardCard label="Active (last hour)" value={stats.active_conversations} />
                <DashboardCard label="Escalated Tickets" value={stats.escalated_tickets} />
                <DashboardCard label="Frustrated Customers" value={stats.frustrated_customers} />
                <DashboardCard label="Open Tickets" value={stats.open_tickets} />
                <DashboardCard label="Resolved Tickets" value={stats.resolved_tickets} />
              </div>

              <div className="page-heading">
                <div>
                  <h2>Recent tickets</h2>
                  <p>Click a row to view the full conversation summary.</p>
                </div>
              </div>

              {tickets.length === 0 ? (
                <div className="empty-state">
                  <h3>No tickets yet</h3>
                  <p>Escalated conversations will show up here.</p>
                </div>
              ) : (
                <TicketTable tickets={tickets} onSelect={setSelectedTicket} />
              )}
            </>
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
