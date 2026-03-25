import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || 'http://localhost:8000',
})

export const ingest = async ({ file, text }) => {
  const form = new FormData()
  if (file) form.append('file', file)
  if (text) form.append('text', text)
  return (await api.post('/ingest', form)).data
}

export const generateVariants = async (payload) => (await api.post('/generate-variants', payload)).data
export const runCompetition = async (payload) => (await api.post('/run-competition', payload)).data
export const selectWinners = async (payload) => (await api.post('/select-winners', payload)).data
export const evolveWinners = async (payload) => (await api.post('/evolve-winners', payload)).data
export const getFlowsByGroup = async (versionGroup) => (await api.get(`/flows/${versionGroup}`)).data
export const getBestFlow = async () => (await api.get('/best-flow')).data
export const getEvolutionHistory = async () => (await api.get('/evolution-history')).data
export const getMutationInsights = async () => (await api.get('/mutation-insights')).data

export const getMetaLearning = async () => (await api.get('/meta-learning')).data
