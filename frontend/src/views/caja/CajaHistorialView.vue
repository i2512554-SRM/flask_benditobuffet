<template>
  <div class="caja-historial">
    <div class="page-hero">
      <div class="hero-left">
        <h1>Historial de Cierres</h1>
        <p>Cierres anteriores de caja con sus montos, responsables y horarios</p>
      </div>
      <button :disabled="$saving || loading" class="btn btn-outline" @click="cargar">
        <i class="fa-solid fa-arrows-rotate"></i> Actualizar
      </button>
    </div>

    <div class="stats-grid" v-if="cierres.length">
      <div class="stat-card">
        <div class="stat-icon purple"><i class="fa-solid fa-clock-rotate-left"></i></div>
        <div class="stat-content">
          <span class="stat-label">Total cierres</span>
          <span class="stat-value">{{ cierres.length }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon positive"><i class="fa-solid fa-arrow-trend-up"></i></div>
        <div class="stat-content">
          <span class="stat-label">Ingresos acumulados</span>
          <span class="stat-value">S/. {{ formatMoney(totalIngresos) }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon negative"><i class="fa-solid fa-arrow-trend-down"></i></div>
        <div class="stat-content">
          <span class="stat-label">Egresos acumulados</span>
          <span class="stat-value">S/. {{ formatMoney(totalEgresos) }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" :class="totalNeto >= 0 ? 'positive' : 'negative'">
          <i class="fa-solid fa-scale-balanced"></i>
        </div>
        <div class="stat-content">
          <span class="stat-label">Saldo acumulado</span>
          <span class="stat-value">S/. {{ formatMoney(totalNeto) }}</span>
        </div>
      </div>
    </div>

    <div class="table-card">
      <DataTable :value="cierres" :paginator="true" :rows="10" dataKey="id_cierre" responsiveLayout="scroll" class="p-datatable-sm">
        <Column field="fecha" header="Fecha">
          <template #body="slotProps">
            <span class="text-muted">{{ soloFecha(slotProps.data.fecha) }}</span>
          </template>
        </Column>
        <Column field="responsable" header="Responsable">
          <template #body="slotProps">
            <span class="text-muted">{{ slotProps.data.responsable || '—' }}</span>
          </template>
        </Column>
        <Column field="monto_inicial" header="Monto inicial">
          <template #body="slotProps">
            <strong>S/. {{ formatMoney(slotProps.data.monto_inicial) }}</strong>
          </template>
        </Column>
        <Column field="total_ventas" header="Ingresos">
          <template #body="slotProps">
            <strong>S/. {{ formatMoney(slotProps.data.total_ventas) }}</strong>
          </template>
        </Column>
        <Column field="total_gastos" header="Egresos">
          <template #body="slotProps">
            <strong>S/. {{ formatMoney(slotProps.data.total_gastos) }}</strong>
          </template>
        </Column>
        <Column field="saldo_final" header="Saldo final">
          <template #body="slotProps">
            <span :class="(slotProps.data.saldo_final ?? 0) >= 0 ? 'neto-pos' : 'neto-neg'">S/. {{ formatMoney(slotProps.data.saldo_final) }}</span>
          </template>
        </Column>
        <Column field="hora_apertura" header="Hora apertura" style="max-width: 7rem;">
          <template #body="slotProps">
            <span class="text-muted">{{ soloHora(slotProps.data.fecha) }}</span>
          </template>
        </Column>
        <Column field="hora_cierre" header="Hora cierre" style="max-width: 7rem;">
          <template #body="slotProps">
            <span class="text-muted">{{ soloHora(slotProps.data.fecha_cierre) }}</span>
          </template>
        </Column>
        <Column header="Acciones" style="max-width: 9rem;">
          <template #body="slotProps">
            <button :disabled="$saving" class="btn btn-outline btn-sm" @click="verDetalle(slotProps.data)">
              <i class="fa-solid fa-eye"></i> Ver detalle
            </button>
          </template>
        </Column>
        <template #empty><EstadoVacio v-if="loading" compacto titulo="Revolviendo los datos…" expresion="pensando" /><EstadoVacio v-else compacto titulo="Aún no hay cierres registrados" mensaje="Aparecerán aquí cuando se cierre la caja." expresion="feliz" /></template>
      </DataTable>
    </div>

    <!-- Dialogo: detalle del cierre -->
    <Dialog v-model:visible="dialogDetalle" :header="'Detalle del cierre — ' + (detalle?.responsable || '')" :modal="true" :style="{ width: '480px' }">
      <div v-if="detalle" class="detalle-caja">
        <div class="dc-row">
          <span class="dc-label">Estado</span>
          <span class="dc-value">{{ estadoLabel(detalle.estado) }}</span>
        </div>
        <div class="dc-row">
          <span class="dc-label">Responsable</span>
          <span class="dc-value">{{ detalle.responsable || '—' }}</span>
        </div>
        <div class="dc-row">
          <span class="dc-label">Fecha</span>
          <span class="dc-value">{{ soloFecha(detalle.fecha) }}</span>
        </div>
        <div class="dc-row">
          <span class="dc-label">Hora de apertura</span>
          <span class="dc-value">{{ soloHora(detalle.fecha) }}</span>
        </div>
        <div class="dc-row">
          <span class="dc-label">Hora de cierre</span>
          <span class="dc-value">{{ soloHora(detalle.fecha_cierre) }}</span>
        </div>
        <div class="dc-row">
          <span class="dc-label">Monto inicial</span>
          <span class="dc-value">S/. {{ fmtMoney(detalle.monto_inicial) }}</span>
        </div>
        <div class="dc-row">
          <span class="dc-label">Ingresos</span>
          <span class="dc-value pos">S/. {{ fmtMoney(detalle.total_ventas) }}</span>
        </div>
        <div class="dc-row">
          <span class="dc-label">Egresos</span>
          <span class="dc-value neg">S/. {{ fmtMoney(detalle.total_gastos) }}</span>
        </div>
        <div class="dc-row">
          <span class="dc-label">Efectivo contado</span>
          <span class="dc-value">{{ detalle.efectivo_contado != null ? 'S/. ' + fmtMoney(detalle.efectivo_contado) : '—' }}</span>
        </div>
        <div class="dc-row dc-total" :class="(detalle.saldo_final ?? 0) >= 0 ? 'pos' : 'neg'">
          <span class="dc-label">Saldo final</span>
          <span class="dc-value">S/. {{ fmtMoney(detalle.saldo_final) }}</span>
        </div>
      </div>
      <template #footer>
        <Button :disabled="$saving" label="Cerrar" severity="secondary" @click="dialogDetalle = false" />
      </template>
    </Dialog>

    <div class="loading-overlay" v-if="loading">
      <i class="fa-solid fa-spinner fa-spin"></i>
    </div>
  </div>
</template>

<script setup>
import { soloFecha, soloHora } from '../../utils/format'
import { ref, computed, onMounted } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import api from '../../config/axios'

const loading = ref(true)
const cierres = ref([])
const dialogDetalle = ref(false)
const detalle = ref(null)

const totalIngresos = computed(() => cierres.value.reduce((acc, c) => acc + Number(c.total_ventas || 0), 0))
const totalEgresos = computed(() => cierres.value.reduce((acc, c) => acc + Number(c.total_gastos || 0), 0))
const totalNeto = computed(() => totalIngresos.value - totalEgresos.value)

const formatMoney = (val) => Number(val || 0).toLocaleString('es-PE', { minimumFractionDigits: 2 })
const fmtMoney = formatMoney
const estadoLabel = (e) => (e === 'abierta' ? 'Abierta' : e === 'cerrada' ? 'Cerrada' : e || '—')

const verDetalle = (cierre) => {
  detalle.value = cierre
  dialogDetalle.value = true
}

const cargar = async () => {
  loading.value = true
  try {
    const res = await api.get('/caja/historial')
    if (res.data?.success) cierres.value = res.data.data
  } catch (err) {
    console.error('Error cargando historial de cierres:', err)
  } finally {
    loading.value = false
  }
}

onMounted(cargar)
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
.stat-icon.purple { background: rgba(139, 92, 246, 0.1); color: #8b5cf6; }

.stat-content { display: flex; flex-direction: column; }
.stat-label { font-size: 0.72rem; color: var(--text-muted); margin-bottom: 0.1rem; }
.stat-value { font-size: 1.15rem; font-weight: 700; color: var(--text-main); }

.table-card {
  margin-top: 1rem;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  padding: 0.75rem;
  box-shadow: var(--shadow-soft);
}

.neto-pos { color: var(--color-verde-fuerte); font-weight: 600; }
.neto-neg { color: var(--color-rojo); font-weight: 600; }

.btn-sm {
  padding: 0.4rem 0.7rem;
  font-size: 0.76rem;
}

.detalle-caja {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
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

.dc-value.pos { color: var(--color-verde-fuerte); }
.dc-value.neg { color: var(--color-rojo); }

.dc-total { margin-top: 0.25rem; }
.dc-total.pos { background: rgba(22, 163, 74, 0.1); }
.dc-total.neg { background: rgba(220, 38, 38, 0.08); }
.dc-total.pos .dc-value { color: var(--color-verde-fuerte); }
.dc-total.neg .dc-value { color: var(--color-rojo); }

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
}
</style>