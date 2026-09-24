import { useEffect, useState } from "react";
import { api } from "../api.js";

export default function ScenarioPanel({ missionId }) {
  const [scenarios, setScenarios] = useState([]);
  const [result, setResult] = useState(null);
  const [activeKey, setActiveKey] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.listScenarios(missionId).then(setScenarios).catch(() => {});
  }, [missionId]);

  const run = async (key) => {
    setLoading(true);
    setActiveKey(key);
    try {
      const res = await api.simulate(missionId, key);
      setResult(res);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2 className="section-title">🧪 What-if simulation</h2>
      <p style={{ color: "var(--text-dim)", fontSize: 13, marginTop: -6, marginBottom: 14 }}>
        Simulates a scenario against the live plan without changing it — a preview before you commit.
      </p>
      <div className="scenario-grid">
        {scenarios.map((s) => (
          <button
            key={s.key}
            className="scenario-btn"
            onClick={() => run(s.key)}
            disabled={loading && activeKey === s.key}
          >
            <div className="scenario-title">{s.label}</div>
            <div className="scenario-sub">{loading && activeKey === s.key ? "Simulating..." : "Click to simulate"}</div>
          </button>
        ))}
      </div>

      {result && (
        <div className="scenario-result">
          <div style={{ fontWeight: 700, marginBottom: 6 }}>
            Scenario: {result.label}
            <span className={`badge ${result.mvp_mode ? "badge-mvp" : "badge-full"}`} style={{ marginLeft: 8 }}>
              {result.mvp_mode ? "MVP mode" : "Full roadmap"}
            </span>
          </div>
          <div style={{ fontSize: 13, color: "var(--text-dim)", marginBottom: 6 }}>
            {result.total_hours}h available · {result.phase_count} phases
          </div>
          <div style={{ fontSize: 13.5 }}>{result.summary}</div>
          {result.changed_decisions.length > 0 && (
            <ul className="diff-list">
              {result.changed_decisions.map((c, i) => (
                <li key={i}>{c}</li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
