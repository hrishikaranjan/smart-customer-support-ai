/**
 * api.js
 *
 * Single place that talks to the FastAPI backend. No component should
 * call fetch() directly — they all go through the functions exported here,
 * so the base URL, error handling, and JSON parsing only need to be
 * written once.
 */

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch (networkErr) {
    throw new ApiError(
      "Can't reach the support server. Is the backend running on port 8000?",
      0
    );
  }

  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      detail = body.detail || detail;
    } catch {
      /* response wasn't JSON, keep default message */
    }
    throw new ApiError(detail, response.status);
  }

  if (response.status === 204) return null;
  return response.json();
}

export const api = {
  health: () => request("/health"),

  sendMessage: (sessionId, message) =>
    request("/chat", {
      method: "POST",
      body: JSON.stringify({ session_id: sessionId, message }),
    }),

  listTickets: (status) =>
    request(`/tickets${status ? `?status=${encodeURIComponent(status)}` : ""}`),

  getTicket: (ticketId) => request(`/tickets/${encodeURIComponent(ticketId)}`),

  updateTicketStatus: (ticketId, status) =>
    request(`/tickets/${encodeURIComponent(ticketId)}`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    }),

  createTicket: (payload) =>
    request("/tickets", { method: "POST", body: JSON.stringify(payload) }),

  listConversations: () => request("/conversations"),

  getConversation: (sessionId) =>
    request(`/conversations/${encodeURIComponent(sessionId)}`),

  getDashboardStats: () => request("/dashboard/stats"),
};

export { ApiError };
