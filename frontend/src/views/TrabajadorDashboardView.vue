<template>
  <div class="trabajador-view">
    <div class="page-header">
      <div>
        <h1>{{ saludo }}, {{ data.usuario?.nombres || 'Trabajador' }} 👋</h1>
        <p>Tu espacio personal: turnos, pagos y solicitudes</p>
        <div class="hero-badges">
          <span class="rol-badge-trab"><i class="fa-solid fa-user-check"></i> Trabajador</span>
          <span class="fecha-badge"><i class="fa-regular fa-calendar"></i> {{ data.fecha || 'Cargando...' }}</span>
        </div>
      </div>
      <div class="header-actions">
        <SolicitarAdelanto @enviado="load" />
        <router-link to="/trabajador/notificaciones" class="btn btn-outline">
          <i class="fa-solid fa-bell"></i> Notificaciones
          <span v-if="resumen.notificaciones_no_leidas" class="notif-badge">{{ resumen.notificaciones_no_leidas }}</span>
        </router-link>
        <button :disabled="$saving" class="btn btn-outline" @click="load">
          <i class="fa-solid fa-arrows-rotate"></i> Actualizar
        </button>
      </div>
    </div>

    <div class="turno-banner" v-if="data.turnos?.length">
      <div class="turno-label"><i class="fa-solid fa-clock"></i> Turno de hoy</div>
      <div class="turno-chips">
        <span v-for="t in data.turnos" :key="t" class="turno-chip">{{ t }}</span>
      </div>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon tone-green">
          <i class="fa-solid fa-money-bill-wave"></i>
        </div>
        <div class="stat-content">
          <span class="stat-label">Total pagado</span>
          <span class="stat-value">S/. {{ formatMoney(resumen.total_pagado) }}</span>
          <span class="stat-badge tone-green">historial completo</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon tone-blue">
          <i class="fa-solid fa-receipt"></i>
        </div>
        <div class="stat-content">
          <span class="stat-label">Pagos registrados</span>
          <span class="stat-value">{{ resumen.pagos }}</span>
          <span class="stat-badge tone-blue">en tu cuenta</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon tone-amber">
          <i class="fa-solid fa-file-invoice-dollar"></i>
        </div>
        <div class="stat-content">
          <span class="stat-label">Adelantos en gestión</span>
          <span class="stat-value">{{ resumen.adelantos_pendientes }}</span>
          <span class="stat-badge tone-amber">por revisar</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon tone-purple">
          <i class="fa-solid fa-sack-dollar"></i>
        </div>
        <div class="stat-content">
          <span class="stat-label">Último pago</span>
          <span class="stat-value">S/. {{ formatMoney(ultimoPago.monto) }}</span>
          <span class="stat-badge tone-purple">{{ ultimoPago.fecha || 'sin pagos aún' }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon tone-red">
          <i class="fa-solid fa-bell"></i>
        </div>
        <div class="stat-content">
          <span class="stat-label">Sin leer</span>
          <span class="stat-value">{{ resumen.notificaciones_no_leidas }}</span>
          <span class="stat-badge tone-red">notificaciones</span>
        </div>
      </div>
    </div>

    <div class="section-block">
      <h2>Acciones rápidas</h2>
      <div class="acciones-grid">
        <router-link to="/trabajador/info" class="accion-chip">
          <i class="fa-solid fa-id-card"></i> Mi Información
        </router-link>
        <router-link to="/trabajador/turnos" class="accion-chip">
          <i class="fa-solid fa-calendar-days"></i> Mis Turnos
        </router-link>
        <router-link to="/trabajador/pagos" class="accion-chip">
          <i class="fa-solid fa-money-check-dollar"></i> Mis Pagos
        </router-link>
        <router-link to="/trabajador/notificaciones" class="accion-chip">
          <i class="fa-solid fa-bell"></i> Notificaciones
        </router-link>
      </div>
    </div>

    <div class="module-grid">
      <router-link to="/trabajador/info" class="module-card">
        <div class="module-icon tone-blue"><i class="fa-solid fa-id-card"></i></div>
        <h3>Mi información</h3>
        <p>Datos personales y contacto</p>
      </router-link>
      <router-link to="/trabajador/turnos" class="module-card">
        <div class="module-icon tone-orange"><i class="fa-solid fa-calendar-days"></i></div>
        <h3>Mis turnos</h3>
        <p>Turno y jornada asignada</p>
      </router-link>
      <router-link to="/trabajador/pagos" class="module-card">
        <div class="module-icon tone-green"><i class="fa-solid fa-money-check-dollar"></i></div>
        <h3>Mis pagos</h3>
        <p>Fecha, monto y estado de pagos</p>
      </router-link>
      <router-link to="/trabajador/pagos" class="module-card">
        <div class="module-icon tone-amber"><i class="fa-solid fa-file-invoice-dollar"></i></div>
        <h3>Mis adelantos</h3>
        <p>Solicita y consulta el estado de tus adelantos</p>
      </router-link>
      <router-link to="/trabajador/notificaciones" class="module-card">
        <div class="module-icon tone-purple"><i class="fa-solid fa-bell"></i></div>
        <h3>Mis solicitudes</h3>
        <p>Avisos y respuestas del sistema</p>
      </router-link>
    </div>

    <div class="section-block" v-if="data.notificaciones?.length">
      <h2>Últimas notificaciones</h2>
      <div class="notif-list" v-for="n in data.notificaciones" :key="n.id_notificacion">
        <div class="notif-dot" :class="{ leida: n.leida }"></div>
        <div class="notif-body">
          <span class="notif-title">{{ n.titulo }}</span>
          <span class="notif-msg">{{ n.mensaje }}</span>
          <span class="notif-date">{{ n.fecha }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../config/axios'

const data = ref({})
const ultimoPago = ref({ monto: null, fecha: null })
const resumen = computed(() => data.value.resumen || { total_pagado: 0, pagos: 0, adelantos_pendientes: 0, notificaciones_no_leidas: 0 })

const saludo = computed(() => {
  const h = new Date().getHours()
  if (h < 12) return '¡Buenos días'
  if (h < 19) return '¡Buenas tardes'
  return '¡Buenas noches'
})

const formatMoney = (v) => Number(v || 0).toLocaleString('es-PE', { minimumFractionDigits: 2 })

const load = async () => {
  try {
    const res = await api.get('/trabajador/dashboard')
    if (res.data.success) data.value = res.data.data
  } catch (e) {
    console.error('Error cargando dashboard trabajador:', e)
  }
  try {
    const resPagos = await api.get('/trabajador/pagos')
    if (resPagos.data.success && resPagos.data.data.pagos?.length) {
      ultimoPago.value = resPagos.data.data.pagos[0]
    }
  } catch (e) {
    // silencioso: último pago opcional
  }
}

onMounted(load)
</script>

<style scoped>
.hero-badges {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.6rem;
  flex-wrap: wrap;
}

.rol-badge-trab,
.fecha-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.72rem;
  font-weight: 600;
  padding: 0.3rem 0.7rem;
  border-radius: 999px;
}

.rol-badge-trab {
  background: rgba(59, 130, 246, 0.1);
  color: #2563eb;
}

.fecha-badge {
  background: var(--bg-secondary);
  color: var(--text-muted);
}

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

.header-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.notif-badge {
  background: linear-gradient(135deg, #f97316, #fb923c);
  color: white;
  font-size: 0.65rem;
  font-weight: 700;
  border-radius: 999px;
  padding: 0.1rem 0.45rem;
}

.turno-banner {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin: 1.5rem 2rem 0;
  padding: 0.75rem 1rem;
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.1), rgba(251, 146, 60, 0.08));
  border: 1px solid rgba(249, 115, 22, 0.25);
  border-radius: 12px;
}

.turno-label {
  font-size: 0.8rem;
  font-weight: 600;
  color: #ea580c;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.turno-chips {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.turno-chip {
  padding: 0.25rem 0.8rem;
  border-radius: 999px;
  background: linear-gradient(135deg, #f97316, #fb923c);
  color: white;
  font-size: 0.75rem;
  font-weight: 600;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  padding: 1.5rem 2rem 0;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem;
  background: var(--bg-card);
  border-radius: 14px;
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-soft);
}

.stat-icon {
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
.tone-orange { background: rgba(255, 122, 0, 0.1); color: var(--btn-primary); }
.tone-purple { background: rgba(139, 92, 246, 0.1); color: #8b5cf6; }

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-bottom: 0.15rem;
}

.stat-value {
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--text-main);
}

.stat-badge {
  font-size: 0.65rem;
  font-weight: 600;
  margin-top: 0.2rem;
}

.acciones-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  margin-top: 1rem;
}

.accion-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1.05rem;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 999px;
  font-size: 0.82rem;
  font-weight: 500;
  color: var(--text-main);
  text-decoration: none;
  transition: all 0.18s ease;
  box-shadow: var(--shadow-soft);
}

.accion-chip i {
  color: var(--btn-primary);
}

.accion-chip:hover {
  border-color: var(--btn-primary);
  color: var(--btn-primary);
  transform: translateY(-1px);
}

.module-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  padding: 1.5rem 2rem;
}

.module-card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  text-align: left;
  padding: 1.1rem 1.25rem;
  background: var(--bg-card);
  border-radius: 14px;
  border: 1px solid var(--border-color);
  text-decoration: none;
  color: inherit;
  transition: all 0.18s ease;
  cursor: pointer;
  box-shadow: var(--shadow-soft);
}

.module-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-medium);
  border-color: var(--btn-primary);
}

.module-icon {
  width: 42px;
  height: 42px;
  border-radius: 11px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  margin-bottom: 0.7rem;
}

.module-card h3 {
  margin: 0 0 0.25rem;
  font-size: 0.92rem;
  color: var(--text-main);
  font-weight: 600;
}

.module-card p {
  margin: 0;
  font-size: 0.75rem;
  color: var(--text-muted);
  line-height: 1.4;
}

.section-block {
  padding: 0 2rem 2rem;
}

.section-block h2 {
  margin: 0 0 1rem;
  font-size: 1rem;
  color: var(--text-main);
  font-weight: 600;
}

.notif-list {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 0.85rem 1rem;
  margin-bottom: 0.6rem;
  box-shadow: var(--shadow-soft);
}

.notif-dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: linear-gradient(135deg, #f97316, #fb923c);
  margin-top: 0.35rem;
  flex-shrink: 0;
}

.notif-dot.leida {
  background: var(--border-color);
}

.notif-body {
  display: flex;
  flex-direction: column;
}

.notif-title {
  font-weight: 600;
  font-size: 0.85rem;
  color: var(--text-main);
}

.notif-msg {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.notif-date {
  font-size: 0.7rem;
  color: var(--text-muted);
  opacity: 0.8;
  margin-top: 0.2rem;
}

@media (max-width: 900px) {
  .stats-grid, .module-grid { grid-template-columns: 1fr; }
  .page-header { flex-direction: column; gap: 1rem; align-items: flex-start; }
  .turno-banner { margin: 1rem; flex-direction: column; align-items: flex-start; }
}
</style>
