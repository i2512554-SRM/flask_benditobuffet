<template>
  <div class="cocina-view">
    <div class="page-header">
      <div>
        <h1>¡Hola, {{ data.usuario?.nombres || 'Cocinero' }}! 👋</h1>
        <p>Tu cocina a un vistazo: stock y solicitudes</p>
        <div class="hero-badges">
          <span class="rol-badge-cocina"><i class="fa-solid fa-utensils"></i> Cocinero</span>
          <span class="fecha-badge"><i class="fa-regular fa-calendar"></i> {{ data.fecha || 'Cargando...' }}</span>
        </div>
      </div>
      <div class="header-actions">
        <router-link to="/cocinero/solicitudes" class="btn btn-outline">
          <i class="fa-solid fa-plus"></i> Solicitar insumo
        </router-link>
        <button class="btn btn-outline" @click="load">
          <i class="fa-solid fa-arrows-rotate"></i> Actualizar
        </button>
      </div>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon tone-green">
          <i class="fa-solid fa-box"></i>
        </div>
        <div class="stat-content">
          <span class="stat-label">Insumos disponibles</span>
          <span class="stat-value">{{ resumen.disponibles }}</span>
          <span class="stat-badge tone-green">de {{ resumen.total_insumos }} en total</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon tone-amber">
          <i class="fa-solid fa-fill-drip"></i>
        </div>
        <div class="stat-content">
          <span class="stat-label">Stock bajo</span>
          <span class="stat-value">{{ resumen.stock_bajo }}</span>
          <span class="stat-badge tone-amber">requieren reposición</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon tone-red">
          <i class="fa-solid fa-triangle-exclamation"></i>
        </div>
        <div class="stat-content">
          <span class="stat-label">Agotados</span>
          <span class="stat-value">{{ resumen.agotados }}</span>
          <span class="stat-badge tone-red">urgente</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon tone-blue">
          <i class="fa-solid fa-list-check"></i>
        </div>
        <div class="stat-content">
          <span class="stat-label">Solicitudes pendientes</span>
          <span class="stat-value">{{ resumen.solicitudes_pendientes }}</span>
          <span class="stat-badge tone-blue">en espera</span>
        </div>
      </div>
    </div>

    <div class="section-block">
      <h2>Acciones rápidas</h2>
      <div class="acciones-grid">
        <router-link to="/cocinero/inventario" class="accion-chip">
          <i class="fa-solid fa-carrot"></i> Ver Insumos
        </router-link>
        <router-link to="/cocinero/alertas" class="accion-chip">
          <i class="fa-solid fa-chart-line"></i> Consultar Stock
        </router-link>
        <router-link to="/cocinero/inventario" class="accion-chip">
          <i class="fa-solid fa-burger"></i> Ver Productos
        </router-link>
        <router-link to="/cocinero/solicitudes" class="accion-chip">
          <i class="fa-solid fa-plus"></i> Realizar Solicitud
        </router-link>
      </div>
    </div>

    <div class="section-block">
      <h2>Notificaciones</h2>
      <div class="notif-card">
        <div v-if="resumen.agotados > 0" class="notif-item notif-error">
          <i class="fa-solid fa-triangle-exclamation"></i>
          <span>Hay {{ resumen.agotados }} producto(s) agotado(s) en almacén.</span>
        </div>
        <div v-if="resumen.stock_bajo > 0" class="notif-item notif-warn">
          <i class="fa-solid fa-fill-drip"></i>
          <span>{{ resumen.stock_bajo }} producto(s) tiene(n) stock bajo.</span>
        </div>
        <div v-if="resumen.solicitudes_pendientes > 0" class="notif-item notif-info">
          <i class="fa-solid fa-clock"></i>
          <span>Tienes {{ resumen.solicitudes_pendientes }} solicitud(es) pendiente(s).</span>
        </div>
        <div v-if="resumen.agotados === 0 && resumen.stock_bajo === 0 && resumen.solicitudes_pendientes === 0" class="notif-empty">
          <i class="fa-solid fa-circle-check"></i>
          <span>Todo en orden. Sin alertas por ahora.</span>
        </div>
      </div>
    </div>

    <div class="module-grid">
      <router-link to="/cocinero/inventario" class="module-card">
        <div class="module-icon tone-green"><i class="fa-solid fa-carrot"></i></div>
        <h3>Insumos</h3>
        <p>Consultar ingredientes disponibles</p>
      </router-link>
      <router-link to="/cocinero/inventario" class="module-card">
        <div class="module-icon tone-blue"><i class="fa-solid fa-burger"></i></div>
        <h3>Productos</h3>
        <p>Consultar productos registrados</p>
      </router-link>
      <router-link to="/cocinero/alertas" class="module-card">
        <div class="module-icon tone-red"><i class="fa-solid fa-chart-line"></i></div>
        <h3>Stock</h3>
        <p>Visualizar disponibilidad y faltantes</p>
      </router-link>
      <router-link to="/cocinero/solicitudes" class="module-card">
        <div class="module-icon tone-amber"><i class="fa-solid fa-clipboard-list"></i></div>
        <h3>Solicitudes</h3>
        <p>Solicitar insumos y ver su estado</p>
      </router-link>
    </div>

    <div class="section-block" v-if="data.pendientes?.length">
      <h2>Últimas solicitudes pendientes</h2>
      <div class="table-card">
        <DataTable :value="data.pendientes" responsiveLayout="scroll">
          <Column field="producto" header="Producto" sortable></Column>
          <Column field="cantidad" header="Cantidad"></Column>
          <Column field="fecha" header="Fecha"></Column>
          <Column header="Estado">
            <template #body="slotProps">
              <Tag value="Pendiente" severity="warning" />
            </template>
          </Column>
        </DataTable>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../config/axios'

const loading = ref(true)
const data = ref({})
const resumen = computed(() => data.value.resumen || { disponibles: 0, stock_bajo: 0, agotados: 0, solicitudes_pendientes: 0, total_insumos: 0 })

const load = async () => {
  loading.value = true
  try {
    const res = await api.get('/cocina/dashboard')
    if (res.data.success) data.value = res.data.data
  } catch (e) {
    console.error('Error cargando dashboard de cocina:', e)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.hero-badges {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.6rem;
  flex-wrap: wrap;
}

.rol-badge-cocina,
.fecha-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.72rem;
  font-weight: 600;
  padding: 0.3rem 0.7rem;
  border-radius: 999px;
}

.rol-badge-cocina {
  background: rgba(255, 122, 0, 0.1);
  color: var(--btn-primary);
}

.fecha-badge {
  background: var(--bg-secondary);
  color: var(--text-muted);
}

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
  padding: 0.6rem 1.05rem;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 999px;
  font-size: 0.82rem;
  font-weight: 500;
  color: var(--text-main);
  text-decoration: none;
  transition: all 0.18s ease;
  box-shadow: var(--shadow-soft);
}

.accion-chip i {
  color: var(--btn-primary);
}

.accion-chip:hover {
  border-color: var(--btn-primary);
  color: var(--btn-primary);
  transform: translateY(-1px);
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
}

.notif-item i {
  font-size: 0.95rem;
  flex-shrink: 0;
}

.notif-item.notif-warn { color: #b45309; background: rgba(245, 158, 11, 0.08); }
.notif-item.notif-error { color: var(--color-rojo); background: rgba(220, 38, 38, 0.06); }
.notif-item.notif-info { color: #2563eb; background: rgba(59, 130, 246, 0.08); }

.notif-empty {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.6rem 0.75rem;
  color: var(--color-verde-fuerte);
  font-size: 0.85rem;
}

.cocina-view {
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

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  padding: 1.5rem 2rem 0;
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

.tone-green { background: rgba(16, 185, 129, 0.1); color: #059669; }
.tone-amber { background: rgba(245, 158, 11, 0.12); color: #d97706; }
.tone-red { background: rgba(220, 38, 38, 0.1); color: #dc2626; }
.tone-blue { background: rgba(59, 130, 246, 0.1); color: #2563eb; }

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
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--text-main);
}

.stat-badge {
  font-size: 0.65rem;
  font-weight: 600;
  margin-top: 0.2rem;
}

.module-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  padding: 1.5rem 2rem;
}

.module-card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  text-align: left;
  padding: 1.1rem 1.25rem;
  background: var(--bg-card);
  border-radius: 14px;
  border: 1px solid var(--border-color);
  text-decoration: none;
  color: inherit;
  transition: all 0.18s ease;
  cursor: pointer;
  box-shadow: var(--shadow-soft);
}

.module-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-medium);
  border-color: var(--btn-primary);
}

.module-icon {
  width: 42px;
  height: 42px;
  border-radius: 11px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  margin-bottom: 0.7rem;
}

.module-card h3 {
  margin: 0 0 0.25rem;
  font-size: 0.92rem;
  color: var(--text-main);
  font-weight: 600;
}

.module-card p {
  margin: 0;
  font-size: 0.75rem;
  color: var(--text-muted);
  line-height: 1.4;
}

.section-block {
  padding: 0 2rem 2rem;
}

.section-block h2 {
  margin: 0 0 1rem;
  font-size: 1rem;
  color: var(--text-main);
  font-weight: 600;
}

.table-card {
  background: var(--bg-card);
  border-radius: 14px;
  border: 1px solid var(--border-color);
  padding: 1rem;
  box-shadow: var(--shadow-soft);
}

@media (max-width: 900px) {
  .stats-grid, .module-grid { grid-template-columns: 1fr; }
  .page-header { flex-direction: column; gap: 1rem; align-items: flex-start; }
}
</style>