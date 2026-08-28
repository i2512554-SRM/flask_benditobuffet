<template>
  <div class="inventario-view">
    <h1>Inventario</h1>
    
    <div class="actions">
      <Button label="Agregar Producto" icon="pi pi-plus" @click="agregarDialog" />
    </div>
    
    <DataTable :value="productos" :paginator="true" :rows="10" :filters="filtros" class="mt-4">
      <template #header>
        <div class="flex justify-content-between">
          <span class="p-input-icon-left">
            <i class="pi pi-search" />
            <InputText v-model="filtros['global'].value" placeholder="Buscar productos..." />
          </span>
        </div>
      </template>
      <Column field="nombre" header="Nombre" sortable></Column>
      <Column field="categoria" header="Categoria" sortable></Column>
      <Column field="precio" header="Precio" sortable>
        <template #body="slotProps">
          S/. {{ slotProps.data.precio }}
        </template>
      </Column>
      <Column field="stock" header="Stock" sortable></Column>
      <Column header="Acciones">
        <template #body="slotProps">
          <Button icon="pi pi-pencil" severity="info" text rounded @click="editar(slotProps.data)" />
          <Button icon="pi pi-trash" severity="danger" text rounded @click="eliminar(slotProps.data)" />
        </template>
      </Column>
    </DataTable>
    
    <Dialog v-model:visible="dialogVisible" :header="editing.id_producto ? 'Editar Producto' : 'Nuevo Producto'" :modal="true" :style="{ width: '500px' }">
      <div class="formgrid grid">
        <div class="field col-12">
          <label for="nombre">Nombre</label>
          <InputText id="nombre" v-model="form.nombre" class="w-full" />
        </div>
        <div class="field col-6">
          <label for="categoria">Categoria</label>
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
        <Button label="Cancelar" severity="secondary" @click="dialogVisible = false" />
        <Button label="Guardar" @click="guardar" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Select from 'primevue/select'
import { FilterMatchMode } from '@primevue/core/api'
import api from '../config/axios'

const productos = ref([])
const categorias = ref([])
const dialogVisible = ref(false)
const editing = ref({})
const form = ref({})
const filtros = ref({ global: { value: null, matchMode: FilterMatchMode.CONTAINS } })

onMounted(async () => {
  await Promise.all([cargarProductos(), cargarCategorias()])
})

const cargarProductos = async () => {
  const res = await api.get('/inventario/productos')
  if (res.data.success) productos.value = res.data.data
}

const cargarCategorias = async () => {
  const res = await api.get('/inventario/categorias')
  if (res.data.success) categorias.value = res.data.data
}

const agregarDialog = () => {
  editing.value = {}
  form.value = { nombre: '', id_categoria: null, precio: 0, stock: 0 }
  dialogVisible.value = true
}

const editar = (prod) => {
  editing.value = prod
  form.value = { ...prod }
  dialogVisible.value = true
}

const guardar = async () => {
  if (editing.value.id_producto) {
    await api.put(`/inventario/productos/${editing.value.id_producto}`, form.value)
  } else {
    await api.post('/inventario/productos', form.value)
  }
  await cargarProductos()
  dialogVisible.value = false
}

const eliminar = async (prod) => {
  if (confirm('Eliminar producto?')) {
    await api.delete(`/inventario/productos/${prod.id_producto}`)
    await cargarProductos()
  }
}
</script>

<style scoped>
.inventario-view { padding: 2rem; }
.actions { display: flex; gap: 1rem; margin-bottom: 1rem; }
.mt-4 { margin-top: 1rem; }
</style>
