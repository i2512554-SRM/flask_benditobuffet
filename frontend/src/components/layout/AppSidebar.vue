<template>
  <aside class="app-sidebar">
    <nav class="sidebar-nav">
      <router-link to="/panel" class="nav-item">
        <div class="nav-icon"><i class="fa-solid fa-gauge-high"></i></div>
        <span>Panel</span>
      </router-link>

      <div class="nav-section">Caja</div>
      <router-link to="/caja" class="nav-item">
        <div class="nav-icon"><i class="fa-solid fa-cash-register"></i></div>
        <span>Caja</span>
      </router-link>

      <div class="nav-section" v-if="isAdmin">Personal</div>
      <template v-if="isAdmin">
        <router-link to="/personal/empleados" class="nav-item">
          <div class="nav-icon"><i class="fa-solid fa-users"></i></div>
          <span>Empleados</span>
        </router-link>
        <router-link to="/personal/pagos" class="nav-item">
          <div class="nav-icon"><i class="fa-solid fa-money-bill-wave"></i></div>
          <span>Pagos</span>
        </router-link>
        <router-link to="/personal/turnos" class="nav-item">
          <div class="nav-icon"><i class="fa-solid fa-calendar-days"></i></div>
          <span>Turnos</span>
        </router-link>
        <router-link to="/personal/adelantos" class="nav-item">
          <div class="nav-icon"><i class="fa-solid fa-file-invoice-dollar"></i></div>
          <span>Adelantos</span>
        </router-link>
        <router-link to="/personal/solicitudes" class="nav-item">
          <div class="nav-icon"><i class="fa-solid fa-file-pen"></i></div>
          <span>Solicitudes</span>
        </router-link>
        <router-link to="/personal/salarios" class="nav-item">
          <div class="nav-icon"><i class="fa-solid fa-coins"></i></div>
          <span>Salarios</span>
        </router-link>
      </template>

      <div class="nav-section">Operaciones</div>
      <router-link to="/inventario" class="nav-item">
        <div class="nav-icon"><i class="fa-solid fa-boxes-stacked"></i></div>
        <span>Inventario</span>
      </router-link>
    </nav>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '../../stores/auth'

const authStore = useAuthStore()
const isAdmin = computed(() => authStore.user?.rol === 1)
</script>

<style scoped>
.app-sidebar {
  width: 250px;
  background: var(--bg-card);
  border-right: 1px solid var(--border-color);
  height: calc(100vh - 60px);
  position: fixed;
  top: 60px;
  left: 0;
  overflow-y: auto;
  padding: 0.75rem 0;
  z-index: 50;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.nav-section {
  padding: 1rem 1.25rem 0.35rem;
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-muted);
  opacity: 0.6;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.6rem 1.25rem;
  text-decoration: none;
  color: var(--text-muted);
  font-size: 0.85rem;
  font-weight: 500;
  transition: all 0.18s ease;
  border-left: 3px solid transparent;
}

.nav-item:hover {
  background: var(--hover-color);
  color: var(--btn-primary);
}

.nav-item.router-link-active {
  background: rgba(255, 123, 0, 0.08);
  color: var(--btn-primary);
  border-left-color: var(--btn-primary);
  font-weight: 600;
}

.nav-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: var(--bg-secondary);
  font-size: 0.8rem;
  flex-shrink: 0;
  transition: all 0.18s ease;
}

.nav-item.router-link-active .nav-icon {
  background: rgba(255, 123, 0, 0.15);
  color: var(--btn-primary);
}

.nav-item:hover .nav-icon {
  background: rgba(255, 123, 0, 0.1);
  color: var(--btn-primary);
}
</style>
