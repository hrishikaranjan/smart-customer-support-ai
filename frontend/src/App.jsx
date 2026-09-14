import { useState } from "react";
import { Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar.jsx";
import ChatPage from "./pages/ChatPage.jsx";
import DashboardPage from "./pages/DashboardPage.jsx";
import TicketsPage from "./pages/TicketsPage.jsx";
import HistoryPage from "./pages/HistoryPage.jsx";

export default function App() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const closeMobile = () => setMobileOpen(false);
  const openMobile = () => setMobileOpen(true);

  return (
    <div className="app-shell">
      <Sidebar mobileOpen={mobileOpen} onClose={closeMobile} />
      <div className="main-column">
        <Routes>
          <Route path="/" element={<ChatPage onMenuClick={openMobile} />} />
          <Route path="/dashboard" element={<DashboardPage onMenuClick={openMobile} />} />
          <Route path="/tickets" element={<TicketsPage onMenuClick={openMobile} />} />
          <Route path="/history" element={<HistoryPage onMenuClick={openMobile} />} />
        </Routes>
      </div>
    </div>
  );
}
