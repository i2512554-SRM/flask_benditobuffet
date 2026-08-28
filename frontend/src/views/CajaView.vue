<template>
  <div class="caja-view">
    <h1>Gestion de Caja</h1>
    
    <div class="actions">
      <Button label="Abrir Caja" icon="pi pi-plus" @click="abrirCajaDialog" :disabled="cajaAbierta" />
      <Button label="Cerrar Caja" icon="pi pi-times" severity="danger" @click="cerrarCajaDialog" :disabled="!cajaAbierta" />
      <Button label="Registrar Transaccion" icon="pi pi-plus" @click="registrarTransaccionDialog" :disabled="!cajaAbierta" />
      <Button label="Historial" icon="pi pi-history" @click="historialDialog" />
    </div>
    
    <div v-if="cajaAbierta" class="status-box">
      <h3>Caja Abierta</h3>
      <p>Monto inicial: S/. {{ cajaActual.neto }}</p>
      <p>Monto actual: S/. {{ montoActual }}</p>
    </div>
    
    <DataTable :value="transacciones" class="mt-4">
      <Column field="fecha" header="Fecha"></Column>
      <Column field="tipo" header="Tipo"></Column>
      <Column field="monto" header="Monto"></Column>
      <Column field="descripcion" header="Descripcion"></Column>
    </DataTable>
    
    <Dialog v-model:visible="dialogAbierta" header="Abrir Caja" :modal="true">
      <div class="field">
        <label for="monto_inicial">Monto Inicial</label>
        <InputNumber id="monto_inicial" v-model="montoInicial" mode="currency" currency="PEN" locale="es-PE" />
      </div>
      <template #footer>
        <Button label="Cancelar" severity="secondary" @click="dialogAbierta = false" />
        <Button label="Abrir" @click="abrirCaja" />
      </template>
    </Dialog>
    
    <Dialog v-model:visible="dialogTransaccion" header="Registrar Transaccion" :modal="true">
      <div class="field">
        <label for="tipo">Tipo</label>
        <Select id="tipo" v-model="nuevaTransaccion.tipo" :options="tiposTransaccion" optionLabel="label" optionValue="value" />
      </div>
      <div class="field">
        <label for="monto">Monto</label>
        <InputNumber id="monto" v-model="nuevaTransaccion.monto" mode="currency" currency="PEN" locale="es-PE" />
      </div>
      <div class="field">
        <label for="descripcion">Descripcion</label>
        <InputText id="descripcion" v-model="nuevaTransaccion.descripcion" />
      </div>
      <template #footer>
        <Button label="Cancelar" severity="secondary" @click="dialogTransaccion = false" />
        <Button label="Registrar" @click="registrarTransaccion" />
      </template>
    </Dialog>
    
    <Dialog v-model:visible="dialogCierre" header="Cerrar Caja" :modal="true">
      <div class="resumen">
        <h3>Resumen de Caja</h3>
        <p>Monto inicial: S/. {{ cajaActual.neto }}</p>
        <p>Total ventas: S/. {{ totalVentas }}</p>
        <p>Total egresos: S/. {{ totalEgresos }}</p>
        <p>Monto final: S/. {{ montoActual }}</p>
      </div>
      <template #footer>
        <Button label="Cancelar" severity="secondary" @click="dialogCierre = false" />
        <Button label="Cerrar Caja" severity="danger" @click="cerrarCaja" />
      </template>
    </Dialog>
    
    <Dialog v-model:visible="dialogHistorial" header="Historial de Cajas" :modal="true" :style="{ width: '80vw' }">
      <DataTable :value="historial" class="mt-4">
        <Column field="fecha" header="Fecha"></Column>
        <Column field="total_ventas" header="Ventas"></Column>
        <Column field="total_gastos" header="Gastos"></Column>
        <Column field="neto" header="Neto"></Column>
        <Column header="Acciones">
          <template #body="slotProps">
            <Button icon="pi pi-eye" severity="info" @click="verDetalle(slotProps.data)" />
          </template>
        </Column>
      </DataTable>
      <template #footer>
        <Button label="Cerrar" severity="secondary" @click="dialogHistorial = false" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import Button from 'primevue/button'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Dialog from 'primevue/dialog'
import InputNumber from 'primevue/inputnumber'
import InputText from 'primevue/inputtext'
import Select from 'primevue/select'
import api from '../config/axios'

const transacciones = ref([])
const historial = ref([])
const cajaActual = ref({})
const dialogAbierta = ref(false)
const dialogTransaccion = ref(false)
const dialogCierre = ref(false)
const dialogHistorial = ref(false)
const montoInicial = ref(0)
const nuevaTransaccion = ref({
  tipo: 'venta',
  monto: 0,
  descripcion: ''
})

const tiposTransaccion = [
  { label: 'Venta', value: 'venta' },
  { label: 'Egreso', value: 'egreso' }
]

const cajaAbierta = computed(() => cajaActual.value.id_cierre && cajaActual.value.fecha === null)

const totalVentas = computed(() => {
  return transacciones.value
    .filter(t => t.tipo === 'venta')
    .reduce((sum, t) => sum + t.monto, 0)
    .toFixed(2)
})

const totalEgresos = computed(() => {
  return transacciones.value
    .filter(t => t.tipo === 'egreso')
    .reduce((sum, t) => sum + t.monto, 0)
    .toFixed(2)
})

const montoActual = computed(() => {
  if (!cajaActual.value.id_cierre) return 0
  let monto = cajaActual.value.neto
  transacciones.value.forEach(t => {
    if (t.tipo === 'venta') monto += t.monto
    else if (t.tipo === 'egreso') monto -= t.monto
  })
  return monto.toFixed(2)
})

onMounted(async () => {
  await cargarCajaActual()
  await cargarTransacciones()
})

const cargarCajaActual = async () => {
  try {
    const response = await api.get('/caja/actual')
    if (response.data.success) {
      cajaActual.value = response.data.data
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
  // TODO: Implementar vista de detalle
  console.log('Ver detalle de caja:', caja)
}

const abrirCaja = async () => {
  try {
    const response = await api.post('/caja/abrir', { monto_inicial: montoInicial.value })
    if (response.data.success) {
      await cargarCajaActual()
      dialogAbierta.value = false
    }
  } catch (error) {
    console.error('Error abriendo caja:', error)
  }
}

const registrarTransaccion = async () => {
  try {
    const response = await api.post('/caja/transacciones', nuevaTransaccion.value)
    if (response.data.success) {
      await cargarTransacciones()
      dialogTransaccion.value = false
      nuevaTransaccion.value = { tipo: 'venta', monto: 0, descripcion: '' }
    }
  } catch (error) {
    console.error('Error registrando transaccion:', error)
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
    console.error('Error cerrando caja:', error)
  }
}
</script>
<style scoped>
.caja-view {
  padding: 2rem;
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
</style>
