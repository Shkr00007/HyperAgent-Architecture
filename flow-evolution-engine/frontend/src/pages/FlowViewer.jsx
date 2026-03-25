import { useMemo } from 'react'
import FlowGraph from '../components/FlowGraph'
import ExecutionCompare from '../components/ExecutionCompare'

export default function FlowViewer({ state, actions }) {
  const selectedFlow = useMemo(() => state.flows.find((f) => f.id === state.selectedFlowId) || state.flows[0], [state])

  return (
    <div className="space-y-4">
      <div className="rounded bg-white p-4 shadow">
        <label className="mr-2 text-sm">Select Variant:</label>
        <select className="rounded border p-2" value={selectedFlow?.id || ''} onChange={(e) => actions.setSelectedFlowId(Number(e.target.value))}>
          {state.flows.map((f) => (
            <option key={f.id} value={f.id}>{f.version_group}-{f.variant_id}</option>
          ))}
        </select>
      </div>
      <FlowGraph flow={selectedFlow?.flow_json} executionPath={state.executions.find((e) => e.flow_id === selectedFlow?.id)?.path || []} />
      <ExecutionCompare executions={state.executions} evaluations={state.evaluations} />
    </div>
  )
}
