import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
} from 'chart.js'
import { Line } from 'react-chartjs-2'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend)

export default function EvolutionChart({ logs }) {
  const labels = logs.map((l, i) => `Gen ${i + 1}`)
  const data = {
    labels,
    datasets: [
      {
        label: 'Old Score',
        data: logs.map((l) => l.old_score),
        borderColor: '#f59e0b',
      },
      {
        label: 'New Score',
        data: logs.map((l) => l.new_score),
        borderColor: '#7c3aed',
      },
    ],
  }

  return (
    <div className="rounded-lg bg-white p-4 shadow">
      <h2 className="mb-3 text-lg font-semibold">Evolution Over Time</h2>
      <Line data={data} />
    </div>
  )
}
