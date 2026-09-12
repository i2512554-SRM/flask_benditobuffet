<template>
  <div>
    <div class="page-hero">
      <VolverBtn to="/inventario" />
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

    <p v-if="error" role="alert">{{ error }}</p>
    <section class="report-detail" v-if="!loading && !error">
      <h2>Existencias por producto</h2>
      <DataTable :value="productos" paginator :rows="10" stripedRows>
        <Column field="nombre" header="Producto" sortable />
        <Column field="unidad_medida" header="Unidad" />
        <Column field="stock" header="Stock" sortable />
        <Column header="Valor actual"><template #body="{data}">S/ {{ formatMoney(data.precio * data.stock) }}</template></Column>
        <template #empty>No hay productos registrados.</template>
      </DataTable>
      <h2>Movimientos recientes</h2>
      <DataTable :value="movimientos" paginator :rows="10" stripedRows>
        <Column field="fecha" header="Fecha" sortable><template #body="{data}">{{ formatFecha(data.fecha) }}</template></Column>
        <Column field="producto" header="Producto" />
        <Column field="tipo" header="Tipo" />
        <Column field="cantidad" header="Cantidad" />
        <Column field="unidad" header="Unidad" />
        <Column field="stock_posterior" header="Stock resultante" />
        <Column field="usuario" header="Responsable" />
        <template #empty>No hay movimientos registrados.</template>
      </DataTable>
    </section>
    <div class="loading-overlay" v-if="loading">
      <i class="fa-solid fa-spinner fa-spin"></i>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import { formatFecha } from '../utils/format'
import api from '../config/axios'

const loading = ref(true)
const productos = ref([]), movimientos = ref([]), error = ref('')
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
    error.value = ''
    const [res, prod, mov] = await Promise.all([api.get('/inventario/resumen'), api.get('/inventario/productos'), api.get('/inventario/movimientos')])
    productos.value = prod.data.data || []
    movimientos.value = mov.data.data || []
    if (res.data.success) resumen.value = res.data.data
  } catch (err) {
    error.value = 'No se pudo cargar el reporte de inventario. Intenta nuevamente.'
    console.error('Error loading reportes inventario:', err)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.report-detail { margin-top: 1.5rem; padding: 1rem; background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 14px; }
.report-detail h2 { margin: 1rem 0; }
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
