<template>
  <div class="salarios-view">
    <h1>Calculo de Salarios</h1>
    
    <div class="actions">
      <Button label="Calcular Mes" icon="pi pi-calculator" @click="calcularMes" />
      <DatePicker v-model="mesSeleccionado" view="month" date-format="mm/yy" placeholder="Seleccionar mes" />
    </div>
    
    <DataTable :value="salarios" class="mt-4">
      <Column field="id_usuario" header="Empleado"></Column>
      <Column field="sueldo_base" header="Sueldo Base">
        <template #body="slotProps">
          S/. {{ slotProps.data.sueldo_base }}
        </template>
      </Column>
      <Column field="total_pagos" header="Pagos">
        <template #body="slotProps">
          S/. {{ slotProps.data.total_pagos }}
        </template>
      </Column>
      <Column field="total_adelantos" header="Adelantos">
        <template #body="slotProps">
          S/. {{ slotProps.data.total_adelantos }}
        </template>
      </Column>
      <Column header="Neto">
        <template #body="slotProps">
          <strong>S/. {{ slotProps.data.neto }}</strong>
        </template>
      </Column>
    </DataTable>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import DatePicker from 'primevue/datepicker'
import api from '../config/axios'

const salarios = ref([])
const mesSeleccionado = ref(new Date())

onMounted(() => calcularMes())

const calcularMes = async () => {
  const mes = mesSeleccionado.value.getMonth() + 1
  const anio = mesSeleccionado.value.getFullYear()
  const res = await api.get(`/personal/salarios?mes=${mes}&anio=${anio}`)
  if (res.data.success) salarios.value = res.data.data
}
</script>

<style scoped>
.salarios-view { padding: 2rem; }
.actions { display: flex; gap: 1rem; margin-bottom: 1rem; align-items: center; }
.mt-4 { margin-top: 1rem; }
</style>
