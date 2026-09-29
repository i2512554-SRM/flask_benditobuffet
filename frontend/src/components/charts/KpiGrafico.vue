<template>
  <div class="kpi-grafico">
    <template v-if="!tieneSerie">
      <div class="kpi-grafico__vacio" :style="{ height: altura + 'px' }">
        <i class="fa-solid fa-chart-column"></i>
        <span>Sin datos para mostrar en este periodo.</span>
      </div>
    </template>
    <LineChartFinanciero v-else-if="kpi.codigo === 'KPI-01'" :puntos="serieFinanciera" :series="['ingresos', 'egresos', 'ganancia']" />
    <DonaChart v-else-if="kpi.codigo === 'KPI-08'" :items="kpi.serie" :moneda="true" :mostrar-total="true" :altura="altura" apilado />
    <BarChart
      v-else
      :categorias="kpi.serie.map(s => s.etiqueta)"
      :series="[{ label: configuracion.etiqueta, valores: kpi.serie.map(s => s[configuracion.campo]), color: configuracion.color }]"
      :moneda="configuracion.moneda"
      :horizontal="kpi.codigo === 'KPI-03'"
      :altura="altura"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import LineChartFinanciero from './LineChartFinanciero.vue'
import BarChart from './BarChart.vue'
import DonaChart from './DonaChart.vue'

const props = defineProps({
  kpi: { type: Object, required: true },
  altura: { type: Number, default: 260 }
})

const GRAFICOS = {
  'KPI-02': { etiqueta: 'Ventas (S/)', campo: 'valor', color: '#3b82f6', moneda: true },
  'KPI-03': { etiqueta: 'Días que alcanza', campo: 'valor', color: '#3b82f6', moneda: false },
  'KPI-04': { etiqueta: 'Merma (%)', campo: 'valor', color: '#dc2626', moneda: false },
  'KPI-05': { etiqueta: 'Sueldos / ventas (%)', campo: 'valor', color: '#8b5cf6', moneda: false },
  'KPI-06': { etiqueta: 'Ganancia descontando insumos (%)', campo: 'valor', color: '#16a34a', moneda: false },
  'KPI-07': { etiqueta: 'Diferencia (S/)', campo: 'diferencia_abs', color: '#f59e0b', moneda: true }
}

const configuracion = computed(() => GRAFICOS[props.kpi.codigo] || { etiqueta: props.kpi.nombre, campo: 'valor', color: '#3b82f6', moneda: false })
const tieneSerie = computed(() => Array.isArray(props.kpi.serie) && props.kpi.serie.length > 0)
const serieFinanciera = computed(() => (props.kpi.serie || []).map((s) => ({
  etiqueta: s.etiqueta,
  ingresos: s.ingresos,
  egresos: s.egresos,
  ganancia: (s.ingresos || 0) - (s.egresos || 0)
})))
</script>

<style scoped>
.kpi-grafico__vacio {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  color: var(--text-muted);
  font-size: 0.85rem;
}

.kpi-grafico__vacio i {
  font-size: 1.6rem;
  opacity: 0.4;
}
</style>
