<template>
  <div class="panel-view">
    <div class="page-header">
      <div>
        <h1>Panel Administrativo</h1>
        <p>Gestion integral del restaurante</p>
      </div>
      <div class="header-actions">
        <button class="btn btn-outline" @click="loadStats">
          <i class="fa-solid fa-arrows-rotate"></i> Actualizar
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon positive">
          <i class="fa-solid fa-arrow-trend-up"></i>
        </div>
        <div class="stat-content">
          <span class="stat-label">Ventas del mes</span>
          <span class="stat-value">S/. {{ formatMoney(stats.ventas_mes) }}</span>
          <span class="stat-badge positive">Mes actual</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon negative">
          <i class="fa-solid fa-arrow-trend-down"></i>
        </div>
        <div class="stat-content">
          <span class="stat-label">Egresos del mes</span>
          <span class="stat-value">S/. {{ formatMoney(stats.egresos_mes) }}</span>
          <span class="stat-badge negative">Mes actual</span>
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

    <!-- Module Cards -->
    <div class="module-grid">
      <router-link to="/caja" class="module-card">
        <div class="module-icon caja">
          <i class="fa-solid fa-cash-register"></i>
        </div>
        <h3>Gestion de Caja</h3>
        <p>Registrar ventas, egresos y cierre diario</p>
      </router-link>
      <router-link to="/personal/empleados" class="module-card">
        <div class="module-icon personal">
          <i class="fa-solid fa-users-gear"></i>
        </div>
        <h3>Gestion del Personal</h3>
        <p>Empleados, pagos, solicitudes y turnos</p>
      </router-link>
      <router-link to="/inventario" class="module-card">
        <div class="module-icon inventario">
          <i class="fa-solid fa-boxes-stacked"></i>
        </div>
        <h3>Inventario e Inversion</h3>
        <p>Compras, equipamiento y costos</p>
      </router-link>
      <div class="module-card ia-card">
        <div class="module-icon ia">
          <i class="fa-solid fa-robot"></i>
        </div>
        <h3>IA Predictiva</h3>
        <p>Analisis y predicciones inteligentes</p>
        <span class="coming-soon">Proximamente</span>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="quick-actions">
      <h2>Acciones Rapidas</h2>
      <div class="actions-grid">
        <router-link to="/caja" class="action-btn primary">
          <i class="fa-solid fa-arrow-right"></i> Ir a Caja
        </router-link>
        <router-link to="/personal/pagos" class="action-btn secondary">
          <i class="fa-solid fa-money-bill-wave"></i> Registrar Pago
        </router-link>
        <router-link to="/inventario" class="action-btn secondary">
          <i class="fa-solid fa-boxes-stacked"></i> Ver Inventario
        </router-link>
        <router-link to="/personal/adelantos" class="action-btn secondary">
          <i class="fa-solid fa-file-invoice-dollar"></i> Adelantos
        </router-link>
      </div>
    </div>

    <!-- Loading overlay -->
    <div class="loading-overlay" v-if="loading">
      <i class="fa-solid fa-spinner fa-spin"></i>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../config/axios'

const loading = ref(true)
const stats = ref({
  ventas_mes: 0,
  egresos_mes: 0,
  neto_mes: 0,
  total_empleados: 0,
  productos_stock_bajo: 0
})

const formatMoney = (val) => {
  return Number(val || 0).toLocaleString('es-PE', { minimumFractionDigits: 2 })
}

const loadStats = async () => {
  loading.value = true
  try {
    const res = await api.get('/admin/panel-stats')
    if (res.data.success) {
      stats.value = res.data.data
    }
  } catch (err) {
    console.error('Error loading stats:', err)
  } finally {
    loading.value = false
  }
}

onMounted(loadStats)
</script>

<style scoped>
.panel-view {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-color);
}

.page-header h1 {
  margin: 0;
  font-size: 1.5rem;
  color: var(--text-main);
}

.page-header p {
  margin: 0.25rem 0 0;
  font-size: 0.85rem;
  color: var(--text-muted);
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

/* Stats */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
  padding: 1.5rem 2rem;
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

.stat-icon.positive {
  background: rgba(22, 163, 74, 0.1);
  color: var(--color-verde-fuerte);
}

.stat-icon.negative {
  background: rgba(220, 38, 38, 0.1);
  color: var(--color-rojo);
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-bottom: 0.15rem;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-main);
}

.stat-badge {
  font-size: 0.65rem;
  font-weight: 600;
  margin-top: 0.2rem;
}

.stat-badge.positive {
  color: var(--color-verde-fuerte);
}

.stat-badge.negative {
  color: var(--color-rojo);
}

/* Modules */
.module-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
  padding: 0 2rem 1.5rem;
}

.module-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 1.75rem 1.25rem;
  background: var(--bg-card);
  border-radius: 14px;
  border: 1px solid var(--border-color);
  text-decoration: none;
  color: inherit;
  transition: all 0.2s ease;
  cursor: pointer;
  box-shadow: var(--shadow-soft);
  position: relative;
}

.module-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.08);
  border-color: var(--btn-primary);
}

.module-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.3rem;
  margin-bottom: 0.85rem;
  color: white;
}

.module-icon.caja {
  background: linear-gradient(135deg, var(--btn-primary), var(--btn-gradient-end));
}

.module-icon.personal {
  background: linear-gradient(135deg, #3b82f6, #60a5fa);
}

.module-icon.inventario {
  background: linear-gradient(135deg, #8b5cf6, #a78bfa);
}

.module-icon.ia {
  background: linear-gradient(135deg, #10b981, #34d399);
}

.module-card h3 {
  margin: 0 0 0.35rem;
  font-size: 0.95rem;
  color: var(--text-main);
  font-weight: 600;
}

.module-card p {
  margin: 0;
  font-size: 0.78rem;
  color: var(--text-muted);
  line-height: 1.4;
}

.coming-soon {
  position: absolute;
  top: 10px;
  right: 10px;
  font-size: 0.6rem;
  font-weight: 600;
  background: rgba(16, 185, 129, 0.12);
  color: #10b981;
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
}

.ia-card {
  cursor: default;
  opacity: 0.7;
}

.ia-card:hover {
  transform: none;
}

/* Quick Actions */
.quick-actions {
  padding: 0 2rem 2rem;
}

.quick-actions h2 {
  margin: 0 0 1rem;
  font-size: 1rem;
  color: var(--text-main);
  font-weight: 600;
}

.actions-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1.25rem;
  border-radius: 10px;
  font-size: 0.85rem;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.18s ease;
  border: 1px solid transparent;
}

.action-btn.primary {
  background: var(--btn-gradient);
  color: white;
  box-shadow: 0 2px 8px rgba(255, 122, 0, 0.25);
}

.action-btn.primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 14px rgba(255, 122, 0, 0.35);
}

.action-btn.secondary {
  background: var(--bg-secondary);
  color: var(--text-main);
  border-color: var(--border-color);
}

.action-btn.secondary:hover {
  border-color: var(--btn-primary);
  color: var(--btn-primary);
}

/* Loading */
.loading-overlay {
  display: flex;
  justify-content: center;
  padding: 2rem;
  color: var(--btn-primary);
  font-size: 1.5rem;
}

/* Responsive */
@media (max-width: 900px) {
  .stats-grid, .module-grid {
    grid-template-columns: 1fr;
  }

  .page-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
}
</style>
