<template>
  <div class="inventario-view">
    <h1>Inventario e Inversión</h1>
    <p class="subtitle">Control de productos, compras e inversiones.</p>

    <div class="actions">
      <Button label="Registrar compra/inversión" icon="pi pi-cart-plus" @click="openCompra" />
      <Button label="Agregar producto" icon="pi pi-plus" severity="secondary" @click="agregarDialog" />
      <Button label="Gestionar proveedores" icon="pi pi-truck" severity="secondary" @click="openProveedores" />
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">Valor total inventario</div>
        <div class="stat-value">S/. {{ fmt(resumen.valor_total) }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Inversiones del mes</div>
        <div class="stat-value">S/. {{ fmt(resumen.inversiones_mes) }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Artículos registrados</div>
        <div class="stat-value">{{ resumen.articulos_registrados }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Productos del mes</div>
        <div class="stat-value">{{ resumen.productos_mes }}</div>
      </div>
    </div>

    <div class="view-toggle">
      <Button label="Productos" :class="{ active: vista === 'productos' }" severity="secondary" plain @click="vista = 'productos'" />
      <Button label="Compras / Inversiones" :class="{ active: vista === 'compras' }" severity="secondary" plain @click="vista = 'compras'" />
    </div>

    <div class="table-card" v-if="vista === 'productos'">
      <div class="table-header">
        <h2>Productos</h2>
        <div class="search-box">
          <InputText v-model="busqueda" placeholder="Buscar producto o categoría..." class="w-full" @input="cargarProductos" />
          <Select v-model="categoriaFiltro" :options="categorias" optionLabel="nombre" optionValue="id_categoria" placeholder="Todas las categorías" showClear class="w-full" @update:model-value="cargarProductos" />
        </div>
      </div>
      <DataTable :value="productos" v-model:editing-rows="editingRows" edit-mode="row" data-key="id_producto" :paginator="true" :rows="10" class="mt-4">
        <Column field="nombre" header="Nombre" sortable></Column>
        <Column field="categoria" header="Categoría" sortable></Column>
        <Column field="precio" header="Precio" sortable>
          <template #body="slotProps">S/. {{ fmt2(slotProps.data.precio) }}</template>
        </Column>
        <Column field="stock" header="Stock" sortable></Column>
        <Column header="Acciones" :exportable="false">
          <template #body="slotProps">
            <Button icon="pi pi-pencil" severity="info" text rounded @click="editar(slotProps.data)" />
            <Button icon="pi pi-trash" severity="danger" text rounded @click="eliminar(slotProps.data)" />
          </template>
        </Column>
      </DataTable>
    </div>

    <div class="table-card" v-if="vista === 'compras'">
      <h2>Compras e inversiones</h2>
      <DataTable :value="inversiones" :paginator="true" :rows="10" class="mt-4">
        <Column field="fecha" header="Fecha" sortable>
          <template #body="slotProps">{{ fmtFecha(slotProps.data.fecha) }}</template>
        </Column>
        <Column field="descripcion" header="Descripción" sortable></Column>
        <Column field="proveedor" header="Proveedor">
          <template #body="slotProps">{{ slotProps.data.proveedor || '-' }}</template>
        </Column>
        <Column field="monto" header="Monto" sortable>
          <template #body="slotProps">S/. {{ fmt2(slotProps.data.monto) }}</template>
        </Column>
        <Column header="Acciones">
          <template #body="slotProps">
            <Button icon="pi pi-eye" severity="info" text rounded @click="verCompra(slotProps.data)" />
            <Button icon="pi pi-trash" severity="danger" text rounded @click="eliminarCompra(slotProps.data)" />
          </template>
        </Column>
      </DataTable>
    </div>

    <Dialog v-model:visible="productoDialog" :header="editing.id_producto ? 'Editar Producto' : 'Nuevo Producto'" :modal="true" :style="{ width: '500px' }">
      <div class="formgrid grid">
        <div class="field col-12">
          <label for="nombre">Nombre</label>
          <InputText id="nombre" v-model="form.nombre" class="w-full" />
        </div>
        <div class="field col-6">
          <label for="categoria">Categoría</label>
          <Select id="categoria" v-model="form.id_categoria" :options="categorias" optionLabel="nombre" optionValue="id_categoria" class="w-full" />
        </div>
        <div class="field col-6">
          <label for="precio">Precio</label>
          <InputNumber id="precio" v-model="form.precio" mode="currency" currency="PEN" locale="es-PE" class="w-full" />
        </div>
        <div class="field col-6">
          <label for="stock">Stock</label>
          <InputNumber id="stock" v-model="form.stock" class="w-full" />
        </div>
      </div>
      <template #footer>
        <Button label="Cancelar" severity="secondary" @click="productoDialog = false" />
        <Button label="Guardar" @click="guardarProducto" />
      </template>
    </Dialog>

    <Dialog v-model:visible="compraDialog" header="Registrar compra/inversión" :modal="true" :style="{ width: '520px' }">
      <div class="formgrid grid">
        <div class="field col-12">
          <label for="descripcion">Descripción</label>
          <InputText id="descripcion" v-model="compraForm.descripcion" class="w-full" />
        </div>
        <div class="field col-12">
          <label for="proveedor">Proveedor</label>
          <Select id="proveedor" v-model="compraForm.id_proveedor" :options="proveedores" optionLabel="nombre" optionValue="id_proveedor" class="w-full" showClear />
        </div>
        <div class="field col-6">
          <label for="monto">Monto</label>
          <InputNumber id="monto" v-model="compraForm.monto" mode="currency" currency="PEN" locale="es-PE" class="w-full" />
        </div>
        <div class="field col-12">
          <label for="notas">Notas</label>
          <Textarea id="notas" v-model="compraForm.notas" rows="3" class="w-full" />
        </div>
      </div>
      <template #footer>
        <Button label="Cancelar" severity="secondary" @click="compraDialog = false" />
        <Button label="Guardar" @click="guardarCompra" />
      </template>
    </Dialog>

    <Dialog v-model:visible="proveedorDialog" header="Gestionar proveedores" :modal="true" :style="{ width: '600px' }">
      <div class="formgrid grid">
        <div class="field col-8">
          <InputText v-model="provForm.nombre" placeholder="Nombre del proveedor" class="w-full" />
        </div>
        <div class="field col-4">
          <Button label="Agregar" icon="pi pi-plus" @click="guardarProveedor" class="w-full" />
        </div>
      </div>
      <DataTable :value="proveedores" :rows="8" class="mt-3">
        <Column field="nombre" header="Proveedor"></Column>
        <Column field="ruc" header="RUC">
          <template #body="slotProps">{{ slotProps.data.ruc || '-' }}</template>
        </Column>
        <Column field="telefono" header="Teléfono">
          <template #body="slotProps">{{ slotProps.data.telefono || '-' }}</template>
        </Column>
        <Column field="correo" header="Correo">
          <template #body="slotProps">{{ slotProps.data.correo || '-' }}</template>
        </Column>
      </DataTable>
    </Dialog>

    <Dialog v-model:visible="compraDetalleDialog" header="Detalle de compra/inversión" :modal="true" :style="{ width: '480px' }">
      <div v-if="compraSeleccionada.id_inversion" class="detalle-info">
        <div class="d-row"><span class="d-label">Descripción</span><span>{{ compraSeleccionada.descripcion }}</span></div>
        <div class="d-row"><span class="d-label">Proveedor</span><span>{{ compraSeleccionada.proveedor || '-' }}</span></div>
        <div class="d-row"><span class="d-label">Monto</span><span>S/. {{ fmt2(compraSeleccionada.monto) }}</span></div>
        <div class="d-row"><span class="d-label">Fecha</span><span>{{ fmtFecha(compraSeleccionada.fecha) }}</span></div>
        <div class="d-row"><span class="d-label">Notas</span><span>{{ compraSeleccionada.notas || '-' }}</span></div>
      </div>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import InputNumber from 'primevue/inputnumber'
import Select from 'primevue/select'
import api from '../config/axios'

const toast = useToast()
const productos = ref([])
const categorias = ref([])
const inversiones = ref([])
const proveedores = ref([])
const resumen = ref({ valor_total: 0, inversiones_mes: 0, articulos_registrados: 0, productos_mes: 0 })
const vista = ref('productos')
const busqueda = ref('')
const categoriaFiltro = ref(null)
const editingRows = ref([])
const productoDialog = ref(false)
const compraDialog = ref(false)
const proveedorDialog = ref(false)
const compraDetalleDialog = ref(false)
const editing = ref({})
const form = ref({})
const compraForm = ref({})
const provForm = ref({ nombre: '' })
const compraSeleccionada = ref({})

const fmt = (v) => Number(v || 0).toFixed(2)
const fmt2 = (v) => Number(v || 0).toFixed(2)
const fmtFecha = (v) => v ? String(v).slice(0, 10) : '-'

const cargarProductos = async () => {
  const params = {}
  if (busqueda.value) params.q = busqueda.value
  if (categoriaFiltro.value) {
    const cat = categorias.value.find(c => c.id_categoria === categoriaFiltro.value)
    if (cat) params.cat = cat.nombre
  }
  const res = await api.get('/inventario/productos', { params })
  if (res.data.success) productos.value = res.data.data
}

const cargarCategorias = async () => {
  const res = await api.get('/inventario/categorias')
  if (res.data.success) categorias.value = res.data.data
}

const cargarInversiones = async () => {
  const res = await api.get('/inventario/inversiones')
  if (res.data.success) inversiones.value = res.data.data
}

const cargarProveedores = async () => {
  const res = await api.get('/inventario/proveedores')
  if (res.data.success) proveedores.value = res.data.data
}

const cargarResumen = async () => {
  const res = await api.get('/inventario/resumen')
  if (res.data.success) resumen.value = res.data.data
}

const agregarDialog = () => {
  editing.value = {}
  form.value = { nombre: '', id_categoria: null, precio: 0, stock: 0 }
  productoDialog.value = true
}

const editar = (prod) => {
  editing.value = prod
  form.value = { ...prod }
  productoDialog.value = true
}

const guardarProducto = async () => {
  try {
    if (editing.value.id_producto) {
      await api.put(`/inventario/productos/${editing.value.id_producto}`, form.value)
    } else {
      await api.post('/inventario/productos', form.value)
    }
    toast.add({ severity: 'success', summary: 'Producto guardado', life: 2500 })
    productoDialog.value = false
    await Promise.all([cargarProductos(), cargarResumen()])
  } catch (e) {
    toast.add({ severity: 'error', summary: e.response?.data?.message || 'Error al guardar', life: 3500 })
  }
}

const eliminar = async (prod) => {
  await api.delete(`/inventario/productos/${prod.id_producto}`)
  toast.add({ severity: 'success', summary: 'Producto eliminado', life: 2500 })
  await Promise.all([cargarProductos(), cargarResumen()])
}

const openCompra = () => {
  compraForm.value = { descripcion: '', id_proveedor: null, monto: 0, notas: '' }
  compraDialog.value = true
}

const guardarCompra = async () => {
  try {
    await api.post('/inventario/inversiones', compraForm.value)
    toast.add({ severity: 'success', summary: 'Compra/inversión registrada', life: 2500 })
    compraDialog.value = false
    await Promise.all([cargarInversiones(), cargarResumen()])
  } catch (e) {
    toast.add({ severity: 'error', summary: e.response?.data?.message || 'Error al registrar', life: 3500 })
  }
}

const openProveedores = () => {
  provForm.value = { nombre: '' }
  proveedorDialog.value = true
}

const guardarProveedor = async () => {
  if (!provForm.value.nombre) return
  await api.post('/inventario/proveedores', provForm.value)
  toast.add({ severity: 'success', summary: 'Proveedor agregado', life: 2500 })
  provForm.value = { nombre: '' }
  await cargarProveedores()
}

const verCompra = (inv) => {
  compraSeleccionada.value = inv
  compraDetalleDialog.value = true
}

const eliminarCompra = async (inv) => {
  await api.delete(`/inventario/inversiones/${inv.id_inversion}`)
  toast.add({ severity: 'success', summary: 'Compra/inversión eliminada', life: 2500 })
  await Promise.all([cargarInversiones(), cargarResumen()])
}

onMounted(async () => {
  await Promise.all([cargarProductos(), cargarCategorias(), cargarInversiones(), cargarProveedores(), cargarResumen()])
})
</script>

<style scoped>
.inventario-view { padding: 2rem; }
.subtitle { color: var(--text-muted); margin-top: 0.25rem; }
.actions { display: flex; gap: 1rem; margin: 1.5rem 0; }
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
.stat-card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 1.25rem; }
.stat-label { font-size: 0.75rem; color: var(--text-muted); }
.stat-value { font-size: 1.5rem; font-weight: 700; margin-top: 0.25rem; }
.table-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; }
.search-box { display: flex; gap: 0.75rem; min-width: 420px; }
.view-toggle { display: flex; gap: 0.5rem; margin-bottom: 1rem; }
.view-toggle .active { background: var(--btn-primary); color: white; border-color: var(--btn-primary); }
.table-card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 1.25rem; }
.mt-4 { margin-top: 1rem; }
.mt-3 { margin-top: 0.75rem; }
.detalle-info .d-row { display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid var(--border-color); }
.detalle-info .d-label { font-weight: 600; color: var(--text-muted); }
</style>
