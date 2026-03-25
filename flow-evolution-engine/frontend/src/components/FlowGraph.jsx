import ReactFlow, { Background, Controls } from 'react-flow-renderer'

export default function FlowGraph({ flow, executionPath = [], onNodeClick }) {
  if (!flow) return <div className="rounded bg-white p-4 shadow">No flow selected.</div>

  const highlighted = new Set(executionPath)
  const nodes = flow.nodes.map((n, i) => ({
    id: n.id,
    data: { label: n.label },
    position: { x: 100 + (i % 4) * 220, y: 50 + Math.floor(i / 4) * 140 },
    style: {
      border: highlighted.has(n.id) ? '3px solid #22c55e' : '1px solid #94a3b8',
      borderRadius: 8,
      padding: 8,
      background: n.type === 'decision' ? '#fef9c3' : '#e0f2fe',
    },
  }))

  const edges = flow.edges.map((e, idx) => ({
    id: `${e.source}-${e.target}-${idx}`,
    source: e.source,
    target: e.target,
    label: e.condition || '',
    animated: highlighted.has(e.source) && highlighted.has(e.target),
  }))

  return (
    <div className="h-[520px] rounded bg-white shadow">
      <ReactFlow nodes={nodes} edges={edges} fitView onNodeClick={(_, node) => onNodeClick?.(node.id)}>
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  )
}
