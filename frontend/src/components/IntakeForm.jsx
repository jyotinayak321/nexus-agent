import { useState } from "react";
import { createGoal, executeGoal } from "../api";

export default function IntakeForm({ onResult, onLoadingChange }) {
  const [goal, setGoal] = useState("");
  const [budget, setBudget] = useState("");
  const [deadline, setDeadline] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState("");
  const [error, setError] = useState("");

  const sampleGoals = [
    "Compare AI agent frameworks: LangChain, LangGraph, and AutoGPT on multi-agent capabilities, pgvector storage, and custom-code requirements.",
    "Build a production-grade local document RAG assistant using PostgreSQL and sentence-transformers within 10 days.",
    "Architect an autonomous code review pipeline with strict budget tracking and automated risk analysis.",
  ];

  async function handleSubmit(e) {
    e.preventDefault();
    if (!goal.trim()) {
      setError("Please enter a research goal.");
      return;
    }

    if (budget !== "" && Number(budget) < 0) {
      setError("Budget cannot be negative.");
      return;
    }

    if (deadline !== "" && Number(deadline) <= 0) {
      setError("Deadline must be at least 1 day.");
      return;
    }

    setLoading(true);
    if (onLoadingChange) onLoadingChange(true);
    setError("");
    setLoadingStep("Creating research goal in database...");

    try {
      const created = await createGoal(
        goal.trim(),
        budget === "" ? null : Number(budget),
        deadline === "" ? null : Number(deadline)
      );

      setLoadingStep("Executing multi-agent pipeline (Research -> Planning -> Risk -> Decision)...");
      const result = await executeGoal(created.goal_id);
      onResult(result);
    } catch (err) {
      setError(err.message || "Failed to execute NEXUS research assistant.");
    } finally {
      setLoading(false);
      setLoadingStep("");
      if (onLoadingChange) onLoadingChange(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-xl border border-gray-200 shadow-sm p-5 space-y-4">
      <div>
        <div className="flex justify-between items-center mb-1">
          <label className="text-sm font-semibold text-gray-800">Research & Architecture Objective</label>
          <span className="text-xs text-gray-500">English prompt recommended</span>
        </div>
        <textarea
          className="w-full border border-gray-300 rounded-lg p-3 text-sm focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-all outline-none"
          rows={3}
          value={goal}
          onChange={(e) => setGoal(e.target.value)}
          placeholder="e.g. Compare LangChain, LangGraph, and AutoGPT for multi-agent RAG with pgvector storage, budget monitoring, and implementation timeline."
        />
        <div className="flex flex-wrap gap-1.5 mt-2">
          <span className="text-xs text-gray-500 py-0.5">Quick prompts:</span>
          {sampleGoals.map((sample, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => setGoal(sample)}
              className="text-xs bg-gray-100 hover:bg-orange-50 hover:text-orange-700 text-gray-700 rounded-md px-2 py-0.5 transition-colors text-left"
            >
              {sample.slice(0, 48)}...
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-1">
        <div>
          <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1">
            Budget Ceiling ($ USD)
          </label>
          <div className="relative rounded-md shadow-sm">
            <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
              <span className="text-gray-500 sm:text-sm">$</span>
            </div>
            <input
              type="number"
              min="0"
              step="any"
              className="block w-full rounded-lg border border-gray-300 pl-7 pr-3 py-2 text-sm focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none"
              placeholder="e.g. 250.00 (optional)"
              value={budget}
              onChange={(e) => setBudget(e.target.value)}
            />
          </div>
          <p className="text-[11px] text-gray-500 mt-1">Tracks estimated LLM inference & compute limits.</p>
        </div>

        <div>
          <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1">
            Target Deadline (Days)
          </label>
          <div className="relative rounded-md shadow-sm">
            <input
              type="number"
              min="1"
              step="1"
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none"
              placeholder="e.g. 14 (optional)"
              value={deadline}
              onChange={(e) => setDeadline(e.target.value)}
            />
          </div>
          <p className="text-[11px] text-gray-500 mt-1">Paces phased milestones and evaluates delivery risk.</p>
        </div>
      </div>

      {error && (
        <div className="rounded-lg bg-red-50 border border-red-200 p-3 text-sm text-red-700 flex items-center gap-2">
          <svg className="w-4 h-4 flex-shrink-0 text-red-500" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
          <span>{error}</span>
        </div>
      )}

      {loading && (
        <div className="rounded-lg bg-orange-50 border border-orange-200 p-3 text-sm text-orange-800 flex items-center gap-3">
          <svg className="animate-spin h-5 w-5 text-orange-600 flex-shrink-0" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <div>
            <p className="font-semibold">{loadingStep || "Processing research goal..."}</p>
            <p className="text-xs text-orange-600">Retrieving vector context and invoking LangGraph supervisor nodes.</p>
          </div>
        </div>
      )}

      <div className="flex justify-end pt-1">
        <button
          type="submit"
          disabled={loading || !goal.trim()}
          className="inline-flex items-center gap-2 bg-orange-600 hover:bg-orange-700 active:bg-orange-800 text-white font-medium text-sm px-5 py-2.5 rounded-lg shadow-sm disabled:opacity-50 disabled:cursor-not-allowed transition-all"
        >
          {loading ? (
            <>
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Analyzing & Planning...
            </>
          ) : (
            <>
              Run NEXUS Agent
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
            </>
          )}
        </button>
      </div>
    </form>
  );
}
