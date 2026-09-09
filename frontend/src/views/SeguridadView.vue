<template>
  <div class="seguridad-view">
    <div class="page-hero">
      <router-link to="/seguridad" class="btn btn-outline btn-back">
        <i class="fa-solid fa-arrow-left"></i> Volver a Seguridad y Accesos
      </router-link>
      <h1>Seguridad del Sistema</h1>
      <p>Monitoreo de intentos de login, bloqueos y actividad sospechosa.</p>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">Intentos exitosos (7 días)</div>
        <div class="stat-value">{{ resumen.exitos }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Intentos fallidos (7 días)</div>
        <div class="stat-value text-error">{{ resumen.fallos }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Intentos bloqueados</div>
        <div class="stat-value text-warn">{{ resumen.bloqueados }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Bloqueos activos</div>
        <div class="stat-value text-error">{{ resumen.bloqueos_activos }}</div>
      </div>
    </div>

    <div class="table-card" v-if="bloqueos.length">
      <h2>Bloqueos activos</h2>
      <DataTable :value="bloqueos" :paginator="true" :rows="5" class="mt-3">
        <Column field="usuario" header="Usuario"></Column>
        <Column field="usuario_nombre" header="Empleado">
          <template #body="slotProps">{{ slotProps.data.usuario_nombre || '-' }}</template>
        </Column>
        <Column field="usuario_rol" header="Rol">
          <template #body="slotProps">{{ rolLabel(slotProps.data.usuario_rol) }}</template>
        </Column>
        <Column field="intentos" header="Intentos fallidos" sortable></Column>
        <Column field="bloqueado_hasta" header="Bloqueado hasta">
          <template #body="slotProps">{{ slotProps.data.bloqueado_hasta }}</template>
        </Column>
        <Column header="Acciones">
          <template #body="slotProps">
            <Button label="Desbloquear" icon="pi pi-unlock" severity="warning" size="small" @click="desbloquear(slotProps.data)" />
          </template>
        </Column>
      </DataTable>
    </div>

    <div class="table-card">
      <div class="table-header">
        <h2>Últimos intentos de login</h2>
        <div class="search-box">
          <Select v-model="filtroResultado" :options="filtros" optionLabel="label" optionValue="value" placeholder="Todos los resultados" showClear class="w-full" @update:model-value="cargar" />
        </div>
      </div>
      <DataTable :value="intentosFiltrados" :paginator="true" :rows="10" class="mt-3">
        <Column field="fecha" header="Fecha" sortable></Column>
        <Column field="identificador" header="Usuario" sortable></Column>
        <Column field="usuario_nombre" header="Empleado">
          <template #body="slotProps">{{ slotProps.data.usuario_nombre || '-' }}</template>
        </Column>
        <Column field="ip" header="IP" sortable></Column>
        <Column field="resultado" header="Resultado" sortable>
          <template #body="slotProps">
            <span :class="['tag-resultado', 'tag-' + slotProps.data.resultado]">{{ resultadoLabel(slotProps.data.resultado) }}</span>
          </template>
        </Column>
      </DataTable>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Select from 'primevue/select'
import api from '../config/axios'

const toast = useToast()
const resumen = ref({ exitos: 0, fallos: 0, bloqueados: 0, bloqueos_activos: 0 })
const intentos = ref([])
const bloqueos = ref([])
const filtroResultado = ref(null)
const filtros = [
  { label: 'Éxito', value: 'exito' },
  { label: 'Fallo', value: 'fallo' },
  { label: 'Bloqueado', value: 'bloqueado' }
]

const intentosFiltrados = computed(() => {
  if (!filtroResultado.value) return intentos.value
  return intentos.value.filter(i => i.resultado === filtroResultado.value)
})

const rolLabel = (r) => ['Admin', 'Cajera', 'Cocinero', 'Mozo'][r - 1] || 'Desconocido'
const resultadoLabel = (r) => ({ exito: 'Éxito', fallo: 'Fallo', bloqueado: 'Bloqueado' }[r] || r)

const cargar = async () => {
  try {
    const res = await api.get('/admin/seguridad')
    if (res.data.success) {
      resumen.value = res.data.data.resumen
      intentos.value = res.data.data.intentos
      bloqueos.value = res.data.data.bloqueos
    }
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error al cargar seguridad', life: 3500 })
  }
}

const desbloquear = async (bloqueo) => {
  try {
    await api.post('/admin/seguridad/desbloquear', { usuario: bloqueo.usuario })
    toast.add({ severity: 'success', summary: `${bloqueo.usuario} desbloqueado`, life: 2500 })
    await cargar()
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error al desbloquear', life: 3500 })
  }
}

onMounted(cargar)
</script>

<style scoped>
.seguridad-view { padding: 0; }
.subtitle { color: var(--text-muted); margin-top: 0.25rem; }
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
.stat-card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 1.25rem; }
.stat-label { font-size: 0.75rem; color: var(--text-muted); }
.stat-value { font-size: 1.5rem; font-weight: 700; margin-top: 0.25rem; }
.text-error { color: #dc2626; }
.text-warn { color: #b45309; }
.table-card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 1.25rem; margin-bottom: 1.5rem; }
.table-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; }
.search-box { display: flex; gap: 0.75rem; min-width: 220px; }
.mt-3 { margin-top: 0.75rem; }
.tag-resultado { padding: 0.15rem 0.6rem; border-radius: 999px; font-size: 0.75rem; font-weight: 600; }
.tag-exito { background: rgba(34, 197, 94, 0.12); color: #16a34a; }
.tag-fallo { background: rgba(239, 68, 68, 0.12); color: #dc2626; }
.tag-bloqueado { background: rgba(245, 158, 11, 0.15); color: #b45309; }
</style>