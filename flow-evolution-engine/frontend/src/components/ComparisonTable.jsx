export default function ComparisonTable({ flows = [], winners = [] }) {
  const winnerIds = new Set(winners.map((w) => w.flow_id))
  return (
    <div className="rounded-lg bg-white p-4 shadow">
      <h2 className="mb-3 text-lg font-semibold">Flow Comparison (A/B/C)</h2>
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b text-left">
            <th>Variant</th>
            <th>Version Group</th>
            <th>Score</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {flows.map((f) => (
            <tr key={f.id} className="border-b">
              <td>{f.variant_id}</td>
              <td>{f.version_group}</td>
              <td>{Number(f.score || 0).toFixed(4)}</td>
              <td className={winnerIds.has(f.id) ? 'font-semibold text-emerald-700' : 'text-slate-600'}>
                {winnerIds.has(f.id) ? 'Winner' : 'Candidate'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
