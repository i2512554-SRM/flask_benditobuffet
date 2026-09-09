<template>
  <div class="cocina-view">
    <VolverBtn to="/cocinero" />
    <div class="page-header">
      <div>
        <h1>Solicitud de insumos</h1>
        <p>Registra las necesidades de la cocina y sigue su estado</p>
      </div>
    </div>

    <div class="grid-solicitudes">
      <div class="panel-solicitud">
        <h2 class="panel-title"><i class="fa-solid fa-basket-shopping"></i> Nueva solicitud</h2>
        <form class="form-grid" @submit.prevent="enviar">
          <div class="form-group col-12">
            <label>Producto / insumo</label>
            <Dropdown
              v-model="form.id_producto"
              :options="insumos"
              optionLabel="nombre"
              optionValue="id_producto"
              placeholder="Selecciona el insumo"
              filter
              class="w-full"
            />
          </div>
          <div class="form-group">
            <label>Cantidad</label>
            <InputNumber v-model="form.cantidad" :min="1" :step="1" mode="decimal" class="w-full" placeholder="0" />
          </div>
          <div class="form-group">
            <label>Observación (opcional)</label>
            <InputText v-model="form.observacion" placeholder="Ej. para el buffet de mañana" class="w-full" />
          </div>
          <div class="form-actions col-12">
            <Button type="submit" label="Enviar solicitud" icon="pi pi-check" severity="success" />
          </div>
        </form>
      </div>

      <div class="panel-historial">
        <h2 class="panel-title"><i class="fa-solid fa-clock-rotate-left"></i> Mis solicitudes</h2>
        <DataTable :value="solicitudes" :paginator="true" :rows="8" dataKey="id_solicitud" responsiveLayout="scroll">
          <Column field="producto" header="Producto" sortable></Column>
          <Column field="cantidad" header="Cantidad"></Column>
          <Column field="fecha" header="Fecha" sortable></Column>
          <Column field="observacion" header="Observación">
            <template #body="slotProps">
              <span class="text-muted">{{ slotProps.data.observacion || '—' }}</span>
            </template>
          </Column>
          <Column header="Estado">
            <template #body="slotProps">
              <Tag :value="slotProps.data.estado" :severity="severidad(slotProps.data.estado)" />
            </template>
          </Column>
          <Column field="respuesta" header="Respuesta">
            <template #body="slotProps">
              <span class="text-muted">{{ slotProps.data.respuesta || '—' }}</span>
            </template>
          </Column>
          <template #empty>
            <div class="empty-state">
              <i class="fa-solid fa-clipboard-list"></i>
              <span>Aún no tienes solicitudes registradas.</span>
            </div>
          </template>
        </DataTable>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import VolverBtn from '../components/ui/VolverBtn.vue'
import api from '../config/axios'

const route = useRoute()
const toast = useToast()

const insumos = ref([])
const solicitudes = ref([])
const form = ref({ id_producto: null, cantidad: 1, observacion: '' })

const severidad = (e) => (e === 'Atendida' ? 'success' : e === 'Rechazada' ? 'danger' : 'warning')

const loadInsumos = async () => {
  try {
    const res = await api.get('/cocina/inventario')
    if (res.data.success) {
      insumos.value = res.data.data
      const pid = Number(route.query.producto)
      if (pid) form.value.id_producto = pid
    }
  } catch (e) {
    console.error('Error cargando insumos:', e)
  }
}

const loadSolicitudes = async () => {
  try {
    const res = await api.get('/cocina/solicitudes')
    if (res.data.success) solicitudes.value = res.data.data
  } catch (e) {
    console.error('Error cargando solicitudes:', e)
  }
}

const enviar = async () => {
  const payload = {
    id_producto: form.value.id_producto,
    cantidad: form.value.cantidad,
    observacion: form.value.observacion
  }
  try {
    const res = await api.post('/cocina/solicitudes', payload)
    if (res.data.success) {
      toast.add({ severity: 'success', summary: 'Solicitud enviada', detail: 'Se notificará al administrador.', life: 3500 })
      form.value = { id_producto: null, cantidad: 1, observacion: '' }
      loadSolicitudes()
    }
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Error', detail: err.response?.data?.error || 'No se pudo enviar la solicitud', life: 4000 })
  }
}

onMounted(() => { loadInsumos(); loadSolicitudes() })
</script>

<style scoped>
.cocina-view {
  padding: 0;
}

.page-header {
  padding: 1.5rem 2rem;
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-color);
}

.page-header h1 {
  margin: 0;
  font-size: 1.5rem;
  color: var(--text-main);
}

.page-header p {
  margin: 0.25rem 0 0;
  font-size: 0.85rem;
  color: var(--text-muted);
}

.grid-solicitudes {
  display: grid;
  grid-template-columns: minmax(300px, 380px) 1fr;
  gap: 1rem;
  padding: 1.5rem 2rem 2rem;
  align-items: start;
}

.panel-solicitud, .panel-historial {
  background: var(--bg-card);
  border-radius: 14px;
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-soft);
}

.panel-solicitud {
  padding: 1.25rem;
  position: sticky;
  top: 80px;
}

.panel-historial {
  padding: 1rem;
}

.panel-title {
  margin: 0 0 1rem;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-main);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.form-grid {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.form-group label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-muted);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 0.25rem;
}

.w-full {
  width: 100%;
}

@media (max-width: 900px) {
  .grid-solicitudes { grid-template-columns: 1fr; }
  .panel-solicitud { position: static; }
  .page-header { padding: 1.5rem 1rem; }
  .grid-solicitudes { padding: 1rem; }
}
</style>