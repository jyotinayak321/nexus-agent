// Central frontend API layer.
const BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8420").replace(/\/+$/, "");

async function parseResponse(response) {
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.detail || payload.error || `Request failed (${response.status})`);
  }
  return payload;
}

export async function createGoal(goal, budget, deadlineDays) {
  const response = await fetch(`${BASE_URL}/goal`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ goal, budget, deadline_days: deadlineDays }),
  });
  return parseResponse(response);
}

export async function executeGoal(goalId) {
  const response = await fetch(`${BASE_URL}/execute/${goalId}`, { method: "POST" });
  return parseResponse(response);
}

export async function getPlan(goalId) {
  const response = await fetch(`${BASE_URL}/plan/${goalId}`);
  return parseResponse(response);
}

export async function uploadDocument(file) {
  const body = new FormData();
  body.append("file", file);
  const response = await fetch(`${BASE_URL}/documents/upload`, {
    method: "POST",
    body,
  });
  return parseResponse(response);
}

export async function searchDocuments(query, topK = 5) {
  const response = await fetch(`${BASE_URL}/rag/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, top_k: topK }),
  });
  return parseResponse(response);
}
