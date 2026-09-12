<template>
  <div class="turnos-view">
    <VolverBtn to="/personal" />
    <div class="page-header animate-item">
      <div>
        <h1>Turnos de Trabajo</h1>
        <p>Asigna y gestiona el turno de cada empleado</p>
      </div>
      <Button :disabled="$saving" label="Actualizar" icon="pi pi-refresh" severity="secondary" :loading="loading" @click="cargar" />
    </div>

    <!-- Skeleton -->
    <Transition name="fade">
      <div v-if="loading" class="table-card">
        <div v-for="n in 6" :key="n" class="skeleton-row">
          <div class="sk sk-avatar"></div>
          <div class="sk sk-line w-25"></div>
          <div class="sk sk-line w-25"></div>
          <div class="sk sk-line w-15"></div>
        </div>
      </div>
    </Transition>

    <Transition name="fade-up">
      <div v-if="!loading" class="table-card">
        <DataTable :value="empleados" :paginator="true" :rows="10" dataKey="id_usuario" stripedRows>
          <Column header="Empleado" sortable :sortField="(r) => r.nombres + ' ' + r.apellido">
            <template #body="slotProps">
              <div class="emp-cell">
                <span class="emp-avatar">{{ iniciales(slotProps.data) }}</span>
                <span class="emp-nombre">{{ slotProps.data.nombres }} {{ slotProps.data.apellido }}</span>
              </div>
            </template>
          </Column>
          <Column field="turno" header="Turno Actual" sortable>
            <template #body="slotProps">
              <span v-if="turnoList(slotProps.data.turno).length" class="turno-tags">
                <span v-for="t in turnoList(slotProps.data.turno)" :key="t" :class="['tag-turno', turnoClase(t)]">{{ t }}</span>
              </span>
              <span v-else class="text-muted">Sin turno</span>
            </template>
          </Column>
          <Column header="Cambiar turno" style="min-width: 220px">
            <template #body="slotProps">
              <MultiSelect
                :modelValue="turnoList(slotProps.data.turno)"
                :options="turnos"
                optionLabel="label"
                optionValue="value"
                placeholder="Asignar turno(s)"
                class="w-full turno-select"
                :loading="guardandoId === slotProps.data.id_usuario"
                @update:modelValue="(v) => cambiarTurno(slotProps.data, v || [])"
              />
            </template>
          </Column>
          <template #empty>
            <div class="empty-state">No hay empleados registrados.</div>
          </template>
        </DataTable>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import VolverBtn from '../components/ui/VolverBtn.vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import MultiSelect from 'primevue/multiselect'
import Button from 'primevue/button'
import { useToast } from 'primevue/usetoast'
import api from '../config/axios'

const toast = useToast()
const empleados = ref([])
const loading = ref(true)
const guardandoId = ref(null)

const turnos = [
  { label: 'Tarde', value: 'Tarde' },
  { label: 'Noche', value: 'Noche' }
]

const turnoList = (t) => {
  if (Array.isArray(t)) return t.filter(Boolean)
  return String(t || '').split(',').map(s => s.trim()).filter(Boolean)
}

const iniciales = (emp) => {
  const n = (emp.nombres || '').trim()
  const a = (emp.apellido || '').trim()
  return ((n[0] || '') + (a[0] || '')).toUpperCase() || '?'
}

const turnoClase = (t) => {
  const map = { 'Mañana': 't-manana', 'Tarde': 't-tarde', 'Noche': 't-noche' }
  return map[t] || 't-vacio'
}

const cargar = async () => {
  loading.value = true
  try {
    const res = await api.get('/personal/')
    if (res.data.success) empleados.value = res.data.data
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Error al cargar empleados', life: 3500 })
  } finally {
    loading.value = false
  }
}

const cambiarTurno = async (emp, nuevoTurno) => {
  const valor = (nuevoTurno || []).join(',')
  if (!nuevoTurno || !nuevoTurno.length || valor === emp.turno) return
  const anterior = emp.turno
  emp.turno = valor
  guardandoId.value = emp.id_usuario
  try {
    await api.put(`/personal/${emp.id_usuario}`, { turno: valor })
    toast.add({
      severity: 'success',
      summary: 'Turno actualizado',
      detail: `${emp.nombres}: ${valor}`,
      life: 2500
    })
  } catch (err) {
    emp.turno = anterior
    toast.add({ severity: 'error', summary: 'No se pudo cambiar el turno', life: 3500 })
  } finally {
    guardandoId.value = null
  }
}

onMounted(cargar)
</script>

<style scoped>
.turnos-view { padding: 2rem; }

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
  background: linear-gradient(135deg, #3b82f6, #60a5fa);
  color: #fff; font-weight: 700; font-size: 0.78rem;
  display: flex; align-items: center; justify-content: center;
}
.emp-nombre { font-weight: 600; color: var(--text-main); }

.tag-turno { padding: 0.2rem 0.7rem; border-radius: 999px; font-size: 0.78rem; font-weight: 600; }
.turno-tags { display: inline-flex; flex-wrap: wrap; gap: 0.3rem; }
.text-muted { color: var(--text-muted); font-size: 0.85rem; }
.t-manana { background: rgba(245, 158, 11, 0.15); color: #b45309; }
.t-tarde { background: rgba(59, 130, 246, 0.12); color: #2563eb; }
.t-noche { background: rgba(99, 102, 241, 0.15); color: #4f46e5; }
.t-vacio { background: rgba(148, 163, 184, 0.15); color: var(--text-muted); }

.turno-select { max-width: 170px; transition: box-shadow 0.2s ease; }

/* Skeletons */
.skeleton-row { display: flex; align-items: center; gap: 1rem; padding: 0.9rem 0.25rem; border-bottom: 1px solid var(--border-color); }
.sk {
  border-radius: 8px;
  background: linear-gradient(90deg, rgba(148,163,184,0.12) 25%, rgba(148,163,184,0.25) 50%, rgba(148,163,184,0.12) 75%);
  background-size: 400% 100%;
  animation: shimmer 1.4s infinite linear;
}
.sk-avatar { width: 34px; height: 34px; border-radius: 10px; }
.sk-line { height: 14px; }
.w-25 { width: 25%; } .w-15 { width: 15%; }
@keyframes shimmer { 0% { background-position: 100% 0; } 100% { background-position: -100% 0; } }

.empty-state { text-align: center; padding: 2rem; color: var(--text-muted); }

.animate-item { animation: slide-in 0.45s cubic-bezier(0.22, 1, 0.36, 1); }
@keyframes slide-in { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: none; } }

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.fade-up-enter-active { transition: all 0.45s cubic-bezier(0.22, 1, 0.36, 1); }
.fade-up-enter-from { opacity: 0; transform: translateY(14px); }
.fade-up-enter-to { opacity: 1; transform: none; }
</style>
