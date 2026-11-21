import MarkdownRenderer from "./MarkdownRenderer";

export default function RiskTab({ result }) {
  if (!result) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-8 text-center space-y-3">
        <div className="mx-auto w-12 h-12 rounded-full bg-orange-100 flex items-center justify-center text-orange-600">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <h3 className="font-semibold text-gray-800 text-base">No Risk Analysis Generated Yet</h3>
        <p className="text-sm text-gray-500 max-w-md mx-auto">
          Submit your research objective above to activate the risk agent for architectural, budget, and deadline assessment.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-3">
        <div className="flex justify-between items-center border-b pb-3">
          <h3 className="font-bold text-gray-900 text-lg flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-red-500"></span>
            Risk Matrix, Severity Levels & Mitigation
          </h3>
          <span className="text-xs font-semibold text-red-700 bg-red-50 border border-red-200 px-2 py-0.5 rounded">
            Risk & Reliability Node
          </span>
        </div>
        <div className="pt-1">
          <MarkdownRenderer content={result.risks || "No critical risks evaluated."} />
        </div>
      </div>
    </div>
  );
}
