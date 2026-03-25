import EvolutionChart from '../components/EvolutionChart'
import EvolutionTree from '../components/EvolutionTree'

export default function Evolution({ state, actions }) {
  return (
    <div className="space-y-4">
      <div className="rounded bg-white p-4 shadow">
        <h2 className="mb-2 text-lg font-semibold">Selection + Evolution</h2>
        <div className="flex gap-2">
          <button className="rounded bg-amber-600 px-3 py-2 text-white" onClick={actions.handleSelectWinners} disabled={state.loading || !state.flows.length}>
            Select Top-2 (discard rest)
          </button>
          <input className="rounded border p-2" value={state.nextVersionGroup} onChange={(e) => actions.setNextVersionGroup(e.target.value)} />
          <button className="rounded bg-purple-700 px-3 py-2 text-white" onClick={actions.handleEvolveWinners} disabled={state.loading || !state.winners.length}>
            Evolve Winners (C/A/H)
          </button>
        </div>
      </div>

      <EvolutionChart points={state.performancePoints} />
      <EvolutionTree history={state.evolutionHistory} flows={state.allFlows} />

      <div className="rounded bg-white p-4 shadow">
        <h2 className="mb-2 text-lg font-semibold">Meta Learning</h2>
        <div className="space-y-1 text-sm">
          {state.metaLearning.map((m) => (
            <div key={m.mutation_type} className="rounded border p-2">
              <strong>{m.mutation_type}</strong> | avg_score={Number(m.avg_score).toFixed(4)} | success_rate={Number(m.success_rate).toFixed(3)} | wins/trials={m.wins}/{m.trials}
            </div>
          ))}
          {state.metaLearning.length === 0 && <div>No meta-learning records yet.</div>}
        </div>
      </div>
    </div>
  )
}
