import { useRef, useState } from "react";
import { api } from "../api.js";

export default function RagPanel({ missionId }) {
  const fileRef = useRef(null);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);
  const [asking, setAsking] = useState(false);
  const [error, setError] = useState(null);

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setError(null);
    try {
      const res = await api.uploadDocument(missionId, file);
      setUploadStatus(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  };

  const handleAsk = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    setAsking(true);
    setError(null);
    try {
      const res = await api.researchQuery(missionId, query.trim());
      setResult(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setAsking(false);
    }
  };

  return (
    <div className="card">
      <h2 className="section-title">📄 Research over your own documents (RAG)</h2>
      <p style={{ color: "var(--text-dim)", fontSize: 13, marginTop: -6, marginBottom: 14 }}>
        Upload a PDF (papers, notes, specs) and ask questions — NEXUS extracts, chunks, embeds, and
        retrieves the relevant passages, then has the Research Agent answer grounded in your document.
      </p>

      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 14 }}>
        <input ref={fileRef} type="file" accept="application/pdf" onChange={handleUpload} disabled={uploading} />
        {uploading && <span className="spinner" />}
        {uploadStatus && (
          <span style={{ fontSize: 12.5, color: "var(--ok)" }}>
            {uploadStatus.filename} — {uploadStatus.chunks_stored} chunks stored
          </span>
        )}
      </div>

      <form onSubmit={handleAsk} className="blocker-row" style={{ marginBottom: 12 }}>
        <input
          type="text"
          placeholder="Ask a question about the uploaded document(s)..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button className="btn-primary" type="submit" disabled={asking}>
          {asking ? <span className="spinner" /> : "Ask"}
        </button>
      </form>

      {error && <div style={{ color: "var(--danger)", fontSize: 13, marginBottom: 10 }}>{error}</div>}

      {result && (
        <div className="scenario-result">
          <div style={{ fontSize: 11, color: "var(--text-dim)", marginBottom: 6 }}>
            answered by: {result.llm_provider}
          </div>
          <div style={{ fontSize: 14, marginBottom: 10, whiteSpace: "pre-wrap" }}>{result.answer}</div>
          {result.chunks.length > 0 && (
            <>
              <div style={{ fontSize: 11.5, color: "var(--text-dim)", marginBottom: 4 }}>Retrieved chunks:</div>
              <ul className="evidence-list">
                {result.chunks.map((c, i) => (
                  <li key={i}>
                    <b>{c.source}:</b> {c.content.slice(0, 160)}…
                  </li>
                ))}
              </ul>
            </>
          )}
        </div>
      )}
    </div>
  );
}
