import { useState } from "react";
import IntakeForm from "./components/IntakeForm";
import PlanTab from "./components/PlanTab";
import DebateTab from "./components/DebateTab";
import KnowledgeBase from "./components/KnowledgeBase";

export default function App() {
  const [result, setResult] = useState(null);
  const [tab, setTab] = useState("plan");

  return (
    <div className="max-w-3xl mx-auto my-8 px-4">
      <h1 className="text-xl font-medium mb-1">NEXUS autonomous agent</h1>
      <p className="text-sm text-gray-500">
        Local document RAG + multi-agent planning pipeline
      </p>

      <KnowledgeBase />
      <IntakeForm onResult={setResult} />

      <div className="flex gap-2 mt-6 border-b">
        <button
          className={`px-4 py-2 ${tab === "plan" ? "border-b-2 border-orange-500" : ""}`}
          onClick={() => setTab("plan")}
        >
          Plan
        </button>
        <button
          className={`px-4 py-2 ${tab === "debate" ? "border-b-2 border-orange-500" : ""}`}
          onClick={() => setTab("debate")}
        >
          Debate
        </button>
      </div>

      {tab === "plan" ? <PlanTab result={result} /> : <DebateTab result={result} />}
    </div>
  );
}
