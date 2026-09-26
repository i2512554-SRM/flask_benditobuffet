<template>
  <div class="adelantos-view">
    <VolverBtn :to="links.personal.modulo" />
    <h1>Adelantos de Salario</h1>
    
    <div class="actions">
      <Button :disabled="$saving" label="Registrar Adelanto" icon="pi pi-plus" @click="registrarDialog" />
    </div>
    
    <DataTable :value="adelantos" :paginator="true" :rows="10" class="mt-4">
      <Column field="fecha" header="Fecha" sortable><template #body="{data}">{{ soloFecha(data.fecha) }}</template></Column>
      <Column field="id_usuario" header="Empleado"></Column>
      <Column field="monto" header="Monto" sortable>
        <template #body="slotProps">
          S/. {{ slotProps.data.monto }}
        </template>
      </Column>
      <Column field="estado" header="Estado">
        <template #body="slotProps">
          <Tag :value="slotProps.data.estado" :severity="slotProps.data.estado === 'Pendiente' ? 'warning' : 'success'" />
        </template>
      </Column>
      <Column field="motivo" header="Motivo"></Column>
    </DataTable>
    
    <Dialog v-model:visible="dialogVisible" header="Registrar Adelanto" :modal="true" :style="{ width: '500px' }">
      <div class="formgrid grid">
        <div class="field col-6">
          <label for="empleado">Empleado</label>
          <Select id="empleado" v-model="form.id_usuario" :options="empleados" optionLabel="nombres" optionValue="id_usuario" class="w-full" />
        </div>
        <div class="field col-6">
          <label for="monto">Monto</label>
          <InputNumber :maxFractionDigits="2" placeholder="Ej. 100.00" id="monto" v-model="form.monto" mode="currency" currency="PEN" locale="es-PE" class="w-full" />
        </div>
        <div class="field col-12">
          <label for="motivo">Motivo</label>
          <InputText id="motivo" v-model="form.motivo" class="w-full" />
        </div>
      </div>
      <template #footer>
        <Button :disabled="$saving || guardando" label="Cancelar" severity="secondary" @click="dialogVisible = false" />
        <Button :disabled="$saving || guardando" :loading="guardando" label="Guardar" @click="guardar" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import VolverBtn from '../../components/ui/VolverBtn.vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Select from 'primevue/select'
import Tag from 'primevue/tag'
import { useToast } from 'primevue/usetoast'
import api from '../../config/axios'
import { links } from '../../router/links'
import { ROLES } from '../../config/roles'
import { soloFecha } from '../../utils/format'

const toast = useToast()
const adelantos = ref([])
const empleados = ref([])
const dialogVisible = ref(false)
const form = ref({})
const guardando = ref(false)

onMounted(async () => {
  try {
    await Promise.all([cargarAdelantos(), cargarEmpleados()])
  } catch (err) {
    toast.add({ severity: 'error', summary: 'No se pudieron cargar los adelantos', life: 3500 })
  }
})

const cargarAdelantos = async () => {
  const res = await api.get('/personal/adelantos')
  if (res.data.success) adelantos.value = res.data.data
}

const cargarEmpleados = async () => {
  const res = await api.get('/personal/')
  if (res.data.success) empleados.value = (res.data.data || []).filter((emp) => emp.estado && emp.id_rol !== ROLES.ADMIN)
}

const registrarDialog = () => {
  form.value = { id_usuario: null, monto: null, motivo: '' }
  dialogVisible.value = true
}

const guardar = async () => {
  if (guardando.value) return
  if (!form.value.id_usuario) {
    toast.add({ severity: 'warn', summary: 'Seleccione un empleado', life: 3000 })
    return
  }
  if (!Number.isFinite(form.value.monto) || form.value.monto <= 0) {
    toast.add({ severity: 'warn', summary: 'Ingrese un monto positivo', life: 3000 })
    return
  }
  if (!form.value.motivo?.trim()) {
    toast.add({ severity: 'warn', summary: 'Ingrese el motivo del adelanto', life: 3000 })
    return
  }

  guardando.value = true
  try {
    await api.post('/personal/adelantos', form.value)
    dialogVisible.value = false
    toast.add({ severity: 'success', summary: 'Adelanto registrado', life: 3000 })
    try {
      await cargarAdelantos()
    } catch {
      toast.add({ severity: 'warn', summary: 'Adelanto registrado', detail: 'Actualiza la lista para ver el nuevo registro.', life: 4000 })
    }
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'No se pudo registrar el adelanto',
      detail: err.response?.data?.error || 'Intenta nuevamente',
      life: 4000
    })
  } finally {
    guardando.value = false
  }
}
</script>

<style scoped>
.adelantos-view { padding: 2rem; }
.actions { display: flex; gap: 1rem; margin-bottom: 1rem; }
.mt-4 { margin-top: 1rem; }
</style>
