export default function UploadBox({ file, setFile, text, setText, onIngest, loading }) {
  return (
    <div className="rounded-lg bg-white p-4 shadow">
      <h2 className="mb-3 text-lg font-semibold">Upload Source</h2>
      <input
        className="mb-3 w-full rounded border p-2"
        type="file"
        accept=".pdf,.txt"
        onChange={(e) => setFile(e.target.files?.[0] || null)}
      />
      <textarea
        className="mb-3 h-36 w-full rounded border p-2"
        placeholder="Or paste text..."
        value={text}
        onChange={(e) => setText(e.target.value)}
      />
      <button className="rounded bg-blue-600 px-4 py-2 text-white" onClick={onIngest} disabled={loading}>
        {loading ? 'Ingesting...' : 'Ingest PDF/Text'}
      </button>
      {file && <p className="mt-2 text-sm text-slate-500">Selected: {file.name}</p>}
    </div>
  )
}
