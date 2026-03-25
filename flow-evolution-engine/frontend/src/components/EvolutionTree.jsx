export default function EvolutionTree({ history = [], flows = [] }) {
  const byId = Object.fromEntries(flows.map((f) => [f.id, f]))
  return (
    <div className="rounded-lg bg-white p-4 shadow">
      <h2 className="mb-3 text-lg font-semibold">Evolution Tree</h2>
      <div className="space-y-2 text-sm">
        {history.map((h) => (
          <div key={h.id} className="rounded border p-2">
            {byId[h.parent_flow]?.version_group || 'v?'}:{byId[h.parent_flow]?.variant_id} → {byId[h.child_flow]?.version_group || 'v?'}:{byId[h.child_flow]?.variant_id}
            <div className="text-slate-600">mutation={h.mutation_type}</div>
          </div>
        ))}
        {history.length === 0 && <div>No evolution yet.</div>}
      </div>
    </div>
  )
}
