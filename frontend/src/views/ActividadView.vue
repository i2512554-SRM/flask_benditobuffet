<template>
  <div>
    <div class="page-hero">
      <VolverBtn to="/seguridad" />
      <h1>Historial de Actividad</h1>
      <p>Registro detallado de las acciones realizadas por los usuarios</p>
    </div>

    <div class="card-section">
      <DataTable :value="actividad" stripedRows paginator :rows="15" :rowsPerPageOptions="[15, 30, 50, 100]"
        class="p-datatable-sm" :loading="loading">
        <Column field="fecha" header="Fecha y hora" sortable></Column>
        <Column field="usuario" header="Usuario" sortable></Column>
        <Column field="correo" header="Correo" sortable></Column>
        <Column field="accion" header="Acción" sortable></Column>
      </DataTable>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import api from '../config/axios'

const loading = ref(true)
const actividad = ref([])

const load = async () => {
  loading.value = true
  try {
    const res = await api.get('/admin/actividad', { params: { limit: 300 } })
    if (res.data.success) actividad.value = res.data.data
  } catch (err) {
    console.error('Error loading actividad:', err)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.card-section {
  margin-top: 1.5rem;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  padding: 1.25rem;
  box-shadow: var(--shadow-soft);
}
</style>