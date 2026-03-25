import { Link, Route, Routes } from 'react-router-dom'
import { useEffect, useState } from 'react'
import Dashboard from './pages/Dashboard'
import FlowViewer from './pages/FlowViewer'
import Evolution from './pages/Evolution'
import { ingest, extractFlow, executeFlow, evaluateFlow, evolveFlow, getEvolutionLog } from './services/api'

export default function App() {
  const [file, setFile] = useState(null)
  const [text, setText] = useState('')
  const [ingestedText, setIngestedText] = useState('')
  const [currentFlow, setCurrentFlow] = useState(null)
  const [execution, setExecution] = useState(null)
  const [evaluation, setEvaluation] = useState(null)
  const [logs, setLogs] = useState([])
  const [selectedNode, setSelectedNode] = useState(null)
  const [loading, setLoading] = useState(false)

  const refreshLogs = async () => {
    try {
      setLogs(await getEvolutionLog())
    } catch {
      setLogs([])
    }
  }

  useEffect(() => {
    refreshLogs()
  }, [])

  const handleIngest = async () => {
    setLoading(true)
    try {
      const data = await ingest({ file, text })
      setIngestedText(data.text)
    } finally {
      setLoading(false)
    }
  }

  const handleGenerate = async () => {
    setLoading(true)
    try {
      const flow = await extractFlow({ text: ingestedText || text, name: 'HyperAgent Flow' })
      setCurrentFlow(flow)
      setExecution(null)
      setEvaluation(null)
      setSelectedNode(null)
    } finally {
      setLoading(false)
    }
  }

  const handleRun = async (scenario) => {
    if (!currentFlow) return
    setLoading(true)
    try {
      const out = await executeFlow({ flow_id: currentFlow.id, scenario })
      setExecution(out)
    } finally {
      setLoading(false)
    }
  }

  const handleEvaluate = async () => {
    if (!currentFlow || !execution) return
    setLoading(true)
    try {
      const out = await evaluateFlow({ flow_id: currentFlow.id, execution_id: execution.execution_id })
      setEvaluation(out)
      setCurrentFlow({ ...currentFlow, score: out.score })
    } finally {
      setLoading(false)
    }
  }

  const handleEvolve = async () => {
    if (!currentFlow) return
    setLoading(true)
    try {
      const evolved = await evolveFlow({ flow_id: currentFlow.id })
      setCurrentFlow(evolved)
      setExecution(null)
      setEvaluation(null)
      await refreshLogs()
    } finally {
      setLoading(false)
    }
  }

  const state = { file, text, ingestedText, currentFlow, execution, evaluation, logs, selectedNode, loading }
  const actions = {
    setFile,
    setText,
    setSelectedNode,
    handleIngest,
    handleGenerate,
    handleRun,
    handleEvaluate,
    handleEvolve,
  }

  return (
    <div className="min-h-screen bg-slate-100">
      <nav className="mb-6 flex gap-4 bg-slate-900 p-4 text-white">
        <Link to="/">Dashboard</Link>
        <Link to="/flow">Flow Viewer</Link>
        <Link to="/evolution">Evolution</Link>
      </nav>
      <main className="mx-auto max-w-6xl p-4">
        <Routes>
          <Route path="/" element={<Dashboard state={state} actions={actions} />} />
          <Route path="/flow" element={<FlowViewer state={state} actions={actions} />} />
          <Route path="/evolution" element={<Evolution logs={logs} />} />
        </Routes>
      </main>
    </div>
  )
}
