<template>
  <div class="empleados-view">
    <VolverBtn to="/personal" />
    <div class="page-header animate-item">
      <div>
        <h1>Empleados</h1>
        <p>Gestión del personal del restaurante</p>
      </div>
      <Button :disabled="$saving" label="Agregar Empleado" icon="pi pi-plus" @click="agregarDialog" />
    </div>

    <!-- Skeleton -->
    <Transition name="fade">
      <div v-if="loading" class="table-card">
        <div v-for="n in 6" :key="n" class="skeleton-row">
          <div class="sk sk-line w-10"></div>
          <div class="sk sk-line w-25"></div>
          <div class="sk sk-line w-20"></div>
          <div class="sk sk-line w-25"></div>
        </div>
      </div>
    </Transition>

    <Transition name="fade-up">
      <div v-if="!loading" class="table-card">
        <DataTable :value="empleados" :paginator="true" :rows="10" :filters="filtros"
                   dataKey="id_usuario" stripedRows class="mt-4">
          <template #header>
            <div class="table-toolbar">
              <span class="p-input-icon-left">
                <i class="pi pi-search" />
                <InputText v-model="filtros['global'].value" placeholder="Buscar empleado..." />
              </span>
              <span class="total-badge">{{ empleados.length }} empleado(s)</span>
            </div>
          </template>
          <Column field="dni" header="DNI" sortable></Column>
          <Column field="nombres" header="Nombres" sortable></Column>
          <Column field="apellido" header="Apellido" sortable></Column>
          <Column field="rol_nombre" header="Rol" sortable>
            <template #body="slotProps">
              <Tag :value="slotProps.data.rol_nombre || '-'" severity="info" />
            </template>
          </Column>
          <Column field="turno" header="Turno" sortable>
            <template #body="slotProps">
              <span v-if="turnoList(slotProps.data.turno).length" class="turno-tags">
                <span v-for="t in turnoList(slotProps.data.turno)" :key="t" :class="['tag-turno', turnoClase(t)]">{{ t }}</span>
              </span>
              <span v-else class="text-muted">Sin turno</span>
            </template>
          </Column>
          <Column field="estado" header="Estado" sortable>
            <template #body="slotProps">
              <Tag :value="slotProps.data.estado ? 'Activo' : 'Inactivo'" :severity="slotProps.data.estado ? 'success' : 'danger'" />
            </template>
          </Column>
          <Column header="Acciones" style="min-width: 15rem">
            <template #body="slotProps">
              <span class="acciones-row">
                <Button :disabled="$saving" label="Editar" icon="pi pi-pencil" severity="info" text rounded class="btn-accion" title="Editar" @click="editar(slotProps.data)" />
                <Button :disabled="$saving"
                  v-if="slotProps.data.estado"
                  label="Desactivar"
                  icon="pi pi-ban"
                  text
                  rounded
                  class="btn-accion"
                  severity="danger"
                  title="Desactivar usuario"
                  @click="cambiarEstado(slotProps.data, false)"
                />
                <Button :disabled="$saving"
                  v-else
                  label="Reactivar"
                  icon="pi pi-check"
                  text
                  rounded
                  class="btn-accion"
                  severity="success"
                  title="Reactivar usuario"
                  @click="cambiarEstado(slotProps.data, true)"
                />
              </span>
            </template>
          </Column>
          <template #empty>
            <div class="empty-state">No hay empleados registrados.</div>
          </template>
        </DataTable>
      </div>
    </Transition>

    <Dialog v-model:visible="dialogVisible" :header="editing.id_usuario ? 'Editar Empleado' : 'Nuevo Empleado'" :modal="true" :style="{ width: '520px' }">
      <div class="formgrid grid">
        <div class="field col-12">
          <label for="dni">DNI</label>
          <div class="dni-row">
            <InputText id="dni" v-model="form.dni" @input="limpiarCampo('dni', $event)" inputmode="numeric" maxlength="8" class="w-full" placeholder="8 dígitos" @keyup.enter="consultarDni" />
            <Button :disabled="$saving" label="Consultar RENIEC" icon="pi pi-search" severity="secondary" :loading="consultandoDni" @click="consultarDni" />
          </div>
        </div>
        <div class="field col-6">
          <label for="nombres">Nombres</label>
          <InputText id="nombres" v-model="form.nombres" @input="limpiarCampo('nombres', $event)" class="w-full" />
        </div>
        <div class="field col-6">
          <label for="apellido">Apellidos</label>
          <InputText id="apellido" v-model="form.apellido" @input="limpiarCampo('apellido', $event)" class="w-full" />
        </div>
        <div class="field col-6">
          <label for="correo">Correo</label>
          <InputText id="correo" v-model="form.correo" class="w-full" placeholder="Opcional" />
        </div>
        <div class="field col-6">
          <label for="telefono">Teléfono</label>
          <InputText id="telefono" v-model="form.telefono" @input="limpiarCampo('telefono', $event)" inputmode="numeric" maxlength="9" class="w-full" />
        </div>
        <div class="field col-6">
          <label for="rol">Rol</label>
          <Select id="rol" v-model="form.id_rol" :options="roles" optionLabel="nombre" optionValue="id_rol" class="w-full" placeholder="Selecciona un rol" />
        </div>
        <div class="field col-6">
          <label for="turno">Turno</label>
          <MultiSelect id="turno" v-model="form.turno" :options="turnos" optionLabel="label" optionValue="value" class="w-full" placeholder="Uno o varios turnos" />
        </div>
      </div>
      <div class="field" v-if="!editing.id_usuario"><label for="clave-empleado">Contraseña inicial *</label><InputText id="clave-empleado" v-model="form.clave" type="password" autocomplete="new-password" placeholder="Mínimo 8 caracteres" class="w-full" /></div>
      <template #footer>
        <Button :disabled="$saving" label="Cancelar" severity="secondary" @click="dialogVisible = false" />
        <Button :disabled="$saving" label="Guardar" :loading="guardando" @click="guardar" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import VolverBtn from '../components/ui/VolverBtn.vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Select from 'primevue/select'
import MultiSelect from 'primevue/multiselect'
import Tag from 'primevue/tag'
import { FilterMatchMode } from '@primevue/core/api'
import { useToast } from 'primevue/usetoast'
import api from '../config/axios'

const toast = useToast()
const empleados = ref([])
const loading = ref(true)
const dialogVisible = ref(false)
const editing = ref({})
const form = ref({})
function limpiarCampo(campo, evento) {
  const valor = evento.target.value
  const limpio = ['dni', 'telefono'].includes(campo)
    ? valor.replace(/[^0-9]/g, '').slice(0, campo === 'dni' ? 8 : 9)
    : valor.replace(/[^\p{L} '-]/gu, '')
  evento.target.value = limpio
  form.value[campo] = limpio
}
const guardando = ref(false)
const consultandoDni = ref(false)
const filtros = ref({ global: { value: null, matchMode: FilterMatchMode.CONTAINS } })
const roles = [
  { id_rol: 1, nombre: 'Administrador' },
  { id_rol: 2, nombre: 'Cajera' },
  { id_rol: 3, nombre: 'Cocinero' },
  { id_rol: 4, nombre: 'Mozo' }
]
const turnos = [
  { label: 'Tarde', value: 'Tarde' },
  { label: 'Noche', value: 'Noche' }
]

const turnoList = (t) => {
  if (Array.isArray(t)) return t.filter(Boolean)
  return String(t || '').split(',').map(s => s.trim()).filter(Boolean)
}

const turnoClase = (t) => {
  const map = { 'Mañana': 't-manana', 'Tarde': 't-tarde', 'Noche': 't-noche' }
  return map[t] || 't-vacio'
}

onMounted(() => cargar())

const cargar = async () => {
  loading.value = true
  try {
    const res = await api.get('/personal/')
    if (res.data.success) empleados.value = res.data.data
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Error al cargar empleados', life: 3500 })
  } finally {
    loading.value = false
  }
}

const agregarDialog = () => {
  editing.value = {}
  form.value = { clave: '', dni: '', nombres: '', apellido: '', correo: '', telefono: '', id_rol: 2, turno: [] }
  dialogVisible.value = true
}

const editar = (emp) => {
  editing.value = emp
  form.value = { ...emp, turno: turnoList(emp.turno).filter(t => t !== 'Mañana') }
  dialogVisible.value = true
}

const consultarDni = async () => {
  const dni = (form.value.dni || '').trim()
  if (!/^\d{8}$/.test(dni)) {
    toast.add({ severity: 'warn', summary: 'Ingresa un DNI válido de 8 dígitos', life: 3000 })
    return
  }
  consultandoDni.value = true
  try {
    const res = await api.get(`/dni/${dni}`)
    const d = res.data
    if (d && (d.nombres || d.nombres === '')) {
      form.value.nombres = d.nombres || form.value.nombres
      form.value.apellido = `${d.apellidoPaterno || ''} ${d.apellidoMaterno || ''}`.trim() || form.value.apellido
      toast.add({ severity: 'success', summary: 'Datos encontrados en RENIEC', life: 2500 })
    } else if (d && d.error) {
      toast.add({ severity: 'warn', summary: d.error, life: 4000 })
    } else {
      toast.add({ severity: 'warn', summary: 'No se encontraron datos para ese DNI', life: 3500 })
    }
  } catch (err) {
    const msg = err.response?.data?.error || 'No se pudo consultar el DNI'
    toast.add({ severity: 'error', summary: msg, life: 4500 })
  } finally {
    consultandoDni.value = false
  }
}

const guardar = async () => {
  if (guardando.value) return
  if (!/^[0-9]{8}$/.test(form.value.dni || '') || !/^[\p{L} '-]+$/u.test(form.value.nombres || '') || !/^[\p{L} '-]+$/u.test(form.value.apellido || '') || (form.value.telefono && !/^[0-9]{9}$/.test(form.value.telefono))) {
    toast.add({severity:'warn', summary:'Revisa DNI (8 números), nombres y teléfono (9 números).', life:4000}); return
  }
  if (!editing.value.id_usuario && (form.value.clave || '').length < 8) {
    toast.add({severity:'warn', summary:'Ingresa una contraseña de al menos 8 caracteres.', life:4000}); return
  }
  if (!form.value.dni || !form.value.nombres || !form.value.apellido) {
    toast.add({ severity: 'warn', summary: 'DNI, nombres y apellidos son obligatorios', life: 3500 })
    return
  }
  if (!form.value.id_rol) {
    toast.add({ severity: 'warn', summary: 'Selecciona un rol', life: 3500 })
    return
  }
  const payload = {
    clave: form.value.clave,
    dni: form.value.dni,
    nombres: form.value.nombres,
    apellido: form.value.apellido,
    correo: form.value.correo,
    telefono: form.value.telefono,
    id_rol: form.value.id_rol,
    turno: (Array.isArray(form.value.turno) ? form.value.turno : turnoList(form.value.turno)).join(',')
  }
  guardando.value = true
  try {
    if (editing.value.id_usuario) {
      await api.put(`/personal/${editing.value.id_usuario}`, payload)
      toast.add({ severity: 'success', summary: 'Empleado actualizado', life: 2500 })
    } else {
      await api.post('/personal/', payload)
      toast.add({ severity: 'success', summary: 'Empleado registrado', life: 2500 })
    }
    await cargar()
    dialogVisible.value = false
  } catch (err) {
    toast.add({ severity: 'error', summary: err.response?.data?.message || 'Error al guardar', life: 4000 })
  } finally {
    guardando.value = false
  }
}

const cambiarEstado = async (emp, estado) => {
  const accion = estado ? 'reactivar' : 'desactivar'
  if (!confirm(`¿${estado ? 'Reactivar' : 'Desactivar'} a ${emp.nombres} ${emp.apellido}?`)) return
  try {
    await api.put(`/personal/${emp.id_usuario}`, { estado })
    toast.add({ severity: 'success', summary: estado ? 'Usuario activado' : 'Usuario desactivado', life: 2500 })
    await cargar()
  } catch (err) {
    toast.add({ severity: 'error', summary: 'No se pudo cambiar el estado', life: 3500 })
  }
}
</script>

<style scoped>
.empleados-view { padding: 2rem; }

.page-header {
  display: flex; justify-content: space-between; align-items: center;
  flex-wrap: wrap; gap: 1rem; margin-bottom: 1.25rem;
}
.page-header h1 { margin: 0; font-size: 1.5rem; color: var(--text-main); }
.page-header p { margin: 0.25rem 0 0; color: var(--text-muted); font-size: 0.9rem; }

.table-card {
  background: var(--bg-card); border: 1px solid var(--border-color);
  border-radius: 14px; padding: 1.25rem; box-shadow: var(--shadow-soft);
}
.mt-4 { margin-top: 1rem; }

.table-toolbar { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.75rem; }
.total-badge { font-size: 0.8rem; color: var(--text-muted); background: var(--bg-secondary); padding: 0.25rem 0.75rem; border-radius: 999px; }

.tag-turno { padding: 0.2rem 0.7rem; border-radius: 999px; font-size: 0.78rem; font-weight: 600; }
.turno-tags { display: inline-flex; flex-wrap: wrap; gap: 0.3rem; }
.text-muted { color: var(--text-muted); font-size: 0.85rem; }
.t-manana { background: rgba(245, 158, 11, 0.15); color: #b45309; }
.t-tarde { background: rgba(59, 130, 246, 0.12); color: #2563eb; }
.t-noche { background: rgba(99, 102, 241, 0.15); color: #4f46e5; }
.t-vacio { background: rgba(148, 163, 184, 0.15); color: var(--text-muted); }

.btn-accion { transition: transform 0.15s cubic-bezier(0.22, 1, 0.36, 1); }
.btn-accion:hover { transform: scale(1.12); }
.btn-accion:active { transform: scale(0.92); }
.acciones-row { display: inline-flex; gap: 0.25rem; align-items: center; }

.dni-row { display: flex; gap: 0.5rem; }
.dni-row .p-inputtext { flex: 1; }

.empty-state { text-align: center; padding: 2rem; color: var(--text-muted); }

/* Skeletons */
.skeleton-row { display: flex; align-items: center; gap: 1rem; padding: 0.9rem 0.25rem; border-bottom: 1px solid var(--border-color); }
.sk {
  border-radius: 8px;
  background: linear-gradient(90deg, rgba(148,163,184,0.12) 25%, rgba(148,163,184,0.25) 50%, rgba(148,163,184,0.12) 75%);
  background-size: 400% 100%;
  animation: shimmer 1.4s infinite linear;
}
.sk-line { height: 14px; }
.w-25 { width: 25%; } .w-20 { width: 20%; } .w-10 { width: 10%; }
@keyframes shimmer { 0% { background-position: 100% 0; } 100% { background-position: -100% 0; } }

.animate-item { animation: slide-in 0.45s cubic-bezier(0.22, 1, 0.36, 1); }
@keyframes slide-in { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: none; } }

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.fade-up-enter-active { transition: all 0.45s cubic-bezier(0.22, 1, 0.36, 1); }
.fade-up-enter-from { opacity: 0; transform: translateY(14px); }
.fade-up-enter-to { opacity: 1; transform: none; }
</style>
