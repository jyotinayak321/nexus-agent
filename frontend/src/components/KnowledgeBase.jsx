import { useState } from "react";
import { searchDocuments, uploadDocument } from "../api";

export default function KnowledgeBase() {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [busy, setBusy] = useState(false);

  async function handleUpload(e) {
    e.preventDefault();
    if (!file) return;
    setBusy(true);
    setMessage("");
    try {
      const data = await uploadDocument(file);
      setMessage(`${data.filename} indexed successfully (${data.chunks} chunks).`);
      setFile(null);
      e.currentTarget.reset();
    } catch (error) {
      setMessage(error.message);
    } finally {
      setBusy(false);
    }
  }

  async function handleSearch(e) {
    e.preventDefault();
    if (!query.trim()) return;
    setBusy(true);
    setMessage("");
    try {
      const data = await searchDocuments(query, 5);
      setResults(data.results || []);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="mt-6 rounded-lg border p-4 space-y-4">
      <div>
        <h2 className="font-semibold">Knowledge base (RAG)</h2>
        <p className="text-sm text-gray-500 mt-1">
          Upload PDF, TXT or MD files. NEXUS will retrieve relevant chunks before the research agent runs.
        </p>
      </div>

      <form onSubmit={handleUpload} className="flex flex-col sm:flex-row gap-2">
        <input
          type="file"
          accept=".pdf,.txt,.md"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          className="text-sm flex-1"
        />
        <button
          type="submit"
          disabled={!file || busy}
          className="bg-gray-900 text-white px-4 py-2 rounded disabled:opacity-50"
        >
          {busy ? "Working..." : "Index document"}
        </button>
      </form>

      <form onSubmit={handleSearch} className="flex gap-2">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Test retrieval, e.g. What are the project constraints?"
          className="border rounded p-2 flex-1 text-sm"
        />
        <button
          type="submit"
          disabled={busy || !query.trim()}
          className="border px-4 py-2 rounded disabled:opacity-50"
        >
          Search
        </button>
      </form>

      {message && <p className="text-sm rounded bg-gray-50 p-2">{message}</p>}

      {results.length > 0 && (
        <div className="space-y-2">
          {results.map((item) => (
            <div key={item.chunk_id} className="rounded border p-3 text-sm">
              <div className="font-medium">
                {item.filename} · chunk {item.chunk_index} · score {item.score}
              </div>
              <p className="mt-1 text-gray-600 whitespace-pre-wrap">{item.content}</p>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
