<template>
  <div class="perfil-view">
    <!-- Notificaciones de adelantos -->
    <div v-if="notificaciones.length" class="notif-list">
      <div
        v-for="notif in notificaciones"
        :key="notif.id_adelanto"
        class="notif-banner success"
        @click="dismissNotif(notif.id_adelanto)"
      >
        <i class="fa-solid fa-bell"></i>
        Tu solicitud de adelanto por
        <strong>S/. {{ formatMoney(notif.monto) }}</strong>
        fue <strong>{{ notif.estado === 'Aprobado' ? 'aprobada' : 'rechazada' }}</strong>
        <span v-if="notif.respuesta_admin">: {{ notif.respuesta_admin }}</span>
      </div>
    </div>

    <!-- Cabecera -->
    <div class="perfil-header">
      <div class="perfil-heading">
        <span class="eyebrow">Perfil del empleado</span>
        <h1>Hola, {{ usuario.nombres }}.</h1>
        <p class="subtitle">Revisa tu informacion profesional, historial de pagos y movimientos recientes.</p>
      </div>
      <div class="header-actions">
        <button class="btn btn-outline" @click="toggleEdit">
          {{ editMode ? 'Volver al perfil' : 'Editar perfil' }}
        </button>
      </div>
    </div>

    <!-- Vista de perfil -->
    <div v-if="!editMode">
      <div class="perfil-grid">
        <div class="card profile-card">
          <div class="profile-card-top">
            <div class="profile-avatar">
              <img v-if="usuario.perfil.foto_perfil" :src="usuario.perfil.foto_perfil" alt="Foto de perfil" />
              <span v-else class="avatar-fallback">{{ initials }}</span>
            </div>
            <div>
              <h2>{{ usuario.nombres }} {{ usuario.apellido }}</h2>
              <span class="badge-rol">{{ usuario.rol }}</span>
            </div>
          </div>
          <div class="profile-keyinfo">
            <div class="info-block">
              <span>Correo</span>
              <strong>{{ usuario.correo || 'No registrado' }}</strong>
            </div>
            <div class="info-block">
              <span>Telefono</span>
              <strong>{{ usuario.telefono || 'No registrado' }}</strong>
            </div>
            <div class="info-block">
              <span>DNI</span>
              <strong>{{ usuario.dni || 'No registrado' }}</strong>
            </div>
            <div class="info-block">
              <span>Fecha de registro</span>
              <strong>{{ usuario.perfil.fecha_ingreso || 'No registrado' }}</strong>
            </div>
            <div class="info-block">
              <span>Turnos</span>
              <strong>
                <span v-for="t in usuario.turnos" :key="t" class="turno-badge">{{ t }}</span>
                <span v-if="!usuario.turnos.length">No registrado</span>
              </strong>
            </div>
            <div class="info-block">
              <span>Salario mensual</span>
              <strong>{{ usuario.perfil.salario != null ? 'S/. ' + formatMoney(usuario.perfil.salario) : 'No registrado' }}</strong>
            </div>
          </div>
        </div>

        <div class="profile-tabs">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            class="btn btn-outline"
            :class="{ active: activeTab === tab.key }"
            @click="activeTab = tab.key"
          >
            {{ tab.label }}
          </button>
        </div>
      </div>

      <!-- Resumen -->
      <div v-if="activeTab === 'resumen'" class="card content-card">
        <h3>Resumen rapido</h3>
        <div class="summary-grid">
          <div class="summary-item">
            <span>Pagos registrados</span>
            <strong>{{ resumen.pagos }}</strong>
          </div>
          <div class="summary-item">
            <span>Adelantos</span>
            <strong>{{ resumen.adelantos }}</strong>
          </div>
        </div>
      </div>

      <!-- Pagos -->
      <div v-if="activeTab === 'pagos'" class="card content-card">
        <div class="section-header">
          <h2>Pagos recientes</h2>
          <p>Revisa los ultimos ingresos.</p>
        </div>
        <div class="table-overflow">
          <table>
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Monto</th>
                <th>Descripcion</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="pago in pagos" :key="pago.id_pago">
                <td data-label="Fecha">{{ pago.fecha_pago }}</td>
                <td data-label="Monto">S/. {{ formatMoney(pago.monto) }}</td>
                <td data-label="Descripcion">{{ pago.descripcion }}</td>
                <td data-label="Estado"><span class="badge badge-paid">{{ pago.estado }}</span></td>
              </tr>
              <tr v-if="!pagos.length">
                <td colspan="4">Aun no tienes pagos registrados.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Adelantos -->
      <div v-if="activeTab === 'adelantos'" class="card content-card">
        <div class="section-header space-between">
          <div>
            <h2>Adelantos</h2>
            <p>Solicita un adelanto rapido y sencillo.</p>
          </div>
          <button class="btn btn-primary" @click="toggleAdelantoForm">
            {{ adelantoFormVisible ? 'Cerrar formulario' : 'Solicitar adelanto' }}
          </button>
        </div>

        <div v-if="adelantoFormVisible" class="adelanto-form">
          <div class="form-row">
            <label>Motivo</label>
            <input type="text" v-model="adelantoForm.motivo" placeholder="Motivo del adelanto" class="input" />
          </div>
          <div class="form-row">
            <label>Monto</label>
            <input type="text" v-model="adelantoForm.monto" placeholder="Ej. 150.00" class="input" />
          </div>
          <div class="form-actions">
            <button class="btn btn-primary" @click="solicitarAdelanto" :disabled="solicitando">
              Enviar solicitud
            </button>
          </div>
        </div>

        <div class="table-overflow">
          <table>
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Motivo</th>
                <th>Monto</th>
                <th>Estado</th>
                <th>Respuesta</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="adelanto in adelantos" :key="adelanto.id_adelanto">
                <td data-label="Fecha">{{ adelanto.fecha }}</td>
                <td data-label="Motivo">{{ adelanto.motivo }}</td>
                <td data-label="Monto">S/. {{ formatMoney(adelanto.monto) }}</td>
                <td data-label="Estado">
                  <span class="badge" :class="adelanto.estado === 'Aprobado' ? 'badge-paid' : adelanto.estado === 'Pendiente' ? 'badge-pending' : 'badge-danger'">
                    {{ adelanto.estado }}
                  </span>
                </td>
                <td data-label="Respuesta">{{ adelanto.respuesta_admin || '—' }}</td>
                <td data-label="Accion">
                  <button
                    v-if="adelanto.estado === 'Pendiente'"
                    class="btn btn-outline btn-sm"
                    @click="cancelarAdelanto(adelanto)"
                  >
                    Cancelar
                  </button>
                </td>
              </tr>
              <tr v-if="!adelantos.length">
                <td colspan="6">No hay adelantos registrados.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Editar perfil -->
    <div v-else class="card profile-editor">
      <div class="section-header">
        <h2>Editar perfil</h2>
        <p>Modifica tu correo, telefono y foto de perfil.</p>
      </div>
      <div class="edit-form">
        <div class="form-row">
          <label>Foto de perfil</label>
          <img v-if="usuario.perfil.foto_perfil" :src="usuario.perfil.foto_perfil" class="edit-avatar" alt="Foto" />
          <input type="file" accept="image/png,image/jpeg,image/webp" @change="onFotoChange" class="input" />
        </div>
        <div class="form-row">
          <label>Correo</label>
          <input type="email" v-model="editarForm.correo" class="input" required />
        </div>
        <div class="form-row">
          <label>Telefono</label>
          <input type="text" v-model="editarForm.telefono" placeholder="Ej. 987654321" class="input" />
        </div>
        <div class="form-row">
          <label>Nueva contrasena (opcional)</label>
          <input type="password" v-model="editarForm.clave" placeholder="Dejar vacio para no cambiar" class="input" />
        </div>
        <div class="form-actions">
          <button class="btn btn-primary" @click="guardarPerfil" :disabled="guardando">Guardar cambios</button>
          <button class="btn btn-outline" @click="toggleEdit">Cancelar</button>
        </div>
        <hr class="divider" />
        <button class="btn btn-outline" @click="openContrasenaModal">
          <i class="fa-solid fa-key"></i> Cambiar contrasena
        </button>
      </div>
    </div>

    <!-- Modal cambiar contrasena -->
    <div v-if="modalContrasena" class="overlay" @click.self="modalContrasena = false">
      <div class="modal-card">
        <button class="close-btn" @click="modalContrasena = false" aria-label="Cerrar">&times;</button>
        <h2>Cambiar contrasena</h2>
        <label>Contrasena actual</label>
        <input type="password" v-model="contrasenaForm.contrasena_actual" placeholder="Ingresa tu contrasena actual" class="input" />
        <label>Contrasena nueva</label>
        <input type="password" v-model="contrasenaForm.contrasena_nueva" placeholder="Ingresa tu nueva contrasena" class="input" />
        <label>Verificar contrasena nueva</label>
        <input type="password" v-model="contrasenaForm.contrasena_verificar" placeholder="Repite tu nueva contrasena" class="input" />
        <button class="btn btn-primary" @click="cambiarContrasena" :disabled="guardando">Cambiar contrasena</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import api from '../config/axios'

const toast = useToast()

const usuario = ref({ nombres: '', apellido: '', perfil: {}, turnos: [] })
const pagos = ref([])
const adelantos = ref([])
const notificaciones = ref([])
const resumen = ref({ pagos: 0, adelantos: 0 })

const editMode = ref(false)
const activeTab = ref('resumen')
const adelantoFormVisible = ref(false)
const modalContrasena = ref(false)
const solicitando = ref(false)
const guardando = ref(false)

const adelantoForm = ref({ motivo: '', monto: '' })
const editarForm = ref({ correo: '', telefono: '', clave: '', foto: null })
const contrasenaForm = ref({ contrasena_actual: '', contrasena_nueva: '', contrasena_verificar: '' })

const tabs = [
  { key: 'resumen', label: 'Resumen' },
  { key: 'pagos', label: 'Pagos' },
  { key: 'adelantos', label: 'Adelantos' }
]

const initials = computed(() => {
  const n = (usuario.value.nombres || '')[0] || ''
  const a = (usuario.value.apellido || '')[0] || ''
  return (n + a).toUpperCase()
})

const formatMoney = (val) => Number(val || 0).toLocaleString('es-PE', { minimumFractionDigits: 2 })

const cargarPerfil = async () => {
  try {
    const res = await api.get('/perfil')
    if (res.data.success) {
      const d = res.data.data
      usuario.value = d.usuario
      pagos.value = d.pagos
      adelantos.value = d.adelantos
      notificaciones.value = d.notificaciones
      resumen.value = d.resumen
      editarForm.value = { correo: d.usuario.correo || '', telefono: d.usuario.telefono || '', clave: '', foto: null }
      if (d.notificaciones && d.notificaciones.length) {
        toast.add({ severity: 'info', summary: 'Notificaciones', detail: `${d.notificaciones.length} resultado(s) de tus adelantos`, life: 4000 })
      }
    }
  } catch (err) {
    console.error('Error cargando perfil:', err)
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo cargar el perfil', life: 3000 })
  }
}

const dismissNotif = (id) => {
  notificaciones.value = notificaciones.value.filter((n) => n.id_adelanto !== id)
  api.post('/perfil/notificaciones/leer').catch(() => {})
}

const toggleEdit = () => {
  editMode.value = !editMode.value
  if (editMode.value) {
    editarForm.value = { correo: usuario.value.correo || '', telefono: usuario.value.telefono || '', clave: '', foto: null }
  }
}

const toggleAdelantoForm = () => {
  adelantoFormVisible.value = !adelantoFormVisible.value
}

const onFotoChange = (e) => {
  editarForm.value.foto = e.target.files[0] || null
}

const guardarPerfil = async () => {
  guardando.value = true
  try {
    const fd = new FormData()
    fd.append('correo', editarForm.value.correo)
    fd.append('telefono', editarForm.value.telefono)
    if (editarForm.value.clave) fd.append('clave', editarForm.value.clave)
    if (editarForm.value.foto) fd.append('foto_perfil', editarForm.value.foto)

    const res = await api.put('/perfil', fd)
    if (res.data.success) {
      toast.add({ severity: 'success', summary: 'Exito', detail: res.data.message, life: 3000 })
      await cargarPerfil()
      editMode.value = false
    } else {
      toast.add({ severity: 'error', summary: 'Error', detail: res.data.error, life: 4000 })
    }
  } catch (err) {
    const msg = err.response?.data?.error || 'No se pudo actualizar el perfil'
    toast.add({ severity: 'error', summary: 'Error', detail: msg, life: 4000 })
  } finally {
    guardando.value = false
  }
}

const solicitarAdelanto = async () => {
  if (!adelantoForm.value.motivo) {
    toast.add({ severity: 'warn', summary: 'Aviso', detail: 'El motivo es obligatorio', life: 3000 })
    return
  }
  if (!adelantoForm.value.monto || Number(adelantoForm.value.monto) <= 0) {
    toast.add({ severity: 'warn', summary: 'Aviso', detail: 'Ingrese un monto valido', life: 3000 })
    return
  }
  solicitando.value = true
  try {
    const res = await api.post('/perfil/adelantos', {
      motivo: adelantoForm.value.motivo,
      monto: adelantoForm.value.monto
    })
    if (res.data.success) {
      toast.add({ severity: 'success', summary: 'Exito', detail: res.data.message, life: 3000 })
      adelantoFormVisible.value = false
      adelantoForm.value = { motivo: '', monto: '' }
      await cargarPerfil()
    }
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Error', detail: err.response?.data?.error || 'No se pudo enviar', life: 4000 })
  } finally {
    solicitando.value = false
  }
}

const cancelarAdelanto = async (adelanto) => {
  if (!confirm(`Cancelar la solicitud de adelanto por S/. ${formatMoney(adelanto.monto)}?`)) return
  try {
    await api.delete(`/perfil/adelantos/${adelanto.id_adelanto}`)
    toast.add({ severity: 'success', summary: 'Exito', detail: 'Solicitud de adelanto cancelada', life: 3000 })
    await cargarPerfil()
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Error', detail: err.response?.data?.error || 'No se pudo cancelar', life: 4000 })
  }
}

const openContrasenaModal = () => {
  contrasenaForm.value = { contrasena_actual: '', contrasena_nueva: '', contrasena_verificar: '' }
  modalContrasena.value = true
}

const cambiarContrasena = async () => {
  if (!contrasenaForm.value.contrasena_actual || !contrasenaForm.value.contrasena_nueva || !contrasenaForm.value.contrasena_verificar) {
    toast.add({ severity: 'warn', summary: 'Aviso', detail: 'Todos los campos son obligatorios', life: 3000 })
    return
  }
  guardando.value = true
  try {
    const res = await api.put('/perfil/contrasena', contrasenaForm.value)
    if (res.data.success) {
      toast.add({ severity: 'success', summary: 'Exito', detail: res.data.message, life: 3000 })
      modalContrasena.value = false
    } else {
      toast.add({ severity: 'error', summary: 'Error', detail: res.data.error, life: 4000 })
    }
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Error', detail: err.response?.data?.error || 'No se pudo cambiar', life: 4000 })
  } finally {
    guardando.value = false
  }
}

onMounted(cargarPerfil)
</script>

<style scoped>
.perfil-view {
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.perfil-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.eyebrow {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--btn-primary);
}

.perfil-heading h1 {
  margin: 0.25rem 0 0.25rem;
  font-size: 1.6rem;
  color: var(--text-main);
}

.subtitle {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.9rem;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

/* Notificaciones */
.notif-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.notif-banner {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.85rem 1.1rem;
  border-radius: 12px;
  cursor: pointer;
  font-size: 0.85rem;
}

.notif-banner.success {
  background: var(--color-success-bg);
  color: var(--color-success-text);
  border: 1px solid rgba(22, 163, 74, 0.3);
}

/* Grid */
.perfil-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}

.profile-card {
  padding: 1.5rem;
}

.profile-card-top {
  display: flex;
  align-items: center;
  gap: 1rem;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 1.25rem;
  margin-bottom: 1.25rem;
}

.profile-avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--btn-gradient-start), var(--btn-gradient-end));
  color: #fff;
  font-size: 1.5rem;
  font-weight: 700;
  overflow: hidden;
  flex-shrink: 0;
}

.profile-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.profile-card-top h2 {
  margin: 0 0 0.25rem;
  font-size: 1.2rem;
  color: var(--text-main);
}

.badge-rol {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  background: rgba(255, 123, 0, 0.12);
  color: var(--btn-primary);
  font-size: 0.72rem;
  font-weight: 600;
}

.profile-keyinfo {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
}

.info-block {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.info-block span {
  font-size: 0.72rem;
  color: var(--text-muted);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.info-block strong {
  font-size: 0.9rem;
  color: var(--text-main);
}

.turno-badge {
  display: inline-block;
  margin-right: 0.35rem;
  padding: 0.15rem 0.55rem;
  border-radius: 999px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  font-size: 0.75rem;
  color: var(--text-main);
  font-weight: 600;
}

.profile-tabs {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.profile-tabs .btn.active {
  background: var(--btn-primary);
  color: #fff;
  border-color: var(--btn-primary);
}

/* Content cards */
.content-card {
  padding: 1.5rem;
}

.section-header {
  margin-bottom: 1rem;
}

.section-header h2 {
  margin: 0 0 0.25rem;
  font-size: 1.1rem;
  color: var(--text-main);
}

.section-header p {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.85rem;
}

.section-header.space-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1rem;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 1rem;
  border-radius: 12px;
  background: var(--bg-secondary);
}

.summary-item span {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.summary-item strong {
  font-size: 1.4rem;
  color: var(--text-main);
}

/* Tables */
.table-overflow {
  overflow-x: auto;
}

.badge {
  padding: 0.2rem 0.6rem;
  border-radius: 6px;
  font-size: 0.7rem;
  font-weight: 600;
}

.badge-paid {
  background: rgba(22, 163, 74, 0.1);
  color: var(--color-verde-fuerte);
}

.badge-pending {
  background: rgba(245, 158, 11, 0.12);
  color: #d97706;
}

.badge-danger {
  background: rgba(220, 38, 38, 0.1);
  color: var(--color-rojo);
}

.btn-sm {
  padding: 0.3rem 0.7rem;
  font-size: 0.75rem;
}

/* Form */
.adelanto-form {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 1rem;
  margin-bottom: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.form-row {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.form-row label {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--text-muted);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

/* Editor */
.profile-editor {
  padding: 1.5rem;
}

.edit-form {
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
  max-width: 520px;
}

.edit-avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid var(--border-color);
}

.divider {
  border: none;
  border-top: 1px solid var(--border-color);
  margin: 0.5rem 0;
}

/* Modal */
.overlay {
  position: fixed;
  inset: 0;
  background: var(--overlay-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}

.modal-card {
  background: var(--bg-card);
  border-radius: 16px;
  padding: 2rem;
  width: 100%;
  max-width: 440px;
  box-shadow: var(--shadow-medium);
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  position: relative;
}

.modal-card h2 {
  margin: 0 0 0.25rem;
  font-size: 1.1rem;
  color: var(--text-main);
}

.modal-card label {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--text-muted);
}

.close-btn {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: transparent;
  border: none;
  font-size: 1.5rem;
  color: var(--text-muted);
  cursor: pointer;
  line-height: 1;
}

@media (max-width: 768px) {
  .perfil-view { padding: 1rem; }
}
</style>
