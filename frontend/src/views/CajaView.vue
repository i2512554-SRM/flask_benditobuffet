<template>
  <div class="caja-view">
    <VolverBtn :to="isAdmin ? '/panel' : '/panel-cajera'" :etiqueta="isAdmin ? 'Volver al Panel' : 'Volver a Mi Panel'" />
    <div class="page-hero">
      <h1>Gestión de Caja</h1>
      <p>Apertura, ingresos, egresos, cierre e historial de movimientos en una sola pantalla</p>
      <router-link to="/caja/reportes" class="btn btn-outline btn-reports">
        <i class="fa-solid fa-chart-line"></i> Reportes Financieros
      </router-link>
    </div>
    
    <div class="actions">
      <Button label="Abrir Caja" icon="pi pi-plus" @click="abrirCajaDialog" :disabled="$saving || (cajaAbierta)" />
      <Button label="Cerrar Caja" icon="pi pi-times" severity="danger" @click="cerrarCajaDialog" :disabled="$saving || (!cajaAbierta)" />
      <Button label="Registrar Ingreso" icon="pi pi-plus" @click="registrarIngresoDialog" :disabled="$saving || (!cajaAbierta)" />
      <Button label="Registrar Egreso" icon="pi pi-minus" severity="warning" @click="registrarEgresoDialog" :disabled="$saving || (!cajaAbierta)" />
      <Button :disabled="$saving" label="Historial" icon="pi pi-history" @click="historialDialog" />
    </div>
    
    <div v-if="cajaAbierta" class="status-box">
      <h3>Caja Abierta</h3>
      <p>Total ventas: S/. {{ totalVentas }}</p>
      <p>Total egresos: S/. {{ totalEgresos }}</p>
      <p>Neto del dia: S/. {{ netoDia }}</p>
    </div>
    
    <DataTable :value="transacciones" class="mt-4">
      <Column field="fecha" header="Fecha"><template #body="{data}">{{ fechaLegible(data.fecha) }}</template></Column>
      <Column field="tipo" header="Tipo"></Column>
      <Column field="monto" header="Monto"></Column>
      <Column field="descripcion" header="Descripcion"></Column>
    </DataTable>
    
    <Dialog v-model:visible="dialogAbierta" header="Abrir Caja" :modal="true">
      <label>Monto inicial (opcional)</label><InputNumber v-model="montoInicial" placeholder="Ej. 100.00" :min="0" :maxFractionDigits="2" />
      <template #footer>
        <Button :disabled="$saving" label="Cancelar" severity="secondary" @click="dialogAbierta = false" />
        <Button :disabled="$saving" label="Abrir" @click="abrirCaja" />
      </template>
    </Dialog>
    
    <Dialog v-model:visible="dialogTransaccion" header="Registrar Transaccion" :modal="true">
      <div class="field">
        <label for="tipo">Tipo</label>
        <Select id="tipo" v-model="nuevaTransaccion.tipo" :options="tiposTransaccion" optionLabel="label" optionValue="value" />
      </div>
      <div class="field">
        <label for="monto">Monto</label>
        <InputNumber placeholder="Ej. 100.00" id="monto" v-model="nuevaTransaccion.monto" mode="decimal" :min="0" :minFractionDigits="2" :maxFractionDigits="2" />
      </div>
      <div class="field"><label for="metodo-pago">Método de pago</label><Select id="metodo-pago" v-model="nuevaTransaccion.metodo_pago" :options="metodosPago" class="w-full" /></div>
      <div class="field">
        <label for="descripcion">Descripcion</label>
        <InputText id="descripcion" v-model="nuevaTransaccion.descripcion" />
      </div>
      <template #footer>
        <Button :disabled="$saving" label="Cancelar" severity="secondary" @click="dialogTransaccion = false" />
        <Button :disabled="$saving" label="Registrar" @click="registrarTransaccion" />
      </template>
    </Dialog>
    
    <Dialog v-model:visible="dialogCierre" header="Cerrar Caja" :modal="true">
      <div class="resumen">
        <h3>Resumen de Caja</h3>
        <p>Total ventas: S/. {{ totalVentas }}</p>
        <p>Total egresos: S/. {{ totalEgresos }}</p>
        <p>Neto del dia: S/. {{ netoDia }}</p>
      </div>
      <template #footer>
        <Button :disabled="$saving" label="Cancelar" severity="secondary" @click="dialogCierre = false" />
        <Button :disabled="$saving" label="Cerrar Caja" severity="danger" @click="cerrarCaja" />
      </template>
    </Dialog>
    
    <Dialog v-model:visible="dialogHistorial" header="Historial de Cajas" :modal="true" :style="{ width: '80vw' }">
      <DataTable :value="historial" class="mt-4">
        <Column field="fecha" header="Fecha"><template #body="{data}">{{ fechaLegible(data.fecha) }}</template></Column>
        <Column field="total_ventas" header="Ventas"></Column>
        <Column field="total_gastos" header="Gastos"></Column>
        <Column field="neto" header="Neto"></Column>
        <Column header="Acciones">
          <template #body="slotProps">
            <Button :disabled="$saving" icon="pi pi-eye" severity="info" @click="verDetalle(slotProps.data)" />
          </template>
        </Column>
      </DataTable>
      <template #footer>
        <Button :disabled="$saving" label="Cerrar" severity="secondary" @click="dialogHistorial = false" />
      </template>
    </Dialog>

    <Dialog v-model:visible="dialogDetalle" header="Detalle de Caja" :modal="true" :style="{ width: '480px' }">
      <div v-if="detalleSeleccionada" class="detalle-caja">
        <div class="dc-row">
          <span class="dc-label">Fecha</span>
          <span class="dc-value">{{ fechaLegible(detalleSeleccionada.fecha) }}</span>
        </div>
        <div class="dc-row">
          <span class="dc-label">Estado</span>
          <span class="dc-value">{{ estadoLabel(detalleSeleccionada.estado) }}</span>
        </div>
        <div class="dc-row">
          <span class="dc-label">Total ventas</span>
          <span class="dc-value">S/. {{ fmtMoney(detalleSeleccionada.total_ventas) }}</span>
        </div>
        <div class="dc-row">
          <span class="dc-label">Total gastos</span>
          <span class="dc-value">S/. {{ fmtMoney(detalleSeleccionada.total_gastos) }}</span>
        </div>
        <div class="dc-row dc-total" :class="(detalleSeleccionada.neto ?? 0) >= 0 ? 'pos' : 'neg'">
          <span class="dc-label">Neto</span>
          <span class="dc-value">S/. {{ fmtMoney(detalleSeleccionada.neto) }}</span>
        </div>
      </div>
      <template #footer>
        <Button :disabled="$saving" label="Cerrar" severity="secondary" @click="dialogDetalle = false" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { formatFecha as fechaLegible } from '../utils/format'
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Button from 'primevue/button'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Select from 'primevue/select'
import { useToast } from 'primevue/usetoast'
import VolverBtn from '../components/ui/VolverBtn.vue'
import { useAuthStore } from '../stores/auth'
import api from '../config/axios'

const route = useRoute()
const router = useRouter()
const toast = useToast()
const authStore = useAuthStore()
const isAdmin = computed(() => authStore.user?.rol === 1)
const transacciones = ref([])
const historial = ref([])
const cajaActual = ref({ abierta: false, cierre: null, ventas_dia: 0, gastos_dia: 0, neto_dia: 0, transacciones: [] })
const montoInicial = ref(null)
const dialogAbierta = ref(false)
const dialogTransaccion = ref(false)
const dialogCierre = ref(false)
const dialogHistorial = ref(false)
const dialogDetalle = ref(false)
const detalleSeleccionada = ref(null)
const metodosPago = ['Efectivo', 'Tarjeta', 'Yape', 'Plin', 'Transferencia', 'Otros']
const nuevaTransaccion = ref({
  tipo: 'Venta', metodo_pago: 'Efectivo',
  monto: null,
  descripcion: ''
})

const tiposTransaccion = [
  { label: 'Venta', value: 'Venta' },
  { label: 'Gasto', value: 'Gasto' }
]

const cajaAbierta = computed(() => !!cajaActual.value.abierta)

const totalVentas = computed(() => {
  return transacciones.value
    .filter(t => t.tipo === 'Venta')
    .reduce((sum, t) => sum + t.monto, 0)
    .toFixed(2)
})

const totalEgresos = computed(() => {
  return transacciones.value
    .filter(t => t.tipo === 'Gasto')
    .reduce((sum, t) => sum + t.monto, 0)
    .toFixed(2)
})

const netoDia = computed(() => {
  return (Number(totalVentas.value) - Number(totalEgresos.value)).toFixed(2)
})

onMounted(async () => {
  await cargarCajaActual()
  await cargarTransacciones()
  abrirSegunAccion()
})

const abrirSegunAccion = async () => {
  const accion = route.query.accion
  if (!accion) return
  if (accion === 'apertura') {
    if (cajaAbierta.value) {
      toast.add({ severity: 'info', summary: 'La caja ya está abierta', life: 3000 })
    } else {
      abrirCajaDialog()
    }
  } else if (accion === 'ingreso') {
    registrarIngresoDialog()
  } else if (accion === 'egreso') {
    registrarEgresoDialog()
  } else if (accion === 'cierre') {
    if (!cajaAbierta.value) {
      toast.add({ severity: 'info', summary: 'No hay una caja abierta para cerrar', life: 3000 })
    } else {
      cerrarCajaDialog()
    }
  } else if (accion === 'historial') {
    historialDialog()
  }
  router.replace({ query: {} })
}

const cargarCajaActual = async () => {
  try {
    const response = await api.get('/caja/actual')
    if (response.data.success) {
      cajaActual.value = response.data.data
      transacciones.value = response.data.data.transacciones || []
    }
  } catch (error) {
    console.error('Error cargando caja:', error)
  }
}

const cargarTransacciones = async () => {
  try {
    const response = await api.get('/caja/transacciones')
    if (response.data.success) {
      transacciones.value = response.data.data
    }
  } catch (error) {
    console.error('Error cargando transacciones:', error)
  }
}

const abrirCajaDialog = () => {
  dialogAbierta.value = true
}

const registrarIngresoDialog = () => {
  nuevaTransaccion.value = { tipo: 'Venta', metodo_pago: 'Efectivo', monto: null, descripcion: '' }
  dialogTransaccion.value = true
}

const registrarEgresoDialog = () => {
  nuevaTransaccion.value = { tipo: 'Gasto', metodo_pago: 'Efectivo', monto: null, descripcion: '' }
  dialogTransaccion.value = true
}

const registrarTransaccionDialog = () => {
  dialogTransaccion.value = true
}

const cerrarCajaDialog = () => {
  dialogCierre.value = true
}

const historialDialog = async () => {
  await cargarHistorial()
  dialogHistorial.value = true
}

const cargarHistorial = async () => {
  try {
    const response = await api.get('/caja/historial')
    if (response.data.success) {
      historial.value = response.data.data
    }
  } catch (error) {
    console.error('Error cargando historial:', error)
  }
}

const verDetalle = (caja) => {
  detalleSeleccionada.value = caja
  dialogDetalle.value = true
}

const fmtMoney = (v) => Number(v || 0).toLocaleString('es-PE', { minimumFractionDigits: 2 })
const estadoLabel = (e) => (e === 'abierta' ? 'Abierta' : e === 'cerrada' ? 'Cerrada' : e || '—')

const abrirCaja = async () => {
  try {
    const response = await api.post('/caja/abrir', { monto_inicial: montoInicial.value || 0 })
    if (response.data.success) {
      await cargarCajaActual()
      dialogAbierta.value = false
    }
  } catch (error) {
    toast.add({ severity: 'error', summary: error.response?.data?.error || 'No se pudo completar la operación', life: 4000 })
  }
}

const registrarTransaccion = async () => {
  const monto = Number(nuevaTransaccion.value.monto)
  if (!monto || monto <= 0) {
    toast.add({ severity: 'warn', summary: 'Ingrese un monto mayor que cero', life: 3000 })
    return
  }
  if (!nuevaTransaccion.value.descripcion || !nuevaTransaccion.value.descripcion.trim()) {
    toast.add({ severity: 'warn', summary: 'Ingrese una descripción', life: 3000 })
    return
  }
  try {
    const response = await api.post('/caja/transacciones', {
      tipo: nuevaTransaccion.value.tipo,
      monto,
      metodo_pago: nuevaTransaccion.value.metodo_pago,
      descripcion: nuevaTransaccion.value.descripcion.trim()
    })
    if (response.data.success) {
      await cargarTransacciones()
      await cargarCajaActual()
      dialogTransaccion.value = false
      nuevaTransaccion.value = { tipo: 'Venta', metodo_pago: 'Efectivo', monto: null, descripcion: '' }
      toast.add({ severity: 'success', summary: 'Transacción registrada', life: 2500 })
    }
  } catch (error) {
    toast.add({ severity: 'error', summary: error.response?.data?.error || 'Error registrando transacción', life: 3500 })
  }
}

const cerrarCaja = async () => {
  try {
    const response = await api.post('/caja/cerrar')
    if (response.data.success) {
      await cargarCajaActual()
      transacciones.value = []
      dialogCierre.value = false
    }
  } catch (error) {
    toast.add({ severity: 'error', summary: error.response?.data?.error || 'No se pudo completar la operación', life: 4000 })
  }
}
</script>
<style scoped>
.caja-view {
  padding: 0;
}

.page-hero {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.5rem;
}

.btn-reports {
  margin-top: 0.5rem;
}

.actions {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.status-box {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.mt-4 {
  margin-top: 1rem;
}

.detalle-caja {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.dc-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.6rem 0.75rem;
  background: var(--bg-secondary);
  border-radius: 10px;
}

.dc-label {
  font-size: 0.78rem;
  color: var(--text-muted);
  font-weight: 600;
}

.dc-value {
  font-size: 0.92rem;
  font-weight: 600;
  color: var(--text-main);
}

.dc-total {
  margin-top: 0.25rem;
}

.dc-total.pos {
  background: rgba(22, 163, 74, 0.1);
}

.dc-total.pos .dc-value { color: var(--color-verde-fuerte); }

.dc-total.neg {
  background: rgba(220, 38, 38, 0.08);
}

.dc-total.neg .dc-value { color: var(--color-rojo); }
</style>
