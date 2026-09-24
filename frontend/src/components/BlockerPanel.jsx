import { useState } from "react";

const EXAMPLES = [
  "GPU is no longer available",
  "Budget cut to zero",
  "Only 7 days left now",
];

export default function BlockerPanel({ onReport, submitting, lastOutcome }) {
  const [text, setText] = useState("");

  const submit = (e) => {
    e.preventDefault();
    if (!text.trim()) return;
    onReport(text.trim());
    setText("");
  };

  return (
    <div className="card">
      <h2 className="section-title">♻️ Self-correcting agent — report a blocker</h2>
      <p style={{ color: "var(--text-dim)", fontSize: 13, marginTop: -6, marginBottom: 14 }}>
        Tell NEXUS what actually happened. It detects the affected constraint, re-runs the debate, and adapts the
        plan — rather than leaving you with a stale roadmap.
      </p>
      <form className="blocker-row" onSubmit={submit} style={{ marginBottom: 10 }}>
        <textarea
          rows={2}
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="e.g. Turns out I don't have a GPU after all"
        />
        <button className="btn-primary" type="submit" disabled={submitting} style={{ alignSelf: "flex-start" }}>
          {submitting ? <span className="spinner" /> : "Report"}
        </button>
      </form>
      <div className="chip-row">
        {EXAMPLES.map((ex) => (
          <span key={ex} className="chip" onClick={() => setText(ex)}>
            {ex}
          </span>
        ))}
      </div>

      {lastOutcome && (
        <div className="scenario-result" style={{ marginTop: 16 }}>
          <div style={{ fontWeight: 700, marginBottom: 8 }}>
            {lastOutcome.changed ? "✅ Plan adapted" : "ℹ️ No change needed"}
          </div>
          <div className="log-feed">
            {lastOutcome.narrative.map((n, i) => (
              <div className="log-line new" key={i}>
                {n}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
