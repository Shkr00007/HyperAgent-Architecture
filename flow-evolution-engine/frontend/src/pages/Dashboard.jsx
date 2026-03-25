import UploadBox from '../components/UploadBox'

export default function Dashboard({ state, actions }) {
  return (
    <div className="grid gap-4 md:grid-cols-2">
      <UploadBox
        file={state.file}
        setFile={actions.setFile}
        text={state.text}
        setText={actions.setText}
        onIngest={actions.handleIngest}
        loading={state.loading}
      />
      <div className="rounded-lg bg-white p-4 shadow">
        <h2 className="mb-3 text-lg font-semibold">Flow Generation</h2>
        <button className="rounded bg-blue-700 px-4 py-2 text-white" onClick={actions.handleGenerate} disabled={state.loading || !state.ingestedText}>
          Generate Flow
        </button>
        {state.currentFlow && (
          <div className="mt-4 space-y-1 text-sm">
            <p><strong>Flow:</strong> {state.currentFlow.name} (v{state.currentFlow.version})</p>
            <p><strong>Nodes:</strong> {state.currentFlow.flow_json.nodes.length}</p>
            <p><strong>Edges:</strong> {state.currentFlow.flow_json.edges.length}</p>
            <p><strong>Score:</strong> {state.currentFlow.score}</p>
          </div>
        )}
      </div>
    </div>
  )
}
