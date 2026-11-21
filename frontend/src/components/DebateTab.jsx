import MarkdownRenderer from "./MarkdownRenderer";

export default function DebateTab({ result }) {
  if (!result) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-8 text-center space-y-3">
        <div className="mx-auto w-12 h-12 rounded-full bg-orange-100 flex items-center justify-center text-orange-600">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3" />
          </svg>
        </div>
        <h3 className="font-semibold text-gray-800 text-base">No Decision Generated Yet</h3>
        <p className="text-sm text-gray-500 max-w-md mx-auto">
          Run the NEXUS agent above to synthesize research findings, evaluate trade-offs, and produce a weighted scoring matrix.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Executive Architectural Decision */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-3">
        <div className="flex justify-between items-center border-b pb-3">
          <h3 className="font-bold text-gray-900 text-lg flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-orange-500"></span>
            Final Recommendation & Architectural Decision
          </h3>
          <span className="text-xs font-semibold text-green-700 bg-green-50 border border-green-200 px-2 py-0.5 rounded">
            Decision Validated
          </span>
        </div>
        <div className="pt-1">
          <MarkdownRenderer content={result.final_decision} />
        </div>
      </div>

      {/* Execution Audit Log */}
      {result.execution_log && (
        <div className="bg-gray-900 text-gray-100 rounded-xl shadow-sm p-5 space-y-2">
          <div className="flex justify-between items-center">
            <h4 className="font-mono text-xs uppercase tracking-wider text-gray-400 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></span>
              Execution Engine & Quality Audit
            </h4>
            <span className="text-xs font-mono text-gray-400">Status: {result.status || "completed"}</span>
          </div>
          <pre className="text-xs font-mono bg-black/40 p-3 rounded-lg overflow-x-auto whitespace-pre-wrap text-emerald-400">
            {result.execution_log}
          </pre>
          {result.review_summary && (
            <p className="text-xs text-gray-300 pt-1 font-mono">
              <span className="text-gray-400">Review check:</span> {result.review_summary}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
