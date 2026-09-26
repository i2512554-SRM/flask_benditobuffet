<template>
  <div>
    <div class="page-hero">
      <VolverBtn :to="links.panel.admin" />
      <h1>Dashboard de Indicadores</h1>
      <p>Ocho indicadores clave del negocio con comparación y tendencia</p>
    </div>

    <div class="kpi-toolbar">
      <label class="kpi-field">
        <span>Periodo</span>
        <select v-model="periodo" class="input" @change="cargar">
          <option v-for="opcion in periodos" :key="opcion.valor" :value="opcion.valor">{{ opcion.label }}</option>
        </select>
      </label>
      <template v-if="periodo !== 'rango' && periodo !== 'mes-anterior'">
        <label class="kpi-field">
          <span>Fecha de referencia</span>
          <input v-model="fecha" type="date" class="input" />
        </label>
      </template>
      <template v-else>
        <label class="kpi-field">
          <span>Desde</span>
          <input v-model="inicioRango" type="date" class="input" />
        </label>
        <label class="kpi-field">
          <span>Hasta</span>
          <input v-model="finRango" type="date" class="input" />
        </label>
      </template>
      <button class="btn btn-primary" :disabled="loading" @click="cargar">
        <i class="fa-solid" :class="loading ? 'fa-spinner fa-spin' : 'fa-rotate'"></i>
        Consultar
      </button>
    </div>

    <div v-if="meta.inicio" class="kpi-rango">
      <i class="fa-solid fa-calendar-days"></i>
      {{ soloFecha(meta.inicio) }} — {{ soloFecha(finVisible) }}
    </div>

    <p v-if="error" role="alert" class="kpi-error">{{ error }}</p>

    <div class="kpi-grid">
      <article v-for="k in kpis" :key="k.codigo" class="kpi-card" :class="{ 'kpi-alerta': !!k.alerta }">
        <div class="kpi-top">
          <span class="kpi-code">{{ k.codigo }}</span>
          <span v-if="k.estimado" class="kpi-badge" title="Cálculo aproximado con la información disponible">Estimado</span>
        </div>
        <h3>{{ k.nombre }}</h3>
        <p v-if="k.descripcion" class="kpi-descripcion">{{ k.descripcion }}</p>
        <div class="kpi-valor">
          <template v-if="k.valor === null || k.valor === undefined">—</template>
          <template v-else-if="k.unidad === 'S/'">S/ {{ fmtDinero(k.valor) }}</template>
          <template v-else>{{ k.unidad === '%' ? k.valor + '%' : k.valor + ' ' + k.unidad }}</template>
        </div>
        <div v-if="tendenciaVisible(k)" class="kpi-tendencias">
          <span class="tendencia" :class="claseTendencia(k)">
            <i class="fa-solid" :class="iconoTendencia(k)"></i>
            {{ textoVariacion(k) }}
          </span>
          <span class="vs-previa">vs periodo anterior</span>
        </div>
        <p v-if="k.nota" class="kpi-nota"><i class="fa-solid fa-circle-info"></i> {{ k.nota }}</p>
        <p v-if="k.alerta" class="kpi-alerta-msg"><i class="fa-solid fa-triangle-exclamation"></i> {{ k.alerta }}</p>
      </article>
    </div>

    <div v-if="kpis.length" class="charts-grid">
      <article v-for="k in kpis" :key="k.codigo" class="chart-card">
        <div class="chart-card-head">
          <h3>{{ k.codigo }} · {{ k.nombre }}</h3>
          <span class="chart-card-valor">
            <template v-if="k.valor === null || k.valor === undefined">Sin datos</template>
            <template v-else-if="k.unidad === 'S/'">S/ {{ fmtDinero(k.valor) }}</template>
            <template v-else>{{ k.unidad === '%' ? k.valor + '%' : k.valor + ' ' + k.unidad }}</template>
          </span>
        </div>
        <template v-if="k.codigo === 'KPI-01'">
          <LineChartFinanciero v-if="k.serie && k.serie.length" :puntos="serieFinanciera(k)" :series="['ingresos', 'egresos', 'ganancia']" />
          <div v-else class="chart-empty"><i class="fa-solid fa-chart-line"></i><span>Sin datos para mostrar en este periodo.</span></div>
        </template>
        <template v-else-if="k.codigo === 'KPI-04'">
          <BarChart v-if="k.serie && k.serie.length" :categorias="k.serie.map(s => s.etiqueta)" :series="[{ label: 'Tasa de merma (%)', valores: k.serie.map(s => s.valor), color: '#dc2626' }]" :moneda="false" />
          <div v-else class="chart-empty"><i class="fa-solid fa-chart-column"></i><span>Sin datos para mostrar en este periodo.</span></div>
        </template>
        <template v-else-if="k.codigo === 'KPI-05'">
          <BarChart v-if="k.serie && k.serie.length" :categorias="k.serie.map(s => s.etiqueta)" :series="[{ label: 'Costo laboral (%)', valores: k.serie.map(s => s.valor), color: '#8b5cf6' }]" :moneda="false" />
          <div v-else class="chart-empty"><i class="fa-solid fa-chart-column"></i><span>Sin datos para mostrar en este periodo.</span></div>
        </template>
        <template v-else-if="k.codigo === 'KPI-06'">
          <BarChart v-if="k.serie && k.serie.length" :categorias="k.serie.map(s => s.etiqueta)" :series="[{ label: 'Margen bruto (%)', valores: k.serie.map(s => s.valor), color: '#16a34a' }]" :moneda="false" />
          <div v-else class="chart-empty"><i class="fa-solid fa-chart-column"></i><span>Sin datos para mostrar en este periodo.</span></div>
        </template>
        <template v-else-if="k.codigo === 'KPI-07'">
          <BarChart v-if="k.serie && k.serie.length" :categorias="k.serie.map(s => s.etiqueta)" :series="[{ label: 'Diferencia', valores: k.serie.map(s => s.diferencia_abs), color: '#f59e0b' }]" />
          <div v-else class="chart-empty"><i class="fa-solid fa-chart-column"></i><span>Sin datos para mostrar en este periodo.</span></div>
        </template>
        <template v-else-if="k.codigo === 'KPI-08'">
          <DonaChart v-if="k.serie && k.serie.length" :items="k.serie" :moneda="true" :mostrar-total="true" :altura="260" apilado />
          <div v-else class="chart-empty"><i class="fa-solid fa-chart-pie"></i><span>Sin datos para mostrar en este periodo.</span></div>
        </template>
        <template v-else>
          <BarChart v-if="k.serie && k.serie.length" :categorias="k.serie.map(s => s.etiqueta)" :series="[{ label: serieNombre(k), valores: k.serie.map(s => s.valor), color: '#3b82f6' }]" :moneda="k.codigo === 'KPI-02'" :horizontal="k.codigo === 'KPI-03'" />
          <div v-else class="chart-empty"><i class="fa-solid fa-chart-column"></i><span>Sin datos para mostrar en este periodo.</span></div>
        </template>
      </article>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { links } from '../../router/links'
import { soloFecha, fechaLocal } from '../../utils/format'
import api from '../../config/axios'
import LineChartFinanciero from '../../components/charts/LineChartFinanciero.vue'
import BarChart from '../../components/charts/BarChart.vue'
import DonaChart from '../../components/charts/DonaChart.vue'

const periodos = [
  { valor: 'dia', label: 'Hoy' },
  { valor: 'semana', label: 'Semana actual' },
  { valor: 'mes', label: 'Mes actual' },
  { valor: 'mes-anterior', label: 'Mes anterior' },
  { valor: 'anio', label: 'Año actual' },
  { valor: 'rango', label: 'Rango personalizado' }
]

const SUBE_ES_MALO = new Set(['KPI-04', 'KPI-05', 'KPI-08'])

const cargar = async () => {
  loading.value = true
  error.value = ''
  try {
    const params = {}
    if (periodo.value === 'rango') {
      if (!inicioRango.value || !finRango.value) {
        error.value = 'Selecciona un rango de fechas válido'
        return
      }
      params.inicio = inicioRango.value
      params.fin = finRango.value
    } else {
      params.periodo = periodo.value === 'mes-anterior' ? 'mes' : periodo.value
      params.fecha = periodo.value === 'mes-anterior' ? fechaMesAnterior() : fecha.value
    }
    const res = await api.get('/indicadores', { params })
    if (res.data.success) {
      kpis.value = res.data.data.kpis || []
      meta.value = res.data.data
    }
  } catch (err) {
    const mensaje = err.response?.data?.error || 'No se pudieron calcular los indicadores. Intenta nuevamente.'
    error.value = mensaje
    console.error('Error cargando indicadores:', err)
  } finally {
    loading.value = false
  }
}

const hoyISO = () => fechaLocal(new Date())

const fechaMesAnterior = () => {
  if (periodo.value !== 'mes-anterior') return null
  const [anio, mes] = hoyISO().split('-').map(Number)
  return new Date(Date.UTC(anio, mes - 1, 0, 12)).toISOString().slice(0, 10)
}

const loading = ref(false)
const error = ref('')
const periodo = ref('mes')
const fecha = ref(hoyISO())
const inicioRango = ref('')
const finRango = ref('')
const kpis = ref([])
const meta = ref({})
const finVisible = computed(() => {
  if (!meta.value.fin) return null
  const finExclusivo = new Date(meta.value.fin)
  finExclusivo.setMilliseconds(finExclusivo.getMilliseconds() - 1)
  return finExclusivo.toISOString()
})

const fmtDinero = (val) => 'S/ ' + Number(val || 0).toLocaleString('es-PE', { minimumFractionDigits: 2 })

const esPorcentaje = (k) => k.codigo === 'KPI-02'

const tendenciaVisible = (k) => k.tendencia && k.tendencia !== 'sin_base' && k.tendencia !== 'sin_datos'

const claseTendencia = (k) => {
  if (k.tendencia === 'estable') return 'tend-estable'
  const mala = SUBE_ES_MALO.has(k.codigo)
  const arriba = k.tendencia === 'sube'
  return (mala ? !arriba : arriba) ? 'tend-buena' : 'tend-mala'
}

const iconoTendencia = (k) => {
  if (k.tendencia === 'estable') return 'fa-minus'
  return k.tendencia === 'sube' ? 'fa-arrow-trend-up' : 'fa-arrow-trend-down'
}

const textoVariacion = (k) => {
  if (k.variacion === null || k.variacion === undefined) return 'Sin comparación'
  const signo = k.variacion > 0 ? '+' : ''
  return signo + Number(k.variacion).toLocaleString('es-PE', { maximumFractionDigits: 2 }) + (esPorcentaje(k) ? '%' : ' pp')
}

const serieNombre = (k) => {
  if (k.codigo === 'KPI-02') return 'Ventas (S/)'
  if (k.codigo === 'KPI-03') return 'Cobertura (días)'
  return k.nombre
}

const serieFinanciera = (k) => (k.serie || []).map((s) => ({
  etiqueta: s.etiqueta,
  ingresos: s.ingresos,
  egresos: s.egresos,
  ganancia: (s.ingresos || 0) - (s.egresos || 0)
}))

onMounted(() => {
  periodo.value = 'mes'
  fecha.value = hoyISO()
  cargar()
})
</script>

<style scoped>
.kpi-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
  padding: 1rem 1.25rem;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  box-shadow: var(--shadow-soft);
}

.kpi-field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.kpi-field span {
  font-size: 0.78rem;
  color: var(--text-muted);
  font-weight: 600;
}

.kpi-field .input {
  min-width: 190px;
}

.kpi-rango {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1rem;
  font-size: 0.85rem;
  color: var(--text-muted);
}

.kpi-rango i {
  color: var(--btn-primary);
}

.kpi-error {
  margin-top: 1rem;
  padding: 0.8rem 1rem;
  border-radius: 10px;
  background: color-mix(in srgb, var(--danger) 12%, transparent);
  color: var(--danger);
  font-size: 0.85rem;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
  margin-top: 1.25rem;
}

.kpi-card {
  padding: 1.25rem;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  box-shadow: var(--shadow-soft);
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.kpi-card.kpi-alerta {
  border-color: color-mix(in srgb, var(--danger) 45%, var(--border-color));
}

.kpi-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.kpi-code {
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  color: var(--btn-primary);
}

.kpi-badge {
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  padding: 0.2rem 0.5rem;
  border-radius: 999px;
  background: color-mix(in srgb, var(--btn-primary) 12%, transparent);
  color: var(--btn-primary);
}

.kpi-card h3 {
  margin: 0;
  font-size: 0.92rem;
  color: var(--text-main);
}

.kpi-descripcion {
  margin: 0;
  font-size: 0.78rem;
  line-height: 1.45;
  color: var(--text-muted);
}

.kpi-valor {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-main);
  line-height: 1.1;
}

.kpi-tendencias {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
}

.tendencia {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-weight: 700;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
}

.tend-buena {
  color: #16a34a;
  background: color-mix(in srgb, #16a34a 12%, transparent);
}

.tend-mala {
  color: var(--danger);
  background: color-mix(in srgb, var(--danger) 12%, transparent);
}

.tend-estable {
  color: var(--text-muted);
  background: color-mix(in srgb, var(--text-muted) 12%, transparent);
}

.vs-previa {
  color: var(--text-muted);
}

.kpi-alerta-msg {
  margin: 0;
  font-size: 0.78rem;
  color: var(--danger);
  display: flex;
  align-items: flex-start;
  gap: 0.4rem;
}

.kpi-nota {
  margin: 0;
  font-size: 0.76rem;
  line-height: 1.45;
  color: var(--text-muted);
  display: flex;
  align-items: flex-start;
  gap: 0.4rem;
}

.kpi-nota i {
  margin-top: 0.15rem;
  color: var(--btn-primary);
}

.kpi-alerta-msg i {
  margin-top: 0.15rem;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
  gap: 1rem;
  margin-top: 1.5rem;
}

.chart-card {
  padding: 1.25rem;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  box-shadow: var(--shadow-soft);
}

.chart-card-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.chart-card-head h3 {
  margin: 0;
  font-size: 0.88rem;
  color: var(--text-main);
}

.chart-card-valor {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--btn-primary);
  white-space: nowrap;
}

.chart-empty {
  height: 220px;
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
