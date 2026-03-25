import EvolutionChart from '../components/EvolutionChart'
import EvolutionTree from '../components/EvolutionTree'

export default function Evolution({ state, actions }) {
  return (
    <div className="space-y-4">
      <div className="rounded bg-white p-4 shadow">
        <h2 className="mb-2 text-lg font-semibold">Selection + Evolution</h2>
        <div className="flex gap-2">
          <button className="rounded bg-amber-600 px-3 py-2 text-white" onClick={actions.handleSelectWinners} disabled={state.loading || !state.flows.length}>
            Select Top-2
          </button>
          <input
            className="rounded border p-2"
            value={state.nextVersionGroup}
            onChange={(e) => actions.setNextVersionGroup(e.target.value)}
          />
          <button className="rounded bg-purple-700 px-3 py-2 text-white" onClick={actions.handleEvolveWinners} disabled={state.loading || !state.winners.length}>
            Evolve Winners
          </button>
        </div>
      </div>
      <EvolutionChart points={state.performancePoints} />
      <EvolutionTree history={state.evolutionHistory} flows={state.allFlows} />
    </div>
  )
}
