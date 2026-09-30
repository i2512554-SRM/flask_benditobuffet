<template>
  <div class="caja-resumen">
    <div class="page-hero">
      <div class="hero-left">
        <h1>Resumen de Caja</h1>
        <p>Estado actual y movimientos recientes de caja</p>
      </div>
      <button :disabled="$saving || loading" class="btn btn-outline" @click="cargar">
        <i class="fa-solid fa-arrows-rotate"></i> Actualizar
      </button>
    </div>

    <!-- Estado de caja -->
    <div class="estado-bar" :class="caja.abierta ? 'es-abierta' : 'es-cerrada'">
      <div class="estado-item estado-principal">
        <span class="estado-pill" :class="caja.abierta ? 'pill-abierta' : 'pill-cerrada'">
          <i :class="caja.abierta ? 'fa-solid fa-lock-open' : 'fa-solid fa-lock'"></i>
          {{ caja.abierta ? 'ABIERTA' : 'CERRADA' }}
        </span>
      </div>
      <template v-if="caja.abierta">
        <div class="estado-item">
          <span class="estado-label">Responsable</span>
          <span class="estado-valor">{{ caja.cierre?.responsable || '—' }}</span>
        </div>
        <div class="estado-item">
          <span class="estado-label">Hora de apertura</span>
          <span class="estado-valor">{{ horaApertura }}</span>
        </div>
        <div class="estado-item">
          <span class="estado-label">Turno actual</span>
          <span class="estado-valor">{{ caja.cierre?.turno || '—' }}</span>
        </div>
      </template>
      <div class="estado-item" v-else>
        <span class="estado-valor muted">No hay una caja abierta en este momento</span>
      </div>
    </div>

    <!-- Tarjetas resumen -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon blue"><i class="fa-solid fa-coins"></i></div>
        <div class="stat-content">
          <span class="stat-label">Monto inicial</span>
          <span class="stat-value">S/ {{ formatMoney(caja.cierre?.monto_inicial) }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon positive"><i class="fa-solid fa-receipt"></i></div>
        <div class="stat-content">
          <span class="stat-label">Ingresos desde apertura</span>
          <span class="stat-value">S/ {{ formatMoney(caja.ventas_apertura) }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green"><i class="fa-solid fa-arrow-trend-up"></i></div>
        <div class="stat-content">
          <span class="stat-label">Ingresos del día</span>
          <span class="stat-value">S/ {{ formatMoney(caja.ventas_dia) }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon negative"><i class="fa-solid fa-arrow-trend-down"></i></div>
        <div class="stat-content">
          <span class="stat-label">Egresos</span>
          <span class="stat-value">S/ {{ formatMoney(caja.gastos_dia) }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" :class="(caja.saldo_actual ?? 0) >= 0 ? 'positive' : 'negative'">
          <i class="fa-solid fa-scale-balanced"></i>
        </div>
        <div class="stat-content">
          <span class="stat-label">Saldo actual</span>
          <span class="stat-value">S/ {{ formatMoney(caja.saldo_actual) }}</span>
        </div>
      </div>
    </div>

    <div class="panel-columns">
      <!-- Últimos movimientos -->
      <div class="col-block">
        <h2 class="seccion-title">Últimos movimientos</h2>
        <div class="table-card">
          <DataTable :value="ultimos" :rows="6" dataKey="id_transaccion" responsiveLayout="scroll" class="p-datatable-sm">
            <Column field="tipo" header="Tipo" style="max-width: 6rem;">
              <template #body="slotProps">
                <Tag :value="tipoLabel(slotProps.data.tipo)"
                  :severity="slotProps.data.tipo === 'Gasto' ? 'danger' : 'success'" />
              </template>
            </Column>
            <Column field="descripcion" header="Concepto">
              <template #body="slotProps">
                <span class="text-muted">{{ concepto(slotProps.data) }}</span>
              </template>
            </Column>
            <Column field="responsable" header="Responsable">
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
            <Column field="hora" header="Hora" style="max-width: 6rem;">
              <template #body="slotProps">
                <span class="text-muted">{{ soloHora(slotProps.data.fecha) }}</span>
              </template>
            </Column>
            <template #empty><EstadoVacio v-if="loading" compacto titulo="Revolviendo los datos…" expresion="pensando" /><EstadoVacio v-else compacto titulo="Todavía no hay movimientos en esta apertura" mensaje="Registra la primera venta del turno." expresion="feliz" /></template>
          </DataTable>
          <div class="col-actions">
            <router-link :to="links.caja.movimientos" class="btn btn-outline btn-block">
              Ver movimientos
            </router-link>
          </div>
        </div>
      </div>

      <!-- Estado de caja -->
      <div class="col-block">
        <h2 class="seccion-title">Estado de Caja</h2>
        <div class="estado-card">
          <div v-if="caja.abierta" class="dc-rows">
            <div class="dc-row">
              <span class="dc-label">Responsable</span>
              <span class="dc-value">{{ caja.cierre?.responsable || '—' }}</span>
            </div>
            <div class="dc-row">
              <span class="dc-label">Apertura</span>
              <span class="dc-value">{{ horaApertura }}</span>
            </div>
            <div class="dc-row">
              <span class="dc-label">Monto inicial</span>
              <span class="dc-value">S/ {{ formatMoney(caja.cierre?.monto_inicial) }}</span>
            </div>
            <div class="dc-row">
              <span class="dc-label">Turno</span>
              <span class="dc-value">{{ caja.cierre?.turno || '—' }}</span>
            </div>
            <div class="dc-row">
              <span class="dc-label">Estado</span>
              <span class="dc-value">
                <span class="estado-pill pill-abierta"><i class="fa-solid fa-lock-open"></i> ABIERTA</span>
              </span>
            </div>
          </div>
          <div v-else class="dc-vacio">
            <i class="fa-solid fa-lock"></i>
            <span>Actualmente no existe una caja abierta.</span>
          </div>
          <router-link :to="links.caja.control" class="btn btn-primary btn-block">
            <i class="fa-solid fa-vault"></i> Ir a Control de Caja
          </router-link>
        </div>
      </div>
    </div>

    <!-- Acciones rápidas -->
    <h2 class="seccion-title">Acciones rápidas</h2>
    <div class="acciones-grid">
      <button class="accion-chip chip-btn" type="button" :disabled="$saving || (!caja.abierta)" @click="abrirRegistro('Venta')">
        <i class="fa-solid fa-circle-plus"></i> Registrar ingreso
      </button>
      <button class="accion-chip chip-btn" type="button" :disabled="$saving || (!caja.abierta)" @click="abrirRegistro('Gasto')">
        <i class="fa-solid fa-circle-minus"></i> Registrar egreso
      </button>
      <router-link :to="links.caja.movimientos" class="accion-chip">
        <i class="fa-solid fa-arrows-rotate"></i> Ver movimientos
      </router-link>
      <router-link :to="links.caja.historial" class="accion-chip">
        <i class="fa-solid fa-clock-rotate-left"></i> Ver cierres
      </router-link>
      <router-link :to="links.caja.reportes" class="accion-chip">
        <i class="fa-solid fa-chart-line"></i> Ver reportes
      </router-link>
    </div>

    <!-- Dialogo: registrar ingreso / egreso -->
    <CajaTransaccionDialog v-model:visible="dialogTransaccion" :tipo="tipoRegistro" @registrado="cargar" />

    <div class="loading-overlay" v-if="loading">
      <i class="fa-solid fa-spinner fa-spin"></i>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { soloHora } from '../../utils/format'
import { links } from '../../router/links'
import CajaTransaccionDialog from '../../components/caja/CajaTransaccionDialog.vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'
import { useToast } from 'primevue/usetoast'
import api from '../../config/axios'

const toast = useToast()
const loading = ref(true)
const caja = ref({ abierta: false, ventas_dia: 0, gastos_dia: 0, neto_dia: 0, ventas_apertura: 0, gastos_apertura: 0, saldo_actual: 0, cierre: null, transacciones: [] })

const tipoRegistro = ref('Venta')
const dialogTransaccion = ref(false)

const horaApertura = computed(() => (caja.value.abierta ? soloHora(caja.value.cierre?.fecha) : '—'))
const ultimos = computed(() => (caja.value.transacciones || []).slice(0, 6))

const formatMoney = (val) => Number(val || 0).toLocaleString('es-PE', { minimumFractionDigits: 2 })
const tipoLabel = (tipo) => (tipo === 'Gasto' ? 'Egreso' : tipo === 'Venta' ? 'Ingreso' : tipo || '—')
const concepto = (t) => t.descripcion || (t.tipo === 'Gasto' ? 'Egreso registrado' : 'Ingreso registrado')

let timer = null

const cargar = async () => {
  loading.value = true
  try {
    const res = await api.get('/caja/actual')
    if (res.data?.success) caja.value = res.data.data
  } catch (err) {
    console.error('Error cargando resumen de caja:', err)
  } finally {
    loading.value = false
  }
}

const abrirRegistro = (tipo) => {
  if (!caja.value.abierta) {
    toast.add({ severity: 'warn', summary: 'Abre la caja antes de registrar movimientos', life: 3000 })
    return
  }
  tipoRegistro.value = tipo
  dialogTransaccion.value = true
}

onMounted(() => {
  cargar()
  timer = setInterval(cargar, 30000)
})

onUnmounted(() => clearInterval(timer))
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

/* Barra de estado */
.estado-bar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 1.4rem;
  margin-top: 1rem;
  padding: 0.9rem 1rem;
  border-radius: 14px;
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-soft);
}

.estado-bar.es-abierta { background: rgba(22, 163, 74, 0.06); }
.estado-bar.es-cerrada { background: var(--bg-secondary); }

.estado-item {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.estado-label {
  font-size: 0.68rem;
  font-weight: 600;
  color: var(--text-muted);
  letter-spacing: 0.02em;
}

.estado-valor {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-main);
}

.estado-valor.muted { font-size: 0.8rem; color: var(--text-muted); }

.estado-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
}

.pill-abierta { background: rgba(22, 163, 74, 0.14); color: #16a34a; }
.pill-cerrada { background: rgba(220, 38, 38, 0.1); color: #dc2626; }

/* Tarjetas */
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
.stat-icon.green { background: rgba(22, 163, 74, 0.1); color: #16a34a; }
.stat-icon.negative { background: rgba(220, 38, 38, 0.1); color: var(--color-rojo); }
.stat-icon.blue { background: rgba(59, 130, 246, 0.1); color: #2563eb; }

.stat-content { display: flex; flex-direction: column; }
.stat-label { font-size: 0.72rem; color: var(--text-muted); margin-bottom: 0.1rem; }
.stat-value { font-size: 1.15rem; font-weight: 700; color: var(--text-main); }

/* Dos columnas */
.panel-columns {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 1.5rem;
  margin-top: 0.25rem;
}

.col-block { min-width: 0; }

.seccion-title {
  margin-top: 1.5rem;
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

.col-actions {
  margin-top: 0.75rem;
}

.btn-block {
  display: flex;
  justify-content: center;
  width: 100%;
}

.estado-card {
  margin-top: 1rem;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  padding: 1rem;
  box-shadow: var(--shadow-soft);
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.dc-rows {
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
}

.dc-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.6rem 0.75rem;
  background: var(--bg-secondary);
  border-radius: 10px;
}

.dc-label {
  font-size: 0.78rem;
  color: var(--text-muted);
  font-weight: 600;
}

.dc-value {
  font-size: 0.92rem;
  font-weight: 600;
  color: var(--text-main);
}

.dc-vacio {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1.5rem 0.5rem;
  color: var(--text-muted);
  font-size: 0.85rem;
  text-align: center;
}

.dc-vacio i { font-size: 1.4rem; opacity: 0.4; }

/* Acciones rápidas */
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

.accion-chip i { color: var(--btn-primary); }

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

/* Formulario */
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
  padding: 1.25rem;
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

@media (max-width: 900px) {
  .panel-columns {
    grid-template-columns: 1fr;
  }
  .page-hero { flex-direction: column; }
}
</style>
