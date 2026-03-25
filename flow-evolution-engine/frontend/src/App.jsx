import { Link, Route, Routes } from 'react-router-dom'
import { useEffect, useMemo, useState } from 'react'
import Dashboard from './pages/Dashboard'
import FlowViewer from './pages/FlowViewer'
import Evolution from './pages/Evolution'
import {
  ingest,
  evolveWinners,
  generateVariants,
  getEvolutionHistory,
  getFlowsByGroup,
  runCompetition,
  selectWinners,
} from './services/api'

export default function App() {
  const [file, setFile] = useState(null)
  const [text, setText] = useState('')
  const [ingestedText, setIngestedText] = useState('')
  const [versionGroup, setVersionGroup] = useState('v1')
  const [nextVersionGroup, setNextVersionGroup] = useState('v2')
  const [flows, setFlows] = useState([])
  const [allFlows, setAllFlows] = useState([])
  const [executions, setExecutions] = useState([])
  const [evaluations, setEvaluations] = useState([])
  const [winners, setWinners] = useState([])
  const [selectedFlowId, setSelectedFlowId] = useState(null)
  const [evolutionHistory, setEvolutionHistory] = useState([])
  const [loading, setLoading] = useState(false)

  const refreshGroup = async (group = versionGroup) => {
    const groupFlows = await getFlowsByGroup(group)
    setFlows(groupFlows)
    setAllFlows((prev) => {
      const map = new Map(prev.map((f) => [f.id, f]))
      groupFlows.forEach((f) => map.set(f.id, f))
      return Array.from(map.values())
    })
    if (groupFlows.length && !selectedFlowId) setSelectedFlowId(groupFlows[0].id)
  }

  const refreshEvolutionHistory = async () => {
    try {
      setEvolutionHistory(await getEvolutionHistory())
    } catch {
      setEvolutionHistory([])
    }
  }

  useEffect(() => {
    refreshEvolutionHistory()
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

  const handleGenerateVariants = async () => {
    setLoading(true)
    try {
      await generateVariants({ text: ingestedText || text, name: 'HyperAgent Flow', version_group: versionGroup, variant_count: 3 })
      await refreshGroup(versionGroup)
      setExecutions([])
      setEvaluations([])
      setWinners([])
    } finally {
      setLoading(false)
    }
  }

  const handleRunCompetition = async () => {
    setLoading(true)
    try {
      const out = await runCompetition({ version_group: versionGroup, scenario: 'User asks for better operational decision outcome under constraints' })
      setExecutions(out.executions)
      setEvaluations(out.evaluations)
      await refreshGroup(versionGroup)
    } finally {
      setLoading(false)
    }
  }

  const handleSelectWinners = async () => {
    setLoading(true)
    try {
      const out = await selectWinners({ version_group: versionGroup, top_k: 2 })
      setWinners(out)
    } finally {
      setLoading(false)
    }
  }

  const handleEvolveWinners = async () => {
    setLoading(true)
    try {
      await evolveWinners({
        version_group: versionGroup,
        top_k: 2,
        next_version_group: nextVersionGroup,
        children_per_winner: 3,
      })
      await refreshEvolutionHistory()
      const nextFlows = await getFlowsByGroup(nextVersionGroup)
      setVersionGroup(nextVersionGroup)
      setNextVersionGroup(`v${Number(nextVersionGroup.slice(1) || 2) + 1}`)
      setFlows(nextFlows)
      setAllFlows((prev) => {
        const map = new Map(prev.map((f) => [f.id, f]))
        nextFlows.forEach((f) => map.set(f.id, f))
        return Array.from(map.values())
      })
      setExecutions([])
      setEvaluations([])
      setWinners([])
      if (nextFlows.length) setSelectedFlowId(nextFlows[0].id)
    } finally {
      setLoading(false)
    }
  }

  const performancePoints = useMemo(() => {
    const groups = [...new Set(allFlows.map((f) => f.version_group))].sort((a, b) => Number(a.slice(1)) - Number(b.slice(1)))
    let bestSoFar = 0
    return groups.map((g) => {
      const best = Math.max(...allFlows.filter((f) => f.version_group === g).map((f) => f.score || 0), 0)
      bestSoFar = Math.max(bestSoFar, best)
      return { label: g, best: bestSoFar }
    })
  }, [allFlows])

  const state = {
    file,
    text,
    ingestedText,
    versionGroup,
    nextVersionGroup,
    flows,
    allFlows,
    executions,
    evaluations,
    winners,
    selectedFlowId,
    evolutionHistory,
    performancePoints,
    loading,
  }

  const actions = {
    setFile,
    setText,
    setVersionGroup,
    setNextVersionGroup,
    setSelectedFlowId,
    handleIngest,
    handleGenerateVariants,
    handleRunCompetition,
    handleSelectWinners,
    handleEvolveWinners,
  }

  return (
    <div className="min-h-screen bg-slate-100">
      <nav className="mb-6 flex gap-4 bg-slate-900 p-4 text-white">
        <Link to="/">Comparison</Link>
        <Link to="/execution">Execution</Link>
        <Link to="/evolution">Evolution</Link>
      </nav>
      <main className="mx-auto max-w-7xl p-4">
        <Routes>
          <Route path="/" element={<Dashboard state={state} actions={actions} />} />
          <Route path="/execution" element={<FlowViewer state={state} actions={actions} />} />
          <Route path="/evolution" element={<Evolution state={state} actions={actions} />} />
        </Routes>
      </main>
    </div>
  )
}
