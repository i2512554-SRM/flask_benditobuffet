<template>
  <Dialog v-model:visible="interno" :header="titulo" :modal="true" :closable="true">
    <div class="field">
      <label for="tipo-tx">Tipo</label>
      <Select id="tipo-tx" v-model="form.tipo" :options="tiposTransaccion" optionLabel="label" optionValue="value" class="w-full" />
    </div>
    <div class="field">
      <label for="monto-tx">Monto (S/.)</label>
      <InputNumber placeholder="Ej. 100.00" id="monto-tx" v-model="form.monto" mode="currency" currency="PEN" locale="es-PE" :min="0" :minFractionDigits="2" :maxFractionDigits="2" class="w-full" />
    </div>
    <div class="field">
      <label for="metodo-pago">Método de pago</label>
      <Select id="metodo-pago" v-model="form.metodo_pago" :options="metodosPago" class="w-full" />
    </div>
    <div class="field">
      <label for="descripcion-tx">Descripción</label>
      <InputText id="descripcion-tx" v-model="form.descripcion" class="w-full" placeholder="Detalle del movimiento" />
    </div>
    <template #footer>
      <Button :disabled="guardando" label="Cancelar" severity="secondary" @click="cerrar" />
      <Button :disabled="guardando" label="Registrar" :loading="guardando" @click="registrar" />
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import Dialog from 'primevue/dialog'
import InputNumber from 'primevue/inputnumber'
import InputText from 'primevue/inputtext'
import Select from 'primevue/select'
import Button from 'primevue/button'
import { useToast } from 'primevue/usetoast'
import api from '../../config/axios'

const props = defineProps({
  visible: { type: Boolean, default: false },
  tipo: { type: String, default: 'Venta' }
})

const emit = defineEmits(['update:visible', 'registrado'])

const toast = useToast()
const guardando = ref(false)

const metodosPago = ['Efectivo', 'Tarjeta', 'Yape', 'Plin', 'Transferencia', 'Otros']
const tiposTransaccion = [
  { label: 'Ingreso (Venta)', value: 'Venta' },
  { label: 'Egreso (Gasto)', value: 'Gasto' }
]

const form = ref({ tipo: 'Venta', metodo_pago: 'Efectivo', monto: null, descripcion: '', clave_operacion: null })

const interno = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

const titulo = computed(() => (form.value.tipo === 'Venta' ? 'Registrar ingreso' : 'Registrar egreso'))

watch(
  () => props.visible,
  (val) => {
    if (val) {
      form.value = {
        tipo: props.tipo === 'Gasto' ? 'Gasto' : 'Venta',
        metodo_pago: 'Efectivo',
        monto: null,
        descripcion: '',
        clave_operacion: crypto.randomUUID()
      }
    }
  }
)

const cerrar = () => {
  interno.value = false
}

const registrar = async () => {
  if (guardando.value) return
  const monto = Number(form.value.monto)
  if (!monto || monto <= 0) {
    toast.add({ severity: 'warn', summary: 'Ingrese un monto mayor que cero', life: 3000 })
    return
  }
  if (!form.value.descripcion || !form.value.descripcion.trim()) {
    toast.add({ severity: 'warn', summary: 'Ingrese una descripción', life: 3000 })
    return
  }
  guardando.value = true
  try {
    const res = await api.post('/caja/transacciones', {
      tipo: form.value.tipo,
      monto,
      metodo_pago: form.value.metodo_pago,
      descripcion: form.value.descripcion.trim(),
      clave_operacion: form.value.clave_operacion
    })
    if (res.data.success) {
      toast.add({ severity: 'success', summary: 'Movimiento registrado', life: 2500 })
      emit('registrado')
      cerrar()
    }
  } catch (err) {
    toast.add({ severity: 'error', summary: err.response?.data?.error || 'Error registrando el movimiento', life: 3500 })
  } finally {
    guardando.value = false
  }
}
</script>

<style scoped>
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

.w-full { width: 100%; }
:deep(.p-inputnumber) { width: 100%; }
:deep(.p-select) { width: 100%; }
</style>