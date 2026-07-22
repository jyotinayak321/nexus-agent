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
};
