<template>
  <div class="caja-historial">
    <div class="page-hero">
      <div class="hero-left">
        <h1>Historial de Cierres</h1>
        <p>Cierres anteriores de caja con sus montos y saldo</p>
      </div>
      <button :disabled="$saving" class="btn btn-outline" @click="cargar">
        <i class="fa-solid fa-arrows-rotate"></i> Actualizar
      </button>
    </div>

    <div class="stats-grid" v-if="cierres.length">
      <div class="stat-card">
        <div class="stat-icon purple"><i class="fa-solid fa-arrow-trend-up"></i></div>
        <div class="stat-content">
          <span class="stat-label">Total cierres</span>
          <span class="stat-value">{{ cierres.length }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon positive"><i class="fa-solid fa-coins"></i></div>
        <div class="stat-content">
          <span class="stat-label">Ventas acumuladas</span>
          <span class="stat-value">S/. {{ formatMoney(totalVentas) }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon negative"><i class="fa-solid fa-cart-flatbed"></i></div>
        <div class="stat-content">
          <span class="stat-label">Gastos acumulados</span>
          <span class="stat-value">S/. {{ formatMoney(totalGastos) }}</span>
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
            <span class="text-muted">{{ formatFecha(slotProps.data.fecha) }}</span>
          </template>
        </Column>
        <Column field="estado" header="Estado">
          <template #body="slotProps">
            <Tag :value="slotProps.data.estado" :severity="slotProps.data.estado === 'cerrada' ? 'secondary' : 'warning'" />
          </template>
        </Column>
        <Column field="monto_inicial" header="Monto inicial">
          <template #body="slotProps">
            <strong>S/. {{ formatMoney(slotProps.data.monto_inicial) }}</strong>
          </template>
        </Column>
        <Column field="total_ventas" header="Ventas">
          <template #body="slotProps">
            <strong>S/. {{ formatMoney(slotProps.data.total_ventas) }}</strong>
          </template>
        </Column>
        <Column field="total_gastos" header="Gastos">
          <template #body="slotProps">
            <strong>S/. {{ formatMoney(slotProps.data.total_gastos) }}</strong>
          </template>
        </Column>
        <Column field="neto" header="Saldo">
          <template #body="slotProps">
            <span :class="(slotProps.data.neto ?? 0) >= 0 ? 'neto-pos' : 'neto-neg'">S/. {{ formatMoney(slotProps.data.neto) }}</span>
          </template>
        </Column>
        <Column field="fecha_cierre" header="Cerrado">
          <template #body="slotProps">
            <span class="text-muted">{{ formatFecha(slotProps.data.fecha_cierre) }}</span>
          </template>
        </Column>
        <template #empty>
          <div class="empty-state">
            <i class="fa-solid fa-clock-rotate-left"></i>
            <span>Aún no hay cierres registrados.</span>
          </div>
        </template>
      </DataTable>
    </div>

    <div class="loading-overlay" v-if="loading">
      <i class="fa-solid fa-spinner fa-spin"></i>
    </div>
  </div>
</template>

<script setup>
import { formatFecha as fechaLegible } from '../utils/format'
import { ref, computed, onMounted } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'
import api from '../config/axios'

const loading = ref(true)
const cierres = ref([])

const totalVentas = computed(() => cierres.value.reduce((acc, c) => acc + Number(c.total_ventas || 0), 0))
const totalGastos = computed(() => cierres.value.reduce((acc, c) => acc + Number(c.total_gastos || 0), 0))
const totalNeto = computed(() => totalVentas.value - totalGastos.value)

const formatMoney = (val) => Number(val || 0).toLocaleString('es-PE', { minimumFractionDigits: 2 })
const formatFecha = fechaLegible

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