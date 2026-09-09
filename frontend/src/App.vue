<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import AppHeader from './components/layout/AppHeader.vue'
import AppDrawer from './components/layout/AppDrawer.vue'
import AppFooter from './components/layout/AppFooter.vue'
import Toast from 'primevue/toast'
import ConfirmDialog from 'primevue/confirmdialog'

const route = useRoute()
const showLayout = computed(() => !['login', 'home'].includes(route.name))
const menuOpen = ref(false)

const toggleMenu = () => {
  menuOpen.value = !menuOpen.value
}
</script>

<template>
  <Toast />
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
  padding: 2rem;
  background: var(--bg-main);
  min-height: calc(100vh - 60px - 50px);
}
</style>