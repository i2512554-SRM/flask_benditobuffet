<template>
  <div>
    <div class="page-hero">
      <router-link to="/caja" class="btn btn-outline btn-back">
        <i class="fa-solid fa-arrow-left"></i> Volver a Caja
      </router-link>
      <h1>Reportes Financieros</h1>
      <p>Resumen de ventas, egresos y ganancia neta del mes</p>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon positive"><i class="fa-solid fa-arrow-trend-up"></i></div>
        <div class="stat-content">
          <span class="stat-label">Ventas del mes</span>
          <span class="stat-value">S/. {{ formatMoney(stats.ventas_mes) }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon negative"><i class="fa-solid fa-arrow-trend-down"></i></div>
        <div class="stat-content">
          <span class="stat-label">Egresos del mes</span>
          <span class="stat-value">S/. {{ formatMoney(stats.egresos_mes) }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" :class="stats.neto_mes >= 0 ? 'positive' : 'negative'">
          <i class="fa-solid fa-scale-balanced"></i>
        </div>
        <div class="stat-content">
          <span class="stat-label">Ganancia neta</span>
          <span class="stat-value">S/. {{ formatMoney(stats.neto_mes) }}</span>
          <span class="stat-badge" :class="stats.neto_mes >= 0 ? 'positive' : 'negative'">
            {{ stats.neto_mes >= 0 ? 'Mes actual' : 'Perdida' }}
          </span>
        </div>
      </div>
    </div>

    <div class="card-section">
      <h2 class="seccion-title">Cierres de Caja</h2>
      <DataTable v-if="cierres.length" :value="cierres" stripedRows paginator :rows="10"
        :rowsPerPageOptions="[10, 25, 50]" class="p-datatable-sm">
        <Column field="fecha" header="Fecha" sortable></Column>
        <Column field="fecha_cierre" header="Cierre"></Column>
        <Column header="Ventas" sortable>
          <template #body="{ data }">S/. {{ formatMoney(data.total_ventas) }}</template>
        </Column>
        <Column header="Gastos" sortable>
          <template #body="{ data }">S/. {{ formatMoney(data.total_gastos) }}</template>
        </Column>
        <Column header="Neto" sortable>
          <template #body="{ data }">
            <span :class="data.neto >= 0 ? 'text-positive' : 'text-negative'">
              S/. {{ formatMoney(data.neto) }}
            </span>
          </template>
        </Column>
        <Column field="estado" header="Estado" sortable>
          <template #body="{ data }">
            <Tag :value="data.estado" :severity="data.estado === 'cerrada' ? 'success' : 'warning'" />
          </template>
        </Column>
      </DataTable>
      <div v-else class="empty-state">
        <i class="fa-solid fa-chart-line"></i>
        <p>Aún no hay cierres de caja registrados.</p>
      </div>
    </div>

    <div class="loading-overlay" v-if="loading">
      <i class="fa-solid fa-spinner fa-spin"></i>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'
import api from '../config/axios'

const loading = ref(true)
const stats = ref({ ventas_mes: 0, egresos_mes: 0, neto_mes: 0 })
const cierres = ref([])

const formatMoney = (val) => Number(val || 0).toLocaleString('es-PE', { minimumFractionDigits: 2 })

const formatFecha = (val) => {
  if (!val) return '-'
  return val
}

const load = async () => {
  loading.value = true
  try {
    const [statsRes, histRes] = await Promise.all([
      api.get('/admin/panel-stats'),
      api.get('/caja/historial')
    ])
    if (statsRes.data.success) stats.value = statsRes.data.data
    if (histRes.data.success) {
      cierres.value = (histRes.data.data || []).map((c) => ({
        ...c,
        fecha: formatFecha(c.fecha),
        fecha_cierre: formatFecha(c.fecha_cierre)
      }))
    }
  } catch (err) {
    console.error('Error loading reportes:', err)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
  margin-top: 1.5rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem;
  background: var(--bg-card);
  border-radius: 14px;
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-soft);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  flex-shrink: 0;
}

.stat-icon.positive { background: rgba(22, 163, 74, 0.1); color: var(--color-verde-fuerte); }
.stat-icon.negative { background: rgba(220, 38, 38, 0.1); color: var(--color-rojo); }

.stat-content { display: flex; flex-direction: column; }
.stat-label { font-size: 0.75rem; color: var(--text-muted); margin-bottom: 0.15rem; }
.stat-value { font-size: 1.25rem; font-weight: 700; color: var(--text-main); }
.stat-badge { font-size: 0.65rem; font-weight: 600; margin-top: 0.2rem; }
.stat-badge.positive { color: var(--color-verde-fuerte); }
.stat-badge.negative { color: var(--color-rojo); }

.card-section {
  margin-top: 1.5rem;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  padding: 1.25rem;
  box-shadow: var(--shadow-soft);
}

.card-section .seccion-title { margin: 0 0 1rem; }

.text-positive { color: var(--color-verde-fuerte); font-weight: 600; }
.text-negative { color: var(--color-rojo); font-weight: 600; }

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 2rem;
  color: var(--text-muted);
  font-size: 0.85rem;
}

.empty-state i { font-size: 1.6rem; opacity: 0.4; }
.empty-state p { margin: 0; }

.loading-overlay {
  display: flex;
  justify-content: center;
  padding: 2rem;
  color: var(--btn-primary);
  font-size: 1.5rem;
}
</style>