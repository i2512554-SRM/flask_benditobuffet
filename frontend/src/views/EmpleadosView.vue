<template>
  <div class="empleados-view">
    <h1>Empleados</h1>
    
    <div class="actions">
      <Button label="Agregar Empleado" icon="pi pi-plus" @click="agregarDialog" />
    </div>
    
    <DataTable :value="empleados" :paginator="true" :rows="10" :filters="filtros" 
               v-model:selection="empleadosSeleccionados" selectionMode="multiple"
               dataKey="id_usuario" class="mt-4">
      <template #header>
        <div class="flex justify-content-between">
          <span class="p-input-icon-left">
            <i class="pi pi-search" />
            <InputText v-model="filtros['global'].value" placeholder="Buscar..." />
          </span>
        </div>
      </template>
      <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
      <Column field="dni" header="DNI" sortable></Column>
      <Column field="nombres" header="Nombres" sortable></Column>
      <Column field="apellido" header="Apellido" sortable></Column>
      <Column field="correo" header="Correo"></Column>
      <Column field="telefono" header="Telefono"></Column>
      <Column field="turno" header="Turno" sortable></Column>
      <Column header="Acciones" style="min-width: 8rem">
        <template #body="slotProps">
          <Button icon="pi pi-pencil" severity="info" text rounded @click="editar(slotProps.data)" />
          <Button icon="pi pi-trash" severity="danger" text rounded @click="eliminar(slotProps.data)" />
        </template>
      </Column>
    </DataTable>
    
    <Dialog v-model:visible="dialogVisible" :header="editing.id_usuario ? 'Editar Empleado' : 'Nuevo Empleado'" :modal="true" :style="{ width: '500px' }">
      <div class="formgrid grid">
        <div class="field col-6">
          <label for="dni">DNI</label>
          <InputText id="dni" v-model="form.dni" class="w-full" />
        </div>
        <div class="field col-6">
          <label for="nombres">Nombres</label>
          <InputText id="nombres" v-model="form.nombres" class="w-full" />
        </div>
        <div class="field col-6">
          <label for="apellido">Apellido</label>
          <InputText id="apellido" v-model="form.apellido" class="w-full" />
        </div>
        <div class="field col-6">
          <label for="correo">Correo</label>
          <InputText id="correo" v-model="form.correo" class="w-full" />
        </div>
        <div class="field col-6">
          <label for="telefono">Telefono</label>
          <InputText id="telefono" v-model="form.telefono" class="w-full" />
        </div>
        <div class="field col-6">
          <label for="turno">Turno</label>
          <Select id="turno" v-model="form.turno" :options="turnos" optionLabel="label" optionValue="value" class="w-full" />
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
import Select from 'primevue/select'
import { FilterMatchMode } from '@primevue/core/api'
import api from '../config/axios'

const empleados = ref([])
const empleadosSeleccionados = ref([])
const dialogVisible = ref(false)
const editing = ref({})
const form = ref({})
const filtros = ref({ global: { value: null, matchMode: FilterMatchMode.CONTAINS } })
const turnos = [
  { label: 'Manana', value: 'Manana' },
  { label: 'Tarde', value: 'Tarde' },
  { label: 'Noche', value: 'Noche' }
]

onMounted(() => cargar())

const cargar = async () => {
  const res = await api.get('/personal/')
  if (res.data.success) empleados.value = res.data.data
}

const agregarDialog = () => {
  editing.value = {}
  form.value = { dni: '', nombres: '', apellido: '', correo: '', telefono: '', turno: 'Manana' }
  dialogVisible.value = true
}

const editar = (emp) => {
  editing.value = emp
  form.value = { ...emp }
  dialogVisible.value = true
}

const guardar = async () => {
  if (editing.value.id_usuario) {
    await api.put(`/personal/${editing.value.id_usuario}`, form.value)
  } else {
    await api.post('/personal/', form.value)
  }
  await cargar()
  dialogVisible.value = false
}

const eliminar = async (emp) => {
  if (confirm('Eliminar empleado?')) {
    await api.delete(`/personal/${emp.id_usuario}`)
    await cargar()
  }
}
</script>

<style scoped>
.empleados-view { padding: 2rem; }
.actions { display: flex; gap: 1rem; margin-bottom: 1rem; }
.mt-4 { margin-top: 1rem; }
</style>
