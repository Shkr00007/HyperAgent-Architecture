import UploadBox from '../components/UploadBox'
import ComparisonTable from '../components/ComparisonTable'

export default function Dashboard({ state, actions }) {
  return (
    <div className="space-y-4">
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
          <h2 className="mb-3 text-lg font-semibold">Variant Generation</h2>
          <label className="mb-2 block text-sm">Version Group</label>
          <input
            className="mb-2 w-full rounded border p-2"
            value={state.versionGroup}
            onChange={(e) => actions.setVersionGroup(e.target.value)}
          />
          <button className="mr-2 rounded bg-blue-700 px-4 py-2 text-white" onClick={actions.handleGenerateVariants} disabled={state.loading || !state.ingestedText}>
            Generate A/B/C
          </button>
          <button className="rounded bg-emerald-700 px-4 py-2 text-white" onClick={actions.handleRunCompetition} disabled={state.loading || !state.flows.length}>
            Run Competition
          </button>
        </div>
      </div>
      <ComparisonTable flows={state.flows} winners={state.winners} />
    </div>
  )
}
