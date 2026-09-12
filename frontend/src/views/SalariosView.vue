<template>
  <div class="salarios-view">
    <VolverBtn to="/personal" />
    <div class="page-header animate-item">
      <div>
        <h1>Sueldos y pagos semanales</h1>
        <p>Sueldo fijo menos adelantos aprobados, descuentos y pagos realizados. De lunes a domingo.</p>
      </div>
      <div class="actions">
        <DatePicker v-model="mesSeleccionado" date-format="dd/mm/yy" placeholder="Selecciona un día de la semana" @update:model-value="calcularMes" class="mes-picker" />
        <Button :disabled="$saving" label="Actualizar historial" icon="pi pi-refresh" :loading="loading" @click="calcularMes" />
      </div>
    </div>

<p>{{ rango }}</p>
    <!-- Resumen -->
    <div class="stats-grid">
      <TransitionGroup name="pop">
        <div v-for="card in resumenCards" :key="card.label" class="stat-card">
          <div class="stat-icon" :class="card.tone">
            <i :class="card.icon"></i>
          </div>
          <div class="stat-content">
            <span class="stat-label">{{ card.label }}</span>
            <span class="stat-value">S/. {{ formatMoney(card.valor) }}</span>
          </div>
        </div>
      </TransitionGroup>
    </div>

    <!-- Skeleton de carga -->
    <Transition name="fade">
      <div v-if="loading" class="table-card">
        <div v-for="n in 5" :key="n" class="skeleton-row">
          <div class="sk sk-avatar"></div>
          <div class="sk sk-line w-30"></div>
          <div class="sk sk-line w-15"></div>
          <div class="sk sk-line w-15"></div>
          <div class="sk sk-line w-15"></div>
        </div>
      </div>
    </Transition>

    <!-- Tabla de resultados -->
    <Transition name="fade-up">
      <div v-if="!loading && salarios.length" class="table-card">
        <DataTable :value="salarios" :paginator="true" :rows="10" stripedRows dataKey="id_usuario" class="mt-4 animated-table">
          <Column header="Empleado" sortable :sortField="(row) => row.empleado">
            <template #body="slotProps">
              <div class="emp-cell">
                <span class="emp-avatar">{{ iniciales(slotProps.data.empleado) }}</span>
                <div class="emp-info">
                  <span class="emp-nombre">{{ slotProps.data.empleado }}</span>
                  <span class="emp-usuario">@{{ slotProps.data.usuario }}</span>
                </div>
              </div>
            </template>
          </Column>
          <Column header="Sueldo semanal"><template #body="{ data }">{{ data.sueldo_base == null ? 'Sin configurar' : 'S/. ' + formatMoney(data.sueldo_base) }}</template></Column>
          <Column field="total_pagos" header="Pagos" sortable>
            <template #body="slotProps">S/. {{ formatMoney(slotProps.data.total_pagos) }}</template>
          </Column>
          <Column field="total_adelantos" header="Adelantos" sortable>
            <template #body="slotProps">S/. {{ formatMoney(slotProps.data.total_adelantos) }}</template>
          </Column>
          <Column field="neto" header="Total entregado" sortable>
            <template #body="slotProps">
              <strong class="neto-val">S/. {{ formatMoney(slotProps.data.neto) }}</strong>
            </template>
          </Column>
          <Column header="Descuentos"><template #body="{ data }">
            <div v-for="d in data.descuentos" :key="d.id" class="descuento">
              <span>{{ d.motivo }}: S/. {{ formatMoney(d.monto) }}</span>
              <Button label="Anular" severity="secondary" size="small" :disabled="$saving" @click="confirmarAnulacion(d)" />
            </div>
            <span v-if="!data.descuentos?.length">Sin descuentos</span>
          </template></Column>
          <Column header="Saldo pendiente"><template #body="{ data }">
            <strong>{{ data.saldo == null ? 'Configure el sueldo' : 'S/. ' + formatMoney(data.saldo) }}</strong>
            <small v-if="data.saldo < 0">Importe entregado o descontado superior al sueldo</small>
          </template></Column>
          <Column header="Acciones"><template #body="{ data }">
            <Button label="Sueldo" size="small" :disabled="$saving" @click="abrir(data, 'sueldo')" />
            <Button label="Descuento" size="small" severity="secondary" :disabled="$saving" @click="abrir(data, 'descuentos')" />
          </template></Column>
          <template #empty>
            <div class="empty-state">No hay datos para esta semana.</div>
          </template>
        </DataTable>
      </div>
    </Transition>

    <Dialog v-model:visible="dialogo" modal :header="tipo === 'sueldo' ? 'Configurar sueldo semanal' : 'Registrar descuento'" :style="{ width: 'min(95vw, 440px)' }">
      <form class="form-nomina" @submit.prevent="guardar">
        <p>{{ empleado?.empleado }} · {{ rango }}</p>
        <p v-if="tipo === 'sueldo'">Este monto rige desde la semana seleccionada hasta el siguiente cambio de sueldo. No modifica semanas anteriores.</p>
        <label for="monto-nomina">Monto</label>
        <InputNumber inputId="monto-nomina" v-model="monto" :min="tipo === 'sueldo' ? 0 : 0.01" :maxFractionDigits="2" placeholder="Ej. 350.00" />
        <template v-if="tipo === 'descuentos'">
          <label for="motivo-nomina">Motivo del descuento</label>
          <InputText id="motivo-nomina" v-model="motivo" required maxlength="255" placeholder="Ej. Platos, falta del martes…" />
        </template>
        <Button type="submit" label="Guardar" :loading="guardando" :disabled="$saving || guardando || monto == null" />
      </form>
    </Dialog>
    <Dialog v-model:visible="anulacionVisible" header="Anular descuento" modal :style="{ width: 'min(95vw, 420px)' }">
      <p>Se retirará del cálculo el descuento «{{ descuentoAnular?.motivo }}». La anulación quedará registrada.</p>
      <Button label="Confirmar anulación" :disabled="$saving" @click="anular" />
    </Dialog>
    <!-- Estado vacío -->
    <Transition name="fade">
      <div v-if="!loading && !salarios.length" class="empty-card">
        <i class="fa-solid fa-coins empty-icon"></i>
        <h3>Sin empleados para calcular</h3>
        <p>No se encontraron empleados activos en el periodo seleccionado.</p>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import VolverBtn from '../components/ui/VolverBtn.vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import DatePicker from 'primevue/datepicker'
import Dialog from 'primevue/dialog'
import InputNumber from 'primevue/inputnumber'
import InputText from 'primevue/inputtext'
import { useToast } from 'primevue/usetoast'
import { fechaLocal, formatFecha } from '../utils/format'
import api from '../config/axios'

const toast = useToast()
const rango = ref('')
const salarios = ref([])
const mesSeleccionado = ref(new Date())
const loading = ref(false)
const dialogo = ref(false), empleado = ref(null), tipo = ref('sueldo'), monto = ref(null), motivo = ref(''), guardando = ref(false)
const anulacionVisible = ref(false), descuentoAnular = ref(null)
function abrir(fila, accion) {
  empleado.value = fila; tipo.value = accion; monto.value = accion === 'sueldo' ? fila.sueldo_base : null
  motivo.value = ''; dialogo.value = true
}
async function guardar() {
  if (guardando.value || monto.value == null) return
  guardando.value = true
  try {
    await api.post('/personal/salarios/' + tipo.value, { id_usuario: empleado.value.id_usuario,
      fecha: fechaLocal(mesSeleccionado.value), monto: monto.value, motivo: motivo.value })
    dialogo.value = false; await calcularMes()
    toast.add({ severity: 'success', summary: 'Registro guardado', life: 2500 })
  } catch (e) {
    toast.add({ severity: 'error', summary: 'No se pudo guardar', detail: e.response?.data?.message || 'Intenta nuevamente', life: 4000 })
  } finally { guardando.value = false }
}
function confirmarAnulacion(d) { descuentoAnular.value = d; anulacionVisible.value = true }
async function anular() {
  try {
    await api.post(`/personal/salarios/descuentos/${descuentoAnular.value.id}/anular`)
    anulacionVisible.value = false; await calcularMes()
  } catch { toast.add({ severity: 'error', summary: 'No se pudo anular', life: 3000 }) }
}

const formatMoney = (val) => Number(val || 0).toLocaleString('es-PE', { minimumFractionDigits: 2 })

const iniciales = (nombre) => {
  if (!nombre) return '?'
  return nombre.split(' ').map(p => p[0]).slice(0, 2).join('').toUpperCase()
}

const resumenCards = computed(() => {
  const totalBase = salarios.value.reduce((s, x) => s + (x.sueldo_base || 0), 0)
  const totalPagos = salarios.value.reduce((s, x) => s + (x.total_pagos || 0), 0)
  const totalAdel = salarios.value.reduce((s, x) => s + (x.total_adelantos || 0), 0)
  const totalNeto = salarios.value.reduce((s, x) => s + (x.neto || 0), 0)
  return [
    { label: 'Total pagado', valor: totalPagos, icon: 'fa-solid fa-sack-dollar', tone: 'pagos' },
    { label: 'Adelantos', valor: totalAdel, icon: 'fa-solid fa-hand-holding-dollar', tone: 'adelantos' },
    { label: 'Neto entregado', valor: totalNeto, icon: 'fa-solid fa-check-double', tone: 'neto' }
  ]
})

const calcularMes = async () => {
  loading.value = true
  try {
    if (!mesSeleccionado.value) return
    const res = await api.get('/personal/salarios', { params: { fecha: fechaLocal(mesSeleccionado.value) } })
    rango.value = formatFecha(res.data.inicio) + ' — ' + formatFecha(res.data.fin)
    if (res.data.success) {
      salarios.value = res.data.data
    } else {
      toast.add({ severity: 'error', summary: 'No se pudo calcular', detail: res.data.error || '', life: 3500 })
    }
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error al calcular salarios', life: 3500 })
  } finally {
    loading.value = false
  }
}

onMounted(calcularMes)
</script>

<style scoped>
.form-nomina { display: grid; gap: .8rem; }
.descuento { display: flex; align-items: center; gap: .5rem; margin-bottom: .5rem; }
small { display: block; }
.salarios-view { padding: 2rem; }

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.5rem;
}
.page-header h1 { margin: 0; font-size: 1.5rem; color: var(--text-main); }
.page-header p { margin: 0.25rem 0 0; color: var(--text-muted); font-size: 0.9rem; }
.actions { display: flex; gap: 0.75rem; align-items: center; }

/* Tarjetas resumen */
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; }
.stat-card {
  display: flex; align-items: center; gap: 1rem;
  background: var(--bg-card); border: 1px solid var(--border-color);
  border-radius: 14px; padding: 1.1rem 1.25rem;
  box-shadow: var(--shadow-soft);
  transition: transform 0.25s cubic-bezier(0.22, 1, 0.36, 1), box-shadow 0.25s ease;
}
.stat-card:hover { transform: translateY(-3px); box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08); }
.stat-icon { width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1rem; flex-shrink: 0; }
.stat-icon.base { background: rgba(59, 130, 246, 0.12); color: #3b82f6; }
.stat-icon.pagos { background: rgba(16, 185, 129, 0.12); color: #10b981; }
.stat-icon.adelantos { background: rgba(245, 158, 11, 0.14); color: #b45309; }
.stat-icon.neto { background: rgba(255, 123, 0, 0.14); color: var(--btn-primary); }
.stat-content { display: flex; flex-direction: column; }
.stat-label { font-size: 0.72rem; color: var(--text-muted); }
.stat-value { font-size: 1.25rem; font-weight: 700; color: var(--text-main); }

/* Tabla */
.table-card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 14px; padding: 1.25rem; margin-top: 1.25rem; box-shadow: var(--shadow-soft); }
.mt-4 { margin-top: 1rem; }

.emp-cell { display: flex; align-items: center; gap: 0.75rem; }
.emp-avatar {
  width: 36px; height: 36px; border-radius: 10px;
  background: linear-gradient(135deg, var(--btn-primary), var(--btn-gradient-end));
  color: #fff; font-weight: 700; font-size: 0.8rem;
  display: flex; align-items: center; justify-content: center;
}
.emp-info { display: flex; flex-direction: column; }
.emp-nombre { font-weight: 600; color: var(--text-main); }
.emp-usuario { font-size: 0.75rem; color: var(--text-muted); }

.neto-val { color: var(--text-main); }

.tag-diff { padding: 0.15rem 0.6rem; border-radius: 999px; font-size: 0.75rem; font-weight: 600; }
.tag-ok { background: rgba(34, 197, 94, 0.12); color: #16a34a; }
.tag-pend { background: rgba(245, 158, 11, 0.15); color: #b45309; }

/* Skeletons */
.skeleton-row { display: flex; align-items: center; gap: 1rem; padding: 0.9rem 0.25rem; border-bottom: 1px solid var(--border-color); }
.sk {
  border-radius: 8px;
  background: linear-gradient(90deg, rgba(148,163,184,0.12) 25%, rgba(148,163,184,0.25) 50%, rgba(148,163,184,0.12) 75%);
  background-size: 400% 100%;
  animation: shimmer 1.4s infinite linear;
}
.sk-avatar { width: 36px; height: 36px; border-radius: 10px; }
.sk-line { height: 14px; }
.w-30 { width: 30%; } .w-15 { width: 15%; }
@keyframes shimmer { 0% { background-position: 100% 0; } 100% { background-position: -100% 0; } }

/* Estado vacío */
.empty-card {
  text-align: center; padding: 3rem 1rem; margin-top: 1.25rem;
  background: var(--bg-card); border: 1px dashed var(--border-color); border-radius: 14px;
}
.empty-icon { font-size: 2rem; color: var(--text-muted); opacity: 0.5; }
.empty-card h3 { margin: 0.75rem 0 0.25rem; color: var(--text-main); }
.empty-card p { margin: 0; color: var(--text-muted); font-size: 0.9rem; }
.empty-state { text-align: center; padding: 2rem; color: var(--text-muted); }

/* Animaciones de entrada */
.animate-item { animation: slide-in 0.45s cubic-bezier(0.22, 1, 0.36, 1); }
@keyframes slide-in { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: none; } }

.pop-enter-active { transition: all 0.4s cubic-bezier(0.22, 1, 0.36, 1); }
.pop-enter-from { opacity: 0; transform: translateY(12px) scale(0.97); }
.pop-enter-to { opacity: 1; transform: none; }
.pop-leave-active { transition: all 0.25s ease; position: absolute; }
.pop-move { transition: transform 0.4s cubic-bezier(0.22, 1, 0.36, 1); }

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.fade-up-enter-active { transition: all 0.45s cubic-bezier(0.22, 1, 0.36, 1); }
.fade-up-enter-from { opacity: 0; transform: translateY(14px); }
.fade-up-enter-to { opacity: 1; transform: none; }

/* Responsive */
@media (max-width: 768px) {
  .page-header { flex-direction: column; align-items: flex-start; }
  .actions { width: 100%; }
  .actions .mes-picker { flex: 1; }
}
</style>
