import { useState } from 'react'

export default function ExecutionPanel({ onRun, onEvaluate, onEvolve, result, evaluation, loading }) {
  const [scenario, setScenario] = useState('Customer asks for refund after delivery delay')

  return (
    <div className="rounded-lg bg-white p-4 shadow">
      <h2 className="mb-3 text-lg font-semibold">Execution Panel</h2>
      <textarea
        className="mb-3 h-24 w-full rounded border p-2"
        value={scenario}
        onChange={(e) => setScenario(e.target.value)}
      />
      <div className="flex gap-2">
        <button className="rounded bg-emerald-600 px-3 py-2 text-white" onClick={() => onRun(scenario)} disabled={loading}>
          Run Flow
        </button>
        <button className="rounded bg-amber-600 px-3 py-2 text-white" onClick={onEvaluate} disabled={!result || loading}>
          Evaluate
        </button>
        <button className="rounded bg-purple-700 px-3 py-2 text-white" onClick={onEvolve} disabled={!evaluation || loading}>
          Evolve
        </button>
      </div>

      {result && (
        <div className="mt-3 rounded bg-slate-100 p-3 text-sm">
          <div><strong>Path:</strong> {result.path.join(' → ')}</div>
          <div><strong>Output:</strong> {result.final_output}</div>
        </div>
      )}

      {evaluation && (
        <div className="mt-3 rounded bg-indigo-50 p-3 text-sm">
          <div><strong>Score:</strong> {evaluation.score}</div>
          <div>{evaluation.notes}</div>
        </div>
      )}
    </div>
  )
}
