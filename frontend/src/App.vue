<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import AppHeader from './components/layout/AppHeader.vue'
import AppDrawer from './components/layout/AppDrawer.vue'
import AppFooter from './components/layout/AppFooter.vue'
import Toast from 'primevue/toast'
import ConfirmDialog from 'primevue/confirmdialog'

const route = useRoute()
const showLayout = computed(() => !['login', 'home'].includes(route.name))
const menuOpen = ref(false)
watch(() => route.fullPath, () => { menuOpen.value = false })

const toggleMenu = () => {
  menuOpen.value = !menuOpen.value
}

const EXPRESION_AVISO = { success: 'celebrando', error: 'preocupada', warn: 'preocupada', info: 'feliz' }
const expresionAviso = (severidad) => EXPRESION_AVISO[severidad] || 'pensando'
</script>

<template>
  <Toast>
    <template #message="{ message }">
      <div class="aviso-ollita">
        <OllitaMascota :expresion="expresionAviso(message.severity)" :tamano="46" :animada="false" />
        <div class="aviso-ollita__texto">
          <span class="p-toast-summary">{{ message.summary }}</span>
          <div v-if="message.detail" class="p-toast-detail">{{ message.detail }}</div>
        </div>
      </div>
    </template>
  </Toast>
  <ConfirmDialog />
  <div class="app-layout" :class="{ 'no-layout': !showLayout }">
    <AppHeader v-if="showLayout" :menu-open="menuOpen" @toggle-menu="toggleMenu" />
    <AppDrawer v-if="showLayout" :open="menuOpen" @close="menuOpen = false" />
    <div class="app-content" v-if="showLayout">
      <main class="main-content">
        <router-view />
      </main>
    </div>
    <router-view v-if="!showLayout" />
    <AppFooter v-if="showLayout" />
  </div>
</template>

<style scoped>
.aviso-ollita {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
  min-width: 0;
}

.aviso-ollita__texto {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  min-width: 0;
  overflow-wrap: anywhere;
}

.app-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-layout.no-layout {
  display: block;
}

.app-content {
  display: flex;
  flex: 1;
}

.main-content {
  flex: 1;
  min-width: 0;
  padding: 2rem;
  background: var(--bg-main);
  min-height: calc(100vh - 60px - 50px);
}
</style>
