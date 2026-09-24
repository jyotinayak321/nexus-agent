const STATUSES = ["pending", "in_progress", "done", "blocked"];

export default function PlanPanel({ mission, onStatusChange }) {
  const { decomposition, task_status } = mission;

  return (
    <div className="card">
      <h2 className="section-title">🗺️ Plan & execution</h2>
      {decomposition.map((phase) => {
        const total = phase.tasks.length;
        const done = phase.tasks.filter((t) => task_status[t.id] === "done").length;
        const pct = total ? Math.round((done / total) * 100) : 0;
        return (
          <div className="phase" key={phase.id}>
            <div className="phase-title">
              {phase.title}
              <span className="phase-hours">
                {phase.tasks.reduce((s, t) => s + t.hours, 0).toFixed(1)}h · {done}/{total} done
              </span>
            </div>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${pct}%` }} />
            </div>
            {phase.tasks.map((t) => (
              <div className="task-row" key={t.id}>
                <span className="task-title">{t.title}</span>
                <span className="task-meta">{t.assignee} · {t.hours}h</span>
                <select
                  className="status-select"
                  value={task_status[t.id] || "pending"}
                  onChange={(e) => onStatusChange(t.id, e.target.value)}
                >
                  {STATUSES.map((s) => (
                    <option key={s} value={s}>
                      {s.replace("_", " ")}
                    </option>
                  ))}
                </select>
              </div>
            ))}
          </div>
        );
      })}
    </div>
  );
}
