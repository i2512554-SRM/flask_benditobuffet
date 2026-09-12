<template>
  <div class="cocina-view">
    <VolverBtn to="/cocinero" />
    <div class="page-header">
      <div>
        <h1>Insumos de cocina</h1>
        <p>Disponibilidad de ingredientes y productos del restaurante</p>
      </div>
      <div class="header-actions">
        <Button :disabled="$saving" label="Agregar stock" icon="pi pi-arrow-down" severity="secondary" size="small" @click="abrirStock('entrada')" />
        <Button :disabled="$saving" label="Registrar salida" icon="pi pi-arrow-up" severity="secondary" size="small" @click="abrirStock('salida')" />
        <router-link to="/cocinero/solicitudes" class="btn btn-outline">
          <i class="fa-solid fa-plus"></i> Solicitar insumo
        </router-link>
      </div>
    </div>

    <div class="view-tabs">
      <Button :disabled="$saving" :label="`Insumos (${insumos.length})`" :class="{ active: vista === 'insumos' }" severity="secondary" plain size="small" @click="vista = 'insumos'" />
      <Button :disabled="$saving" label="Historial de movimientos" :class="{ active: vista === 'movimientos' }" severity="secondary" plain size="small" @click="cargarMovimientos(); vista = 'movimientos'" />
    </div>

    <div class="table-card" v-if="vista === 'insumos'">
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
            <strong>{{ fmtStock(slotProps.data.stock) }}</strong>
            <small class="text-muted"> {{ unidadLabel(slotProps.data.unidad_medida) }}</small>
          </template>
        </Column>
        <Column header="Estado del stock" sortable>
          <template #body="slotProps">
            <Tag :value="slotProps.data.estado" :severity="severidad(slotProps.data.estado)" />
          </template>
        </Column>
        <Column header="Acción" style="min-width: 15rem">
          <template #body="slotProps">
            <div class="row-actions">
              <Button :disabled="$saving" icon="pi pi-arrow-down" text rounded title="Agregar stock" @click="abrirStock('entrada', slotProps.data)" />
              <Button :disabled="$saving" icon="pi pi-arrow-up" text rounded title="Registrar salida" @click="abrirStock('salida', slotProps.data)" />
              <Button :disabled="$saving"
                v-if="slotProps.data.estado !== 'Disponible'"
                label="Solicitar"
                icon="pi pi-basket"
                size="small"
                @click="solicitar(slotProps.data)"
              />
              <span v-else class="text-muted ok-label"><i class="fa-solid fa-circle-check"></i> Disp.</span>
            </div>
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

    <div class="table-card" v-if="vista === 'movimientos'">
      <div class="table-toolbar">
        <div class="toolbar-left">
          <span class="p-input-icon-left">
            <i class="pi pi-search" />
            <InputText v-model="movBusqueda" placeholder="Buscar por producto..." class="input-search" @input="cargarMovimientos" />
          </span>
        </div>
        <div class="toolbar-right">
          <Select v-model="movTipo" :options="['Entrada', 'Salida', 'Ajuste']" placeholder="Todos los tipos" showClear class="input-search" @update:model-value="cargarMovimientos" />
        </div>
      </div>
      <DataTable :value="movimientos" :paginator="true" :rows="12" stripedRows dataKey="id_movimiento" responsiveLayout="scroll">
        <Column field="fecha" header="Fecha" sortable>
          <template #body="slotProps">{{ fmtFechaHora(slotProps.data.fecha) }}</template>
        </Column>
        <Column field="producto" header="Producto" sortable></Column>
        <Column field="tipo" header="Tipo" sortable>
          <template #body="slotProps">
            <Tag :value="slotProps.data.tipo" :severity="slotProps.data.tipo === 'Entrada' ? 'success' : slotProps.data.tipo === 'Salida' ? 'danger' : 'warning'" />
          </template>
        </Column>
        <Column field="cantidad" header="Cantidad" sortable>
          <template #body="slotProps">
            <strong :class="{ 'mov-menos': Number(slotProps.data.cantidad) < 0 }">{{ firmar(slotProps.data.cantidad) }}</strong>
            <small class="text-muted"> {{ unidadLabel(slotProps.data.unidad) }}</small>
          </template>
        </Column>
        <Column field="stock_anterior" header="Anterior" sortable>
          <template #body="slotProps">{{ fmtStock(slotProps.data.stock_anterior) }} {{ unidadLabel(slotProps.data.unidad) }}</template>
        </Column>
        <Column field="stock_posterior" header="Posterior" sortable>
          <template #body="slotProps">{{ fmtStock(slotProps.data.stock_posterior) }} {{ unidadLabel(slotProps.data.unidad) }}</template>
        </Column>
        <Column field="motivo" header="Motivo"></Column>
        <Column field="usuario" header="Responsable">
          <template #body="slotProps">{{ slotProps.data.usuario || '-' }}</template>
        </Column>
        <template #empty>
          <div class="empty-state">
            <i class="fa-solid fa-clock-rotate-left"></i>
            <span>No hay movimientos.</span>
          </div>
        </template>
      </DataTable>
    </div>

    <Dialog v-model:visible="stockDialog" :header="stockModo === 'entrada' ? 'Agregar stock' : 'Registrar salida'" :modal="true" :style="{ width: '440px' }">
      <div class="formgrid grid">
        <div class="field col-12">
          <label for="stock-producto">Producto *</label>
          <Select id="stock-producto" v-model="stockForm.id_producto" :options="insumos" filter optionLabel="nombre" optionValue="id_producto" placeholder="Selecciona un insumo" class="w-full">
            <template #option="slotProps">
              <div class="opt-prod">
                <span>{{ slotProps.option.nombre }}</span>
                <span class="opt-stock">{{ fmtStock(slotProps.option.stock) }} {{ unidadLabel(slotProps.option.unidad_medida) }}</span>
              </div>
            </template>
          </Select>
        </div>
        <div class="field col-6" v-if="stockProducto">
          <label>Stock actual</label>
          <div class="stock-actual">{{ fmtStock(stockProducto.stock) }} {{ unidadLabel(stockProducto.unidad_medida) }}</div>
        </div>
        <div class="field col-6">
          <label for="stock-cantidad">Cantidad *</label>
          <InputNumber :maxFractionDigits="2" placeholder="Ej. 100.00" id="stock-cantidad" v-model="stockForm.cantidad" :min="0" class="w-full" />
        </div>
        <div class="field col-12">
          <label for="stock-motivo">{{ stockModo === 'entrada' ? 'Motivo (opcional)' : 'Motivo *' }}</label>
          <InputText id="stock-motivo" v-model="stockForm.motivo" :placeholder="stockModo === 'entrada' ? 'Ej. Reposición de almacén' : 'Ej. Preparación de menú del día'" class="w-full" />
        </div>
      </div>
      <div v-if="stockWarning" class="dup-advice warn">
        <i class="pi pi-exclamation-triangle"></i>
        <span>{{ stockWarning }}</span>
      </div>
      <template #footer>
        <Button :disabled="$saving" label="Cancelar" severity="secondary" @click="stockDialog = false" />
        <Button :disabled="$saving" label="Confirmar" @click="confirmarStock" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Select from 'primevue/select'
import Tag from 'primevue/tag'
import VolverBtn from '../components/ui/VolverBtn.vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import api from '../config/axios'

const router = useRouter()
const toast = useToast()
const insumos = ref([])
const busqueda = ref('')
const vista = ref('insumos')
const movimientos = ref([])
const movBusqueda = ref('')
const movTipo = ref(null)
const stockDialog = ref(false)
const stockModo = ref('entrada')
const stockForm = ref({})
const stockWarning = ref('')

const filtered = computed(() => {
  const q = busqueda.value.trim().toLowerCase()
  if (!q) return insumos.value
  return insumos.value.filter((p) =>
    (p.nombre || '').toLowerCase().includes(q) || (p.categoria || '').toLowerCase().includes(q)
  )
})

const stockProducto = computed(() => {
  const sel = stockForm.value.id_producto
  return insumos.value.find(p => p.id_producto === sel) || null
})

const unidadLabel = (u) => u === 'Kg' ? 'Kg' : u === 'Lt' ? 'Lt' : 'Un'
const fmtStock = (v) => {
  const n = Number(v || 0)
  return n % 1 === 0 ? String(n) : n.toFixed(2)
}
const firmar = (v) => {
  const n = Number(v || 0)
  return n > 0 ? `+${fmtStock(n)}` : fmtStock(n)
}
const fmtFechaHora = (v) => v ? String(v).slice(0, 16).replace('T', ' ') : '-'
const severidad = (estado) => (estado === 'Agotado' ? 'danger' : estado === 'Stock bajo' ? 'warning' : 'success')
const solicitar = (prod) => router.push({ path: '/cocinero/solicitudes', query: { producto: prod.id_producto } })

const abrirStock = (modo, prod = null) => {
  stockModo.value = modo
  stockWarning.value = ''
  stockForm.value = { id_producto: prod?.id_producto || null, cantidad: null, motivo: '' }
  stockDialog.value = true
}

const confirmarStock = async () => {
  stockWarning.value = ''
  const prod = stockProducto.value
  if (!stockForm.value.id_producto || !prod) {
    toast.add({ severity: 'warn', summary: 'Selecciona un insumo', life: 3000 })
    return
  }
  const cantidad = Number(stockForm.value.cantidad)
  if (!cantidad || cantidad <= 0) {
    toast.add({ severity: 'warn', summary: 'La cantidad debe ser mayor a cero', life: 3000 })
    return
  }
  if (stockModo.value === 'salida') {
    if (!stockForm.value.motivo || !stockForm.value.motivo.trim()) {
      toast.add({ severity: 'warn', summary: 'El motivo de la salida es obligatorio', life: 3000 })
      return
    }
    if (cantidad > Number(prod.stock)) {
      stockWarning.value = `No hay suficiente stock disponible (actual: ${fmtStock(prod.stock)} ${unidadLabel(prod.unidad_medida)}).`
      return
    }
  }
  try {
    const body = { cantidad }
    if (stockForm.value.motivo) body.motivo = stockForm.value.motivo
    await api.post(`/inventario/productos/${stockForm.value.id_producto}/stock/${stockModo.value}`, body)
    toast.add({ severity: 'success', summary: stockModo.value === 'entrada' ? 'Stock agregado' : 'Salida registrada', life: 2500 })
    stockDialog.value = false
    await load()
  } catch (e) {
    toast.add({ severity: 'error', summary: e.response?.data?.error || 'Error en la operación', life: 3500 })
  }
}

const cargarMovimientos = async () => {
  const params = {}
  if (movBusqueda.value) params.producto = movBusqueda.value
  if (movTipo.value) params.tipo = movTipo.value
  try {
    const res = await api.get('/inventario/movimientos', { params })
    if (res.data.success) movimientos.value = res.data.data
  } catch (e) {
    console.error('Error cargando movimientos:', e)
  }
}

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
.cocina-view { padding: 0; }
.page-header { display: flex; justify-content: space-between; align-items: center; gap: 1rem; padding: 1.5rem 2rem; background: var(--bg-card); border-bottom: 1px solid var(--border-color); }
.page-header h1 { margin: 0; font-size: 1.5rem; color: var(--text-main); }
.page-header p { margin: 0.25rem 0 0; font-size: 0.85rem; color: var(--text-muted); }
.header-actions { display: flex; align-items: center; gap: 0.6rem; flex-wrap: wrap; }
.view-tabs { display: flex; gap: 0.5rem; margin: 1.25rem 2rem 0; }
.view-tabs .active { background: var(--btn-primary); color: white; border-color: var(--btn-primary); }
.table-card { margin: 1.25rem 2rem 2rem; background: var(--bg-card); border-radius: 14px; border: 1px solid var(--border-color); padding: 1rem; box-shadow: var(--shadow-soft); }
.table-toolbar { display: flex; justify-content: space-between; align-items: center; gap: 1rem; margin-bottom: 1rem; }
.toolbar-left, .toolbar-right { display: flex; align-items: center; gap: 0.6rem; }
.input-search { min-width: 280px; }
.total-badge { font-size: 0.75rem; font-weight: 600; color: var(--text-muted); background: var(--bg-secondary); padding: 0.3rem 0.75rem; border-radius: 999px; }
.prod-cell { display: flex; align-items: center; gap: 0.75rem; }
.prod-icon { width: 36px; height: 36px; border-radius: 10px; background: rgba(249, 115, 22, 0.12); color: #f97316; display: flex; align-items: center; justify-content: center; font-size: 0.9rem; flex-shrink: 0; }
.prod-name { font-weight: 600; color: var(--text-main); }
.prod-cat { font-size: 0.72rem; color: var(--text-muted); }
.ok-label { display: inline-flex; align-items: center; gap: 0.35rem; color: var(--color-verde-fuerte); font-size: 0.8rem; }
.row-actions { display: flex; align-items: center; gap: 0.15rem; }
.mov-menos { color: #dc2626; }
.opt-prod { display: flex; justify-content: space-between; gap: 1rem; width: 100%; }
.opt-stock { color: var(--text-muted); font-size: 0.85rem; }
.stock-actual { font-size: 1.05rem; font-weight: 700; padding-top: 0.5rem; }
.dup-advice { display: flex; flex-direction: column; gap: 0.75rem; align-items: flex-start; margin-top: 1rem; background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.4); padding: 0.9rem; border-radius: 8px; font-size: 0.9rem; }
.dup-advice.warn { background: rgba(239, 68, 68, 0.08); border-color: rgba(239, 68, 68, 0.4); color: #b91c1c; }
@media (max-width: 768px) { .page-header { flex-direction: column; align-items: flex-start; } .table-card { margin: 1rem; } .table-toolbar { flex-direction: column; align-items: stretch; } .input-search { min-width: 100%; } }
</style>