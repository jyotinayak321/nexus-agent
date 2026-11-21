import MarkdownRenderer from "./MarkdownRenderer";

export default function PlanTab({ result }) {
  if (!result) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-8 text-center space-y-3">
        <div className="mx-auto w-12 h-12 rounded-full bg-orange-100 flex items-center justify-center text-orange-600">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
          </svg>
        </div>
        <h3 className="font-semibold text-gray-800 text-base">No Research Plan Generated Yet</h3>
        <p className="text-sm text-gray-500 max-w-md mx-auto">
          Submit an objective above (e.g. comparing AI agent frameworks or evaluating pgvector storage) to trigger the planning agent.
        </p>
      </div>
    );
  }

  const cost = result.cost_summary || {};
  const budgetStatus = cost.budget_status || "unspecified";
  const deadlineStatus = cost.deadline_status || "unspecified";

  const budgetBadge = {
    within_budget: "bg-green-100 text-green-800 border-green-200",
    exceeded: "bg-red-100 text-red-800 border-red-200",
    zero_budget: "bg-blue-100 text-blue-800 border-blue-200",
    unspecified: "bg-gray-100 text-gray-700 border-gray-200",
  }[budgetStatus] || "bg-gray-100 text-gray-700 border-gray-200";

  const deadlineBadge = {
    feasible: "bg-green-100 text-green-800 border-green-200",
    tight: "bg-yellow-100 text-yellow-800 border-yellow-200",
    at_risk: "bg-red-100 text-red-800 border-red-200",
    unspecified: "bg-gray-100 text-gray-700 border-gray-200",
  }[deadlineStatus] || "bg-gray-100 text-gray-700 border-gray-200";

  return (
    <div className="space-y-6">
      {/* Budget & Deadline Metrics Panel */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4">
        <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3">
          Execution Controls & Cost Tracking
        </h4>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-sm">
          <div className="bg-gray-50 rounded-lg p-3 border border-gray-100">
            <span className="text-xs text-gray-500 block">Est. LLM Cost</span>
            <span className="text-base font-bold text-gray-900">
              ${cost.estimated_cost_usd !== undefined ? cost.estimated_cost_usd.toFixed(4) : "0.0000"}
            </span>
            <span className="text-[11px] text-gray-400 block mt-0.5">
              ~{cost.estimated_tokens || 0} tokens
            </span>
          </div>

          <div className="bg-gray-50 rounded-lg p-3 border border-gray-100">
            <span className="text-xs text-gray-500 block">Budget Ceiling</span>
            <span className="text-base font-bold text-gray-900">
              {cost.budget_limit_usd !== null && cost.budget_limit_usd !== undefined
                ? `$${Number(cost.budget_limit_usd).toFixed(2)}`
                : "No limit"}
            </span>
            <span className={`text-[10px] font-semibold uppercase px-1.5 py-0.5 rounded border inline-block mt-1 ${budgetBadge}`}>
              {budgetStatus.replace("_", " ")}
            </span>
          </div>

          <div className="bg-gray-50 rounded-lg p-3 border border-gray-100">
            <span className="text-xs text-gray-500 block">Target Timeline</span>
            <span className="text-base font-bold text-gray-900">
              {cost.deadline_days ? `${cost.deadline_days} days` : "Unspecified"}
            </span>
            <span className={`text-[10px] font-semibold uppercase px-1.5 py-0.5 rounded border inline-block mt-1 ${deadlineBadge}`}>
              {deadlineStatus.replace("_", " ")}
            </span>
          </div>

          <div className="bg-gray-50 rounded-lg p-3 border border-gray-100">
            <span className="text-xs text-gray-500 block">Enforcement Mode</span>
            <span className="text-xs font-semibold text-gray-800 block mt-1">
              Active Tracking
            </span>
            <span className="text-[10px] text-gray-500 block mt-0.5">
              Milestone & Token Analysis
            </span>
          </div>
        </div>

        {cost.budget_notes && (
          <p className="text-xs text-gray-600 mt-3 pt-2 border-t border-gray-100">
            <span className="font-semibold text-gray-700">Cost note:</span> {cost.budget_notes}
          </p>
        )}
      </div>

      {/* Structured Implementation Plan */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-3">
        <div className="flex justify-between items-center border-b pb-3">
          <h3 className="font-bold text-gray-900 text-lg flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-orange-500"></span>
            Implementation Plan & Deliverables
          </h3>
          <span className="text-xs font-medium text-gray-500 bg-gray-100 px-2 py-1 rounded">
            English Synthesis
          </span>
        </div>
        <div className="pt-1">
          <MarkdownRenderer content={result.task_plan} />
        </div>
      </div>

      {/* RAG Context Attribution */}
      {result.rag_sources && result.rag_sources.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5 space-y-3">
          <h4 className="font-bold text-gray-900 text-sm uppercase tracking-wider flex items-center gap-2">
            <svg className="w-4 h-4 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
            Attributed Document Sources & Citations
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {result.rag_sources.map((source, index) => (
              <div key={index} className="bg-gray-50 border border-gray-200 rounded-lg p-3 space-y-1 text-xs">
                <div className="flex justify-between items-center">
                  <span className="font-semibold text-gray-900 truncate">
                    {source.filename}
                  </span>
                  <span className="bg-orange-100 text-orange-800 font-bold px-1.5 py-0.5 rounded text-[10px]">
                    {Math.round((source.score || 0) * 100)}% Match
                  </span>
                </div>
                <div className="text-gray-500 font-mono text-[11px]">
                  Chunk #{source.chunk_index} · {source.citation || `[${source.filename}#chunk-${source.chunk_index}]`}
                </div>
                {source.snippet && (
                  <p className="text-gray-600 italic mt-1 line-clamp-3">
                    "{source.snippet}"
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
