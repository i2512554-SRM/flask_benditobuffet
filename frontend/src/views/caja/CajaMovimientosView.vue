<template>
  <div class="caja-movimientos">
    <div class="page-hero">
      <div class="hero-left">
        <h1>Movimientos</h1>
        <p>Ingresos y egresos de caja con filtros por fecha, tipo y responsable</p>
      </div>
      <button :disabled="loading" class="btn btn-primary" @click="abrirRegistro('ingreso')">
        <i class="fa-solid fa-plus"></i> Registrar movimiento
      </button>
    </div>

    <!-- Filtros -->
    <div class="filtros-bar">
      <div class="filtro-grupo">
        <label>Fecha</label>
        <input type="date" v-model="fechaDesde" aria-label="Desde" />
        <span class="filtro-sep">a</span>
        <input type="date" v-model="fechaHasta" aria-label="Hasta" />
      </div>
      <div class="filtro-grupo">
        <label>Tipo</label>
        <div class="tipo-pills">
          <button class="tipo-pill" :class="{ active: tipoFiltro === 'ingreso' }" @click="toggleTipo('ingreso')">Ingreso</button>
          <button class="tipo-pill" :class="{ active: tipoFiltro === 'egreso' }" @click="toggleTipo('egreso')">Egreso</button>
        </div>
      </div>
      <div class="filtro-grupo">
        <label>Responsable</label>
        <select v-model="responsableFiltro" class="filtro-select">
          <option :value="null">Todos</option>
          <option v-for="r in responsables" :key="r" :value="r">{{ r }}</option>
        </select>
      </div>
      <button v-if="filtrosActivos" class="btn btn-outline btn-sm" @click="limpiarFiltros">
        <i class="fa-solid fa-xmark"></i> Limpiar filtros
      </button>
      <button class="btn btn-outline btn-sm" :disabled="loading" @click="cargar">
        <i class="fa-solid fa-arrows-rotate"></i> Actualizar
      </button>
    </div>

    <div class="table-card">
      <DataTable :value="filas" :paginator="true" :rows="10" dataKey="id_transaccion" responsiveLayout="scroll" class="p-datatable-sm">
        <Column field="fecha" header="Fecha" style="max-width: 7rem;">
          <template #body="slotProps">
            <span class="text-muted">{{ soloFecha(slotProps.data.fecha) }}</span>
          </template>
        </Column>
        <Column field="hora" header="Hora" style="max-width: 5rem;">
          <template #body="slotProps">
            <span class="text-muted">{{ soloHora(slotProps.data.fecha) }}</span>
          </template>
        </Column>
        <Column field="tipo" header="Tipo" style="max-width: 7rem;">
          <template #body="slotProps">
            <Tag :value="slotProps.data.tipo === 'Venta' ? 'Ingreso' : 'Egreso'"
              :severity="slotProps.data.tipo === 'Venta' ? 'success' : 'danger'" />
          </template>
        </Column>
        <Column field="descripcion" header="Concepto">
          <template #body="slotProps">
            <span class="text-muted">{{ slotProps.data.descripcion || (slotProps.data.tipo === 'Gasto' ? 'Egreso registrado' : 'Ingreso registrado') }}</span>
          </template>
        </Column>
        <Column field="responsable" header="Responsable" style="max-width: 11rem;">
          <template #body="slotProps">
            <span class="text-muted">{{ slotProps.data.responsable || '—' }}</span>
          </template>
        </Column>
        <Column field="monto" header="Monto">
          <template #body="slotProps">
            <span :class="slotProps.data.tipo === 'Gasto' ? 'monto-neg' : 'monto-pos'">
              {{ slotProps.data.tipo === 'Gasto' ? '−' : '+' }} S/ {{ formatMoney(slotProps.data.monto) }}
            </span>
          </template>
        </Column>
        <template #empty><EstadoVacio v-if="loading" compacto titulo="Revolviendo los datos…" expresion="pensando" /><EstadoVacio v-else compacto titulo="No encontré movimientos" mensaje="Prueba cambiando los filtros." expresion="pensando" /></template>
      </DataTable>
    </div>

    <!-- Dialogo: registrar movimiento -->
    <CajaTransaccionDialog v-model:visible="dialogTransaccion" :tipo="tipoRegistro" @registrado="cargar" />

    <div class="loading-overlay" v-if="loading">
      <i class="fa-solid fa-spinner fa-spin"></i>
    </div>
  </div>
</template>

<script setup>
import { soloFecha, soloHora } from '../../utils/format'
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import CajaTransaccionDialog from '../../components/caja/CajaTransaccionDialog.vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'
import api from '../../config/axios'

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const data = ref({ transacciones: [], historico: [], ultimos_movimientos: [] })

const fechaDesde = ref('')
const fechaHasta = ref('')
const tipoFiltro = ref(null)
const responsableFiltro = ref(null)

const tipoRegistro = ref('Venta')
const dialogTransaccion = ref(false)

const responsables = computed(() =>
  [...new Set((data.value.ultimos_movimientos || []).map((t) => t.responsable).filter(Boolean))]
)

const filtrosActivos = computed(() => !!tipoFiltro.value || !!responsableFiltro.value || !!fechaDesde.value || !!fechaHasta.value)

const diaClave = (iso) => {
  const fecha = new Date(iso)
  if (Number.isNaN(fecha.getTime())) return iso
  return fecha.toLocaleDateString('en-CA', { timeZone: 'America/Lima' })
}

const filas = computed(() => {
  let items = data.value.ultimos_movimientos || []
  if (tipoFiltro.value === 'ingreso') items = items.filter((t) => t.tipo === 'Venta')
  else if (tipoFiltro.value === 'egreso') items = items.filter((t) => t.tipo === 'Gasto')
  if (responsableFiltro.value) items = items.filter((t) => (t.responsable || '') === responsableFiltro.value)
  if (fechaDesde.value) items = items.filter((t) => diaClave(t.fecha) >= fechaDesde.value)
  if (fechaHasta.value) items = items.filter((t) => diaClave(t.fecha) <= fechaHasta.value)
  return items
})

const formatMoney = (val) => Number(val || 0).toLocaleString('es-PE', { minimumFractionDigits: 2 })

const toggleTipo = (tipo) => {
  tipoFiltro.value = tipoFiltro.value === tipo ? null : tipo
}

const limpiarFiltros = () => {
  tipoFiltro.value = null
  responsableFiltro.value = null
  fechaDesde.value = ''
  fechaHasta.value = ''
}

const cargar = async () => {
  loading.value = true
  try {
    const res = await api.get('/caja/transacciones?historico=1&limit=500')
    if (res.data?.success) data.value = res.data.data
  } catch (err) {
    console.error('Error cargando movimientos:', err)
  } finally {
    loading.value = false
  }
}

const abrirRegistro = (direccion) => {
  tipoRegistro.value = direccion === 'egreso' ? 'Gasto' : 'Venta'
  dialogTransaccion.value = true
}

onMounted(() => {
  const filtro = route.query.filtro
  if (filtro === 'egresos') {
    tipoFiltro.value = 'egreso'
  } else if (filtro === 'ventas' || filtro === 'ingresos') {
    tipoFiltro.value = 'ingreso'
  }
  const registrar = route.query.registrar
  if (registrar === 'ingreso' || registrar === 'egreso') {
    abrirRegistro(registrar)
  }
  if (route.query.filtro || route.query.registrar) {
    router.replace({ query: {} })
  }
  cargar()
})
</script>

<style scoped>
.page-hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.text-muted { color: var(--text-muted); }

.filtros-bar {
  display: flex;
  align-items: flex-end;
  flex-wrap: wrap;
  gap: 1rem;
  margin-top: 1rem;
  padding: 0.9rem 1rem;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  box-shadow: var(--shadow-soft);
}

.filtro-grupo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filtro-grupo label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-muted);
}

.filtros-bar input[type='date'],
.filtro-select {
  padding: 0.45rem 0.7rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-card);
  color: var(--text-main);
  font: inherit;
  font-size: 0.8rem;
}

.filtro-sep {
  color: var(--text-muted);
  font-size: 0.8rem;
}

.tipo-pills {
  display: inline-flex;
  gap: 0.35rem;
}

.tipo-pill {
  padding: 0.4rem 0.9rem;
  border-radius: 999px;
  border: 1px solid var(--border-color);
  background: var(--bg-secondary);
  color: var(--text-muted);
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.tipo-pill.active {
  border-color: var(--btn-primary);
  background: var(--btn-primary);
  color: #fff;
}

.btn-sm {
  padding: 0.45rem 0.9rem;
  font-size: 0.8rem;
}

.table-card {
  margin-top: 1rem;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  padding: 0.75rem;
  box-shadow: var(--shadow-soft);
}

.monto-pos { color: var(--color-verde-fuerte); font-weight: 600; }
.monto-neg { color: var(--color-rojo); font-weight: 600; }

.field {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  margin-bottom: 1rem;
}

.field label {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--text-muted);
}

.w-full { width: 100%; }
:deep(.p-inputnumber) { width: 100%; }
:deep(.p-select) { width: 100%; }

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.3rem;
  padding: 1.5rem;
  color: var(--text-muted);
  font-size: 0.85rem;
}

.empty-state i {
  font-size: 1.3rem;
  opacity: 0.4;
}

.loading-overlay {
  display: flex;
  justify-content: center;
  padding: 2rem;
  color: var(--btn-primary);
  font-size: 1.5rem;
}

@media (max-width: 768px) {
  .page-hero { flex-direction: column; }
  .filtro-grupo { flex-wrap: wrap; }
}
</style>
