<template>
  <div class="personal-view">
    <h1>Gestion del Personal</h1>
    
    <div class="actions">
      <Button label="Agregar Empleado" icon="pi pi-plus" @click="agregarEmpleadoDialog" />
    </div>
    
    <DataTable :value="empleados" class="mt-4" :paginator="true" :rows="10" :filters="filtros">
      <template #header>
        <div class="flex justify-content-between">
          <span class="p-input-icon-left">
            <i class="pi pi-search" />
            <InputText v-model="filtros['global'].value" placeholder="Buscar empleados..." />
          </span>
        </div>
      </template>
      <Column field="dni" header="DNI"></Column>
      <Column field="nombres" header="Nombres"></Column>
      <Column field="apellido" header="Apellido"></Column>
      <Column field="correo" header="Correo"></Column>
      <Column field="telefono" header="Telefono"></Column>
      <Column field="turno" header="Turno"></Column>
      <Column header="Acciones">
        <template #body="slotProps">
          <Button icon="pi pi-pencil" severity="info" @click="editarEmpleado(slotProps.data)" />
          <Button icon="pi pi-trash" severity="danger" @click="eliminarEmpleado(slotProps.data)" />
        </template>
      </Column>
    </DataTable>
    
    <Dialog v-model:visible="dialogEmpleado" :header="empleadoSeleccionado.id_usuario ? 'Editar Empleado' : 'Nuevo Empleado'" :modal="true">
      <div class="field">
        <label for="dni">DNI</label>
        <InputText id="dni" v-model="empleadoForm.dni" />
      </div>
      <div class="field">
        <label for="nombres">Nombres</label>
        <InputText id="nombres" v-model="empleadoForm.nombres" />
      </div>
      <div class="field">
        <label for="apellido">Apellido</label>
        <InputText id="apellido" v-model="empleadoForm.apellido" />
      </div>
      <div class="field">
        <label for="correo">Correo</label>
        <InputText id="correo" v-model="empleadoForm.correo" />
      </div>
      <div class="field">
        <label for="telefono">Telefono</label>
        <InputText id="telefono" v-model="empleadoForm.telefono" />
      </div>
      <div class="field">
        <label for="turno">Turno</label>
        <Select id="turno" v-model="empleadoForm.turno" :options="turnos" optionLabel="label" optionValue="value" />
      </div>
      <template #footer>
        <Button label="Cancelar" severity="secondary" @click="dialogEmpleado = false" />
        <Button label="Guardar" @click="guardarEmpleado" />
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
const dialogEmpleado = ref(false)
const empleadoSeleccionado = ref({})
const empleadoForm = ref({
  dni: '',
  nombres: '',
  apellido: '',
  correo: '',
  telefono: '',
  turno: 'Mañana'
})

const turnos = [
  { label: 'Mañana', value: 'Mañana' },
  { label: 'Tarde', value: 'Tarde' },
  { label: 'Noche', value: 'Noche' }
]

const filtros = ref({
  global: { value: null, matchMode: FilterMatchMode.CONTAINS }
})

onMounted(async () => {
  await cargarEmpleados()
})

const cargarEmpleados = async () => {
  try {
    const response = await api.get('/personal/')
    if (response.data.success) {
      empleados.value = response.data.data
    }
  } catch (error) {
    console.error('Error cargando empleados:', error)
  }
}

const agregarEmpleadoDialog = () => {
  empleadoSeleccionado.value = {}
  empleadoForm.value = { dni: '', nombres: '', apellido: '', correo: '', telefono: '', turno: 'Mañana' }
  dialogEmpleado.value = true
}

const editarEmpleado = (empleado) => {
  empleadoSeleccionado.value = empleado
  empleadoForm.value = { ...empleado }
  dialogEmpleado.value = true
}

const guardarEmpleado = async () => {
  try {
    if (empleadoSeleccionado.value.id_usuario) {
      await api.put(`/personal/${empleadoSeleccionado.value.id_usuario}`, empleadoForm.value)
    } else {
      await api.post('/personal/', empleadoForm.value)
    }
    await cargarEmpleados()
    dialogEmpleado.value = false
  } catch (error) {
    console.error('Error guardando empleado:', error)
  }
}

const eliminarEmpleado = async (empleado) => {
  if (confirm('¿Estás seguro de eliminar este empleado?')) {
    try {
      await api.delete(`/personal/${empleado.id_usuario}`)
      await cargarEmpleados()
    } catch (error) {
      console.error('Error eliminando empleado:', error)
    }
  }
}
</script>

<style scoped>
.personal-view {
  padding: 2rem;
}

.actions {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.mt-4 {
  margin-top: 1rem;
}

.field {
  margin-bottom: 1rem;
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
}
</style>
