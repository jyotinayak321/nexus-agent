export default function LogPanel({ log }) {
  return (
    <div className="card">
      <h2 className="section-title">📜 Mission log</h2>
      <div className="log-feed">
        {log.map((line, i) => (
          <div className="log-line" key={i}>
            {line}
          </div>
        ))}
      </div>
    </div>
  );
}
