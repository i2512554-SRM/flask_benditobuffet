<template>
  <div class="inventario-view">
    <h1>Inventario e Inversión</h1>
    <p class="subtitle">Control de productos, compras e inversiones.</p>

    <div class="actions">
      <Button label="Registrar compra" icon="pi pi-cart-plus" @click="openCompra" />
      <Button label="Registrar inversión" icon="pi pi-chart-line" severity="secondary" @click="openInversion" />
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
      <Button label="Compras" :class="{ active: vista === 'compras' }" severity="secondary" plain @click="vista = 'compras'" />
      <Button label="Inversiones" :class="{ active: vista === 'inversiones' }" severity="secondary" plain @click="vista = 'inversiones'" />
      <Button label="Movimientos" :class="{ active: vista === 'movimientos' }" severity="secondary" plain @click="vista = 'movimientos'" />
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
      <h2>Compras de inventario</h2>
      <DataTable :value="compras" :paginator="true" :rows="10" class="mt-4">
        <Column field="codigo" header="Código" sortable></Column>
        <Column field="fecha" header="Fecha" sortable>
          <template #body="slotProps">{{ fmtFecha(slotProps.data.fecha) }}</template>
        </Column>
        <Column field="proveedor" header="Proveedor">
          <template #body="slotProps">{{ slotProps.data.proveedor || '-' }}</template>
        </Column>
        <Column field="n_detalle" header="Productos" sortable></Column>
        <Column field="total_compra" header="Total" sortable>
          <template #body="slotProps">S/. {{ fmt2(slotProps.data.total_compra) }}</template>
        </Column>
        <Column field="estado" header="Estado" sortable></Column>
        <Column header="Acciones">
          <template #body="slotProps">
            <Button icon="pi pi-eye" severity="info" text rounded @click="verCompra(slotProps.data)" />
            <Button icon="pi pi-trash" severity="danger" text rounded @click="eliminarCompra(slotProps.data)" />
          </template>
        </Column>
      </DataTable>
    </div>

    <div class="table-card" v-if="vista === 'inversiones'">
      <h2>Inversiones</h2>
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
            <Button icon="pi pi-eye" severity="info" text rounded @click="verInversion(slotProps.data)" />
            <Button icon="pi pi-trash" severity="danger" text rounded @click="eliminarInversion(slotProps.data)" />
          </template>
        </Column>
      </DataTable>
    </div>

    <div class="table-card" v-if="vista === 'movimientos'">
      <div class="table-header">
        <h2>Historial de movimientos</h2>
        <div class="search-box">
          <InputText v-model="movBusqueda" placeholder="Buscar por producto..." class="w-full" @input="cargarMovimientos" />
          <Select v-model="movTipo" :options="['Entrada', 'Salida', 'Ajuste']" placeholder="Todos los tipos" showClear class="w-full" @update:model-value="cargarMovimientos" />
        </div>
      </div>
      <DataTable :value="movimientos" :paginator="true" :rows="10" class="mt-4">
        <Column field="fecha" header="Fecha" sortable>
          <template #body="slotProps">{{ fmtFechaHora(slotProps.data.fecha) }}</template>
        </Column>
        <Column field="producto" header="Producto" sortable></Column>
        <Column field="tipo" header="Tipo" sortable>
          <template #body="slotProps">
            <span :class="['mov-tipo', 'mov-' + slotProps.data.tipo.toLowerCase()]">{{ slotProps.data.tipo }}</span>
          </template>
        </Column>
        <Column field="cantidad" header="Cantidad" sortable></Column>
        <Column field="usuario" header="Responsable">
          <template #body="slotProps">{{ slotProps.data.usuario || '-' }}</template>
        </Column>
        <Column field="observacion" header="Observación"></Column>
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

    <Dialog v-model:visible="compraDialog" header="Registrar compra de inventario" :modal="true" :style="{ width: '620px' }">
      <div class="formgrid grid">
        <div class="field col-12">
          <label for="proveedor">Proveedor</label>
          <Select id="proveedor" v-model="compraForm.id_proveedor" :options="proveedores" optionLabel="nombre" optionValue="id_proveedor" class="w-full" showClear />
        </div>
        <div class="field col-12">
          <label>Detalle de productos</label>
          <div v-for="(linea, idx) in compraForm.detalle" :key="idx" class="detalle-row">
            <Select v-model="linea.id_producto" :options="productos" optionLabel="nombre" optionValue="id_producto" placeholder="Producto" class="w-full" />
            <InputNumber v-model="linea.cantidad" placeholder="Cant." :min="0" class="w-full" />
            <InputNumber v-model="linea.precio_unitario" placeholder="P. unit." mode="currency" currency="PEN" locale="es-PE" :min="0" class="w-full" />
            <Button icon="pi pi-trash" severity="danger" text rounded @click="quitarLinea(idx)" />
          </div>
          <Button label="Agregar línea" icon="pi pi-plus" severity="secondary" text @click="agregarLinea" class="mt-1" />
        </div>
        <div class="field col-12">
          <label for="notas">Notas</label>
          <Textarea id="notas" v-model="compraForm.notas" rows="2" class="w-full" />
        </div>
      </div>
      <template #footer>
        <Button label="Cancelar" severity="secondary" @click="compraDialog = false" />
        <Button label="Guardar compra" :disabled="!compraForm.detalle.length" @click="guardarCompra" />
      </template>
    </Dialog>

    <Dialog v-model:visible="inversionDialog" header="Registrar inversión" :modal="true" :style="{ width: '520px' }">
      <div class="formgrid grid">
        <div class="field col-12">
          <label for="descripcion">Descripción</label>
          <InputText id="descripcion" v-model="inversionForm.descripcion" class="w-full" />
        </div>
        <div class="field col-12">
          <label for="proveedor">Proveedor</label>
          <Select id="proveedor" v-model="inversionForm.id_proveedor" :options="proveedores" optionLabel="nombre" optionValue="id_proveedor" class="w-full" showClear />
        </div>
        <div class="field col-6">
          <label for="monto">Monto</label>
          <InputNumber id="monto" v-model="inversionForm.monto" mode="currency" currency="PEN" locale="es-PE" class="w-full" />
        </div>
        <div class="field col-12">
          <label for="notas">Notas</label>
          <Textarea id="notas" v-model="inversionForm.notas" rows="3" class="w-full" />
        </div>
      </div>
      <template #footer>
        <Button label="Cancelar" severity="secondary" @click="inversionDialog = false" />
        <Button label="Guardar" @click="guardarInversion" />
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

    <Dialog v-model:visible="compraDetalleDialog" header="Detalle de compra" :modal="true" :style="{ width: '560px' }">
      <div v-if="compraSeleccionada.codigo" class="detalle-info">
        <div class="d-row"><span class="d-label">Código</span><span>{{ compraSeleccionada.codigo }}</span></div>
        <div class="d-row"><span class="d-label">Proveedor</span><span>{{ compraSeleccionada.proveedor || '-' }}</span></div>
        <div class="d-row"><span class="d-label">Fecha</span><span>{{ fmtFecha(compraSeleccionada.fecha) }}</span></div>
        <div class="d-row"><span class="d-label">Total</span><span>S/. {{ fmt2(compraSeleccionada.total_compra) }}</span></div>
        <h4 class="sub-det">Productos</h4>
        <div v-for="d in compraSeleccionada.detalle || []" :key="d.id_detalle" class="det-line">
          <span>{{ d.producto }}</span>
          <span>{{ d.cantidad }} × S/. {{ fmt2(d.precio_unitario) }} = S/. {{ fmt2(d.subtotal) }}</span>
        </div>
        <div class="d-row"><span class="d-label">Notas</span><span>{{ compraSeleccionada.notas || '-' }}</span></div>
      </div>
    </Dialog>

    <Dialog v-model:visible="inversionDetalleDialog" header="Detalle de inversión" :modal="true" :style="{ width: '480px' }">
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
const compras = ref([])
const inversiones = ref([])
const movimientos = ref([])
const proveedores = ref([])
const resumen = ref({ valor_total: 0, inversiones_mes: 0, articulos_registrados: 0, productos_mes: 0 })
const vista = ref('productos')
const busqueda = ref('')
const categoriaFiltro = ref(null)
const movBusqueda = ref('')
const movTipo = ref(null)
const editingRows = ref([])
const productoDialog = ref(false)
const compraDialog = ref(false)
const inversionDialog = ref(false)
const proveedorDialog = ref(false)
const compraDetalleDialog = ref(false)
const inversionDetalleDialog = ref(false)
const editing = ref({})
const form = ref({})
const compraForm = ref({})
const inversionForm = ref({})
const provForm = ref({ nombre: '' })
const compraSeleccionada = ref({})

const fmt = (v) => Number(v || 0).toFixed(2)
const fmt2 = (v) => Number(v || 0).toFixed(2)
const fmtFecha = (v) => v ? String(v).slice(0, 10) : '-'
const fmtFechaHora = (v) => v ? String(v).slice(0, 16).replace('T', ' ') : '-'

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

const cargarCompras = async () => {
  const res = await api.get('/inventario/compras')
  if (res.data.success) compras.value = res.data.data
}

const cargarInversiones = async () => {
  const res = await api.get('/inventario/inversiones')
  if (res.data.success) inversiones.value = res.data.data
}

const cargarMovimientos = async () => {
  const params = {}
  if (movBusqueda.value) params.producto = movBusqueda.value
  if (movTipo.value) params.tipo = movTipo.value
  const res = await api.get('/inventario/movimientos', { params })
  if (res.data.success) movimientos.value = res.data.data
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
  compraForm.value = { id_proveedor: null, detalle: [{ id_producto: null, cantidad: 1, precio_unitario: 0 }], notas: '' }
  compraDialog.value = true
}

const agregarLinea = () => {
  compraForm.value.detalle.push({ id_producto: null, cantidad: 1, precio_unitario: 0 })
}

const quitarLinea = (idx) => {
  compraForm.value.detalle.splice(idx, 1)
}

const guardarCompra = async () => {
  try {
    const lineas = compraForm.value.detalle.filter(l => l.id_producto && l.cantidad > 0)
    if (!lineas.length) {
      toast.add({ severity: 'warn', summary: 'Agrega al menos un producto con cantidad', life: 3000 })
      return
    }
    await api.post('/inventario/compras', {
      id_proveedor: compraForm.value.id_proveedor || null,
      notas: compraForm.value.notas,
      detalle: lineas
    })
    toast.add({ severity: 'success', summary: 'Compra registrada y stock actualizado', life: 2500 })
    compraDialog.value = false
    await Promise.all([cargarCompras(), cargarProductos(), cargarMovimientos(), cargarResumen()])
  } catch (e) {
    toast.add({ severity: 'error', summary: e.response?.data?.error || 'Error al registrar', life: 3500 })
  }
}

const verCompra = async (compra) => {
  try {
    const res = await api.get(`/inventario/compras/${compra.id_compra}`)
    if (res.data.success) {
      compraSeleccionada.value = res.data.data
      compraDetalleDialog.value = true
    }
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error al cargar detalle', life: 3000 })
  }
}

const eliminarCompra = async (compra) => {
  if (!confirm(`¿Anular la compra ${compra.codigo}? Se revertirá el stock.`)) return
  try {
    await api.delete(`/inventario/compras/${compra.id_compra}`)
    toast.add({ severity: 'success', summary: 'Compra anulada y stock revertido', life: 2500 })
    await Promise.all([cargarCompras(), cargarProductos(), cargarMovimientos(), cargarResumen()])
  } catch (e) {
    toast.add({ severity: 'error', summary: e.response?.data?.error || 'Error al anular', life: 3500 })
  }
}

const openInversion = () => {
  inversionForm.value = { descripcion: '', id_proveedor: null, monto: 0, notas: '' }
  inversionDialog.value = true
}

const guardarInversion = async () => {
  try {
    await api.post('/inventario/inversiones', inversionForm.value)
    toast.add({ severity: 'success', summary: 'Inversión registrada', life: 2500 })
    inversionDialog.value = false
    await Promise.all([cargarInversiones(), cargarResumen()])
  } catch (e) {
    toast.add({ severity: 'error', summary: e.response?.data?.message || 'Error al registrar', life: 3500 })
  }
}

const verInversion = (inv) => {
  compraSeleccionada.value = inv
  inversionDetalleDialog.value = true
}

const eliminarInversion = async (inv) => {
  await api.delete(`/inventario/inversiones/${inv.id_inversion}`)
  toast.add({ severity: 'success', summary: 'Inversión eliminada', life: 2500 })
  await Promise.all([cargarInversiones(), cargarResumen()])
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

onMounted(async () => {
  await Promise.all([
    cargarProductos(), cargarCategorias(), cargarCompras(), cargarInversiones(),
    cargarMovimientos(), cargarProveedores(), cargarResumen()
  ])
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
.sub-det { margin: 1rem 0 0.5rem; }
.det-line { display: flex; justify-content: space-between; gap: 1rem; padding: 0.35rem 0; font-size: 0.9rem; border-bottom: 1px dashed var(--border-color); }
.mt-1 { margin-top: 0.25rem; }
.detalle-row { display: grid; grid-template-columns: 2fr 1fr 1.5fr auto; gap: 0.5rem; margin-bottom: 0.5rem; align-items: center; }
.mov-tipo { padding: 0.15rem 0.6rem; border-radius: 999px; font-size: 0.75rem; font-weight: 600; }
.mov-entrada { background: rgba(34, 197, 94, 0.12); color: #16a34a; }
.mov-salida { background: rgba(239, 68, 68, 0.12); color: #dc2626; }
.mov-ajuste { background: rgba(245, 158, 11, 0.15); color: #b45309; }
</style>
