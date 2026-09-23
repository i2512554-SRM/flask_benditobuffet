<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppHeader from './components/layout/AppHeader.vue'
import AppSidebar from './components/layout/AppSidebar.vue'
import AppFooter from './components/layout/AppFooter.vue'
import Toast from 'primevue/toast'
import ConfirmDialog from 'primevue/confirmdialog'

const route = useRoute()
const showLayout = computed(() => !['login', 'home'].includes(route.name))
</script>

<template>
  <Toast />
  <ConfirmDialog />
  <div class="app-layout" :class="{ 'no-layout': !showLayout }">
    <AppHeader v-if="showLayout" />
    <div class="app-content" v-if="showLayout">
      <AppSidebar />
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
  margin-left: 250px;
  padding: 2rem;
  background: var(--bg-main);
  min-height: calc(100vh - 60px - 50px);
}
</style>
