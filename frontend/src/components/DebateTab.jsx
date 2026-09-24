// DebateTab.jsx
// -------------
// Final decision aur reasoning dikhata hai.

export default function DebateTab({ result }) {
  if (!result) return <p className="p-4 text-gray-500">Koi decision nahi hua abhi tak.</p>;

  return (
    <div className="p-4">
      <h3 className="font-semibold">Final decision</h3>
      <p className="text-sm mt-2 border rounded p-3 bg-orange-50">
        {result.final_decision}
      </p>
    </div>
  );
}
