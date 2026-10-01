import { useState } from "react";

import IntakeForm from "./components/IntakeForm";
import KnowledgeBase from "./components/KnowledgeBase";
import PlanTab from "./components/PlanTab";
import DebateTab from "./components/DebateTab";

export default function App() {
  const [result, setResult] = useState(null);
  const [tab, setTab] = useState("plan");
  const [dark, setDark] = useState(false);

  function toggleTheme() {
    const next = !dark;
    setDark(next);

    document.documentElement.setAttribute(
      "data-theme",
      next ? "dark" : "light"
    );
  }

  return (
    <>
      <header className="app-header">
        <div className="brand">
          <div className="brand-title">NEXUS</div>

          <div className="brand-tag">
            Autonomous Research, Decision & Execution Agent
          </div>
        </div>

        <div
          style={{
            display: "flex",
            gap: 10,
            alignItems: "center",
          }}
        >
          <span className="pill">● Backend connected</span>

          <button
            className="btn-secondary btn-sm"
            onClick={toggleTheme}
          >
            {dark ? "Light mode" : "Dark mode"}
          </button>
        </div>
      </header>

      <main>
        <div className="card">
          <h2 className="section-title">
            Mission control
          </h2>

          <p
            style={{
              color: "var(--text-dim)",
              fontSize: 13,
              marginBottom: 0,
            }}
          >
            Define your goal, constraints and timeline.
            NEXUS will research, plan and generate a
            decision-oriented execution strategy.
          </p>

          <IntakeForm onResult={setResult} />
        </div>

        <KnowledgeBase />

        {result ? (
          <>
            <div
              className="stat-row"
              style={{ marginTop: 22 }}
            >
              <div className="stat">
                <div className="stat-label">
                  Pipeline
                </div>

                <div className="stat-value">
                  Complete
                </div>
              </div>

              <div className="stat">
                <div className="stat-label">
                  Agent
                </div>

                <div className="stat-value">
                  NEXUS
                </div>
              </div>

              <div className="stat">
                <div className="stat-label">
                  Status
                </div>

                <div className="stat-value">
                  Ready
                </div>
              </div>
            </div>

            <div
              className="tabs"
              style={{ marginTop: 22 }}
            >
              <button
                className={`tab ${
                  tab === "plan" ? "active" : ""
                }`}
                onClick={() => setTab("plan")}
              >
                Plan
              </button>

              <button
                className={`tab ${
                  tab === "debate" ? "active" : ""
                }`}
                onClick={() => setTab("debate")}
              >
                Debate / Decision
              </button>
            </div>

            {tab === "plan" ? (
              <PlanTab result={result} />
            ) : (
              <DebateTab result={result} />
            )}
          </>
        ) : (
          <div className="card empty-state">
            <h3>No mission executed yet</h3>

            <p>
              Enter a goal above and click
              <strong> Run NEXUS</strong>.
            </p>
          </div>
        )}
      </main>
    </>
  );
}