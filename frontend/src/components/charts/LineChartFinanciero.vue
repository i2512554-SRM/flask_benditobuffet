<template>
  <div class="line-chart">
    <div v-if="!puntos.length" class="chart-empty">
      <i class="fa-solid fa-chart-line"></i>
      <span>Sin datos para mostrar en este periodo.</span>
    </div>
    <Line v-else :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import { Line } from 'vue-chartjs'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

const props = defineProps({
  puntos: { type: Array, default: () => [] },
  series: { type: Array, default: () => ['ingresos', 'egresos', 'ganancia'] }
})

const COLORS = {
  ingresos: '#16a34a',
  egresos: '#dc2626',
  ganancia: '#ff7b00'
}

const seriesList = [
  { key: 'ingresos', label: 'Ingresos' },
  { key: 'egresos', label: 'Egresos' },
  { key: 'ganancia', label: 'Balance' }
]

const chartData = computed(() => {
  const labels = props.puntos.map((p) => p.etiqueta)
  const datasets = seriesList
    .filter((s) => props.series.includes(s.key))
    .map((s) => {
      const color = COLORS[s.key]
      return {
        label: s.label,
        data: props.puntos.map((p) => Number(p[s.key] || 0)),
        borderColor: color,
        backgroundColor: s.key === 'ganancia' ? 'rgba(255, 123, 0, 0.12)' : color,
        fill: s.key === 'ganancia',
        tension: 0.15,
        pointRadius: 3,
        pointHoverRadius: 5,
        borderWidth: 2
      }
    })
  return { labels, datasets }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: { mode: 'index', intersect: false },
  plugins: {
    legend: {
      position: 'bottom',
      labels: {
        usePointStyle: true,
        boxWidth: 8,
        padding: 16,
        color: '#64748b',
        font: { size: 11 }
      }
    },
    tooltip: {
      backgroundColor: '#ffffff',
      titleColor: '#172033',
      bodyColor: '#172033',
      borderColor: '#e2e8f0',
      borderWidth: 1,
      padding: 10,
      cornerRadius: 8,
      callbacks: {
        label: (ctx) =>
          ` ${ctx.dataset.label}: S/. ${Number(ctx.parsed.y).toLocaleString('es-PE', { minimumFractionDigits: 2 })}`
      }
    }
  },
  scales: {
    x: {
      grid: { display: false },
      ticks: { color: '#64748b', maxTicksLimit: 8, font: { size: 10 } }
    },
    y: {
      grid: { color: '#e2e8f0', drawBorder: false },
      border: { display: false },
      ticks: {
        color: '#64748b',
        font: { size: 10 },
        callback: (v) => 'S/' + Number(v).toLocaleString('es-PE')
      }
    }
  }
}
</script>

<style scoped>
.line-chart {
  height: 280px;
  width: 100%;
  position: relative;
}

.chart-empty {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  color: var(--text-muted);
  font-size: 0.85rem;
}

.chart-empty i {
  font-size: 1.6rem;
  opacity: 0.4;
}
</style>
