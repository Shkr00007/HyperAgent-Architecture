import { useMemo } from 'react'
import FlowGraph from '../components/FlowGraph'
import ExecutionPanel from '../components/ExecutionPanel'

export default function FlowViewer({ state, actions }) {
  const nodeDetails = useMemo(() => {
    if (!state.selectedNode || !state.currentFlow) return null
    return state.currentFlow.flow_json.nodes.find((n) => n.id === state.selectedNode)
  }, [state.selectedNode, state.currentFlow])

  return (
    <div className="space-y-4">
      <FlowGraph
        flow={state.currentFlow?.flow_json}
        executionPath={state.execution?.path || []}
        onNodeClick={actions.setSelectedNode}
      />
      {nodeDetails && (
        <div className="rounded bg-white p-3 text-sm shadow">
          <strong>Node:</strong> {nodeDetails.label} ({nodeDetails.type}) - {nodeDetails.details}
        </div>
      )}
      <ExecutionPanel
        onRun={actions.handleRun}
        onEvaluate={actions.handleEvaluate}
        onEvolve={actions.handleEvolve}
        result={state.execution}
        evaluation={state.evaluation}
        loading={state.loading}
      />
    </div>
  )
}
