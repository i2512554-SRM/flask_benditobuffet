<template>
  <div class="solicitudes-view">
    <VolverBtn to="/personal" />
    <div class="page-header animate-item">
      <div>
        <h1>Solicitudes de Adelantos</h1>
        <p>Revisa y gestiona las solicitudes de adelanto del personal</p>
      </div>
      <Button label="Actualizar" icon="pi pi-refresh" severity="secondary" :loading="loading" @click="cargar" />
    </div>

    <!-- Skeleton -->
    <Transition name="fade">
      <div v-if="loading" class="table-card">
        <div v-for="n in 4" :key="n" class="skeleton-row">
          <div class="sk sk-line w-20"></div>
          <div class="sk sk-line w-15"></div>
          <div class="sk sk-line w-30"></div>
          <div class="sk sk-line w-15"></div>
        </div>
      </div>
    </Transition>

    <Transition name="fade-up">
      <div v-if="!loading" class="table-card">
        <DataTable :value="solicitudes" :paginator="true" :rows="10" dataKey="id_adelanto" stripedRows>
          <Column field="empleado" header="Empleado" sortable>
            <template #body="slotProps">
              <div class="emp-cell">
                <span class="emp-avatar">{{ iniciales(slotProps.data.empleado) }}</span>
                <span class="emp-nombre">{{ slotProps.data.empleado }}</span>
              </div>
            </template>
          </Column>
          <Column field="fecha" header="Fecha" sortable></Column>
          <Column field="motivo" header="Motivo"></Column>
          <Column field="monto" header="Monto" sortable>
            <template #body="slotProps">
              <strong>S/. {{ formatMoney(slotProps.data.monto) }}</strong>
            </template>
          </Column>
          <Column field="estado" header="Estado" sortable>
            <template #body="slotProps">
              <Tag :value="slotProps.data.estado" :severity="getEstadoSeverity(slotProps.data.estado)" class="tag-anim" />
            </template>
          </Column>
          <Column field="respuesta_admin" header="Respuesta">
            <template #body="slotProps">
              <span class="respuesta">{{ slotProps.data.respuesta_admin || '—' }}</span>
            </template>
          </Column>
          <Column header="Acciones" style="min-width: 220px">
            <template #body="slotProps">
              <div v-if="slotProps.data.estado === 'Pendiente'" class="acciones-row">
                <Button label="Aprobar" icon="pi pi-check" severity="success" size="small" @click="abrirModal(slotProps.data, 'aprobar')" />
                <Button label="Rechazar" icon="pi pi-times" severity="danger" size="small" outlined @click="abrirModal(slotProps.data, 'rechazar')" />
              </div>
              <span v-else class="gestionado">
                <i class="fa-solid fa-circle-check"></i> Gestionado
              </span>
            </template>
          </Column>
          <template #empty>
            <div class="empty-state">
              <i class="fa-solid fa-file-circle-question"></i>
              <p>No hay solicitudes de adelanto registradas.</p>
            </div>
          </template>
        </DataTable>
      </div>
    </Transition>

    <Dialog v-model:visible="dialogVisible" :header="modalAccion === 'aprobar' ? 'Aprobar adelanto' : 'Rechazar adelanto'" :modal="true" :style="{ width: '500px' }">
      <p class="modal-desc">Agrega una respuesta opcional para el empleado:</p>
      <Textarea v-model="respuesta" rows="4" placeholder="Ej: Adelanto aprobado, se acreditará en tu próximo pago..." maxlength="500" class="w-full" />
      <template #footer>
        <Button label="Cancelar" severity="secondary" @click="dialogVisible = false" />
        <Button
          :label="modalAccion === 'aprobar' ? 'Aprobar' : 'Rechazar'"
          :severity="modalAccion === 'aprobar' ? 'success' : 'danger'"
          :loading="gestionando"
          @click="gestionar"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import VolverBtn from '../components/ui/VolverBtn.vue'
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
const loading = ref(true)
const dialogVisible = ref(false)
const modalAccion = ref('aprobar')
const solicitudActual = ref(null)
const respuesta = ref('')
const gestionando = ref(false)

const formatMoney = (val) => Number(val || 0).toLocaleString('es-PE', { minimumFractionDigits: 2 })

const iniciales = (nombre) => {
  if (!nombre) return '?'
  return nombre.split(' ').map(p => p[0]).slice(0, 2).join('').toUpperCase()
}

const getEstadoSeverity = (estado) => {
  const map = { Pendiente: 'warning', Aprobado: 'success', Rechazado: 'danger', Cancelado: 'secondary' }
  return map[estado] || 'info'
}

const cargar = async () => {
  loading.value = true
  try {
    const res = await api.get('/admin/adelantos')
    if (res.data.success) solicitudes.value = res.data.data
  } catch (err) {
    toast.add({ severity: 'error', summary: 'No se pudieron cargar las solicitudes', life: 3500 })
  } finally {
    loading.value = false
  }
}

const abrirModal = (sol, accion) => {
  solicitudActual.value = sol
  modalAccion.value = accion
  respuesta.value = ''
  dialogVisible.value = true
}

const gestionar = async () => {
  gestionando.value = true
  try {
    const res = await api.put(`/admin/adelantos/${solicitudActual.value.id_adelanto}`, {
      accion: modalAccion.value,
      respuesta: respuesta.value
    })
    if (res.data.success) {
      toast.add({ severity: 'success', summary: modalAccion.value === 'aprobar' ? 'Adelanto aprobado' : 'Adelanto rechazado', life: 3000 })
      dialogVisible.value = false
      await cargar()
    } else {
      toast.add({ severity: 'error', summary: res.data.error || 'Error al gestionar', life: 4000 })
    }
  } catch (err) {
    toast.add({ severity: 'error', summary: err.response?.data?.error || 'No se pudo gestionar', life: 4000 })
  } finally {
    gestionando.value = false
  }
}

onMounted(cargar)
</script>

<style scoped>
.solicitudes-view { padding: 2rem; }

.page-header {
  display: flex; justify-content: space-between; align-items: center;
  flex-wrap: wrap; gap: 1rem; margin-bottom: 1.25rem;
}
.page-header h1 { margin: 0; font-size: 1.5rem; color: var(--text-main); }
.page-header p { margin: 0.25rem 0 0; color: var(--text-muted); font-size: 0.9rem; }

.table-card {
  background: var(--bg-card); border: 1px solid var(--border-color);
  border-radius: 14px; padding: 1.25rem; box-shadow: var(--shadow-soft);
}

.emp-cell { display: flex; align-items: center; gap: 0.75rem; }
.emp-avatar {
  width: 34px; height: 34px; border-radius: 10px; flex-shrink: 0;
  background: linear-gradient(135deg, #8b5cf6, #a78bfa);
  color: #fff; font-weight: 700; font-size: 0.78rem;
  display: flex; align-items: center; justify-content: center;
}
.emp-nombre { font-weight: 600; color: var(--text-main); }

.respuesta { font-size: 0.85rem; color: var(--text-muted); }

.acciones-row { display: flex; gap: 0.5rem; }
.acciones-row button { transition: transform 0.15s cubic-bezier(0.22, 1, 0.36, 1), box-shadow 0.15s ease; }
.acciones-row button:hover { transform: translateY(-1px); }
.acciones-row button:active { transform: translateY(0) scale(0.97); }

.tag-anim { animation: tag-in 0.3s cubic-bezier(0.22, 1, 0.36, 1); }
@keyframes tag-in { from { opacity: 0; transform: scale(0.9); } to { opacity: 1; transform: scale(1); } }

.gestionado { color: var(--text-muted); font-size: 0.85rem; display: inline-flex; align-items: center; gap: 0.35rem; }
.gestionado i { color: #16a34a; }

.empty-state { text-align: center; padding: 2.5rem 1rem; color: var(--text-muted); }
.empty-state i { font-size: 1.75rem; opacity: 0.5; display: block; margin-bottom: 0.5rem; }

.modal-desc { margin: 0 0 0.5rem; color: var(--text-muted); font-size: 0.85rem; }

/* Skeletons */
.skeleton-row { display: flex; align-items: center; gap: 1rem; padding: 0.9rem 0.25rem; border-bottom: 1px solid var(--border-color); }
.sk {
  border-radius: 8px;
  background: linear-gradient(90deg, rgba(148,163,184,0.12) 25%, rgba(148,163,184,0.25) 50%, rgba(148,163,184,0.12) 75%);
  background-size: 400% 100%;
  animation: shimmer 1.4s infinite linear;
}
.sk-line { height: 14px; }
.w-30 { width: 30%; } .w-20 { width: 20%; } .w-15 { width: 15%; }
@keyframes shimmer { 0% { background-position: 100% 0; } 100% { background-position: -100% 0; } }

.animate-item { animation: slide-in 0.45s cubic-bezier(0.22, 1, 0.36, 1); }
@keyframes slide-in { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: none; } }

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.fade-up-enter-active { transition: all 0.45s cubic-bezier(0.22, 1, 0.36, 1); }
.fade-up-enter-from { opacity: 0; transform: translateY(14px); }
.fade-up-enter-to { opacity: 1; transform: none; }

@media (max-width: 768px) {
  .acciones-row { flex-direction: column; }
}
</style>
