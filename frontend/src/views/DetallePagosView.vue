<template>
  <div class="detalle-view">
    <div class="header">
      <Button icon="pi pi-arrow-left" severity="secondary" text @click="$router.push('/personal/pagos')" />
      <div>
        <h1>Historial de {{ detalle.empleado?.nombres }} {{ detalle.empleado?.apellido }}</h1>
        <p class="subtitle">Historial de pagos, adelantos y movimientos</p>
      </div>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">Total pagado</div>
        <div class="stat-value">S/. {{ fmt(totales.pagado) }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Total adelantos</div>
        <div class="stat-value">S/. {{ fmt(totales.adelantos) }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Neto</div>
        <div class="stat-value">S/. {{ fmt(totales.neto) }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Mes</div>
        <div class="stat-value small">{{ mesNombres[detalle.mes - 1] }} {{ detalle.anio }}</div>
      </div>
    </div>

    <div class="view-toggle">
      <Button label="Pagos Registrados" :class="{ active: vista === 'pagos' }" severity="secondary" plain @click="vista = 'pagos'" />
      <Button label="Pagos Personal" :class="{ active: vista === 'personal' }" severity="secondary" plain @click="vista = 'personal'" />
      <Button label="Adelantos" :class="{ active: vista === 'adelantos' }" severity="secondary" plain @click="vista = 'adelantos'" />
    </div>

    <div class="table-card" v-if="vista === 'pagos'">
      <h2>Pagos registrados</h2>
      <DataTable :value="detalle.pagos || []" :paginator="true" :rows="10" class="mt-4">
        <Column field="fecha" header="Fecha" sortable></Column>
        <Column field="monto" header="Monto" sortable>
          <template #body="slotProps">S/. {{ fmt(slotProps.data.monto) }}</template>
        </Column>
        <Column field="estado" header="Estado">
          <template #body="slotProps">
            <Tag :value="slotProps.data.estado" :severity="slotProps.data.estado === 'Pagado' ? 'success' : 'warning'" />
          </template>
        </Column>
        <Column field="descripcion" header="Descripción">
          <template #body="slotProps">{{ slotProps.data.descripcion || '-' }}</template>
        </Column>
      </DataTable>
    </div>

    <div class="table-card" v-if="vista === 'personal'">
      <h2>Pagos de personal</h2>
      <DataTable :value="detalle.pagos_personal || []" :paginator="true" :rows="10" class="mt-4">
        <Column field="fecha" header="Fecha" sortable></Column>
        <Column field="tipo" header="Tipo" sortable>
          <template #body="slotProps">{{ slotProps.data.tipo || 'Pago' }}</template>
        </Column>
        <Column field="monto" header="Monto" sortable>
          <template #body="slotProps">S/. {{ fmt(slotProps.data.monto) }}</template>
        </Column>
      </DataTable>
    </div>

    <div class="table-card" v-if="vista === 'adelantos'">
      <h2>Adelantos</h2>
      <DataTable :value="detalle.adelantos || []" :paginator="true" :rows="10" class="mt-4">
        <Column field="fecha" header="Fecha" sortable></Column>
        <Column field="motivo" header="Motivo" sortable></Column>
        <Column field="monto" header="Monto" sortable>
          <template #body="slotProps">S/. {{ fmt(slotProps.data.monto) }}</template>
        </Column>
        <Column field="estado" header="Estado">
          <template #body="slotProps">
            <Tag :value="slotProps.data.estado" :severity="slotProps.data.estado === 'Aprobado' ? 'success' : (slotProps.data.estado === 'Rechazado' || slotProps.data.estado === 'Cancelado' ? 'danger' : 'warning')" />
          </template>
        </Column>
        <Column field="respuesta" header="Respuesta Admin">
          <template #body="slotProps">{{ slotProps.data.respuesta || '-' }}</template>
        </Column>
      </DataTable>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import api from '../config/axios'

const route = useRoute()
const detalle = ref({ pagos: [], pagos_personal: [], adelantos: [], totales: { pagado: 0, adelantos: 0, neto: 0 } })
const vista = ref('pagos')
const mesNombres = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

const fmt = (v) => Number(v || 0).toFixed(2)
const totales = () => detalle.value.totales || { pagado: 0, adelantos: 0, neto: 0 }

onMounted(async () => {
  const id = route.params.id
  const res = await api.get(`/personal/pagos/empleado/${id}`)
  if (res.data.success) detalle.value = res.data.data
})
</script>

<style scoped>
.detalle-view { padding: 2rem; }
.header { display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem; }
.subtitle { color: var(--text-muted); margin-top: 0.25rem; }
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
.stat-card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 1.25rem; }
.stat-label { font-size: 0.75rem; color: var(--text-muted); }
.stat-value { font-size: 1.5rem; font-weight: 700; margin-top: 0.25rem; }
.stat-value.small { font-size: 1.1rem; margin-top: 0.5rem; }
.view-toggle { display: flex; gap: 0.5rem; margin-bottom: 1rem; }
.view-toggle .active { background: var(--btn-primary); color: white; border-color: var(--btn-primary); }
.table-card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 1.25rem; }
.mt-4 { margin-top: 1rem; }
</style>
