<template>
  <div>
    <div class="page-hero">
      <VolverBtn :to="links.panel.admin" />
      <h1>¿Cómo va el negocio?</h1>
      <p>Los indicadores clave con semáforo. Toca cualquiera para ver el detalle y qué hacer.</p>
    </div>

    <div class="kpi-toolbar">
      <label class="kpi-field">
        <span>Periodo</span>
        <select v-model="periodo" class="input" @change="cargar()">
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
      <button class="btn btn-primary" :disabled="loading" @click="cargar()">
        <i class="fa-solid" :class="loading ? 'fa-spinner fa-spin' : 'fa-rotate'"></i>
        Consultar
      </button>
    </div>

    <div v-if="meta.inicio" class="kpi-rango">
      <span><i class="fa-solid fa-calendar-days"></i> {{ soloFecha(meta.inicio) }} — {{ soloFecha(finVisible) }}</span>
      <span v-if="meta.calculado" class="kpi-calculado">
        <i class="fa-regular fa-clock"></i> Calculado a las {{ soloHora(meta.calculado) }}
        <button type="button" class="kpi-recalcular" :disabled="loading" @click="cargar(true)">
          <i class="fa-solid fa-rotate" :class="{ 'fa-spin': loading }"></i> Recalcular
        </button>
      </span>
    </div>

    <p v-if="error" role="alert" class="kpi-error">{{ error }}</p>

    <EstadoVacio v-if="loading && !kpis.length" titulo="Revolviendo los datos…" mensaje="Calculando los indicadores del periodo." expresion="pensando" />

    <section v-if="kpis.length" class="kpi-resumen">
      <OllitaMascota :expresion="resumen.expresion" :tamano="76" />
      <div>
        <h2>{{ resumen.titulo }}</h2>
        <div class="kpi-resumen__chips">
          <span v-for="estado in ['revisar', 'atencion', 'bien', 'sin_datos']" v-show="resumen.conteo[estado]" :key="estado" class="estado-pill" :class="`estado-${estado}`">
            <i :class="ESTADOS[estado].icono"></i> {{ resumen.conteo[estado] }} {{ ESTADOS[estado].etiqueta.toLowerCase() }}
          </span>
        </div>
      </div>
    </section>

    <section v-for="area in areasConKpis" :key="area.id" class="kpi-area">
      <h2 class="kpi-area__titulo"><i :class="area.icono"></i> {{ area.titulo }}</h2>
      <div class="kpi-grid">
        <button
          v-for="k in area.kpis"
          :key="k.codigo"
          type="button"
          class="kpi-card"
          :class="`borde-${estadoIndicador(k)}`"
          :aria-label="`${infoIndicador(k.codigo).nombre}: ${valorIndicador(k)}. ${ESTADOS[estadoIndicador(k)].etiqueta}. Ver detalle`"
          @click="abrirDetalle(k)"
        >
          <div class="kpi-top">
            <span class="kpi-icono" :class="`estado-${estadoIndicador(k)}`"><i :class="infoIndicador(k.codigo).icono"></i></span>
            <span class="estado-pill" :class="`estado-${estadoIndicador(k)}`">
              <i :class="ESTADOS[estadoIndicador(k)].icono"></i> {{ ESTADOS[estadoIndicador(k)].etiqueta }}
            </span>
          </div>
          <h3>{{ infoIndicador(k.codigo).nombre }}</h3>
          <p class="kpi-pregunta">{{ infoIndicador(k.codigo).pregunta }}</p>
          <div class="kpi-valor">{{ valorIndicador(k) }}</div>
          <div v-if="tendenciaVisible(k)" class="kpi-tendencias">
            <span class="tendencia" :class="claseTendencia(k)">
              <i class="fa-solid" :class="iconoTendencia(k)"></i>
              {{ textoVariacion(k) }}
            </span>
            <span class="vs-previa">{{ meta.comparacion_parcial ? 'vs mismo tramo anterior' : 'vs periodo anterior' }}</span>
          </div>
          <span class="kpi-ver">Ver detalle <i class="fa-solid fa-arrow-right"></i></span>
        </button>
      </div>
    </section>

    <KpiDetalle
      v-model:visible="detalleVisible"
      :kpi="kpiSeleccionado"
      :periodo-texto="periodoTexto"
      :comparacion-parcial="Boolean(meta.comparacion_parcial)"
      @meta-actualizada="aplicarMeta"
    />
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { links } from '../../router/links'
import { soloFecha, soloHora, fechaLocal } from '../../utils/format'
import api from '../../config/axios'
import KpiDetalle from '../../components/indicadores/KpiDetalle.vue'
import { AREAS, ESTADOS, infoIndicador, valorIndicador, estadoIndicador } from '../../config/indicadores'

const periodos = [
  { valor: 'dia', label: 'Hoy' },
  { valor: 'semana', label: 'Semana actual' },
  { valor: 'mes', label: 'Mes actual' },
  { valor: 'mes-anterior', label: 'Mes anterior' },
  { valor: 'anio', label: 'Año actual' },
  { valor: 'rango', label: 'Rango personalizado' }
]

const SUBE_ES_MALO = new Set(['KPI-04', 'KPI-05', 'KPI-08'])

const cargar = async (refrescar = false) => {
  loading.value = true
  error.value = ''
  try {
    const params = refrescar ? { refrescar: '1' } : {}
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
      if (kpiSeleccionado.value) {
        kpiSeleccionado.value = kpis.value.find((k) => k.codigo === kpiSeleccionado.value.codigo) || null
      }
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

const detalleVisible = ref(false)
const kpiSeleccionado = ref(null)
const abrirDetalle = (kpi) => {
  kpiSeleccionado.value = kpi
  detalleVisible.value = true
}

const aplicarMeta = (codigo, limites) => {
  const kpi = kpis.value.find((k) => k.codigo === codigo)
  if (kpi) kpi.limites = limites
  cargar()
}

const periodoTexto = computed(() => (meta.value.inicio ? `${soloFecha(meta.value.inicio)} — ${soloFecha(finVisible.value)}` : ''))

const areasConKpis = computed(() => AREAS
  .map((area) => ({ ...area, kpis: kpis.value.filter((k) => infoIndicador(k.codigo).area === area.id) }))
  .filter((area) => area.kpis.length))

const resumen = computed(() => {
  const conteo = { bien: 0, atencion: 0, revisar: 0, sin_datos: 0 }
  kpis.value.forEach((k) => { conteo[estadoIndicador(k)] += 1 })
  if (conteo.revisar) return { conteo, expresion: 'preocupada', titulo: conteo.revisar === 1 ? 'Hay 1 indicador para revisar' : `Hay ${conteo.revisar} indicadores para revisar` }
  if (conteo.atencion) return { conteo, expresion: 'pensando', titulo: 'Todo en orden, con algunos puntos a vigilar' }
  if (conteo.bien) return { conteo, expresion: 'celebrando', titulo: '¡El negocio va bien en este periodo!' }
  return { conteo, expresion: 'pensando', titulo: 'Aún no hay datos suficientes para este periodo' }
})

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
  return signo + Number(k.variacion).toLocaleString('es-PE', { maximumFractionDigits: 2 }) + (esPorcentaje(k) ? '%' : ' puntos')
}

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

.kpi-rango {
  flex-wrap: wrap;
  justify-content: space-between;
}

.kpi-rango i {
  color: var(--btn-primary);
}

.kpi-calculado {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
}

.kpi-recalcular {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  margin-left: 0.35rem;
  padding: 0.25rem 0.65rem;
  font: inherit;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--btn-primary);
  background: transparent;
  border: 1px solid color-mix(in srgb, var(--btn-primary) 45%, transparent);
  border-radius: 999px;
  cursor: pointer;
}

.kpi-recalcular:disabled {
  opacity: 0.6;
  cursor: wait;
}

.kpi-recalcular i {
  color: inherit;
}

.kpi-error {
  margin-top: 1rem;
  padding: 0.8rem 1rem;
  border-radius: 10px;
  background: color-mix(in srgb, var(--color-rojo) 12%, transparent);
  color: var(--color-rojo);
  font-size: 0.85rem;
}

.kpi-resumen {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-top: 1.25rem;
  padding: 1rem 1.25rem;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  box-shadow: var(--shadow-soft);
}

.kpi-resumen h2 {
  margin: 0 0 0.5rem;
  font-size: 1.1rem;
  color: var(--text-main);
}

.kpi-resumen__chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.kpi-area {
  margin-top: 1.5rem;
}

.kpi-area__titulo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 0 0.75rem;
  font-size: 1rem;
  color: var(--text-main);
}

.kpi-area__titulo i {
  color: var(--btn-primary);
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1rem;
}

.kpi-card {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  width: 100%;
  padding: 1.1rem 1.25rem;
  text-align: left;
  font: inherit;
  color: inherit;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-top-width: 4px;
  border-radius: 14px;
  box-shadow: var(--shadow-soft);
  cursor: pointer;
  transition: transform var(--transition-fast) ease, box-shadow var(--transition-fast) ease;
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-medium);
}

.kpi-card:focus-visible {
  outline: 3px solid var(--btn-primary);
  outline-offset: 2px;
}

.borde-bien { border-top-color: #16a34a; }
.borde-atencion { border-top-color: #f59e0b; }
.borde-revisar { border-top-color: var(--color-rojo); }
.borde-sin_datos { border-top-color: var(--border-color); }

.kpi-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.kpi-icono {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  font-size: 1rem;
}

.kpi-card h3 {
  margin: 0.2rem 0 0;
  font-size: 1rem;
  color: var(--text-main);
}

.kpi-pregunta {
  margin: 0;
  font-size: 0.8rem;
  line-height: 1.4;
  color: var(--text-muted);
}

.kpi-valor {
  margin-top: 0.2rem;
  font-size: 1.6rem;
  font-weight: 700;
  line-height: 1.15;
  color: var(--text-main);
}

.kpi-tendencias {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
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
  color: #15803d;
  background: color-mix(in srgb, #16a34a 12%, transparent);
}

.tend-mala {
  color: var(--color-rojo);
  background: color-mix(in srgb, var(--color-rojo) 12%, transparent);
}

.tend-estable {
  color: var(--text-muted);
  background: color-mix(in srgb, var(--text-muted) 12%, transparent);
}

.vs-previa {
  color: var(--text-muted);
}

.kpi-ver {
  margin-top: auto;
  padding-top: 0.35rem;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--btn-primary);
}

.estado-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.22rem 0.65rem;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 700;
}

.estado-bien { color: #15803d; background: color-mix(in srgb, #16a34a 14%, transparent); }
.estado-atencion { color: #b45309; background: color-mix(in srgb, #f59e0b 18%, transparent); }
.estado-revisar { color: var(--color-rojo); background: color-mix(in srgb, var(--color-rojo) 14%, transparent); }
.estado-sin_datos { color: var(--text-muted); background: color-mix(in srgb, var(--text-muted) 14%, transparent); }

@media (max-width: 600px) {
  .kpi-resumen {
    flex-direction: column;
    text-align: center;
  }

  .kpi-resumen__chips {
    justify-content: center;
  }
}
</style>
