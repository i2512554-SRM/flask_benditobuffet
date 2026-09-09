<template>
  <div class="cocina-view">
    <VolverBtn to="/cocinero" />
    <div class="page-header">
      <div>
        <h1>Alertas de stock</h1>
        <p>Productos que necesitan atención para la preparación del buffet</p>
      </div>
      <button class="btn btn-outline" @click="load">
        <i class="fa-solid fa-arrows-rotate"></i> Actualizar
      </button>
    </div>

    <div class="alert-summary">
      <div class="alert-chip danger">
        <i class="fa-solid fa-triangle-exclamation"></i>
        <span><strong>{{ agotados.length }}</strong> agotados</span>
      </div>
      <div class="alert-chip warning">
        <i class="fa-solid fa-fill-drip"></i>
        <span><strong>{{ stockBajo.length }}</strong> con stock bajo</span>
      </div>
    </div>

    <div class="table-card">
      <h2 class="section-title"><i class="fa-solid fa-box-open"></i> Agotados</h2>
      <DataTable :value="agotados" :paginator="true" :rows="8" responsiveLayout="scroll">
        <Column field="nombre" header="Producto" sortable></Column>
        <Column field="categoria" header="Categoría"></Column>
        <Column field="stock" header="Stock actual">
          <template #body="slotProps">
            <strong class="text-danger">0 / {{ formatStock(slotProps.data.stock) }}</strong>
          </template>
        </Column>
        <Column header="Estado">
          <template #body="slotProps">
            <Tag value="Agotado" severity="danger" />
          </template>
        </Column>
        <template #empty>
          <div class="empty-state small">
            <i class="fa-solid fa-thumbs-up"></i>
            <span>No hay productos agotados.</span>
          </div>
        </template>
      </DataTable>
    </div>

    <div class="table-card">
      <h2 class="section-title"><i class="fa-solid fa-gauge-low"></i> Stock bajo</h2>
      <DataTable :value="stockBajo" :paginator="true" :rows="8" responsiveLayout="scroll">
        <Column field="nombre" header="Producto" sortable></Column>
        <Column field="categoria" header="Categoría"></Column>
        <Column field="stock" header="Stock actual">
          <template #body="slotProps">
            <strong class="text-warning">{{ formatStock(slotProps.data.stock) }}</strong> unid.
          </template>
        </Column>
        <Column header="Estado">
          <template #body="slotProps">
            <Tag value="Stock bajo" severity="warning" />
          </template>
        </Column>
        <template #empty>
          <div class="empty-state small">
            <i class="fa-solid fa-thumbs-up"></i>
            <span>No hay productos con stock bajo.</span>
          </div>
        </template>
      </DataTable>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import VolverBtn from '../components/ui/VolverBtn.vue'
import api from '../config/axios'

const alertas = ref([])

const agotados = computed(() => alertas.value.filter((p) => p.estado === 'Agotado'))
const stockBajo = computed(() => alertas.value.filter((p) => p.estado === 'Stock bajo'))

const formatStock = (v) => Number(v || 0).toLocaleString('es-PE')

const load = async () => {
  try {
    const res = await api.get('/cocina/alertas')
    if (res.data.success) alertas.value = res.data.data
  } catch (e) {
    console.error('Error cargando alertas:', e)
  }
}

onMounted(load)
</script>

<style scoped>
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

.alert-summary {
  display: flex;
  gap: 0.75rem;
  padding: 1.5rem 2rem 0;
}

.alert-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.55rem 1rem;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 500;
}

.alert-chip.danger { background: rgba(220, 38, 38, 0.1); color: #dc2626; }
.alert-chip.warning { background: rgba(245, 158, 11, 0.12); color: #d97706; }

.table-card {
  margin: 1.5rem 2rem 0;
  background: var(--bg-card);
  border-radius: 14px;
  border: 1px solid var(--border-color);
  padding: 1rem;
  box-shadow: var(--shadow-soft);
}

.table-card:last-of-type {
  margin-bottom: 2rem;
}

.section-title {
  margin: 0 0 0.75rem;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-main);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.text-danger { color: #dc2626; }
.text-warning { color: #d97706; }

.empty-state.small {
  padding: 2rem;
}

@media (max-width: 768px) {
  .page-header { flex-direction: column; gap: 1rem; align-items: flex-start; }
  .alert-summary { flex-direction: column; padding: 1rem; }
  .table-card { margin: 1rem; }
}
</style>