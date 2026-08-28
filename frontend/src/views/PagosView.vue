<template>
  <div class="pagos-view">
    <h1>Pagos al Personal</h1>
    <p class="subtitle">Control mensual de salarios, adelantos y netos.</p>

    <div class="actions">
      <Button label="Registrar pago" icon="pi pi-plus" @click="openRegistrar('pago')" />
      <Button label="Registrar adelanto" icon="pi pi-plus" severity="secondary" @click="openRegistrar('adelanto')" />
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">Total pagado</div>
        <div class="stat-value">S/. {{ fmt(totales.pagado) }}</div>
        <div class="stat-note positive">Mes seleccionado</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Total adelantos</div>
        <div class="stat-value">S/. {{ fmt(totales.adelantos) }}</div>
        <div class="stat-note negative">Mes seleccionado</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Neto del mes</div>
        <div class="stat-value">S/. {{ fmt(totales.neto) }}</div>
        <div class="stat-note" :class="totales.neto >= 0 ? 'positive' : 'negative'">Mes seleccionado</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Empleados activos</div>
        <div class="stat-value">{{ empleadosActivos }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Próximo pago</div>
        <div class="stat-value small">{{ proximoPago !== null ? proximoPago + ' días' : 'No hay pagos pendientes' }}</div>
      </div>
    </div>

    <div class="filters">
      <label>Mes</label>
      <DatePicker v-model="mesSeleccionado" view="month" date-format="mm/yy" :max-date="new Date()" @update:model-value="cargarDatos" />
      <Button label="Consultar" icon="pi pi-search" @click="cargarDatos" />
    </div>

    <div class="view-toggle">
      <Button label="Empleados" :class="{ active: vista === 'empleados' }" severity="secondary" plain @click="vista = 'empleados'" />
      <Button label="Historial" :class="{ active: vista === 'historial' }" severity="secondary" plain @click="vista = 'historial'" />
    </div>

    <div class="table-card" v-if="vista === 'empleados'">
      <h2>Resumen por empleado</h2>
      <DataTable :value="resumen" :paginator="true" :rows="10" class="mt-4">
        <Column field="nombres" header="Empleado">
          <template #body="slotProps">{{ slotProps.data.nombres }} {{ slotProps.data.apellido }}</template>
        </Column>
        <Column field="total_pagado" header="Pagado" sortable>
          <template #body="slotProps">S/. {{ fmt(slotProps.data.total_pagado) }}</template>
        </Column>
        <Column field="total_adelantos" header="Adelantos" sortable>
          <template #body="slotProps">S/. {{ fmt(slotProps.data.total_adelantos) }}</template>
        </Column>
        <Column field="neto" header="Neto" sortable>
          <template #body="slotProps">S/. {{ fmt(slotProps.data.neto) }}</template>
        </Column>
        <Column header="Acción">
          <template #body="slotProps">
            <Button label="Historial" size="small" severity="secondary" @click="$router.push(`/personal/pagos/empleado/${slotProps.data.id_usuario}`)" />
          </template>
        </Column>
      </DataTable>
    </div>

    <div class="table-card" v-if="vista === 'historial'">
      <h2>Historial de pagos</h2>
      <DataTable :value="historial" :paginator="true" :rows="10" class="mt-4">
        <Column field="fecha" header="Fecha" sortable></Column>
        <Column field="empleado" header="Empleado" sortable></Column>
        <Column field="monto" header="Monto" sortable>
          <template #body="slotProps">S/. {{ fmt(slotProps.data.monto) }}</template>
        </Column>
        <Column field="estado" header="Estado">
          <template #body="slotProps">
            <Tag :value="slotProps.data.estado" :severity="slotProps.data.estado === 'Pagado' ? 'success' : 'warning'" />
          </template>
        </Column>
      </DataTable>
    </div>

    <Dialog v-model:visible="dialogVisible" :header="modal === 'pago' ? 'Registrar pago' : 'Registrar adelanto'" :modal="true" :style="{ width: '520px' }">
      <div class="formgrid grid">
        <div class="field col-12">
          <label for="empleado">Empleado</label>
          <Select id="empleado" v-model="form.id_usuario" :options="empleados" optionLabel="nombres" optionValue="id_usuario" class="w-full" placeholder="Seleccione..." />
        </div>
        <template v-if="modal === 'pago'">
          <div class="field col-6">
            <label for="tipo">Tipo de pago</label>
            <InputText id="tipo" v-model="form.tipo" class="w-full" placeholder="Salario, Bono, Extra" />
          </div>
          <div class="field col-6">
            <label for="estado">Estado</label>
            <Select id="estado" v-model="form.estado" :options="[{label:'Pagado',value:'Pagado'},{label:'Pendiente',value:'Pendiente'}]" optionLabel="label" optionValue="value" class="w-full" />
          </div>
        </template>
        <template v-else>
          <div class="field col-12">
            <label for="motivo">Motivo</label>
            <InputText id="motivo" v-model="form.motivo" class="w-full" placeholder="Motivo del adelanto" />
          </div>
        </template>
        <div class="field col-6">
          <label for="monto">Monto</label>
          <InputNumber id="monto" v-model="form.monto" mode="currency" currency="PEN" locale="es-PE" class="w-full" />
        </div>
        <div class="field col-6">
          <label for="fecha">Fecha</label>
          <DatePicker id="fecha" v-model="form.fecha" date-format="yy-mm-dd" :max-date="new Date()" class="w-full" />
        </div>
        <div class="field col-12" v-if="modal === 'pago'">
          <label for="descripcion">Descripción</label>
          <InputText id="descripcion" v-model="form.descripcion" class="w-full" />
        </div>
      </div>
      <template #footer>
        <Button label="Cancelar" severity="secondary" @click="dialogVisible = false" />
        <Button label="Guardar" @click="guardar" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Select from 'primevue/select'
import DatePicker from 'primevue/datepicker'
import Tag from 'primevue/tag'
import api from '../config/axios'

const router = useRouter()
const toast = useToast()

const pagos = ref({
  mes: new Date().getMonth() + 1,
  anio: new Date().getFullYear(),
  totales: { pagado: 0, adelantos: 0, neto: 0 },
  empleados_activos: 0,
  proximo_pago: null,
  resumen: [],
  historial: []
})
const empleados = ref([])
const dialogVisible = ref(false)
const modal = ref('pago')
const vista = ref('historial')
const mesSeleccionado = ref(new Date())
const form = ref({})

const fmt = (v) => Number(v || 0).toFixed(2)

const cargarDatos = async () => {
  const mes = mesSeleccionado.value ? mesSeleccionado.value.getMonth() + 1 : new Date().getMonth() + 1
  const anio = mesSeleccionado.value ? mesSeleccionado.value.getFullYear() : new Date().getFullYear()
  const res = await api.get('/personal/pagos', { params: { mes, anio } })
  if (res.data.success) {
    pagos.value = res.data.data
    vista.value = res.data.data.resumen.length ? vista.value : 'historial'
  }
}

const cargarEmpleados = async () => {
  const res = await api.get('/personal/')
  if (res.data.success) empleados.value = res.data.data
}

const openRegistrar = (tipo) => {
  modal.value = tipo
  form.value = {
    id_usuario: null,
    monto: 0,
    fecha: new Date(),
    tipo: 'Salario',
    estado: 'Pagado',
    descripcion: '',
    motivo: ''
  }
  dialogVisible.value = true
}

const guardar = async () => {
  if (!form.value.id_usuario) {
    toast.add({ severity: 'warn', summary: 'Seleccione un empleado', life: 3000 })
    return
  }
  if (modal.value === 'pago') {
    await api.post('/personal/pagos', form.value)
  } else {
    await api.post('/personal/pagos/adelanto', form.value)
  }
  toast.add({ severity: 'success', summary: 'Registrado correctamente', life: 3000 })
  dialogVisible.value = false
  await cargarDatos()
}

onMounted(async () => {
  await Promise.all([cargarDatos(), cargarEmpleados()])
})
</script>

<style scoped>
.pagos-view { padding: 2rem; }
.subtitle { color: var(--text-muted); margin-top: 0.25rem; }
.actions { display: flex; gap: 1rem; margin: 1.5rem 0; }
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
.stat-card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 1.25rem; }
.stat-label { font-size: 0.75rem; color: var(--text-muted); }
.stat-value { font-size: 1.5rem; font-weight: 700; margin-top: 0.25rem; }
.stat-value.small { font-size: 1rem; margin-top: 0.6rem; }
.stat-note { font-size: 0.7rem; margin-top: 0.25rem; }
.positive { color: green; }
.negative { color: red; }
.filters { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem; }
.filters label { font-weight: 600; }
.view-toggle { display: flex; gap: 0.5rem; margin-bottom: 1rem; }
.view-toggle .active { background: var(--btn-primary); color: white; border-color: var(--btn-primary); }
.table-card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 1.25rem; }
.mt-4 { margin-top: 1rem; }
</style>
