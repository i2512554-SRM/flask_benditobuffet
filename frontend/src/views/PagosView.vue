<template>
  <div class="pagos-view">
    <h1>Historial de Pagos</h1>
    
    <div class="actions">
      <Button label="Registrar Pago" icon="pi pi-plus" @click="registrarDialog" />
    </div>
    
    <DataTable :value="pagos" :paginator="true" :rows="10" class="mt-4">
      <Column field="fecha" header="Fecha" sortable></Column>
      <Column field="id_usuario" header="Empleado"></Column>
      <Column field="tipo" header="Tipo" sortable></Column>
      <Column field="monto" header="Monto" sortable>
        <template #body="slotProps">
          S/. {{ slotProps.data.monto }}
        </template>
      </Column>
      <Column field="estado" header="Estado">
        <template #body="slotProps">
          <Tag :value="slotProps.data.estado" :severity="slotProps.data.estado === 'Completado' ? 'success' : 'warning'" />
        </template>
      </Column>
      <Column field="descripcion" header="Descripcion"></Column>
    </DataTable>
    
    <Dialog v-model:visible="dialogVisible" header="Registrar Pago" :modal="true" :style="{ width: '500px' }">
      <div class="formgrid grid">
        <div class="field col-6">
          <label for="empleado">Empleado</label>
          <Select id="empleado" v-model="form.id_usuario" :options="empleados" optionLabel="nombres" optionValue="id_usuario" class="w-full" />
        </div>
        <div class="field col-6">
          <label for="tipo">Tipo</label>
          <Select id="tipo" v-model="form.tipo" :options="tiposPago" optionLabel="label" optionValue="value" class="w-full" />
        </div>
        <div class="field col-6">
          <label for="monto">Monto</label>
          <InputNumber id="monto" v-model="form.monto" mode="currency" currency="PEN" locale="es-PE" class="w-full" />
        </div>
        <div class="field col-6">
          <label for="fecha">Fecha</label>
          <DatePicker id="fecha" v-model="form.fecha" date-format="yy-mm-dd" class="w-full" />
        </div>
        <div class="field col-12">
          <label for="descripcion">Descripcion</label>
          <InputText id="descripcion" v-model="form.descripcion" class="w-full" />
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
import DatePicker from 'primevue/datepicker'
import Tag from 'primevue/tag'
import api from '../config/axios'

const pagos = ref([])
const empleados = ref([])
const dialogVisible = ref(false)
const form = ref({})

const tiposPago = [
  { label: 'Salario', value: 'Salario' },
  { label: 'Adelanto', value: 'Adelanto' },
  { label: 'Bonificacion', value: 'Bonificacion' },
  { label: 'Descuento', value: 'Descuento' }
]

onMounted(async () => {
  await Promise.all([cargarPagos(), cargarEmpleados()])
})

const cargarPagos = async () => {
  const res = await api.get('/personal/pagos')
  if (res.data.success) pagos.value = res.data.data
}

const cargarEmpleados = async () => {
  const res = await api.get('/personal/')
  if (res.data.success) empleados.value = res.data.data
}

const registrarDialog = () => {
  form.value = { id_usuario: null, tipo: 'Salario', monto: 0, fecha: new Date(), descripcion: '' }
  dialogVisible.value = true
}

const guardar = async () => {
  await api.post('/personal/pagos', form.value)
  await cargarPagos()
  dialogVisible.value = false
}
</script>

<style scoped>
.pagos-view { padding: 2rem; }
.actions { display: flex; gap: 1rem; margin-bottom: 1rem; }
.mt-4 { margin-top: 1rem; }
</style>
