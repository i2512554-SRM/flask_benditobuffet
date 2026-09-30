<template>
  <template v-if="auth.userRole !== 1">
    <Button label="Solicitar adelanto" icon="pi pi-wallet" @click="visible = true" />
    <Dialog v-model:visible="visible" header="Solicitar adelanto" modal :style="{ width: 'min(440px, 95vw)' }" :closable="!enviando">
      <form @submit.prevent="enviar" class="solicitud-form">
        <label for="adelanto-motivo">Motivo</label>
        <InputText id="adelanto-motivo" v-model="motivo" required maxlength="255" />
        <label for="adelanto-monto">Monto (S/)</label>
        <InputNumber id="adelanto-monto" v-model="monto" placeholder="Ej. 150.00" :min="0.01" :maxFractionDigits="2" />
        <Button type="submit" label="Enviar solicitud" :loading="enviando" :disabled="enviando" />
      </form>
    </Dialog>
  </template>
</template>
<script setup>
import { ref } from 'vue'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import { useToast } from 'primevue/usetoast'
import { useAuthStore } from '../../stores/auth'
import api from '../../config/axios'
const auth = useAuthStore()
const toast = useToast()
const emit = defineEmits(['enviado'])
const visible = ref(false), enviando = ref(false), motivo = ref(''), monto = ref(null)
async function enviar() {
  if (enviando.value) return
  if (!motivo.value.trim() || !Number.isFinite(monto.value) || monto.value <= 0) {
    toast.add({ severity: 'warn', summary: 'Completa el motivo y un monto positivo.', life: 3500 }); return
  }
  enviando.value = true
  try {
    await api.post('/perfil/adelantos', { motivo: motivo.value.trim(), monto: monto.value })
    visible.value = false; motivo.value = ''; monto.value = null
    toast.add({ severity: 'success', summary: 'Solicitud registrada como pendiente', life: 3500 })
    emit('enviado')
  } catch (e) {
    toast.add({ severity: 'error', summary: e.response?.data?.error || 'No se pudo enviar la solicitud', life: 4000 })
  } finally { enviando.value = false }
}
</script>
<style scoped>.solicitud-form { display: grid; gap: .8rem; padding-top: .5rem; }</style>
