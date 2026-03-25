import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || 'http://localhost:8000',
})

export const ingest = async ({ file, text }) => {
  const form = new FormData()
  if (file) form.append('file', file)
  if (text) form.append('text', text)
  const { data } = await api.post('/ingest', form)
  return data
}

export const extractFlow = async (payload) => (await api.post('/extract-flow', payload)).data
export const getFlows = async () => (await api.get('/flows')).data
export const executeFlow = async (payload) => (await api.post('/execute-flow', payload)).data
export const evaluateFlow = async (payload) => (await api.post('/evaluate', payload)).data
export const evolveFlow = async (payload) => (await api.post('/evolve', payload)).data
export const getEvolutionLog = async () => (await api.get('/evolution-log')).data
export const getBestFlow = async () => (await api.get('/best-flow')).data
