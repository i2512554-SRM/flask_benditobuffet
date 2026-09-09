import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../config/axios'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || null)
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
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
        guardarSesion(token.value, {
          id: info.id,
          nombre: info.nombre,
          rol: info.rol
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

  const logout = () => {
    api.post('/auth/logout').catch(() => {})
    limpiarSesion()
  }

  const refreshToken = async () => {
    try {
      const response = await api.post('/auth/refresh')
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
    checkSession
  }
})