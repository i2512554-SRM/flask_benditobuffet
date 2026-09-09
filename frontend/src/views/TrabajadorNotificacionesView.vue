<template>
  <div class="trabajador-view">
    <VolverBtn to="/trabajador" />
    <div class="page-header">
      <div>
        <h1>Notificaciones</h1>
        <p>Avisos enviados por la administración</p>
      </div>
      <button class="btn btn-outline" :disabled="!noLeidas" @click="marcarLeidas">
        <i class="fa-solid fa-check-double"></i> Marcar todas como leídas
      </button>
    </div>

    <div class="notif-wrap">
      <div v-for="n in notifs" :key="n.id_notificacion" class="notif-card" :class="{ unread: !n.leida }">
        <div class="notif-icon" :class="{ leida: n.leida }">
          <i :class="n.leida ? 'fa-regular fa-bell' : 'fa-solid fa-bell'"></i>
        </div>
        <div class="notif-body">
          <div class="notif-head">
            <span class="notif-title">{{ n.titulo }}</span>
            <span class="notif-date">{{ n.fecha }}</span>
          </div>
          <p class="notif-msg">{{ n.mensaje }}</p>
        </div>
        <span v-if="!n.leida" class="unread-dot" title="No leída"></span>
      </div>

      <div v-if="!notifs.length" class="empty-state">
        <i class="fa-regular fa-bell-slash"></i>
        <span>No tienes notificaciones.</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import VolverBtn from '../components/ui/VolverBtn.vue'
import api from '../config/axios'

const toast = useToast()
const notifs = ref([])

const noLeidas = computed(() => notifs.value.some((n) => !n.leida))

const load = async () => {
  try {
    const res = await api.get('/trabajador/notificaciones')
    if (res.data.success) notifs.value = res.data.data
  } catch (e) {
    console.error('Error cargando notificaciones:', e)
  }
}

const marcarLeidas = async () => {
  try {
    const res = await api.post('/trabajador/notificaciones/leer')
    if (res.data.success) {
      notifs.value = notifs.value.map((n) => ({ ...n, leida: true }))
      toast.add({ severity: 'success', summary: 'Listo', detail: 'Notificaciones marcadas como leídas', life: 3000 })
    }
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron marcar las notificaciones', life: 4000 })
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

.notif-wrap {
  padding: 1.5rem 2rem 2rem;
  max-width: 860px;
}

.notif-card {
  display: flex;
  gap: 0.85rem;
  align-items: flex-start;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 0.9rem 1rem;
  margin-bottom: 0.65rem;
  box-shadow: var(--shadow-soft);
  position: relative;
}

.notif-card.unread {
  border-color: rgba(249, 115, 22, 0.4);
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.03), var(--bg-card));
}

.notif-icon {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: rgba(249, 115, 22, 0.12);
  color: #f97316;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
  flex-shrink: 0;
}

.notif-icon.leida {
  background: var(--bg-secondary);
  color: var(--text-muted);
}

.notif-body {
  flex: 1;
}

.notif-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.notif-title {
  font-weight: 600;
  font-size: 0.88rem;
  color: var(--text-main);
}

.notif-date {
  font-size: 0.7rem;
  color: var(--text-muted);
  white-space: nowrap;
}

.notif-msg {
  margin: 0.25rem 0 0;
  font-size: 0.82rem;
  color: var(--text-muted);
}

.unread-dot {
  width: 9px;
  height: 9px;
  border-radius: 999px;
  background: linear-gradient(135deg, #f97316, #fb923c);
  flex-shrink: 0;
  margin-top: 0.35rem;
}

@media (max-width: 768px) {
  .page-header { flex-direction: column; gap: 1rem; align-items: flex-start; }
  .notif-wrap { padding: 1rem; }
  .notif-head { flex-direction: column; align-items: flex-start; gap: 0.25rem; }
}
</style>