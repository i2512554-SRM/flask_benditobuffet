<template>
  <div class="cocina-view">
    <VolverBtn to="/cocinero" />
    <div class="page-header">
      <div>
        <h1>Insumos de cocina</h1>
        <p>Disponibilidad de ingredientes y productos del restaurante</p>
      </div>
      <router-link to="/cocinero/solicitudes" class="btn btn-outline">
        <i class="fa-solid fa-plus"></i> Solicitar insumo
      </router-link>
    </div>

    <div class="table-card">
      <div class="table-toolbar">
        <div class="toolbar-left">
          <span class="p-input-icon-left">
            <i class="pi pi-search" />
            <InputText v-model="busqueda" placeholder="Buscar insumo o categoría..." class="input-search" />
          </span>
        </div>
        <div class="toolbar-right">
          <span class="total-badge">{{ insumos.length }} insumo(s)</span>
        </div>
      </div>

      <DataTable :value="filtered" :paginator="true" :rows="12" stripedRows dataKey="id_producto" responsiveLayout="scroll">
        <Column field="nombre" header="Producto" sortable>
          <template #body="slotProps">
            <div class="prod-cell">
              <div class="prod-icon"><i class="fa-solid fa-drumstick-bite"></i></div>
              <div>
                <div class="prod-name">{{ slotProps.data.nombre }}</div>
                <div class="prod-cat">{{ slotProps.data.categoria || 'Sin categoría' }}</div>
              </div>
            </div>
          </template>
        </Column>
        <Column field="stock" header="Cantidad" sortable>
          <template #body="slotProps">
            <strong>{{ formatStock(slotProps.data.stock) }}</strong> <small class="text-muted">unid.</small>
          </template>
        </Column>
        <Column header="Estado del stock" sortable>
          <template #body="slotProps">
            <Tag :value="slotProps.data.estado" :severity="severidad(slotProps.data.estado)" />
          </template>
        </Column>
        <Column header="Acción" style="min-width: 9rem">
          <template #body="slotProps">
            <Button
              v-if="slotProps.data.estado !== 'Disponible'"
              label="Solicitar"
              icon="pi pi-basket"
              size="small"
              @click="solicitar(slotProps.data)"
            />
            <span v-else class="text-muted ok-label"><i class="fa-solid fa-circle-check"></i> Disponible</span>
          </template>
        </Column>
        <template #empty>
          <div class="empty-state">
            <i class="fa-solid fa-utensils"></i>
            <span>No se encontraron insumos.</span>
          </div>
        </template>
      </DataTable>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import VolverBtn from '../components/ui/VolverBtn.vue'
import api from '../config/axios'

const router = useRouter()
const insumos = ref([])
const busqueda = ref('')

const filtered = computed(() => {
  const q = busqueda.value.trim().toLowerCase()
  if (!q) return insumos.value
  return insumos.value.filter((p) =>
    (p.nombre || '').toLowerCase().includes(q) || (p.categoria || '').toLowerCase().includes(q)
  )
})

const formatStock = (v) => Number(v || 0).toLocaleString('es-PE')
const severidad = (estado) => (estado === 'Agotado' ? 'danger' : estado === 'Stock bajo' ? 'warning' : 'success')
const solicitar = (prod) => router.push({ path: '/cocinero/solicitudes', query: { producto: prod.id_producto } })

const load = async () => {
  try {
    const res = await api.get('/cocina/inventario')
    if (res.data.success) insumos.value = res.data.data
  } catch (e) {
    console.error('Error cargando insumos:', e)
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

.button.primary {
  background: linear-gradient(135deg, #f97316, #fb923c);
  color: white;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
}

.table-card {
  margin: 1.5rem 2rem 2rem;
  background: var(--bg-card);
  border-radius: 14px;
  border: 1px solid var(--border-color);
  padding: 1rem;
  box-shadow: var(--shadow-soft);
}

.table-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.toolbar-left, .toolbar-right {
  display: flex;
  align-items: center;
}

.input-search {
  min-width: 280px;
}

.total-badge {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-muted);
  background: var(--bg-secondary);
  padding: 0.3rem 0.75rem;
  border-radius: 999px;
}

.prod-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.prod-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: rgba(249, 115, 22, 0.12);
  color: #f97316;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
  flex-shrink: 0;
}

.prod-name {
  font-weight: 600;
  color: var(--text-main);
}

.prod-cat {
  font-size: 0.72rem;
  color: var(--text-muted);
}

.ok-label {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  color: var(--color-verde-fuerte);
  font-size: 0.8rem;
}

@media (max-width: 768px) {
  .page-header { flex-direction: column; gap: 1rem; align-items: flex-start; }
  .table-card { margin: 1rem; }
  .table-toolbar { flex-direction: column; align-items: stretch; }
  .input-search { min-width: 100%; }
}
</style>