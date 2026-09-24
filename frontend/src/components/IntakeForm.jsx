import { useState } from "react";
import { createGoal, executeGoal } from "../api";

export default function IntakeForm({ onResult }) {
  const [goal, setGoal] = useState("");
  const [budget, setBudget] = useState("");
  const [deadline, setDeadline] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    if (!goal.trim()) return;

    setLoading(true);
    setError("");
    try {
      const created = await createGoal(
        goal,
        budget === "" ? null : Number(budget),
        deadline === "" ? null : Number(deadline),
      );
      const result = await executeGoal(created.goal_id);
      onResult(result);
    } catch (err) {
      setError(err.message || "Could not run NEXUS");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 mt-6 rounded-lg border p-4">
      <div>
        <label className="block text-sm font-medium">Your goal</label>
        <textarea
          className="w-full border rounded p-2 mt-1"
          value={goal}
          onChange={(e) => setGoal(e.target.value)}
          placeholder="e.g. Build an AI resume analyzer in 15 days"
        />
      </div>

      <div className="flex gap-4">
        <div className="flex-1">
          <label className="block text-sm font-medium">Budget ($)</label>
          <input
            type="number"
            min="0"
            className="border rounded p-2 mt-1 w-full"
            value={budget}
            onChange={(e) => setBudget(e.target.value)}
          />
        </div>
        <div className="flex-1">
          <label className="block text-sm font-medium">Deadline (days)</label>
          <input
            type="number"
            min="0"
            className="border rounded p-2 mt-1 w-full"
            value={deadline}
            onChange={(e) => setDeadline(e.target.value)}
          />
        </div>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      <button
        type="submit"
        disabled={loading}
        className="bg-orange-500 text-white px-4 py-2 rounded disabled:opacity-50"
      >
        {loading ? "Processing..." : "Run NEXUS"}
      </button>
    </form>
  );
}
