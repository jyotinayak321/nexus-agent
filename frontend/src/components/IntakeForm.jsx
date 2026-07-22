import { useState } from "react";

const EXAMPLE_GOALS = [
  "Mujhe 30 days mein AI/ML project complete karna hai",
  "Build an AI Healthcare diagnosis assistant",
  "Build a RAG-based customer support chatbot",
];

export default function IntakeForm({ onSubmit, submitting, error }) {
  const [goal, setGoal] = useState("");
  const [days, setDays] = useState(30);
  const [hoursPerDay, setHoursPerDay] = useState(2);
  const [budget, setBudget] = useState(5000);
  const [hasGpu, setHasGpu] = useState(false);
  const [team, setTeam] = useState([]);

  const addMember = () => setTeam([...team, { name: "", skills: "" }]);
  const updateMember = (i, field, value) => {
    const next = [...team];
    next[i] = { ...next[i], [field]: value };
    setTeam(next);
  };
  const removeMember = (i) => setTeam(team.filter((_, idx) => idx !== i));

  const submit = (e) => {
    e.preventDefault();
    if (!goal.trim()) return;
    onSubmit({
      goal: goal.trim(),
      days: Number(days),
      hours_per_day: Number(hoursPerDay),
      budget_inr: Number(budget),
      has_gpu: hasGpu,
      team: team.filter((m) => m.name.trim()).map((m) => ({ name: m.name.trim(), skills: m.skills })),
    });
  };

  return (
    <form className="card" onSubmit={submit}>
      <h2 className="section-title">🎯 Define your mission</h2>

      <div style={{ marginBottom: 14 }}>
        <label>Goal</label>
        <textarea
          value={goal}
          onChange={(e) => setGoal(e.target.value)}
          placeholder="e.g. Mujhe 30 days mein AI/ML project complete karna hai"
        />
        <div className="chip-row">
          {EXAMPLE_GOALS.map((g) => (
            <span key={g} className="chip" onClick={() => setGoal(g)}>
              {g}
            </span>
          ))}
        </div>
      </div>

      <div className="form-grid" style={{ marginBottom: 14 }}>
        <div>
          <label>Days available</label>
          <input type="number" min={1} value={days} onChange={(e) => setDays(e.target.value)} />
        </div>
        <div>
          <label>Hours / day</label>
          <input type="number" min={0.5} step={0.5} value={hoursPerDay} onChange={(e) => setHoursPerDay(e.target.value)} />
        </div>
        <div>
          <label>Budget (₹)</label>
          <input type="number" min={0} value={budget} onChange={(e) => setBudget(e.target.value)} />
        </div>
        <div className="checkbox-row">
          <input type="checkbox" id="gpu" checked={hasGpu} onChange={(e) => setHasGpu(e.target.checked)} />
          <label htmlFor="gpu" style={{ marginBottom: 0 }}>I have a GPU</label>
        </div>
      </div>

      <div style={{ marginBottom: 14 }}>
        <label>Team (optional — leave empty if solo)</label>
        {team.map((m, i) => (
          <div className="team-row" key={i}>
            <input
              type="text"
              placeholder="Name"
              value={m.name}
              onChange={(e) => updateMember(i, "name", e.target.value)}
            />
            <input
              type="text"
              placeholder="Skills e.g. python, ai, ml"
              value={m.skills}
              onChange={(e) => updateMember(i, "skills", e.target.value)}
            />
            <button type="button" className="btn-ghost btn-sm" onClick={() => removeMember(i)}>
              ✕
            </button>
          </div>
        ))}
        <button type="button" className="btn-secondary btn-sm" onClick={addMember}>
          + Add team member
        </button>
      </div>

      {error && (
        <div style={{ color: "var(--danger)", fontSize: 13, marginBottom: 10 }}>{error}</div>
      )}

      <button className="btn-primary" type="submit" disabled={submitting}>
        {submitting ? (
          <>
            <span className="spinner" /> Running mission agent...
          </>
        ) : (
          "Run NEXUS →"
        )}
      </button>
    </form>
  );
}
