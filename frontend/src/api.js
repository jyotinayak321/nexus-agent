<<<<<<< HEAD
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
=======
const BASE = "/api/mission";

async function handle(res) {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed (${res.status})`);
  }
  return res.json();
}

export const api = {
  createMission: (input) =>
    fetch(BASE, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(input),
    }).then(handle),

  getMission: (id) => fetch(`${BASE}/${id}`).then(handle),

  listScenarios: (id) => fetch(`${BASE}/${id}/scenarios`).then(handle),

  simulate: (id, key) => fetch(`${BASE}/${id}/simulate/${key}`, { method: "POST" }).then(handle),

  reportBlocker: (id, description) =>
    fetch(`${BASE}/${id}/blocker`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ description }),
    }).then(handle),

  updateTaskStatus: (id, taskId, status) =>
    fetch(`${BASE}/${id}/task/${taskId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status }),
    }).then(handle),

  uploadDocument: (id, file) => {
    const form = new FormData();
    form.append("file", file);
    return fetch(`${BASE}/${id}/documents`, { method: "POST", body: form }).then(handle);
  },

  researchQuery: (id, query) =>
    fetch(`${BASE}/${id}/research-query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    }).then(handle),
};
>>>>>>> 7cbc55677b79be1bd66e40b264776391f23037bb
