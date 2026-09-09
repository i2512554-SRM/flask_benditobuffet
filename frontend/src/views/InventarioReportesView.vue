<template>
  <div>
    <div class="page-hero">
      <router-link to="/inventario" class="btn btn-outline btn-back">
        <i class="fa-solid fa-arrow-left"></i> Volver a Inventario
      </router-link>
      <h1>Reportes de Inventario</h1>
      <p>Resumen del valor del almacén y tendencias del mes</p>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon ic-purple-icon"><i class="fa-solid fa-boxes-stacked"></i></div>
        <div class="stat-content">
          <span class="stat-label">Valor total del inventario</span>
          <span class="stat-value">S/. {{ formatMoney(resumen.valor_total) }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon positive"><i class="fa-solid fa-cubes"></i></div>
        <div class="stat-content">
          <span class="stat-label">Artículos registrados</span>
          <span class="stat-value">{{ resumen.articulos_registrados }}</span>
          <span class="stat-badge positive">+{{ resumen.productos_mes }} este mes</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon ic-cyan-icon"><i class="fa-solid fa-chart-pie"></i></div>
        <div class="stat-content">
          <span class="stat-label">Inversiones del mes</span>
          <span class="stat-value">S/. {{ formatMoney(resumen.inversiones_mes) }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon ic-amber-icon"><i class="fa-solid fa-gears"></i></div>
        <div class="stat-content">
          <span class="stat-label">Equipamiento</span>
          <span class="stat-value">S/. {{ formatMoney(resumen.equipamiento_valor) }}</span>
        </div>
      </div>
    </div>

    <div class="loading-overlay" v-if="loading">
      <i class="fa-solid fa-spinner fa-spin"></i>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../config/axios'

const loading = ref(true)
const resumen = ref({
  valor_total: 0,
  inversiones_mes: 0,
  articulos_registrados: 0,
  productos_mes: 0,
  equipamiento_valor: 0
})

const formatMoney = (val) => Number(val || 0).toLocaleString('es-PE', { minimumFractionDigits: 2 })

const load = async () => {
  loading.value = true
  try {
    const res = await api.get('/inventario/resumen')
    if (res.data.success) resumen.value = res.data.data
  } catch (err) {
    console.error('Error loading reportes inventario:', err)
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
.stat-icon.ic-purple-icon { background: rgba(139, 92, 246, 0.1); color: #8b5cf6; }
.stat-icon.ic-cyan-icon { background: rgba(8, 145, 178, 0.1); color: #0891b2; }
.stat-icon.ic-amber-icon { background: rgba(245, 158, 11, 0.12); color: #f59e0b; }

.stat-content { display: flex; flex-direction: column; }
.stat-label { font-size: 0.75rem; color: var(--text-muted); margin-bottom: 0.15rem; }
.stat-value { font-size: 1.25rem; font-weight: 700; color: var(--text-main); }
.stat-badge { font-size: 0.65rem; font-weight: 600; margin-top: 0.2rem; }
.stat-badge.positive { color: var(--color-verde-fuerte); }

.loading-overlay {
  display: flex;
  justify-content: center;
  padding: 2rem;
  color: var(--btn-primary);
  font-size: 1.5rem;
}
</style>