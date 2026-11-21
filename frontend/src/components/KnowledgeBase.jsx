import { useState, useEffect } from "react";
import { searchDocuments, uploadDocument, listDocuments } from "../api";

export default function KnowledgeBase() {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [busy, setBusy] = useState(false);
  const [documents, setDocuments] = useState([]);
  const [loadingDocs, setLoadingDocs] = useState(false);

  useEffect(() => {
    fetchDocuments();
  }, []);

  async function fetchDocuments() {
    setLoadingDocs(true);
    try {
      const data = await listDocuments();
      setDocuments(data || []);
    } catch {
      // Ignored if backend starting
    } finally {
      setLoadingDocs(false);
    }
  }

  async function handleUpload(e) {
    e.preventDefault();
    if (!file) return;
    setBusy(true);
    setMessage("");
    setErrorMessage("");
    try {
      const data = await uploadDocument(file);
      setMessage(`Successfully indexed "${data.filename}" into ${data.chunks} vector chunks (pgvector).`);
      setFile(null);
      e.currentTarget.reset();
      fetchDocuments();
    } catch (error) {
      setErrorMessage(error.message);
    } finally {
      setBusy(false);
    }
  }

  async function handleSearch(e) {
    e.preventDefault();
    if (!query.trim()) return;
    setBusy(true);
    setMessage("");
    setErrorMessage("");
    try {
      const data = await searchDocuments(query, 5);
      setResults(data.results || []);
      if (!data.results || data.results.length === 0) {
        setMessage("Search executed successfully, but no matching document chunks met the threshold.");
      }
    } catch (error) {
      setErrorMessage(error.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="bg-white rounded-xl border border-gray-200 shadow-sm p-5 space-y-5">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b pb-3">
        <div>
          <h2 className="text-base font-bold text-gray-900 flex items-center gap-2">
            <svg className="w-5 h-5 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            Knowledge Base & RAG Pipeline (PostgreSQL / pgvector)
          </h2>
          <p className="text-xs text-gray-500 mt-0.5">
            Ingest local documentation to ground the multi-agent research workflow with verified context.
          </p>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="text-[11px] font-medium bg-gray-100 text-gray-600 px-2 py-0.5 rounded">.pdf</span>
          <span className="text-[11px] font-medium bg-gray-100 text-gray-600 px-2 py-0.5 rounded">.txt</span>
          <span className="text-[11px] font-medium bg-gray-100 text-gray-600 px-2 py-0.5 rounded">.md</span>
        </div>
      </div>

      {/* Document Upload Form */}
      <form onSubmit={handleUpload} className="flex flex-col sm:flex-row gap-2.5">
        <div className="relative flex-1">
          <input
            type="file"
            accept=".pdf,.txt,.md"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            className="block w-full text-xs text-gray-500 file:mr-3 file:py-2 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-gray-100 file:text-gray-700 hover:file:bg-gray-200 border border-gray-300 rounded-lg p-1 focus:outline-none"
          />
        </div>
        <button
          type="submit"
          disabled={!file || busy}
          className="inline-flex items-center justify-center gap-1.5 bg-gray-900 hover:bg-black text-white px-4 py-2 rounded-lg text-xs font-semibold disabled:opacity-50 transition-all sm:w-auto"
        >
          {busy ? "Indexing..." : "Index Document"}
        </button>
      </form>

      {/* Vector Retrieval Tester */}
      <form onSubmit={handleSearch} className="flex gap-2">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Test vector similarity, e.g. What are the multi-agent capabilities and budget constraints?"
          className="border border-gray-300 rounded-lg px-3 py-2 flex-1 text-xs focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none"
        />
        <button
          type="submit"
          disabled={busy || !query.trim()}
          className="border border-gray-300 hover:bg-gray-50 text-gray-800 px-4 py-2 rounded-lg text-xs font-semibold disabled:opacity-50 transition-all"
        >
          {busy ? "Searching..." : "Vector Search"}
        </button>
      </form>

      {/* Success and Error Alerts */}
      {message && (
        <div className="rounded-lg bg-green-50 border border-green-200 p-3 text-xs text-green-800 flex items-center gap-2">
          <svg className="w-4 h-4 text-green-600 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
          <span>{message}</span>
        </div>
      )}

      {errorMessage && (
        <div className="rounded-lg bg-red-50 border border-red-200 p-3 text-xs text-red-800 flex items-center gap-2">
          <svg className="w-4 h-4 text-red-600 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Search Results Display */}
      {results.length > 0 && (
        <div className="space-y-2.5 pt-1">
          <h4 className="text-xs font-bold text-gray-700 uppercase tracking-wider">
            Vector Similarity Matches ({results.length})
          </h4>
          <div className="space-y-2">
            {results.map((item) => (
              <div key={item.chunk_id} className="rounded-lg border border-gray-200 p-3 text-xs bg-gray-50/50 space-y-1">
                <div className="flex justify-between items-center">
                  <span className="font-semibold text-gray-900">
                    {item.filename} · chunk {item.chunk_index}
                  </span>
                  <span className="bg-orange-100 text-orange-800 font-bold px-1.5 py-0.5 rounded text-[10px]">
                    {Math.round((item.score || 0) * 100)}% Similarity
                  </span>
                </div>
                <div className="text-[11px] font-mono text-gray-500">
                  {item.citation || `[${item.filename}#chunk-${item.chunk_index}]`}
                </div>
                <p className="mt-1 text-gray-700 whitespace-pre-wrap font-sans bg-white p-2 rounded border border-gray-100">
                  {item.content}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Indexed Document Inventory */}
      {documents.length > 0 && (
        <div className="pt-2 border-t border-gray-100">
          <div className="flex justify-between items-center mb-2">
            <h4 className="text-xs font-bold text-gray-600 uppercase tracking-wider">
              Indexed Documents ({documents.length})
            </h4>
            <button
              type="button"
              onClick={fetchDocuments}
              className="text-[11px] text-orange-600 hover:text-orange-700 font-medium"
            >
              Refresh
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {documents.map((doc) => (
              <div key={doc.document_id} className="bg-gray-100 border border-gray-200 rounded-lg px-2.5 py-1 text-[11px] text-gray-700 flex items-center gap-1.5">
                <span className="font-medium text-gray-900">{doc.filename}</span>
                <span className="text-gray-500">({doc.chunks} chunks)</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
