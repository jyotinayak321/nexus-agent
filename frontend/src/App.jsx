import { useState } from "react";
<<<<<<< HEAD
import IntakeForm from "./components/IntakeForm";
import PlanTab from "./components/PlanTab";
import DebateTab from "./components/DebateTab";
import KnowledgeBase from "./components/KnowledgeBase";

export default function App() {
  const [result, setResult] = useState(null);
  const [tab, setTab] = useState("plan");

  return (
    <div className="max-w-3xl mx-auto my-8 px-4">
      <h1 className="text-xl font-medium mb-1">NEXUS autonomous agent</h1>
      <p className="text-sm text-gray-500">
        Local document RAG + multi-agent planning pipeline
      </p>

      <KnowledgeBase />
      <IntakeForm onResult={setResult} />

      <div className="flex gap-2 mt-6 border-b">
        <button
          className={`px-4 py-2 ${tab === "plan" ? "border-b-2 border-orange-500" : ""}`}
          onClick={() => setTab("plan")}
        >
          Plan
        </button>
        <button
          className={`px-4 py-2 ${tab === "debate" ? "border-b-2 border-orange-500" : ""}`}
          onClick={() => setTab("debate")}
        >
          Debate
        </button>
      </div>

      {tab === "plan" ? <PlanTab result={result} /> : <DebateTab result={result} />}
    </div>
=======
import { api } from "./api.js";
import IntakeForm from "./components/IntakeForm.jsx";
import DebatePanel from "./components/DebatePanel.jsx";
import ResearchPanel from "./components/ResearchPanel.jsx";
import RagPanel from "./components/RagPanel.jsx";
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
          {tab === "research" && (
            <>
              <RagPanel missionId={mission.mission_id} />
              <ResearchPanel research={mission.research} />
            </>
          )}
          {tab === "simulate" && <ScenarioPanel missionId={mission.mission_id} />}
          {tab === "adapt" && (
            <BlockerPanel onReport={handleBlocker} submitting={blockerSubmitting} lastOutcome={lastOutcome} />
          )}
          {tab === "log" && <LogPanel log={mission.execution_log} />}
        </>
      )}
    </>
>>>>>>> 7cbc55677b79be1bd66e40b264776391f23037bb
  );
}
