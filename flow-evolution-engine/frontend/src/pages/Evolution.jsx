import EvolutionChart from '../components/EvolutionChart'

export default function Evolution({ logs }) {
  return (
    <div className="space-y-4">
      <EvolutionChart logs={logs} />
      <div className="rounded bg-white p-4 shadow">
        <h2 className="mb-2 text-lg font-semibold">Evolution Log</h2>
        <div className="space-y-2 text-sm">
          {logs.map((l) => (
            <div key={l.id} className="rounded border p-2">
              #{l.id}: {l.old_flow_id} → {l.new_flow_id} | {l.old_score} → {l.new_score}<br />
              <span className="text-slate-600">{l.reason}</span>
            </div>
          ))}
          {logs.length === 0 && <p>No evolution records yet.</p>}
        </div>
      </div>
    </div>
  )
}
