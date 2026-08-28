<template>
  <div class="solicitudes-view">
    <div class="page-header">
      <h1>Solicitudes de Adelantos</h1>
      <p>Revisa y gestiona las solicitudes de adelanto del personal</p>
    </div>

    <DataTable :value="solicitudes" :paginator="true" :rows="10" class="mt-4">
      <Column field="empleado" header="Empleado" sortable></Column>
      <Column field="fecha" header="Fecha" sortable></Column>
      <Column field="motivo" header="Motivo"></Column>
      <Column field="monto" header="Monto" sortable>
        <template #body="slotProps">
          S/. {{ formatMoney(slotProps.data.monto) }}
        </template>
      </Column>
      <Column field="estado" header="Estado">
        <template #body="slotProps">
          <Tag :value="slotProps.data.estado" :severity="getEstadoSeverity(slotProps.data.estado)" />
        </template>
      </Column>
      <Column field="respuesta_admin" header="Respuesta">
        <template #body="slotProps">
          <span>{{ slotProps.data.respuesta_admin || '—' }}</span>
        </template>
      </Column>
      <Column header="Acciones">
        <template #body="slotProps">
          <template v-if="slotProps.data.estado === 'Pendiente'">
            <Button label="Aprobar" icon="pi pi-check" severity="success" size="small" @click="abrirModal(slotProps.data, 'aprobar')" class="mr-2" />
            <Button label="Rechazar" icon="pi pi-times" severity="danger" size="small" outlined @click="abrirModal(slotProps.data, 'rechazar')" />
          </template>
          <span v-else class="gestionado">Gestionado</span>
        </template>
      </Column>
    </DataTable>

    <Dialog v-model:visible="dialogVisible" :header="modalAccion === 'aprobar' ? 'Aprobar adelanto' : 'Rechazar adelanto'" :modal="true" :style="{ width: '500px' }">
      <p class="modal-desc">Agrega una respuesta opcional para el empleado:</p>
      <Textarea v-model="respuesta" rows="4" placeholder="Ej: Adelanto aprobado, se acreditara en tu proximo pago..." maxlength="500" class="w-full" />
      <template #footer>
        <Button label="Cancelar" severity="secondary" @click="dialogVisible = false" />
        <Button :label="modalAccion === 'aprobar' ? 'Aprobar' : 'Rechazar'" :severity="modalAccion === 'aprobar' ? 'success' : 'danger'" @click="gestionar" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import Dialog from 'primevue/dialog'
import Textarea from 'primevue/textarea'
import { useToast } from 'primevue/usetoast'
import api from '../config/axios'

const toast = useToast()
const solicitudes = ref([])
const dialogVisible = ref(false)
const modalAccion = ref('aprobar')
const solicitudActual = ref(null)
const respuesta = ref('')

const formatMoney = (val) => Number(val || 0).toLocaleString('es-PE', { minimumFractionDigits: 2 })

const getEstadoSeverity = (estado) => {
  const map = { Pendiente: 'warning', Aprobado: 'success', Rechazado: 'danger', Cancelado: 'secondary' }
  return map[estado] || 'info'
}

onMounted(cargar)

const cargar = async () => {
  try {
    const res = await api.get('/admin/adelantos')
    if (res.data.success) solicitudes.value = res.data.data
  } catch (err) {
    console.error('Error cargando solicitudes:', err)
  }
}

const abrirModal = (sol, accion) => {
  solicitudActual.value = sol
  modalAccion.value = accion
  respuesta.value = ''
  dialogVisible.value = true
}

const gestionar = async () => {
  try {
    const res = await api.put(`/admin/adelantos/${solicitudActual.value.id_adelanto}`, {
      accion: modalAccion.value,
      respuesta: respuesta.value
    })
    if (res.data.success) {
      toast.add({ severity: 'success', summary: 'Exito', detail: res.data.message, life: 3000 })
      dialogVisible.value = false
      await cargar()
    } else {
      toast.add({ severity: 'error', summary: 'Error', detail: res.data.error, life: 4000 })
    }
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Error', detail: err.response?.data?.error || 'No se pudo gestionar', life: 4000 })
  }
}
</script>

<style scoped>
.solicitudes-view { padding: 2rem; }

.page-header h1 {
  margin: 0;
  font-size: 1.5rem;
  color: var(--text-main);
}

.page-header p {
  margin: 0.25rem 0 0;
  color: var(--text-muted);
  font-size: 0.9rem;
}

.mt-4 { margin-top: 1rem; }
.mr-2 { margin-right: 0.5rem; }

.modal-desc {
  margin: 0 0 0.5rem;
  color: var(--text-muted);
  font-size: 0.85rem;
}

.gestionado {
  color: var(--text-muted);
  font-size: 0.85rem;
}
</style>
