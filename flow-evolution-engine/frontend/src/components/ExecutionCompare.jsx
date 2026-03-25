export default function ExecutionCompare({ executions = [], evaluations = [] }) {
  const byFlow = Object.fromEntries(evaluations.map((e) => [e.flow_id, e]))

  return (
    <div className="rounded-lg bg-white p-4 shadow">
      <h2 className="mb-3 text-lg font-semibold">Execution View (Per Variant)</h2>
      <div className="grid gap-3 md:grid-cols-3">
        {executions.map((e) => (
          <div key={e.execution_id} className="rounded border p-3 text-sm">
            <p><strong>{e.version_group}-{e.variant_id}</strong></p>
            <p><strong>Path:</strong> {e.path.join(' → ')}</p>
            <p><strong>Output:</strong> {e.output_text}</p>
            <p><strong>Score:</strong> {byFlow[e.flow_id]?.score?.toFixed?.(4) ?? 'n/a'}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
