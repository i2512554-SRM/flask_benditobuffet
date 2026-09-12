<template>
  <div>
    <div class="page-hero">
      <VolverBtn to="/seguridad" />
      <h1>Roles del Sistema</h1>
      <p>Roles de acceso y cantidad de usuarios asignados</p>
    </div>

    <div class="card-section">
      <DataTable :value="roles" stripedRows paginator :rows="10" :rowsPerPageOptions="[10, 25, 50]"
        class="p-datatable-sm" :loading="loading">
        <Column field="id_rol" header="ID"></Column>
        <Column field="nombre" header="Rol" sortable></Column>
        <Column field="total_usuarios" header="Usuarios" sortable>
          <template #body="{ data }">
            <Tag :value="String(data.total_usuarios)" severity="info" />
          </template>
        </Column>
        <Column header="Estado">
          <template #body="{ data }">
            <Tag :value="data.estado ? 'Activo' : 'Inactivo'" :severity="data.estado ? 'success' : 'danger'" />
          </template>
        </Column>
        <Column field="fecha_creacion" header="Creado" sortable></Column>
      </DataTable>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'
import api from '../config/axios'

const loading = ref(true)
const roles = ref([])

const load = async () => {
  loading.value = true
  try {
    const res = await api.get('/admin/roles')
    if (res.data.success) roles.value = res.data.data
  } catch (err) {
    console.error('Error loading roles:', err)
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