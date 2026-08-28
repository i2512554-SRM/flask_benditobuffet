<template>
  <header class="app-header">
    <div class="header-left">
      <img :src="logoSrc" alt="Logo" class="header-logo" />
      <div class="header-brand">
        <h1>Bendito Buffet</h1>
        <span class="header-subtitle">Sistema de Gestion</span>
      </div>
    </div>
    <div class="header-right">
      <router-link to="/perfil" class="header-user" v-if="authStore.user">
        <i class="fa-solid fa-user-circle"></i>
        <span>{{ authStore.user.nombre }}</span>
      </router-link>
      <button class="theme-toggle" @click="toggleDarkMode" :title="isDarkMode ? 'Modo claro' : 'Modo oscuro'">
        <i :class="isDarkMode ? 'fa-solid fa-sun' : 'fa-solid fa-moon'"></i>
      </button>
      <button class="btn-logout" @click="handleLogout">
        <i class="fa-solid fa-right-from-bracket"></i>
        <span>Cerrar Sesion</span>
      </button>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import logoSrc from '../../assets/logo.png'

const router = useRouter()
const authStore = useAuthStore()
const isDarkMode = ref(false)

onMounted(() => {
  const saved = localStorage.getItem('dark-mode')
  if (saved === 'true') {
    isDarkMode.value = true
  }
})

const toggleDarkMode = () => {
  isDarkMode.value = !isDarkMode.value
  document.documentElement.classList.toggle('dark-mode')
  localStorage.setItem('dark-mode', isDarkMode.value)
}

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 1.5rem;
  height: 60px;
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-color);
  box-shadow: var(--shadow-soft);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.header-logo {
  width: 36px;
  height: 36px;
  object-fit: contain;
}

.header-brand h1 {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--text-main);
  line-height: 1.2;
}

.header-subtitle {
  font-size: 0.7rem;
  color: var(--text-muted);
  letter-spacing: 0.05em;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-user {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: var(--text-main);
  font-weight: 500;
  text-decoration: none;
  padding: 0.4rem 0.75rem;
  border-radius: 10px;
  border: 1px solid transparent;
  transition: all 0.18s ease;
}

.header-user:hover {
  background: var(--bg-secondary);
  border-color: var(--border-color);
  color: var(--btn-primary);
}

.header-user i {
  font-size: 1.3rem;
  color: var(--btn-primary);
}

.theme-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  border: 1px solid var(--border-color);
  background: var(--bg-secondary);
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.18s ease;
  font-size: 1rem;
}

.theme-toggle:hover {
  color: var(--btn-primary);
  border-color: var(--btn-primary);
  background: var(--hover-color);
}

.btn-logout {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 10px;
  border: 1px solid var(--border-color);
  background: var(--bg-secondary);
  color: var(--text-muted);
  cursor: pointer;
  font-size: 0.8rem;
  font-weight: 500;
  transition: all 0.18s ease;
}

.btn-logout:hover {
  color: var(--color-rojo);
  border-color: var(--color-rojo);
  background: rgba(220, 38, 38, 0.08);
}
</style>
