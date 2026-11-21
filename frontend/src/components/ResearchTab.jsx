import MarkdownRenderer from "./MarkdownRenderer";

export default function ResearchTab({ result }) {
  if (!result) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-8 text-center space-y-3">
        <div className="mx-auto w-12 h-12 rounded-full bg-orange-100 flex items-center justify-center text-orange-600">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        <h3 className="font-semibold text-gray-800 text-base">No Research Findings Yet</h3>
        <p className="text-sm text-gray-500 max-w-md mx-auto">
          Submit your research objective above to activate the research node and query the local vector store.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Research Findings Card */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-3">
        <div className="flex justify-between items-center border-b pb-3">
          <h3 className="font-bold text-gray-900 text-lg flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-orange-500"></span>
            Technical Research Findings & Framework Evidence
          </h3>
          <span className="text-xs font-semibold text-orange-700 bg-orange-50 border border-orange-200 px-2 py-0.5 rounded">
            Research Node
          </span>
        </div>
        <div className="pt-1">
          <MarkdownRenderer content={result.research_findings || "No specific research findings recorded."} />
        </div>
      </div>

      {/* Verification & Web Search Status Notice */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 text-xs text-blue-800 space-y-1">
        <div className="font-semibold flex items-center gap-1.5">
          <svg className="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          Verification Boundaries & Assumptions
        </div>
        <p className="text-blue-700">
          Findings are extracted from local uploaded documents and model baseline technical knowledge.
          External live web search is not currently connected in this environment; all external citations and benchmarks should be treated as model architectural recommendations rather than live web validations.
        </p>
      </div>
    </div>
  );
}
