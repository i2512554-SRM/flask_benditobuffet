<template>
  <Dialog
    :visible="avisoVisible"
    modal
    :closable="false"
    :draggable="false"
    :style="{ width: '420px' }"
    :breakpoints="{ '520px': '92vw' }"
    header="¿Sigues ahí?"
  >
    <div class="aviso-inactividad" role="alertdialog" aria-live="assertive">
      <OllitaMascota expresion="pensando" :tamano="96" />
      <p>
        Por seguridad cerraremos tu sesión en
        <strong>{{ segundosRestantes }} {{ segundosRestantes === 1 ? 'segundo' : 'segundos' }}</strong>
        si no hay actividad.
      </p>
    </div>
    <template #footer>
      <Button label="Cerrar sesión ahora" severity="secondary" text @click="cerrarAhora" />
      <Button label="Seguir aquí" icon="pi pi-check" autofocus @click="seguirAqui" />
    </template>
  </Dialog>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import { useAuthStore } from '../../stores/auth'
import { links } from '../../router/links'
import { useInactividad, MINUTOS_INACTIVIDAD } from '../../composables/useInactividad'

const route = useRoute()
const router = useRouter()
const toast = useToast()
const authStore = useAuthStore()

const cerrarSesion = async (motivo) => {
  try {
    await authStore.logout()
  } catch {
    authStore.limpiarSesion()
  }
  toast.add({ severity: 'info', summary: 'Sesión cerrada', detail: motivo, life: 6000 })
  router.replace(links.login)
}

const { avisoVisible, segundosRestantes, seguirAqui } = useInactividad({
  activa: () => authStore.isAuthenticated && !['login', 'home'].includes(route.name),
  alExpirar: () => cerrarSesion(`Cerramos tu sesión tras ${MINUTOS_INACTIVIDAD} minutos sin actividad.`)
})

const cerrarAhora = () => {
  avisoVisible.value = false
  cerrarSesion('Cerraste tu sesión.')
}
</script>

<style scoped>
.aviso-inactividad {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.aviso-inactividad p {
  margin: 0;
  line-height: 1.55;
  color: var(--text-main);
}

@media (max-width: 520px) {
  .aviso-inactividad {
    flex-direction: column;
    text-align: center;
  }
}
</style>
