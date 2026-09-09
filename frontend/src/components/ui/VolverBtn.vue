<template>
  <router-link v-if="to" :to="to" class="volver-btn">
    <i class="fa-solid fa-arrow-left"></i> {{ etiqueta }}
  </router-link>
  <button v-else class="volver-btn" type="button" @click="goBack">
    <i class="fa-solid fa-arrow-left"></i> {{ etiqueta }}
  </button>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const props = defineProps({
  to: { type: [String, Object], default: null },
  etiqueta: { type: String, default: 'Volver' }
})

const router = useRouter()
const route = useRoute()
const historyPop = ref(false)

const goBack = () => {
  if (historyPop.value || window.history.length > 1) {
    router.back()
  } else {
    router.push('/')
  }
}

const guard = () => { historyPop.value = true }

onMounted(() => window.addEventListener('popstate', guard))
onUnmounted(() => window.removeEventListener('popstate', guard))
</script>

<style scoped>
.volver-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.55rem;
  padding: 0.5rem 1rem;
  margin-bottom: 1rem;
  border-radius: 999px;
  border: 1px solid var(--border-color);
  background: var(--bg-card);
  color: var(--text-muted);
  font-size: 0.82rem;
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
  box-shadow: var(--shadow-soft);
  transition: all 0.18s ease;
}

.volver-btn i {
  color: var(--btn-primary);
  font-size: 0.8rem;
}

.volver-btn:hover {
  border-color: var(--btn-primary);
  color: var(--btn-primary);
  transform: translateX(-2px);
}
</style>