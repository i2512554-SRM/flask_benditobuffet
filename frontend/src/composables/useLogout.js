import { useRouter } from 'vue-router'
import { useConfirm } from 'primevue/useconfirm'
import { useAuthStore } from '../stores/auth'

export function useLogout() {
  const router = useRouter()
  const authStore = useAuthStore()
  const confirm = useConfirm()

  const cerrarSesion = () => {
    authStore.logout()
    router.replace('/login')
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