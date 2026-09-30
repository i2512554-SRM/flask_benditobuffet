<template>
  <div v-if="!categorias.length" class="chart-empty">
    <i class="fa-solid fa-chart-column"></i>
    <span>Sin datos para mostrar en este periodo.</span>
  </div>
  <div v-else class="bar-scroll" :class="{ 'bar-scroll-horizontal': horizontal }">
    <div class="bar-chart" :style="{ height: altura + 'px' }">
      <Bar :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'
import { Bar } from 'vue-chartjs'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
)

const props = defineProps({
  categorias: { type: Array, default: () => [] },
  series: { type: Array, default: () => [] },
  horizontal: { type: Boolean, default: false },
  moneda: { type: Boolean, default: true },
  altura: { type: Number, default: 260 }
})

const chartData = computed(() => ({
  labels: props.categorias,
  datasets: props.series.map((s) => ({
    label: s.label,
    data: s.valores || [],
    backgroundColor: s.color || '#16a34a',
    borderColor: s.color || '#16a34a',
    borderRadius: 6,
    maxBarThickness: 34
  }))
}))

const fmtValor = (v) => props.moneda
  ? 'S/ ' + Number(v).toLocaleString('es-PE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
  : Number(v).toLocaleString('es-PE')

const tooltipLabel = (ctx) => {
  const v = props.horizontal ? ctx.parsed.x : ctx.parsed.y
  return ` ${ctx.dataset.label}: ${fmtValor(v)}`
}

const valor = props.horizontal ? 'x' : 'y'
const categorias = props.horizontal ? 'y' : 'x'

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  indexAxis: props.horizontal ? 'y' : 'x',
  interaction: { mode: 'index', intersect: false },
  plugins: {
    legend: {
      display: props.series.length > 1,
      position: 'bottom',
      labels: {
        usePointStyle: true,
        boxWidth: 8,
        padding: 14,
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
      callbacks: { label: tooltipLabel }
    }
  },
  scales: {
    [categorias]: {
      grid: { display: false },
      ticks: {
        color: '#64748b',
        font: { size: 10 },
        autoSkip: true,
        maxTicksLimit: props.horizontal ? 12 : 10
      }
    },
    [valor]: {
      grid: { color: '#e2e8f0', drawBorder: false },
      border: { display: false },
      beginAtZero: true,
      ticks: {
        color: '#64748b',
        font: { size: 10 },
        callback: (v) => props.moneda ? 'S/' + Number(v).toLocaleString('es-PE') : Number(v).toLocaleString('es-PE')
      }
    }
  }
}
</script>

<style scoped>
.bar-scroll {
  width: 100%;
  overflow-x: auto;
}

.bar-chart {
  width: 100%;
  min-width: 0;
}

.bar-scroll-horizontal .bar-chart {
  min-width: 460px;
}

.chart-empty {
  height: 100%;
  min-height: 120px;
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