import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend } from 'chart.js'
import { Line } from 'react-chartjs-2'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend)

export default function EvolutionChart({ points = [] }) {
  const data = {
    labels: points.map((p) => p.label),
    datasets: [
      {
        label: 'Best score over time',
        data: points.map((p) => p.best),
        borderColor: '#2563eb',
      },
    ],
  }

  return (
    <div className="rounded-lg bg-white p-4 shadow">
      <h2 className="mb-3 text-lg font-semibold">Performance Graph</h2>
      <Line data={data} />
    </div>
  )
}
