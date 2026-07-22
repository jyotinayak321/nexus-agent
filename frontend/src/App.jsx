import { useState } from "react";
import { api } from "./api.js";
import IntakeForm from "./components/IntakeForm.jsx";
import DebatePanel from "./components/DebatePanel.jsx";
import ResearchPanel from "./components/ResearchPanel.jsx";
import PlanPanel from "./components/PlanPanel.jsx";
import ScenarioPanel from "./components/ScenarioPanel.jsx";
import BlockerPanel from "./components/BlockerPanel.jsx";
import LogPanel from "./components/LogPanel.jsx";

const TABS = [
  { key: "plan", label: "🗺️ Plan" },
  { key: "debate", label: "🧠 Debate" },
  { key: "research", label: "🔬 Research" },
  { key: "simulate", label: "🧪 What-if" },
  { key: "adapt", label: "♻️ Adapt" },
  { key: "log", label: "📜 Log" },
];

export default function App() {
  const [mission, setMission] = useState(null);
  const [tab, setTab] = useState("plan");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [blockerSubmitting, setBlockerSubmitting] = useState(false);
  const [lastOutcome, setLastOutcome] = useState(null);

  const handleCreate = async (input) => {
    setSubmitting(true);
    setError(null);
    try {
      const result = await api.createMission(input);
      setMission(result);
      setTab("plan");
      setLastOutcome(null);
    } catch (e) {
      setError(e.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleStatusChange = async (taskId, status) => {
    const updated = await api.updateTaskStatus(mission.mission_id, taskId, status);
    setMission(updated);
  };

  const handleBlocker = async (description) => {
    setBlockerSubmitting(true);
    try {
      const res = await api.reportBlocker(mission.mission_id, description);
      setMission(res.mission);
      setLastOutcome(res);
      setTab("adapt");
    } finally {
      setBlockerSubmitting(false);
    }
  };

  const reset = () => {
    setMission(null);
    setLastOutcome(null);
    setError(null);
  };

  return (
    <>
      <div className="app-header">
        <div className="brand">
          <div className="brand-title">NEXUS</div>
          <div className="brand-tag">
            Autonomous Research, Decision &amp; Execution Agent — "From Idea to Execution: an AI Agent that thinks,
            plans, acts, and adapts."
          </div>
        </div>
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          {mission && (
            <span className="pill">Mission #{mission.mission_id}</span>
          )}
          {mission && (
            <button className="btn-ghost btn-sm" onClick={reset}>
              New mission
            </button>
          )}
        </div>
      </div>

      {!mission && <IntakeForm onSubmit={handleCreate} submitting={submitting} error={error} />}

      {mission && (
        <>
          <div className="card" style={{ marginBottom: 18 }}>
            <div className="stat-row">
              <div className="stat">
                <div className="stat-label">Goal</div>
                <div className="stat-value" style={{ fontSize: 14 }}>{mission.input.goal}</div>
              </div>
              <div className="stat">
                <div className="stat-label">Available hours</div>
                <div className="stat-value">{mission.total_hours}h</div>
              </div>
              <div className="stat">
                <div className="stat-label">Mode</div>
                <div className="stat-value">
                  <span className={`badge ${mission.mvp_mode ? "badge-mvp" : "badge-full"}`}>
                    {mission.mvp_mode ? "MVP" : "Full roadmap"}
                  </span>
                </div>
              </div>
              <div className="stat">
                <div className="stat-label">Budget</div>
                <div className="stat-value">₹{mission.input.budget_inr}</div>
              </div>
              <div className="stat">
                <div className="stat-label">GPU</div>
                <div className="stat-value">{mission.input.has_gpu ? "Yes" : "No"}</div>
              </div>
              <div className="stat">
                <div className="stat-label">Team</div>
                <div className="stat-value">{mission.input.team.length || "Solo"}</div>
              </div>
            </div>
          </div>

          <div className="tabs">
            {TABS.map((t) => (
              <div key={t.key} className={`tab ${tab === t.key ? "active" : ""}`} onClick={() => setTab(t.key)}>
                {t.label}
              </div>
            ))}
          </div>

          {tab === "plan" && <PlanPanel mission={mission} onStatusChange={handleStatusChange} />}
          {tab === "debate" && <DebatePanel debate={mission.debate} />}
          {tab === "research" && <ResearchPanel research={mission.research} />}
          {tab === "simulate" && <ScenarioPanel missionId={mission.mission_id} />}
          {tab === "adapt" && (
            <BlockerPanel onReport={handleBlocker} submitting={blockerSubmitting} lastOutcome={lastOutcome} />
          )}
          {tab === "log" && <LogPanel log={mission.execution_log} />}
        </>
      )}
    </>
  );
}
