<template>
  <div class="cajera-panel">
    <div class="page-hero">
      <div class="hero-left">
        <h1>¡Hola, {{ nombre }}! 👋</h1>
        <p>Bienvenida a tu panel de Caja</p>
        <div class="hero-badges">
          <span class="rol-badge" style="background: rgba(16, 185, 129, 0.1); color: #059669;">
            <i class="fa-solid fa-cash-register"></i> Cajera
          </span>
          <span class="fecha-badge"><i class="fa-regular fa-calendar"></i> {{ fechaHoy }}</span>
        </div>
      </div>
      <router-link to="/caja" class="btn btn-outline">
        <i class="fa-solid fa-vault"></i> Ir al Control de Caja
      </router-link>
    </div>

    <!-- Resumen de caja -->
    <h2 class="seccion-title">Resumen de caja</h2>
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon" :class="caja.abierta ? 'positive' : 'negative'">
          <i :class="caja.abierta ? 'fa-solid fa-lock-open' : 'fa-solid fa-lock'"></i>
        </div>
        <div class="stat-content">
          <span class="stat-label">Estado</span>
          <span class="stat-value" style="text-transform: capitalize;">{{ caja.abierta ? 'Abierta' : 'Cerrada' }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon blue">
          <i class="fa-solid fa-clock"></i>
        </div>
        <div class="stat-content">
          <span class="stat-label">Monto inicial / apertura</span>
          <span class="stat-value">S/. {{ formatMoney(caja.cierre?.monto_inicial) }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon positive">
          <i class="fa-solid fa-arrow-trend-up"></i>
        </div>
        <div class="stat-content">
          <span class="stat-label">Ingresos del día</span>
          <span class="stat-value">S/. {{ formatMoney(caja.ventas_dia) }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon negative">
          <i class="fa-solid fa-arrow-trend-down"></i>
        </div>
        <div class="stat-content">
          <span class="stat-label">Egresos del día</span>
          <span class="stat-value">S/. {{ formatMoney(caja.gastos_dia) }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" :class="(caja.neto_dia ?? 0) >= 0 ? 'positive' : 'negative'">
          <i class="fa-solid fa-scale-balanced"></i>
        </div>
        <div class="stat-content">
          <span class="stat-label">Saldo actual</span>
          <span class="stat-value">S/. {{ formatMoney(caja.neto_dia) }}</span>
        </div>
      </div>
    </div>

    <!-- Acciones rápidas -->
    <h2 class="seccion-title">Acciones rápidas</h2>
    <div class="acciones-grid">
      <button class="accion-chip chip-btn" :class="{ primary: !caja.abierta }" type="button" @click="abrirDialogApertura" :disabled="caja.abierta">
        <i class="fa-solid fa-door-open"></i> Abrir Caja
      </button>
      <button class="accion-chip chip-btn" type="button" @click="abrirDialogTransaccion('Venta')" :disabled="!caja.abierta">
        <i class="fa-solid fa-circle-plus"></i> Registrar Ingreso
      </button>
      <button class="accion-chip chip-btn" type="button" @click="abrirDialogTransaccion('Gasto')" :disabled="!caja.abierta">
        <i class="fa-solid fa-circle-minus"></i> Registrar Egreso
      </button>
      <router-link to="/caja" class="accion-chip">
        <i class="fa-solid fa-vault"></i> Ir al Control de Caja
      </router-link>
      <router-link to="/caja/movimientos" class="accion-chip">
        <i class="fa-solid fa-arrows-rotate"></i> Movimientos
      </router-link>
      <router-link to="/caja/historial" class="accion-chip">
        <i class="fa-solid fa-clock-rotate-left"></i> Historial de Cierres
      </router-link>
    </div>

    <!-- Diálogo: apertura de caja con monto inicial -->
    <Dialog v-model:visible="dialogApertura" header="Abrir caja" :modal="true" :closable="true">
      <div class="field">
        <label for="monto-inicial">Monto inicial (S/.)</label>
        <InputNumber id="monto-inicial" v-model="montoInicial" mode="currency" currency="PEN" locale="es-PE" :min="0" :minFractionDigits="2" :maxFractionDigits="2" class="w-full" />
      </div>
      <template #footer>
        <Button label="Cancelar" severity="secondary" @click="dialogApertura = false" />
        <Button label="Abrir caja" :loading="guardando" @click="abrirCaja" />
      </template>
    </Dialog>

    <!-- Diálogo: ingreso / egreso -->
    <Dialog v-model:visible="dialogTransaccion" :header="nuevaTransaccion.tipo === 'Venta' ? 'Registrar ingreso' : 'Registrar egreso'" :modal="true" :closable="true">
      <div class="field">
        <label for="tipo-tx">Tipo</label>
        <Select id="tipo-tx" v-model="nuevaTransaccion.tipo" :options="tiposTransaccion" optionLabel="label" optionValue="value" class="w-full" />
      </div>
      <div class="field">
        <label for="monto-tx">Monto (S/.)</label>
        <InputNumber id="monto-tx" v-model="nuevaTransaccion.monto" mode="currency" currency="PEN" locale="es-PE" :min="0" :minFractionDigits="2" :maxFractionDigits="2" class="w-full" />
      </div>
      <div class="field">
        <label for="descripcion-tx">Descripción</label>
        <InputText id="descripcion-tx" v-model="nuevaTransaccion.descripcion" class="w-full" placeholder="Detalle del movimiento" />
      </div>
      <template #footer>
        <Button label="Cancelar" severity="secondary" @click="dialogTransaccion = false" />
        <Button label="Registrar" :loading="guardando" @click="registrarTransaccion" />
      </template>
    </Dialog>

    <!-- Rendimiento financiero -->
    <h2 class="seccion-title">Rendimiento financiero</h2>
    <div class="chart-card">
      <div class="filtros-bar">
        <div class="periodo-tabs">
          <button
            v-for="p in periodos"
            :key="p.key"
            class="filtro-btn"
            :class="{ active: periodo === p.key }"
            @click="cambiarPeriodo(p.key)"
          >
            {{ p.label }}
          </button>
        </div>
        <div class="serie-toggles">
          <button
            v-for="s in series"
            :key="s.key"
            class="serie-toggle"
            :class="{ active: seriesVisibles[s.key], [s.key]: true }"
            @click="toggleSerie(s.key)"
          >
            <span class="dot"></span>{{ s.label }}
          </button>
        </div>
      </div>
      <LineChartFinanciero :puntos="rendimientoPuntos" :series="seriesActivas" />
    </div>

    <div class="panel-columns">
      <!-- Movimientos recientes -->
      <div class="col-block">
        <h2 class="seccion-title">Movimientos recientes</h2>
        <div class="table-card">
          <DataTable :value="caja.transacciones || []" :paginator="true" :rows="6" dataKey="id_transaccion" responsiveLayout="scroll" class="p-datatable-sm">
            <Column field="fecha" header="Fecha" style="max-width: 9rem;">
              <template #body="slotProps">
                <span class="text-muted">{{ formatFecha(slotProps.data.fecha) }}</span>
              </template>
            </Column>
            <Column field="tipo" header="Tipo">
              <template #body="slotProps">
                <Tag :value="slotProps.data.tipo === 'Venta' ? 'Ingreso' : 'Egreso'"
                  :severity="slotProps.data.tipo === 'Venta' ? 'success' : 'danger'" />
              </template>
            </Column>
            <Column field="monto" header="Monto">
              <template #body="slotProps">
                <strong>S/. {{ formatMoney(slotProps.data.monto) }}</strong>
              </template>
            </Column>
            <Column field="descripcion" header="Descripción">
              <template #body="slotProps">
                <span class="text-muted">{{ slotProps.data.descripcion || '—' }}</span>
              </template>
            </Column>
            <template #empty>
              <div class="empty-state">
                <i class="fa-solid fa-receipt"></i>
                <span>Aún no hay movimientos registrados hoy.</span>
              </div>
            </template>
          </DataTable>
        </div>
      </div>

      <!-- Notificaciones -->
      <div class="col-block">
        <h2 class="seccion-title">Notificaciones</h2>
        <div class="notif-card">
          <div v-for="(n, i) in notificaciones" :key="i" class="notif-item" :class="'notif-' + n.tipo">
            <i :class="n.icono"></i>
            <div>
              <span class="notif-texto">{{ n.titulo }}</span>
            </div>
          </div>
          <div v-if="!notificaciones.length" class="notif-empty">
            <i class="fa-solid fa-circle-check"></i>
            <span>Todo en orden por ahora.</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'
import Dialog from 'primevue/dialog'
import InputNumber from 'primevue/inputnumber'
import InputText from 'primevue/inputtext'
import Select from 'primevue/select'
import Button from 'primevue/button'
import { useToast } from 'primevue/usetoast'
import LineChartFinanciero from '../components/charts/LineChartFinanciero.vue'
import api from '../config/axios'

const authStore = useAuthStore()
const toast = useToast()
const loading = ref(true)
const caja = ref({ abierta: false, ventas_dia: 0, gastos_dia: 0, neto_dia: 0, transacciones: [] })

const dialogApertura = ref(false)
const dialogTransaccion = ref(false)
const guardando = ref(false)
const montoInicial = ref(0)
const nuevaTransaccion = ref({ tipo: 'Venta', monto: 0, descripcion: '' })
const tiposTransaccion = [
  { label: 'Venta (Ingreso)', value: 'Venta' },
  { label: 'Gasto (Egreso)', value: 'Gasto' }
]

const periodos = [
  { key: 'dia', label: 'Día' },
  { key: 'semana', label: 'Semana' },
  { key: 'mes', label: 'Mes' },
  { key: 'anio', label: 'Año' }
]
const series = [
  { key: 'ingresos', label: 'Ingresos' },
  { key: 'egresos', label: 'Egresos' },
  { key: 'ganancia', label: 'Ganancia' }
]
const periodo = ref('dia')
const seriesVisibles = ref({ ingresos: true, egresos: true, ganancia: true })
const rendimientoPuntos = ref([])

const seriesActivas = computed(() => series.filter((s) => seriesVisibles.value[s.key]).map((s) => s.key))

const cambiarPeriodo = (key) => {
  periodo.value = key
  cargarRendimiento()
}

const toggleSerie = (key) => {
  seriesVisibles.value[key] = !seriesVisibles.value[key]
}

const cargarRendimiento = async () => {
  try {
    const res = await api.get(`/rendimiento?periodo=${periodo.value}`)
    if (res.data.success) rendimientoPuntos.value = res.data.data || []
  } catch (err) {
    console.error('Error cargando rendimiento:', err)
    rendimientoPuntos.value = []
  }
}

const nombre = computed(() => authStore.user?.nombre || 'Cajera')
const fechaHoy = computed(() => new Intl.DateTimeFormat('es-PE', {
  weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'
}).format(new Date()))

const notificaciones = computed(() => {
  const items = []
  if (!caja.value.abierta) {
    items.push({ tipo: 'error', icono: 'fa-solid fa-lock', titulo: 'La caja está pendiente de apertura.' })
  } else {
    items.push({ tipo: 'info', icono: 'fa-solid fa-lock-open', titulo: 'Tienes una caja abierta actualmente.' })
  }
  if ((caja.value.transacciones || []).length > 0) {
    items.push({ tipo: 'ok', icono: 'fa-solid fa-check', titulo: `Se registró(n) ${caja.value.transacciones.length} movimiento(s) hoy.` })
  }
  if (caja.value.abierta && (caja.value.transacciones || []).length === 0) {
    items.push({ tipo: 'warn', icono: 'fa-solid fa-circle-info', titulo: 'Aún no hay movimientos registrados hoy.' })
  }
  if (caja.value.abierta) {
    items.push({ tipo: 'info', icono: 'fa-solid fa-key', titulo: 'Recuerda realizar el cierre de caja al finalizar el turno.' })
  }
  return items
})

const formatMoney = (val) => Number(val || 0).toLocaleString('es-PE', { minimumFractionDigits: 2 })
const formatFecha = (val) => {
  if (!val) return '-'
  return String(val).slice(0, 16).replace('T', ' ').slice(11)
}

const cargar = async () => {
  loading.value = true
  try {
    const res = await api.get('/caja/actual')
    if (res.data.success) caja.value = res.data.data
  } catch (err) {
    console.error('Error cargando panel cajera:', err)
  } finally {
    loading.value = false
  }
}

const abrirDialogApertura = () => {
  montoInicial.value = 0
  dialogApertura.value = true
}

const abrirCaja = async () => {
  const monto = Number(montoInicial.value || 0)
  guardando.value = true
  try {
    const res = await api.post('/caja/abrir', { monto_inicial: monto })
    if (res.data.success) {
      toast.add({ severity: 'success', summary: 'Caja abierta', life: 2500 })
      dialogApertura.value = false
      await cargar()
      await cargarRendimiento()
    }
  } catch (err) {
    toast.add({ severity: 'error', summary: err.response?.data?.error || err.response?.data?.message || 'Error abriendo la caja', life: 3500 })
  } finally {
    guardando.value = false
  }
}

const abrirDialogTransaccion = (tipo) => {
  nuevaTransaccion.value = { tipo, monto: 0, descripcion: '' }
  dialogTransaccion.value = true
}

const registrarTransaccion = async () => {
  const monto = Number(nuevaTransaccion.value.monto)
  if (!monto || monto <= 0) {
    toast.add({ severity: 'warn', summary: 'Ingrese un monto mayor que cero', life: 3000 })
    return
  }
  if (!nuevaTransaccion.value.descripcion || !nuevaTransaccion.value.descripcion.trim()) {
    toast.add({ severity: 'warn', summary: 'Ingrese una descripción', life: 3000 })
    return
  }
  guardando.value = true
  try {
    const res = await api.post('/caja/transacciones', {
      tipo: nuevaTransaccion.value.tipo,
      monto,
      descripcion: nuevaTransaccion.value.descripcion.trim()
    })
    if (res.data.success) {
      toast.add({ severity: 'success', summary: 'Movimiento registrado', life: 2500 })
      dialogTransaccion.value = false
      nuevaTransaccion.value = { tipo: 'Venta', monto: 0, descripcion: '' }
      await cargar()
      await cargarRendimiento()
    }
  } catch (err) {
    toast.add({ severity: 'error', summary: err.response?.data?.error || 'Error registrando el movimiento', life: 3500 })
  } finally {
    guardando.value = false
  }
}

onMounted(() => {
  cargar()
  cargarRendimiento()
})
</script>

<style scoped>
.cajera-panel {
  padding: 0;
}

.page-hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.hero-badges {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.6rem;
  flex-wrap: wrap;
}

.rol-badge,
.fecha-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.72rem;
  font-weight: 600;
  padding: 0.3rem 0.7rem;
  border-radius: 999px;
}

.rol-badge { background: rgba(16, 185, 129, 0.1); color: #059669; }
.fecha-badge { background: var(--bg-secondary); color: var(--text-muted); }

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
  gap: 0.9rem;
  margin-top: 1rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 0.9rem;
  padding: 1rem 1.05rem;
  background: var(--bg-card);
  border-radius: 14px;
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-soft);
}

.stat-icon {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  flex-shrink: 0;
}

.stat-icon.positive { background: rgba(22, 163, 74, 0.1); color: var(--color-verde-fuerte); }
.stat-icon.negative { background: rgba(220, 38, 38, 0.1); color: var(--color-rojo); }
.stat-icon.blue { background: rgba(59, 130, 246, 0.1); color: #2563eb; }

.stat-content { display: flex; flex-direction: column; }
.stat-label { font-size: 0.72rem; color: var(--text-muted); margin-bottom: 0.1rem; }
.stat-value { font-size: 1.15rem; font-weight: 700; color: var(--text-main); }

.acciones-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  margin-top: 1rem;
}

.accion-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.55rem 1rem;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--text-main);
  text-decoration: none;
  transition: all 0.18s ease;
  box-shadow: var(--shadow-soft);
}

.accion-chip i {
  color: var(--btn-primary);
}

.accion-chip.primary {
  background: var(--btn-primary);
  color: white;
  border-color: var(--btn-primary);
}

.accion-chip.primary i {
  color: white;
}

.accion-chip:hover {
  border-color: var(--btn-primary);
  transform: translateY(-1px);
}

.chip-btn {
  font-family: inherit;
  cursor: pointer;
}

.chip-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
  transform: none;
}

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

.w-full {
  width: 100%;
}

:deep(.p-inputnumber) {
  width: 100%;
}

:deep(.p-select) {
  width: 100%;
}

.panel-columns {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 1.5rem;
  margin-top: 0.5rem;
}

.col-block {
  min-width: 0;
}

.table-card {
  margin-top: 1rem;
  background: var(--bg-card);
  border-radius: 14px;
  border: 1px solid var(--border-color);
  padding: 0.75rem;
  box-shadow: var(--shadow-soft);
}

.notif-card {
  margin-top: 1rem;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  padding: 0.75rem;
  box-shadow: var(--shadow-soft);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.notif-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.6rem 0.75rem;
  border-radius: 10px;
  font-size: 0.83rem;
  background: var(--bg-secondary);
}

.notif-item i {
  font-size: 0.95rem;
  flex-shrink: 0;
}

.notif-item.notif-ok { color: var(--color-verde-fuerte); background: rgba(22, 163, 74, 0.06); }
.notif-item.notif-warn { color: #b45309; background: rgba(245, 158, 11, 0.08); }
.notif-item.notif-error { color: var(--color-rojo); background: rgba(220, 38, 38, 0.06); }
.notif-item.notif-info { color: #2563eb; background: rgba(59, 130, 246, 0.08); }

.notif-texto {
  color: var(--text-main);
  font-weight: 500;
}

.notif-empty {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.6rem 0.75rem;
  color: var(--color-verde-fuerte);
  font-size: 0.85rem;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.3rem;
  padding: 1.25rem;
  color: var(--text-muted);
  font-size: 0.85rem;
}

.empty-state i {
  font-size: 1.3rem;
  opacity: 0.4;
}

.chart-card {
  margin-top: 1rem;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  padding: 1rem;
  box-shadow: var(--shadow-soft);
}

.filtros-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.periodo-tabs,
.serie-toggles {
  display: flex;
  gap: 0.4rem;
  flex-wrap: wrap;
}

.filtro-btn {
  padding: 0.35rem 0.8rem;
  border-radius: 999px;
  border: 1px solid var(--border-color);
  background: var(--bg-secondary);
  color: var(--text-muted);
  font-size: 0.76rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.filtro-btn:hover {
  border-color: var(--btn-primary);
  color: var(--btn-primary);
}

.filtro-btn.active {
  background: var(--btn-primary);
  border-color: var(--btn-primary);
  color: #fff;
}

.serie-toggle {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.35rem 0.8rem;
  border-radius: 999px;
  border: 1px solid var(--border-color);
  background: var(--bg-secondary);
  color: var(--text-muted);
  font-size: 0.76rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.serie-toggle.active {
  border-color: currentColor;
}

.serie-toggle .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
}

.serie-toggle.ingresos { color: #16a34a; }
.serie-toggle.egresos { color: #dc2626; }
.serie-toggle.ganancia { color: #ff7b00; }

@media (max-width: 900px) {
  .panel-columns {
    grid-template-columns: 1fr;
  }
  .page-hero { flex-direction: column; }
}
</style>