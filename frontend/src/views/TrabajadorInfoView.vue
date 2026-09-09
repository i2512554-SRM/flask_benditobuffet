<template>
  <div class="trabajador-view">
    <VolverBtn to="/trabajador" />

    <div class="page-header">
      <div>
        <h1>Mi información</h1>
        <p>Datos personales</p>
      </div>
      <router-link to="/perfil" class="btn btn-outline">
        <i class="fa-solid fa-user-gear"></i> Editar perfil
      </router-link>
    </div>

    <div class="info-grid" v-if="info">
      <div class="info-card">
        <div class="info-icon tone-green"><i class="fa-solid fa-user"></i></div>
        <div>
          <div class="info-label">Nombre completo</div>
          <div class="info-value">{{ info.nombres }} {{ info.apellido }}</div>
        </div>
      </div>

      <div class="info-card">
        <div class="info-icon tone-blue"><i class="fa-solid fa-briefcase"></i></div>
        <div>
          <div class="info-label">Cargo</div>
          <div class="info-value">{{ info.cargo || '—' }}</div>
        </div>
      </div>

      <div class="info-card">
        <div class="info-icon" :class="info.estado_laboral === 'Activo' ? 'tone-green' : 'tone-red'">
          <i class="fa-solid fa-user-check"></i>
        </div>
        <div>
          <div class="info-label">Estado laboral</div>
          <div class="info-value">{{ info.estado_laboral }}</div>
        </div>
      </div>

      <div class="info-card">
        <div class="info-icon tone-blue"><i class="fa-solid fa-id-card"></i></div>
        <div>
          <div class="info-label">DNI</div>
          <div class="info-value">{{ info.dni || '—' }}</div>
        </div>
      </div>

      <div class="info-card">
        <div class="info-icon tone-amber"><i class="fa-solid fa-envelope"></i></div>
        <div>
          <div class="info-label">Correo</div>
          <div class="info-value">{{ info.correo || '—' }}</div>
        </div>
      </div>

      <div class="info-card">
        <div class="info-icon tone-green"><i class="fa-solid fa-phone"></i></div>
        <div>
          <div class="info-label">Teléfono</div>
          <div class="info-value">{{ info.telefono || '—' }}</div>
        </div>
      </div>

      <div class="info-card">
        <div class="info-icon tone-red"><i class="fa-solid fa-calendar-check"></i></div>
        <div>
          <div class="info-label">Fecha de ingreso</div>
          <div class="info-value">{{ info.fecha_ingreso || '—' }}</div>
          <div class="info-sub">{{ info.horario || 'Sin horario definido' }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import VolverBtn from '../components/ui/VolverBtn.vue'
import api from '../config/axios'

const info = ref(null)

const load = async () => {
  try {
    const res = await api.get('/trabajador/mi-info')
    if (res.data.success) info.value = res.data.data
  } catch (e) {
    console.error('Error cargando información:', e)
  }
}

onMounted(load)
</script>

<style scoped>
.trabajador-view {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-color);
  border-radius: 14px 14px 0 0;
}

.page-header h1 {
  margin: 0;
  font-size: 1.5rem;
  color: var(--text-main);
}

.page-header p {
  margin: 0.25rem 0 0;
  font-size: 0.85rem;
  color: var(--text-muted);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
  padding: 1.5rem 2rem 2rem;
}

.info-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem;
  background: var(--bg-card);
  border-radius: 14px;
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-soft);
}

.info-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  flex-shrink: 0;
}

.tone-green { background: rgba(16, 185, 129, 0.1); color: #059669; }
.tone-amber { background: rgba(245, 158, 11, 0.12); color: #d97706; }
.tone-red { background: rgba(220, 38, 38, 0.1); color: #dc2626; }
.tone-blue { background: rgba(59, 130, 246, 0.1); color: #2563eb; }

.info-label {
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  margin-bottom: 0.2rem;
}

.info-value {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-main);
}

.info-sub {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 0.15rem;
}

@media (max-width: 900px) {
  .page-header { flex-direction: column; gap: 1rem; align-items: flex-start; }
  .info-grid { padding: 1rem; }
}
</style>