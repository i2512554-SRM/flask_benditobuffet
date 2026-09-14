import { useRouter } from 'vue-router'
import { useConfirm } from 'primevue/useconfirm'
import { useAuthStore } from '../stores/auth'
import { useToast } from 'primevue/usetoast'

export function useLogout() {
  const router = useRouter()
  const authStore = useAuthStore()
  const confirm = useConfirm()
  const toast = useToast()

  const cerrarSesion = async () => {
    try {
      await authStore.logout()
      router.replace('/login')
    } catch (error) {
      if (error.response?.status === 401) {
        authStore.limpiarSesion(); router.replace('/login')
      } else {
        toast.add({ severity: 'error', summary: 'No se pudo cerrar la sesión', detail: 'Comprueba la conexión e intenta nuevamente.', life: 4000 })
      }
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
