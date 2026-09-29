import { ref, onMounted, onBeforeUnmount } from 'vue'

export const MINUTOS_INACTIVIDAD = 15
export const SEGUNDOS_AVISO = 60

const CLAVE_ACTIVIDAD = 'ultimaActividad'
const EVENTOS = ['mousedown', 'mousemove', 'keydown', 'touchstart', 'wheel', 'scroll']

const leerUltimaActividad = () => {
  try {
    return Number(localStorage.getItem(CLAVE_ACTIVIDAD)) || Date.now()
  } catch {
    return Date.now()
  }
}

const guardarActividad = (instante) => {
  try {
    localStorage.setItem(CLAVE_ACTIVIDAD, String(instante))
  } catch {
    return
  }
}

export function useInactividad({ activa, alExpirar }) {
  const avisoVisible = ref(false)
  const segundosRestantes = ref(SEGUNDOS_AVISO)
  let ultimaEscritura = 0
  let temporizador = null
  let cerrando = false

  const registrarActividad = () => {
    const ahora = Date.now()
    if (avisoVisible.value || ahora - ultimaEscritura < 5000) return
    ultimaEscritura = ahora
    guardarActividad(ahora)
  }

  const seguirAqui = () => {
    ultimaEscritura = Date.now()
    guardarActividad(ultimaEscritura)
    avisoVisible.value = false
  }

  const revisar = async () => {
    if (!activa() || cerrando) {
      avisoVisible.value = false
      return
    }
    const limite = MINUTOS_INACTIVIDAD * 60 * 1000
    const inactivo = Date.now() - leerUltimaActividad()
    if (inactivo >= limite) {
      cerrando = true
      avisoVisible.value = false
      try {
        await alExpirar()
      } finally {
        cerrando = false
        guardarActividad(Date.now())
      }
      return
    }
    if (inactivo >= limite - SEGUNDOS_AVISO * 1000) {
      segundosRestantes.value = Math.max(0, Math.ceil((limite - inactivo) / 1000))
      avisoVisible.value = true
    } else {
      avisoVisible.value = false
    }
  }

  onMounted(() => {
    guardarActividad(Date.now())
    EVENTOS.forEach((evento) => window.addEventListener(evento, registrarActividad, { passive: true }))
    temporizador = window.setInterval(revisar, 1000)
  })

  onBeforeUnmount(() => {
    EVENTOS.forEach((evento) => window.removeEventListener(evento, registrarActividad))
    window.clearInterval(temporizador)
  })

  return { avisoVisible, segundosRestantes, seguirAqui }
}
