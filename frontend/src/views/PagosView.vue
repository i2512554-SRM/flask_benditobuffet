<template>
  <div class="pagos-view">
    <VolverBtn to="/personal" />
    <div class="page-header animate-item">
      <div>
        <h1>Pagos al Personal</h1>
        <p class="subtitle">Control mensual de salarios, adelantos y netos.</p>
      </div>
      <div class="actions">
        <Button :disabled="$saving" label="Registrar pago" icon="pi pi-plus" @click="openRegistrar('pago')" />
        <Button :disabled="$saving" label="Registrar adelanto" icon="pi pi-plus" severity="secondary" @click="openRegistrar('adelanto')" />
      </div>
    </div>

    <div class="stats-grid">
      <TransitionGroup name="pop">
        <div v-for="card in statCards" :key="card.label" class="stat-card">
          <div class="stat-icon" :class="card.tone">
            <i :class="card.icon"></i>
          </div>
          <div class="stat-content">
            <span class="stat-label">{{ card.label }}</span>
            <span class="stat-value">{{ card.valor }}</span>
          </div>
        </div>
      </TransitionGroup>
    </div>

    <div class="filters">
      <label>Mes</label>
      <DatePicker v-model="mesSeleccionado" view="month" date-format="mm/yy" :max-date="new Date()" @update:model-value="cargarDatos" />
      <Button :disabled="$saving" label="Consultar" icon="pi pi-search" :loading="loading" @click="cargarDatos" />
    </div>

    <div class="view-toggle">
      <Button :disabled="$saving" label="Empleados" :class="{ active: vista === 'empleados' }" severity="secondary" plain @click="vista = 'empleados'" />
      <Button :disabled="$saving" label="Historial" :class="{ active: vista === 'historial' }" severity="secondary" plain @click="vista = 'historial'" />
    </div>

    <!-- Skeleton -->
    <Transition name="fade">
      <div v-if="loading" class="table-card">
        <div v-for="n in 5" :key="n" class="skeleton-row">
          <div class="sk sk-line w-30"></div>
          <div class="sk sk-line w-20"></div>
          <div class="sk sk-line w-20"></div>
          <div class="sk sk-line w-15"></div>
        </div>
      </div>
    </Transition>

    <Transition name="fade-up">
      <div v-if="!loading && vista === 'empleados'" class="table-card">
        <h2>Resumen por empleado</h2>
        <DataTable :value="resumen" :paginator="true" :rows="10" dataKey="id_usuario" stripedRows class="mt-4">
          <Column field="nombres" header="Empleado" sortable>
            <template #body="slotProps">{{ slotProps.data.nombres }} {{ slotProps.data.apellido }}</template>
          </Column>
          <Column field="total_pagado" header="Pagado" sortable>
            <template #body="slotProps">S/. {{ fmt(slotProps.data.total_pagado) }}</template>
          </Column>
          <Column field="total_adelantos" header="Adelantos" sortable>
            <template #body="slotProps">S/. {{ fmt(slotProps.data.total_adelantos) }}</template>
          </Column>
          <Column field="neto" header="Neto" sortable>
            <template #body="slotProps"><strong>S/. {{ fmt(slotProps.data.neto) }}</strong></template>
          </Column>
          <Column header="Acción">
            <template #body="slotProps">
              <Button :disabled="$saving" label="Historial" size="small" severity="secondary" @click="$router.push(`/personal/pagos/empleado/${slotProps.data.id_usuario}`)" />
            </template>
          </Column>
          <template #empty>
            <div class="empty-state">
              <i class="fa-solid fa-money-bill-wave"></i>
              <p>No hay pagos ni adelantos en este mes. Registra uno con los botones de arriba.</p>
            </div>
          </template>
        </DataTable>
      </div>
    </Transition>

    <Transition name="fade-up">
      <div v-if="!loading && vista === 'historial'" class="table-card">
        <h2>Historial de pagos</h2>
        <DataTable :value="historial" :paginator="true" :rows="10" dataKey="id_pago" stripedRows class="mt-4">
          <Column field="fecha" header="Fecha" sortable><template #body="{data}">{{ fechaLegible(data.fecha) }}</template></Column>
          <Column field="empleado" header="Empleado" sortable></Column>
          <Column field="monto" header="Monto" sortable>
            <template #body="slotProps">S/. {{ fmt(slotProps.data.monto) }}</template>
          </Column>
          <Column field="estado" header="Estado">
            <template #body="slotProps">
              <Tag :value="slotProps.data.estado" :severity="slotProps.data.estado === 'Pagado' ? 'success' : 'warning'" />
            </template>
          </Column>
          <template #empty>
            <div class="empty-state">
              <i class="fa-solid fa-receipt"></i>
              <p>No hay pagos registrados en el periodo seleccionado.</p>
            </div>
          </template>
        </DataTable>
      </div>
    </Transition>

    <Dialog v-model:visible="dialogVisible" :header="modal === 'pago' ? 'Registrar pago' : 'Registrar adelanto'" :modal="true" :style="{ width: '520px' }">
      <div class="formgrid grid">
        <div class="field col-12">
          <label for="empleado">Empleado</label>
          <Select id="empleado" v-model="form.id_usuario" :options="empleados" :optionLabel="(e) => `${e.nombres} ${e.apellido}`" optionValue="id_usuario" class="w-full" placeholder="Seleccione..." />
        </div>
        <template v-if="modal === 'pago'">
          <div class="field col-6">
            <label for="tipo">Tipo de pago</label>
            <Select id="tipo" v-model="form.tipo" :options="['Salario semanal', 'Bono', 'Horas extra', 'Otros']" class="w-full" /><InputText v-if="form.tipo === 'Otros'" v-model="form.otroTipo" placeholder="Especifica el tipo" />
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
          <InputNumber :maxFractionDigits="2" placeholder="Ej. 100.00" id="monto" v-model="form.monto" mode="currency" currency="PEN" locale="es-PE" class="w-full" />
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
        <Button :disabled="$saving" label="Cancelar" severity="secondary" @click="dialogVisible = false" />
        <Button :disabled="$saving" label="Guardar" :loading="guardando" @click="guardar" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { formatFecha as fechaLegible } from '../utils/format'
import { ref, computed, onMounted } from 'vue'
import VolverBtn from '../components/ui/VolverBtn.vue'
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
const vista = ref('empleados')
const mesSeleccionado = ref(new Date())
const form = ref({})
const loading = ref(true)
const guardando = ref(false)

const totales = computed(() => pagos.value.totales || { pagado: 0, adelantos: 0, neto: 0 })
const empleadosActivos = computed(() => pagos.value.empleados_activos || 0)
const proximoPago = computed(() => pagos.value.proximo_pago)
const resumen = computed(() => pagos.value.resumen || [])
const historial = computed(() => pagos.value.historial || [])

const fmt = (v) => Number(v || 0).toLocaleString('es-PE', { minimumFractionDigits: 2 })

const statCards = computed(() => [
  { label: 'Total pagado', valor: 'S/. ' + fmt(totales.value.pagado), icon: 'fa-solid fa-sack-dollar', tone: 'pagos' },
  { label: 'Total adelantos', valor: 'S/. ' + fmt(totales.value.adelantos), icon: 'fa-solid fa-hand-holding-dollar', tone: 'adelantos' },
  { label: 'Total entregado del mes', valor: 'S/. ' + fmt(totales.value.neto), icon: 'fa-solid fa-scale-balanced', tone: 'neto' },
  { label: 'Empleados activos', valor: String(empleadosActivos.value), icon: 'fa-solid fa-users', tone: 'empleados' },
  { label: 'Próximo pago', valor: proximoPago.value !== null && proximoPago.value !== undefined ? proximoPago.value + ' días' : 'Sin pendientes', icon: 'fa-solid fa-calendar-day', tone: 'proximo' }
])

const cargarDatos = async () => {
  loading.value = true
  try {
    const mes = mesSeleccionado.value ? mesSeleccionado.value.getMonth() + 1 : new Date().getMonth() + 1
    const anio = mesSeleccionado.value ? mesSeleccionado.value.getFullYear() : new Date().getFullYear()
    const res = await api.get('/personal/pagos', { params: { mes, anio } })
    if (res.data.success) {
      pagos.value = res.data.data
    }
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Error al cargar pagos', life: 3500 })
  } finally {
    loading.value = false
  }
}

const cargarEmpleados = async () => {
  try {
    const res = await api.get('/personal/')
    if (res.data.success) empleados.value = res.data.data
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Error al cargar empleados', life: 3500 })
  }
}

const openRegistrar = (tipo) => {
  modal.value = tipo
  form.value = {
    id_usuario: null,
    monto: null,
    fecha: new Date(),
    tipo: 'Salario semanal',
    estado: 'Pagado',
    descripcion: '',
    motivo: ''
  }
  dialogVisible.value = true
}

const guardar = async () => {
  if (guardando.value) return
  if (form.value.tipo === 'Otros' && !form.value.otroTipo?.trim()) {
    toast.add({ severity: 'warn', summary: 'Especifica el tipo de pago.', life: 3000 }); return
  }
  if (!Number.isFinite(form.value.monto) || form.value.monto <= 0) {
    toast.add({ severity: 'warn', summary: 'Ingresa un monto positivo.', life: 3000 }); return
  }
  if (!form.value.id_usuario) {
    toast.add({ severity: 'warn', summary: 'Seleccione un empleado', life: 3000 })
    return
  }
  if (modal.value === 'adelanto' && !form.value.motivo?.trim()) {
    toast.add({ severity: 'warn', summary: 'Ingrese el motivo del adelanto', life: 3000 })
    return
  }
  guardando.value = true
  try {
    if (modal.value === 'pago') {
      await api.post('/personal/pagos', { ...form.value, tipo: form.value.tipo === 'Otros' ? form.value.otroTipo : form.value.tipo })
    } else {
      await api.post('/personal/pagos/adelanto', form.value)
    }
    toast.add({ severity: 'success', summary: modal.value === 'pago' ? 'Pago registrado' : 'Adelanto registrado', life: 3000 })
    dialogVisible.value = false
    await cargarDatos()
  } catch (err) {
    toast.add({ severity: 'error', summary: err.response?.data?.message || 'No se pudo registrar', life: 4000 })
  } finally {
    guardando.value = false
  }
}

onMounted(async () => {
  await Promise.all([cargarDatos(), cargarEmpleados()])
})
</script>

<style scoped>
.pagos-view { padding: 2rem; }

.page-header {
  display: flex; justify-content: space-between; align-items: center;
  flex-wrap: wrap; gap: 1rem; margin-bottom: 1.25rem;
}
.page-header h1 { margin: 0; font-size: 1.5rem; color: var(--text-main); }
.subtitle { color: var(--text-muted); margin: 0.25rem 0 0; }
.actions { display: flex; gap: 0.75rem; }

.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
.stat-card {
  display: flex; align-items: center; gap: 1rem;
  background: var(--bg-card); border: 1px solid var(--border-color);
  border-radius: 14px; padding: 1.1rem 1.25rem; box-shadow: var(--shadow-soft);
  transition: transform 0.25s cubic-bezier(0.22, 1, 0.36, 1), box-shadow 0.25s ease;
}
.stat-card:hover { transform: translateY(-3px); box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08); }
.stat-icon { width: 42px; height: 42px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1rem; flex-shrink: 0; }
.stat-icon.pagos { background: rgba(16, 185, 129, 0.12); color: #10b981; }
.stat-icon.adelantos { background: rgba(245, 158, 11, 0.14); color: #b45309; }
.stat-icon.neto { background: rgba(255, 123, 0, 0.14); color: var(--btn-primary); }
.stat-icon.empleados { background: rgba(59, 130, 246, 0.12); color: #3b82f6; }
.stat-icon.proximo { background: rgba(139, 92, 246, 0.12); color: #8b5cf6; }
.stat-content { display: flex; flex-direction: column; }
.stat-label { font-size: 0.72rem; color: var(--text-muted); }
.stat-value { font-size: 1.2rem; font-weight: 700; margin-top: 0.15rem; color: var(--text-main); }

.filters { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem; flex-wrap: wrap; }
.filters label { font-weight: 600; }

.view-toggle { display: flex; gap: 0.5rem; margin-bottom: 1rem; }
.view-toggle .active { background: var(--btn-primary); color: white; border-color: var(--btn-primary); }

.table-card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 14px; padding: 1.25rem; box-shadow: var(--shadow-soft); }
.table-card h2 { margin: 0 0 0.5rem; font-size: 1.05rem; color: var(--text-main); }
.mt-4 { margin-top: 1rem; }

.empty-state { text-align: center; padding: 2.5rem 1rem; color: var(--text-muted); }
.empty-state i { font-size: 1.75rem; opacity: 0.5; display: block; margin-bottom: 0.5rem; }

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

/* Animaciones */
.animate-item { animation: slide-in 0.45s cubic-bezier(0.22, 1, 0.36, 1); }
@keyframes slide-in { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: none; } }

.pop-enter-active { transition: all 0.4s cubic-bezier(0.22, 1, 0.36, 1); }
.pop-enter-from { opacity: 0; transform: translateY(12px) scale(0.97); }
.pop-enter-to { opacity: 1; transform: none; }
.pop-move { transition: transform 0.4s cubic-bezier(0.22, 1, 0.36, 1); }

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.fade-up-enter-active { transition: all 0.45s cubic-bezier(0.22, 1, 0.36, 1); }
.fade-up-enter-from { opacity: 0; transform: translateY(14px); }
.fade-up-enter-to { opacity: 1; transform: none; }

@media (max-width: 768px) {
  .page-header { flex-direction: column; align-items: flex-start; }
}
</style>
