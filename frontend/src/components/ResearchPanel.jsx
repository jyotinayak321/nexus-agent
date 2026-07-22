export default function ResearchPanel({ research }) {
  return (
    <div className="card">
      <h2 className="section-title">🔬 Evidence-based research</h2>
      {research.map((r) => (
        <div className="research-card" key={r.topic}>
          <div className="research-topic">{r.topic}</div>
          <div className="research-rec">Recommendation: {r.recommendation}</div>
          <div style={{ fontSize: 13, marginBottom: 8 }}>{r.reasoning}</div>
          <ul className="evidence-list">
            {r.evidence.map((e, i) => (
              <li key={i}>{e}</li>
            ))}
          </ul>
          <div className="alt-note">
            <b>Alternative considered:</b> {r.alternative}
          </div>
        </div>
      ))}
    </div>
  );
}
