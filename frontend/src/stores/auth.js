import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../config/axios'

const leerUsuarioGuardado = () => {
  try {
    const valor = JSON.parse(localStorage.getItem('user') || 'null')
    return valor && typeof valor === 'object' ? valor : null
  } catch {
    localStorage.removeItem('user')
    return null
  }
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || null)
  const user = ref(leerUsuarioGuardado())
  const sessionValid = ref(false)
  const sessionChecked = ref(false)

  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const userRole = computed(() => user.value?.rol || null)

  const guardarSesion = (tok, usr, refresh) => {
    token.value = tok
    user.value = usr
    localStorage.setItem('token', tok)
    localStorage.setItem('user', JSON.stringify(usr))
    if (refresh) {
      localStorage.setItem('refresh_token', refresh)
    }
  }

  const limpiarSesion = () => {
    token.value = null
    user.value = null
    sessionValid.value = false
    sessionChecked.value = false
    localStorage.removeItem('token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  }

  const actualizarTokens = (tok, refresh) => {
    if (!tok) return
    token.value = tok
    localStorage.setItem('token', tok)
    if (refresh) localStorage.setItem('refresh_token', refresh)
  }

  const actualizarUsuario = (datos) => {
    if (!user.value) return
    user.value = { ...user.value, ...datos }
    localStorage.setItem('user', JSON.stringify(user.value))
  }

  const checkSession = async () => {
    if (!token.value) {
      sessionValid.value = false
      sessionChecked.value = true
      return false
    }
    try {
      const response = await api.get('/auth/me')
      const info = response.data?.data
      if (response.data?.success && info) {
        guardarSesion(localStorage.getItem('token'), {
          id: info.id,
          nombre: info.nombre,
          rol: info.rol,
          foto_perfil: info.foto_perfil || null
        }, null)
        sessionValid.value = true
        sessionChecked.value = true
        return true
      }
    } catch (error) {
      sessionValid.value = false
    }
    limpiarSesion()
    sessionChecked.value = true
    return false
  }

  const login = async (credentials) => {
    try {
      const response = await api.post('/auth/login', credentials)
      const data = response.data

      if (data.success) {
        guardarSesion(data.data.token, data.data.user, data.data.refresh_token)
        sessionValid.value = true
        sessionChecked.value = true
        return true
      } else {
        throw new Error(data.error || 'Error en login')
      }
    } catch (error) {
      console.error('Error en login:', error)
      throw error
    }
  }

  const logout = async () => {
    try {
      await api.post('/auth/logout')
    } finally {
      limpiarSesion()
    }
  }

  const refreshToken = async () => {
    try {
      const response = await api.post('/auth/refresh', {}, { headers: { Authorization: `Bearer ${localStorage.getItem('refresh_token')}` } })
      const data = response.data

      if (data.success) {
        token.value = data.data.token
        localStorage.setItem('token', token.value)
        return true
      }
    } catch (error) {
      console.error('Error refreshing token:', error)
      throw error
    }
  }

  return {
    token,
    user,
    sessionValid,
    sessionChecked,
    isAuthenticated,
    userRole,
    login,
    logout,
    refreshToken,
    checkSession,
    actualizarUsuario,
    actualizarTokens,
    limpiarSesion
  }
})
