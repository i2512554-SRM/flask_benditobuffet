import { useRouter } from 'vue-router'
import { useConfirm } from 'primevue/useconfirm'
import { useAuthStore } from '../stores/auth'
import { useToast } from 'primevue/usetoast'
import { links } from '../router/links'

export function useLogout() {
  const router = useRouter()
  const authStore = useAuthStore()
  const confirm = useConfirm()
  const toast = useToast()

  const cerrarSesion = async () => {
    try {
      await authStore.logout()
    } catch (error) {
      if (error.response?.status !== 401) {
        toast.add({ severity: 'warn', summary: 'Sesión cerrada localmente', detail: 'No se pudo confirmar el cierre en el servidor.', life: 4000 })
      }
    } finally {
      authStore.limpiarSesion()
      router.replace(links.login)
    }
  }

  const confirmarCierre = () => {
    confirm.require({
      header: 'Cerrar sesión',
      message: '¿Estás seguro de que deseas cerrar tu sesión?',
      rejectLabel: 'Cancelar',
      acceptLabel: 'Sí, cerrar sesión',
      acceptClass: 'p-button-danger p-button-sm',
      rejectClass: 'p-button-text p-button-sm',
      accept: cerrarSesion
    })
  }

  return { confirmarCierre, cerrarSesion }
}
