import { useState } from "react";

const STORAGE_KEY = "shopease_session_id";

function generateSessionId() {
  return `session_${Math.random().toString(36).slice(2, 10)}${Date.now().toString(36)}`;
}

/**
 * Returns a stable session id for this browser, creating and persisting
 * one in localStorage on first use. The backend uses this id to keep
 * conversation memory (see backend/memory.py).
 */
export function useSessionId() {
  const [sessionId] = useState(() => {
    const existing = localStorage.getItem(STORAGE_KEY);
    if (existing) return existing;
    const created = generateSessionId();
    localStorage.setItem(STORAGE_KEY, created);
    return created;
  });
  return sessionId;
}
