<template>
  <div v-if="open" class="drawer-root">
    <div class="drawer-backdrop" @click="$emit('close')"></div>
    <aside class="app-drawer">
      <div class="drawer-header">
        <img :src="logoSrc" alt="Logo" class="drawer-logo" />
        <div>
          <h2>Bendito Buffet</h2>
          <span class="drawer-subtitle">{{ subtitle }}</span>
        </div>
      </div>

      <nav class="drawer-nav">
        <template v-if="isAdmin">
          <router-link to="/panel" class="drawer-item" @click="$emit('close')">
            <div class="drawer-icon ic-orange"><i class="fa-solid fa-gauge-high"></i></div>
            <span>Panel Principal</span>
          </router-link>
          <router-link to="/caja" class="drawer-item" @click="$emit('close')">
            <div class="drawer-icon ic-green"><i class="fa-solid fa-cash-register"></i></div>
            <span>Gestión de Caja</span>
          </router-link>
          <router-link to="/personal" class="drawer-item" @click="$emit('close')">
            <div class="drawer-icon ic-blue"><i class="fa-solid fa-users"></i></div>
            <span>Gestión del Personal</span>
          </router-link>
          <router-link to="/inventario" class="drawer-item" @click="$emit('close')">
            <div class="drawer-icon ic-purple"><i class="fa-solid fa-cubes-stacked"></i></div>
            <span>Inventario e Inversión</span>
          </router-link>
          <router-link to="/seguridad" class="drawer-item" @click="$emit('close')">
            <div class="drawer-icon ic-red"><i class="fa-solid fa-shield-halved"></i></div>
            <span>Seguridad y Accesos</span>
          </router-link>
          <router-link to="/ia" class="drawer-item" @click="$emit('close')">
            <div class="drawer-icon ic-cyan"><i class="fa-solid fa-brain"></i></div>
            <span>IA Predictiva</span>
          </router-link>
        </template>
        <template v-else-if="isCocinero">
          <div class="drawer-section">Cocina</div>
          <router-link to="/cocinero" class="drawer-item" @click="$emit('close')">
            <div class="drawer-icon ic-orange"><i class="fa-solid fa-gauge-high"></i></div>
            <span>Mi Panel</span>
          </router-link>
          <router-link to="/cocinero/inventario" class="drawer-item" @click="$emit('close')">
            <div class="drawer-icon ic-purple"><i class="fa-solid fa-boxes-stacked"></i></div>
            <span>Insumos</span>
          </router-link>
          <router-link to="/cocinero/solicitudes" class="drawer-item" @click="$emit('close')">
            <div class="drawer-icon ic-blue"><i class="fa-solid fa-list-check"></i></div>
            <span>Mis Solicitudes</span>
          </router-link>
          <router-link to="/cocinero/alertas" class="drawer-item" @click="$emit('close')">
            <div class="drawer-icon ic-red"><i class="fa-solid fa-triangle-exclamation"></i></div>
            <span>Alertas</span>
          </router-link>
          <div class="drawer-section">Mi Área</div>
          <router-link to="/trabajador/info" class="drawer-item" @click="$emit('close')">
            <div class="drawer-icon ic-blue"><i class="fa-solid fa-id-card"></i></div>
            <span>Mi Información</span>
          </router-link>
          <router-link to="/trabajador/turnos" class="drawer-item" @click="$emit('close')">
            <div class="drawer-icon ic-orange"><i class="fa-solid fa-calendar-days"></i></div>
            <span>Mis Turnos</span>
          </router-link>
          <router-link to="/trabajador/pagos" class="drawer-item" @click="$emit('close')">
            <div class="drawer-icon ic-green"><i class="fa-solid fa-money-check-dollar"></i></div>
            <span>Mis Pagos</span>
          </router-link>
          <router-link to="/trabajador/notificaciones" class="drawer-item" @click="$emit('close')">
            <div class="drawer-icon ic-purple"><i class="fa-solid fa-bell"></i></div>
            <span>Notificaciones</span>
          </router-link>
        </template>

        <template v-else-if="isCajera">
          <div class="drawer-section">Caja</div>
          <router-link to="/panel-cajera" class="drawer-item" @click="$emit('close')">
            <div class="drawer-icon ic-green"><i class="fa-solid fa-gauge-high"></i></div>
            <span>Mi Panel</span>
          </router-link>
          <router-link to="/caja" class="drawer-item" @click="$emit('close')">
            <div class="drawer-icon ic-blue"><i class="fa-solid fa-cash-register"></i></div>
            <span>Control de Caja</span>
          </router-link>
          <div class="drawer-section">Mi Área</div>
          <router-link to="/trabajador/info" class="drawer-item" @click="$emit('close')">
            <div class="drawer-icon ic-blue"><i class="fa-solid fa-id-card"></i></div>
            <span>Mi Información</span>
          </router-link>
          <router-link to="/trabajador/turnos" class="drawer-item" @click="$emit('close')">
            <div class="drawer-icon ic-orange"><i class="fa-solid fa-calendar-days"></i></div>
            <span>Mis Turnos</span>
          </router-link>
          <router-link to="/trabajador/pagos" class="drawer-item" @click="$emit('close')">
            <div class="drawer-icon ic-green"><i class="fa-solid fa-money-check-dollar"></i></div>
            <span>Mis Pagos</span>
          </router-link>
          <router-link to="/trabajador/notificaciones" class="drawer-item" @click="$emit('close')">
            <div class="drawer-icon ic-purple"><i class="fa-solid fa-bell"></i></div>
            <span>Notificaciones</span>
          </router-link>
        </template>

        <template v-else>
          <div class="drawer-section">Mi Área</div>
          <router-link to="/trabajador" class="drawer-item" @click="$emit('close')">
            <div class="drawer-icon ic-orange"><i class="fa-solid fa-gauge-high"></i></div>
            <span>Mi Panel</span>
          </router-link>
          <router-link to="/trabajador/info" class="drawer-item" @click="$emit('close')">
            <div class="drawer-icon ic-blue"><i class="fa-solid fa-id-card"></i></div>
            <span>Mi Información</span>
          </router-link>
          <router-link to="/trabajador/turnos" class="drawer-item" @click="$emit('close')">
            <div class="drawer-icon ic-orange"><i class="fa-solid fa-calendar-days"></i></div>
            <span>Mis Turnos</span>
          </router-link>
          <router-link to="/trabajador/pagos" class="drawer-item" @click="$emit('close')">
            <div class="drawer-icon ic-green"><i class="fa-solid fa-money-check-dollar"></i></div>
            <span>Mis Pagos</span>
          </router-link>
          <router-link to="/trabajador/notificaciones" class="drawer-item" @click="$emit('close')">
            <div class="drawer-icon ic-purple"><i class="fa-solid fa-bell"></i></div>
            <span>Notificaciones</span>
          </router-link>
        </template>
      </nav>

      <div class="drawer-footer">
        <button class="drawer-logout" @click="confirmarCierre">
          <i class="fa-solid fa-right-from-bracket"></i>
          <span>Cerrar sesión</span>
        </button>
      </div>
    </aside>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { useLogout } from '../../composables/useLogout'
import logoSrc from '../../assets/logo.png'

defineProps({
  open: { type: Boolean, default: false }
})
defineEmits(['close'])

const { confirmarCierre } = useLogout()
const authStore = useAuthStore()

const isAdmin = computed(() => authStore.user?.rol === 1)
const isCocinero = computed(() => authStore.user?.rol === 3)
const isCajera = computed(() => authStore.user?.rol === 2)
const subtitle = computed(() => {
  if (isAdmin.value) return 'Panel Administrativo'
  if (isCocinero.value) return 'Área de Cocina'
  if (isCajera.value) return 'Área de Caja'
  return 'Área del Colaborador'
})
</script>

<style scoped>
.drawer-root {
  position: fixed;
  inset: 0;
  z-index: 200;
}

.drawer-backdrop {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(2px);
  animation: fadeIn 0.2s ease;
}

.app-drawer {
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  width: 280px;
  max-width: 85vw;
  background: var(--bg-card);
  box-shadow: var(--shadow-medium);
  display: flex;
  flex-direction: column;
  animation: slideIn 0.25s ease;
}

@keyframes slideIn {
  from { transform: translateX(-100%); }
  to { transform: translateX(0); }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.drawer-header {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 1.25rem 1.25rem 1rem;
  border-bottom: 1px solid var(--border-color);
}

.drawer-logo {
  width: 40px;
  height: 40px;
  object-fit: contain;
}

.drawer-header h2 {
  margin: 0;
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-main);
}

.drawer-subtitle {
  font-size: 0.7rem;
  color: var(--text-muted);
  letter-spacing: 0.05em;
}

.drawer-nav {
  flex: 1;
  overflow-y: auto;
  padding: 0.75rem 0.75rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.drawer-section {
  padding: 1rem 0.75rem 0.35rem;
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-muted);
  opacity: 0.6;
}

.drawer-item {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 0.65rem 0.75rem;
  border-radius: 12px;
  text-decoration: none;
  color: var(--text-muted);
  font-size: 0.85rem;
  font-weight: 500;
  transition: all 0.18s ease;
}

.drawer-item:hover {
  background: var(--hover-color);
  color: var(--btn-primary);
}

.drawer-item.router-link-active {
  background: rgba(255, 123, 0, 0.08);
  color: var(--btn-primary);
  font-weight: 600;
}

.drawer-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 9px;
  color: white;
  font-size: 0.85rem;
  flex-shrink: 0;
}

.drawer-footer {
  padding: 1rem;
  border-top: 1px solid var(--border-color);
}

.drawer-logout {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.6rem;
  width: 100%;
  padding: 0.7rem;
  border-radius: 12px;
  border: 1px solid var(--border-color);
  background: var(--bg-secondary);
  color: var(--color-rojo);
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 600;
  transition: all 0.18s ease;
}

.drawer-logout:hover {
  border-color: var(--color-rojo);
  background: rgba(220, 38, 38, 0.08);
}
</style>