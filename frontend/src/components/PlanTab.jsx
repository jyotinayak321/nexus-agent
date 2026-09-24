export default function PlanTab({ result }) {
  if (!result) return <p className="p-4 text-gray-500">Koi plan generate nahi hua abhi tak.</p>;

  return (
    <div className="p-4 space-y-4">
      <div>
        <h3 className="font-semibold">Task plan</h3>
        <pre className="whitespace-pre-wrap text-sm mt-1">{result.task_plan}</pre>
      </div>
      <div>
        <h3 className="font-semibold">Risks</h3>
        <pre className="whitespace-pre-wrap text-sm mt-1">{result.risks}</pre>
      </div>

      {result.rag_sources?.length > 0 && (
        <div>
          <h3 className="font-semibold">Retrieved document sources</h3>
          <div className="mt-2 flex flex-wrap gap-2">
            {result.rag_sources.map((source, index) => (
              <span key={`${source.filename}-${source.chunk_index}-${index}`} className="text-xs border rounded-full px-2 py-1">
                {source.filename} · chunk {source.chunk_index} · {source.score}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
