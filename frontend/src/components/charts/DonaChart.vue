<template>
  <div class="dona-chart" :class="{ 'dona-apilado': apilado }">
    <div v-if="!itemsFiltrados.length" class="chart-empty">
      <i class="fa-solid fa-chart-pie"></i>
      <span>Sin datos para mostrar en este periodo.</span>
    </div>
    <template v-else>
      <div class="dona-canvas" :style="{ width: 'min(100%, ' + altura + 'px)' }">
        <Doughnut :data="chartData" :options="chartOptions" />
        <div v-if="mostrarTotal" class="dona-total">
          <span class="dona-total-label">Total</span>
          <span class="dona-total-valor">{{ formato(total) }}</span>
        </div>
      </div>
      <ul class="dona-leyenda">
        <li v-for="item in itemsFiltrados" :key="item.etiqueta">
          <span class="dona-punto" :style="{ background: item.color }"></span>
          <span class="dona-nombre">{{ item.etiqueta }}</span>
          <span class="dona-monto">{{ formato(item.valor) }}</span>
          <span class="dona-pct">{{ porcentaje(item.valor) }}</span>
        </li>
      </ul>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'
import { Doughnut } from 'vue-chartjs'

ChartJS.register(ArcElement, Tooltip, Legend)

const props = defineProps({
  items: { type: Array, default: () => [] },
  moneda: { type: Boolean, default: true },
  mostrarTotal: { type: Boolean, default: true },
  altura: { type: Number, default: 250 },
  apilado: { type: Boolean, default: false }
})

const PALETA = ['#16a34a', '#3b82f6', '#f59e0b', '#8b5cf6', '#dc2626', '#0891b2']

const itemsFiltrados = computed(() => (props.items || [])
  .filter((it) => Number(it.valor || 0) > 0)
  .map((it, i) => ({
    etiqueta: it.etiqueta,
    valor: Number(it.valor || 0),
    color: it.color || PALETA[i % PALETA.length]
  })))

const total = computed(() => itemsFiltrados.value.reduce((sum, it) => sum + it.valor, 0))

const formato = (v) => props.moneda
  ? 'S/ ' + Number(v).toLocaleString('es-PE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
  : Number(v).toLocaleString('es-PE')

const porcentaje = (v) => (total.value
  ? ((Number(v) / total.value) * 100).toLocaleString('es-PE', { maximumFractionDigits: 1 })
  : '0') + '%'

const chartData = computed(() => ({
  labels: itemsFiltrados.value.map((it) => it.etiqueta),
  datasets: [{
    data: itemsFiltrados.value.map((it) => it.valor),
    backgroundColor: itemsFiltrados.value.map((it) => it.color),
    borderColor: '#ffffff',
    borderWidth: 2,
    hoverOffset: 4
  }]
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: '68%',
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: '#ffffff',
      titleColor: '#172033',
      bodyColor: '#172033',
      borderColor: '#e2e8f0',
      borderWidth: 1,
      padding: 10,
      cornerRadius: 8,
      callbacks: {
        label: (ctx) => {
          const it = itemsFiltrados.value[ctx.dataIndex]
          const pct = total.value ? ((it.valor / total.value) * 100).toFixed(1) : '0'
          return props.moneda
            ? ` ${it.etiqueta}: S/ ${it.valor.toLocaleString('es-PE', { minimumFractionDigits: 2 })} (${pct}%)`
            : ` ${it.etiqueta}: ${it.valor.toLocaleString('es-PE')} (${pct}%)`
        }
      }
    }
  }
}
</script>

<style scoped>
.dona-chart {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 1.25rem;
  align-items: center;
}

.dona-chart.dona-apilado {
  grid-template-columns: 1fr;
  justify-items: center;
}

.dona-chart.dona-apilado .dona-canvas {
  width: 100% !important;
  max-width: 260px;
}

.dona-chart.dona-apilado .dona-leyenda {
  min-width: 0;
  width: 100%;
  max-width: 420px;
}

.dona-canvas {
  position: relative;
  aspect-ratio: 1 / 1;
  height: auto;
  margin: 0 auto;
}

.dona-total {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

.dona-total-label {
  font-size: 0.7rem;
  color: var(--text-muted);
}

.dona-total-valor {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--text-main);
}

.dona-leyenda {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 0.55rem;
  min-width: 180px;
}

.dona-leyenda li {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.82rem;
}

.dona-punto {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.dona-nombre {
  color: var(--text-main);
  font-weight: 600;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dona-monto {
  color: var(--text-main);
  font-variant-numeric: tabular-nums;
}

.dona-pct {
  color: var(--text-muted);
  min-width: 48px;
  text-align: right;
  font-variant-numeric: tabular-nums;
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

@media (max-width: 560px) {
  .dona-chart {
    grid-template-columns: 1fr;
  }

  .dona-leyenda {
    min-width: 0;
  }
}
</style>