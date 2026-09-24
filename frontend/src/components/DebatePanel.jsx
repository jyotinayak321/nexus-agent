export default function DebatePanel({ debate }) {
  return (
    <div className="card">
      <h2 className="section-title">🧠 Multi-agent debate</h2>
      {debate.map((d) => (
        <div className="decision-card" key={d.topic}>
          <div className="decision-topic">{d.topic}</div>
          <div className="opinions-grid">
            {d.opinions.map((op) => (
              <div className="opinion" key={op.agent}>
                <div className="opinion-agent">
                  {op.icon} {op.agent} agent
                </div>
                <div className="opinion-stance">{op.stance}</div>
                <div className="opinion-argument">{op.argument}</div>
              </div>
            ))}
          </div>
          <div className="final-decision">
            <div className="final-decision-label">👑 Final decision</div>
            <div className="final-decision-text">{d.final_decision}</div>
            <div className="final-decision-rationale">{d.rationale}</div>
          </div>
        </div>
      ))}
    </div>
  );
}
