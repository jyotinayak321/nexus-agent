import { useState, useEffect } from "react";
import IntakeForm from "./components/IntakeForm";
import PlanTab from "./components/PlanTab";
import DebateTab from "./components/DebateTab";
import ResearchTab from "./components/ResearchTab";
import RiskTab from "./components/RiskTab";
import KnowledgeBase from "./components/KnowledgeBase";
import { getHealth } from "./api";

export default function App() {
  const [result, setResult] = useState(null);
  const [tab, setTab] = useState("plan");
  const [healthStatus, setHealthStatus] = useState({ backend: "checking", database: "checking" });

  useEffect(() => {
    checkHealth();
  }, []);

  async function checkHealth() {
    try {
      const data = await getHealth();
      setHealthStatus({
        backend: "online",
        database: data.database || "connected",
        groqConfigured: data.groq_configured,
        ragAvailable: data.rag_available,
      });
    } catch {
      setHealthStatus({ backend: "offline", database: "unreachable" });
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 text-gray-900 pb-16">
      {/* Top Navigation Bar */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-30 shadow-xs">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-orange-600 flex items-center justify-center text-white font-black text-lg shadow-sm">
              N
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-base font-bold text-gray-900 tracking-tight">NEXUS AI</h1>
                <span className="text-[10px] font-semibold uppercase px-1.5 py-0.5 rounded bg-orange-100 text-orange-800">
                  Research Assistant
                </span>
              </div>
              <p className="text-xs text-gray-500">
                Multi-agent LangGraph supervisor, pgvector RAG & budget governance
              </p>
            </div>
          </div>

          {/* System Health Badges */}
          <div className="flex items-center gap-2 text-xs">
            <div className="flex items-center gap-1.5 bg-gray-50 border border-gray-200 px-2.5 py-1 rounded-full">
              <span
                className={`w-2 h-2 rounded-full ${
                  healthStatus.backend === "online"
                    ? "bg-emerald-500 animate-pulse"
                    : healthStatus.backend === "checking"
                    ? "bg-amber-400"
                    : "bg-red-500"
                }`}
              />
              <span className="text-gray-700 font-medium">
                API: {healthStatus.backend}
              </span>
            </div>

            <div className="flex items-center gap-1.5 bg-gray-50 border border-gray-200 px-2.5 py-1 rounded-full">
              <span
                className={`w-2 h-2 rounded-full ${
                  healthStatus.database === "connected"
                    ? "bg-emerald-500"
                    : healthStatus.database === "checking"
                    ? "bg-amber-400"
                    : "bg-red-500"
                }`}
              />
              <span className="text-gray-700 font-medium">
                PostgreSQL: {healthStatus.database}
              </span>
            </div>

            <button
              onClick={checkHealth}
              title="Refresh connection status"
              className="text-gray-400 hover:text-gray-600 p-1"
            >
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content Container */}
      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pt-6 space-y-6">
        {/* Intake Form Section */}
        <IntakeForm onResult={setResult} />

        {/* Execution Summary Pill (when result exists) */}
        {result && (
          <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-xs flex flex-wrap items-center justify-between gap-3 text-xs">
            <div className="flex items-center gap-2">
              <span className="font-semibold text-gray-700">Goal #{result.goal_id}</span>
              <span className="text-gray-400">|</span>
              <span className="text-emerald-700 font-medium bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                Status: {result.status || "Completed"}
              </span>
              {result.rag_sources && result.rag_sources.length > 0 && (
                <span className="text-blue-700 font-medium bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                  {result.rag_sources.length} Sources Cited
                </span>
              )}
            </div>

            {result.cost_summary && (
              <div className="flex items-center gap-3 text-gray-600">
                <span>
                  Est. Cost:{" "}
                  <strong className="text-gray-900">
                    ${result.cost_summary.estimated_cost_usd?.toFixed(4) || "0.0000"}
                  </strong>
                </span>
                <span>
                  Tokens:{" "}
                  <strong className="text-gray-900">
                    {result.cost_summary.estimated_tokens || 0}
                  </strong>
                </span>
                {result.cost_summary.deadline_days && (
                  <span>
                    Target:{" "}
                    <strong className="text-gray-900">
                      {result.cost_summary.deadline_days}d
                    </strong>
                  </span>
                )}
              </div>
            )}
          </div>
        )}

        {/* Tab Navigation */}
        <div className="border-b border-gray-200">
          <nav className="flex space-x-1 sm:space-x-4 overflow-x-auto pb-px" aria-label="Tabs">
            <button
              onClick={() => setTab("plan")}
              className={`py-3 px-3 text-xs sm:text-sm font-semibold rounded-t-lg border-b-2 flex items-center gap-1.5 transition-colors whitespace-nowrap ${
                tab === "plan"
                  ? "border-orange-500 text-orange-600 bg-white"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
              </svg>
              Implementation Plan
            </button>

            <button
              onClick={() => setTab("debate")}
              className={`py-3 px-3 text-xs sm:text-sm font-semibold rounded-t-lg border-b-2 flex items-center gap-1.5 transition-colors whitespace-nowrap ${
                tab === "debate"
                  ? "border-orange-500 text-orange-600 bg-white"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3" />
              </svg>
              Decision & Scoring
            </button>

            <button
              onClick={() => setTab("research")}
              className={`py-3 px-3 text-xs sm:text-sm font-semibold rounded-t-lg border-b-2 flex items-center gap-1.5 transition-colors whitespace-nowrap ${
                tab === "research"
                  ? "border-orange-500 text-orange-600 bg-white"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              Research & Evidence
            </button>

            <button
              onClick={() => setTab("risks")}
              className={`py-3 px-3 text-xs sm:text-sm font-semibold rounded-t-lg border-b-2 flex items-center gap-1.5 transition-colors whitespace-nowrap ${
                tab === "risks"
                  ? "border-orange-500 text-orange-600 bg-white"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              Risks & Mitigation
            </button>

            <button
              onClick={() => setTab("kb")}
              className={`py-3 px-3 text-xs sm:text-sm font-semibold rounded-t-lg border-b-2 flex items-center gap-1.5 transition-colors whitespace-nowrap ${
                tab === "kb"
                  ? "border-orange-500 text-orange-600 bg-white"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              Knowledge Base (RAG)
            </button>
          </nav>
        </div>

        {/* Tab Content Display */}
        <div className="pt-2">
          {tab === "plan" && <PlanTab result={result} />}
          {tab === "debate" && <DebateTab result={result} />}
          {tab === "research" && <ResearchTab result={result} />}
          {tab === "risks" && <RiskTab result={result} />}
          {tab === "kb" && <KnowledgeBase />}
        </div>
      </main>
    </div>
  );
}
