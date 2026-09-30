<template><button class="volver-btn" type="button" @click="goBack"><i class="fa-solid fa-arrow-left"></i> {{ props.etiqueta }}</button></template>
<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { homeForRole } from '../../router/links'
const props = defineProps({ to: { type: [String, Object], default: null }, etiqueta: { type: String, default: 'Volver' } })
const router = useRouter()
const auth = useAuthStore()
function goBack() {
  router.push(props.to || homeForRole(auth.userRole))
}
</script>
<style scoped>
.volver-btn {
  display: inline-flex;
  align-self: flex-start;
  width: max-content;
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
