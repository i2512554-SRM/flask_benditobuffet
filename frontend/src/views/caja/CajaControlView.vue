<template>
  <div class="caja-view">
    <VolverBtn :to="isAdmin ? links.panel.admin : links.panel.cajera" :etiqueta="isAdmin ? 'Volver al Panel' : 'Volver a Mi Panel'" />
    <div class="page-hero">
      <h1>Control de Caja</h1>
      <p>Abre la caja, consulta la caja activa y ciérrala al finalizar el turno</p>
    </div>

    <div class="estado-panel">
      <!-- Caja cerrada -->
      <div v-if="!cajaAbierta" class="panel-body estado-cerrado">
        <div class="panel-icono"><i class="fa-solid fa-lock"></i></div>
        <h3>Actualmente no existe una caja abierta</h3>
        <p>Para registrar movimientos de caja debes abrirla primero.</p>
        <button :disabled="guardando" class="btn btn-primary" @click="abrirCajaDialog">
          <i class="fa-solid fa-door-open"></i> Abrir caja
        </button>
      </div>

      <!-- Caja abierta -->
      <div v-else class="panel-body">
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">Responsable</span>
            <span class="info-value">{{ caja.cierre?.responsable || '—' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Hora de apertura</span>
            <span class="info-value">{{ soloHora(caja.cierre?.fecha) }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Monto inicial</span>
            <span class="info-value">S/ {{ formatMoney(caja.cierre?.monto_inicial) }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Estado</span>
            <span class="info-value">
              <span class="estado-pill pill-abierta"><i class="fa-solid fa-lock-open"></i> ABIERTA</span>
            </span>
          </div>
          <div class="info-item">
            <span class="info-label">Saldo estimado</span>
            <span class="info-value saldo" :class="(caja.saldo_actual ?? 0) >= 0 ? 'pos' : 'neg'">
              S/ {{ formatMoney(caja.saldo_actual) }}
            </span>
          </div>
        </div>
        <button :disabled="guardando" class="btn btn-danger" @click="cerrarCajaDialog">
          <i class="fa-solid fa-lock"></i> Cerrar caja
        </button>
      </div>
    </div>

    <!-- Dialogo: abrir caja -->
    <Dialog v-model:visible="dialogApertura" header="Abrir caja" :modal="true" :closable="true">
      <div class="field">
        <label for="monto-inicial">Monto inicial (S/.)</label>
        <InputNumber placeholder="Ej. 200.00" id="monto-inicial" v-model="montoInicial" mode="currency" currency="PEN" locale="es-PE" :min="0" :minFractionDigits="2" :maxFractionDigits="2" class="w-full" />
      </div>
      <div class="field">
        <label for="responsable-apertura">Responsable</label>
        <InputText id="responsable-apertura" :model-value="responsable" disabled class="w-full" />
      </div>
      <div class="form-dos-cols">
        <div class="field">
          <label for="fecha-apertura">Fecha</label>
          <InputText id="fecha-apertura" :model-value="fechaApertura" disabled class="w-full" />
        </div>
        <div class="field">
          <label for="hora-apertura">Hora</label>
          <InputText id="hora-apertura" :model-value="horaApertura" disabled class="w-full" />
        </div>
      </div>
      <template #footer>
        <Button :disabled="guardando" label="Cancelar" severity="secondary" @click="dialogApertura = false" />
        <Button :disabled="guardando" label="Abrir caja" :loading="guardando" @click="abrirCaja" />
      </template>
    </Dialog>

    <!-- Dialogo: confirmación de cierre -->
    <Dialog v-model:visible="dialogCierre" header="Cerrar caja" :modal="true" :closable="false">
      <div class="confirm-cuerpo">
        <i class="fa-solid fa-triangle-exclamation"></i>
        <span>Confirma el cierre registrando el efectivo contado en la caja.</span>
      </div>
      <div class="field" style="margin-top: 1rem;">
        <label for="efectivo-contado">Efectivo contado (S/)</label>
        <InputNumber id="efectivo-contado" v-model="efectivoContado" :min="0" mode="currency" currency="PEN" locale="es-PE" class="w-full" placeholder="0.00" :max-fraction-digits="2" />
      </div>
      <p class="saldo-esperado">Efectivo esperado: <strong>S/. {{ fmtEsperado }}</strong></p>
      <template #footer>
        <Button :disabled="guardando" label="Cancelar" severity="secondary" @click="dialogCierre = false" />
        <Button :disabled="guardando || efectivoContado === null" label="Confirmar cierre" severity="danger" :loading="guardando" @click="cerrarCaja" />
      </template>
    </Dialog>

    <div class="loading-overlay" v-if="loading">
      <i class="fa-solid fa-spinner fa-spin"></i>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { soloFecha, soloHora } from '../../utils/format'
import { links } from '../../router/links'
import { ROLES } from '../../config/roles'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import { useToast } from 'primevue/usetoast'
import VolverBtn from '../../components/ui/VolverBtn.vue'
import { useAuthStore } from '../../stores/auth'
import api from '../../config/axios'

const route = useRoute()
const router = useRouter()
const toast = useToast()
const authStore = useAuthStore()
const isAdmin = computed(() => authStore.user?.rol === ROLES.ADMIN)

const loading = ref(true)
const guardando = ref(false)
const caja = ref({ abierta: false, cierre: null, saldo_actual: 0 })
const dialogApertura = ref(false)
const dialogCierre = ref(false)
const montoInicial = ref(null)
const efectivoContado = ref(null)
const fechaApertura = ref('')
const horaApertura = ref('')

const cajaAbierta = computed(() => !!caja.value.abierta)
const responsable = computed(() => authStore.user?.nombre || '—')
const formatMoney = (val) => Number(val || 0).toLocaleString('es-PE', { minimumFractionDigits: 2 })
const efectivoEsperado = computed(() => {
  const inicial = Number(caja.value.cierre?.monto_inicial || 0)
  const flujo = (caja.value.transacciones || []).reduce((acc, t) => {
    if (t.metodo_pago !== 'Efectivo') return acc
    return acc + (t.tipo === 'Venta' ? Number(t.monto || 0) : -Number(t.monto || 0))
  }, 0)
  return Number((inicial + flujo).toFixed(2))
})
const fmtEsperado = computed(() => formatMoney(efectivoEsperado.value))

const cargarCajaActual = async () => {
  loading.value = true
  try {
    const res = await api.get('/caja/actual')
    if (res.data.success) caja.value = res.data.data
  } catch (error) {
    console.error('Error cargando caja:', error)
  } finally {
    loading.value = false
  }
}

const abrirSegunAccion = async () => {
  const accion = route.query.accion
  if (!accion) return
  if (accion === 'apertura') {
    if (cajaAbierta.value) {
      toast.add({ severity: 'info', summary: 'La caja ya está abierta', life: 3000 })
    } else {
      abrirCajaDialog()
    }
  } else if (accion === 'cierre') {
    if (!cajaAbierta.value) {
      toast.add({ severity: 'info', summary: 'No hay una caja abierta para cerrar', life: 3000 })
    } else {
      cerrarCajaDialog()
    }
  } else if (accion === 'ingreso') {
    router.replace({ path: links.caja.movimientos, query: { registrar: 'ingreso' } })
    return
  } else if (accion === 'egreso') {
    router.replace({ path: links.caja.movimientos, query: { registrar: 'egreso' } })
    return
  } else if (accion === 'historial') {
    router.replace(links.caja.historial)
    return
  }
  router.replace({ query: {} })
}

onMounted(async () => {
  await cargarCajaActual()
  abrirSegunAccion()
})

const abrirCajaDialog = () => {
  montoInicial.value = null
  const ahora = new Date()
  fechaApertura.value = soloFecha(ahora.toISOString())
  horaApertura.value = soloHora(ahora.toISOString())
  dialogApertura.value = true
}

const abrirCaja = async () => {
  if (guardando.value) return
  guardando.value = true
  try {
    const res = await api.post('/caja/abrir', { monto_inicial: Number(montoInicial.value || 0) })
    if (res.data.success) {
      toast.add({ severity: 'success', summary: 'Caja abierta', life: 2500 })
      dialogApertura.value = false
      await cargarCajaActual()
    }
  } catch (error) {
    toast.add({ severity: 'error', summary: error.response?.data?.error || 'No se pudo abrir la caja', life: 4000 })
  } finally {
    guardando.value = false
  }
}

const cerrarCajaDialog = () => {
  efectivoContado.value = efectivoEsperado.value ?? null
  dialogCierre.value = true
}

const cerrarCaja = async () => {
  if (guardando.value) return
  guardando.value = true
  try {
    const res = await api.post('/caja/cerrar', { efectivo_contado: Number(efectivoContado.value ?? 0) })
    if (res.data.success) {
      toast.add({ severity: 'success', summary: 'Caja cerrada correctamente', life: 2500 })
      dialogCierre.value = false
      await cargarCajaActual()
    }
  } catch (error) {
    toast.add({ severity: 'error', summary: error.response?.data?.error || 'No se pudo cerrar la caja', life: 4000 })
  } finally {
    guardando.value = false
  }
}
</script>

<style scoped>
.caja-view { padding: 0; }

.page-hero {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.5rem;
}

.estado-panel {
  margin-top: 1rem;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  box-shadow: var(--shadow-soft);
  padding: 1.25rem;
}

.panel-body {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  text-align: center;
}

.panel-icono {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  background: rgba(220, 38, 38, 0.1);
  color: var(--color-rojo);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
}

.estado-cerrado h3 {
  margin: 0;
  font-size: 1rem;
  color: var(--text-main);
}

.estado-cerrado p {
  margin: 0;
  font-size: 0.85rem;
  color: var(--text-muted);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 0.9rem;
  width: 100%;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 0.9rem 1rem;
  background: var(--bg-secondary);
  border-radius: 12px;
}

.info-label {
  font-size: 0.7rem;
  color: var(--text-muted);
  font-weight: 600;
}

.info-value {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--text-main);
}

.info-value.saldo.pos { color: var(--color-verde-fuerte); }
.info-value.saldo.neg { color: var(--color-rojo); }

.estado-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
}

.pill-abierta { background: rgba(22, 163, 74, 0.14); color: #16a34a; }

.btn-danger {
  background: var(--color-rojo);
  color: #fff;
  border: 1px solid var(--color-rojo);
}

.btn-danger:hover {
  filter: brightness(0.95);
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  margin-bottom: 1rem;
}

.field label {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--text-muted);
}

.form-dos-cols {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.w-full { width: 100%; }
:deep(.p-inputnumber) { width: 100%; }

.confirm-cuerpo {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0;
  text-align: center;
  color: var(--text-main);
  font-size: 0.95rem;
  font-weight: 600;
}

.confirm-cuerpo i {
  font-size: 1.6rem;
  color: #b45309;
}

.saldo-esperado {
  margin: 0.85rem 0 0;
  font-size: 0.85rem;
  color: var(--text-muted);
  text-align: center;
}

.saldo-esperado strong {
  color: var(--text-main);
}

.loading-overlay {
  display: flex;
  justify-content: center;
  padding: 2rem;
  color: var(--btn-primary);
  font-size: 1.5rem;
}

@media (max-width: 600px) {
  .form-dos-cols { grid-template-columns: 1fr; }
}
</style>
