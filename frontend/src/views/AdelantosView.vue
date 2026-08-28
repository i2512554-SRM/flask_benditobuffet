<template>
  <div class="adelantos-view">
    <h1>Adelantos de Salario</h1>
    
    <div class="actions">
      <Button label="Registrar Adelanto" icon="pi pi-plus" @click="registrarDialog" />
    </div>
    
    <DataTable :value="adelantos" :paginator="true" :rows="10" class="mt-4">
      <Column field="fecha" header="Fecha" sortable></Column>
      <Column field="id_usuario" header="Empleado"></Column>
      <Column field="monto" header="Monto" sortable>
        <template #body="slotProps">
          S/. {{ slotProps.data.monto }}
        </template>
      </Column>
      <Column field="estado" header="Estado">
        <template #body="slotProps">
          <Tag :value="slotProps.data.estado" :severity="slotProps.data.estado === 'Pendiente' ? 'warning' : 'success'" />
        </template>
      </Column>
      <Column field="motivo" header="Motivo"></Column>
    </DataTable>
    
    <Dialog v-model:visible="dialogVisible" header="Registrar Adelanto" :modal="true" :style="{ width: '500px' }">
      <div class="formgrid grid">
        <div class="field col-6">
          <label for="empleado">Empleado</label>
          <Select id="empleado" v-model="form.id_usuario" :options="empleados" optionLabel="nombres" optionValue="id_usuario" class="w-full" />
        </div>
        <div class="field col-6">
          <label for="monto">Monto</label>
          <InputNumber id="monto" v-model="form.monto" mode="currency" currency="PEN" locale="es-PE" class="w-full" />
        </div>
        <div class="field col-12">
          <label for="motivo">Motivo</label>
          <InputText id="motivo" v-model="form.motivo" class="w-full" />
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
import Tag from 'primevue/tag'
import api from '../config/axios'

const adelantos = ref([])
const empleados = ref([])
const dialogVisible = ref(false)
const form = ref({})

onMounted(async () => {
  await Promise.all([cargarAdelantos(), cargarEmpleados()])
})

const cargarAdelantos = async () => {
  const res = await api.get('/personal/adelantos')
  if (res.data.success) adelantos.value = res.data.data
}

const cargarEmpleados = async () => {
  const res = await api.get('/personal/')
  if (res.data.success) empleados.value = res.data.data
}

const registrarDialog = () => {
  form.value = { id_usuario: null, monto: 0, motivo: '' }
  dialogVisible.value = true
}

const guardar = async () => {
  await api.post('/personal/adelantos', form.value)
  await cargarAdelantos()
  dialogVisible.value = false
}
</script>

<style scoped>
.adelantos-view { padding: 2rem; }
.actions { display: flex; gap: 1rem; margin-bottom: 1rem; }
.mt-4 { margin-top: 1rem; }
</style>
