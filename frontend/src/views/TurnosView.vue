<template>
  <div class="turnos-view">
    <h1>Turnos de Trabajo</h1>
    
    <DataTable :value="empleados" class="mt-4">
      <Column field="nombres" header="Empleado"></Column>
      <Column field="apellido" header="Apellido"></Column>
      <Column field="turno" header="Turno Actual">
        <template #body="slotProps">
          <Tag :value="slotProps.data.turno" :severity="getSeverity(slotProps.data.turno)" />
        </template>
      </Column>
      <Column header="Acciones">
        <template #body="slotProps">
          <Select v-model="slotProps.data.turno" :options="turnos" optionLabel="label" optionValue="value" 
                  @change="cambiarTurno(slotProps.data)" class="w-full" style="width: 150px" />
        </template>
      </Column>
    </DataTable>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Select from 'primevue/select'
import Tag from 'primevue/tag'
import api from '../config/axios'

const empleados = ref([])
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

const getSeverity = (turno) => {
  const map = { Manana: 'success', Tarde: 'warn', Noche: 'danger' }
  return map[turno] || 'info'
}

const cambiarTurno = async (emp) => {
  await api.put(`/personal/${emp.id_usuario}`, { turno: emp.turno })
}
</script>

<style scoped>
.turnos-view { padding: 2rem; }
.mt-4 { margin-top: 1rem; }
</style>
