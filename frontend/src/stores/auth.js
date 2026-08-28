import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../config/axios'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || null)
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isAuthenticated = computed(() => !!token.value)
  const userRole = computed(() => user.value?.rol || null)

  const login = async (credentials) => {
    try {
      const response = await api.post('/auth/login', credentials)
      const data = response.data
      
      if (data.success) {
        token.value = data.data.token
        user.value = data.data.user
        
        localStorage.setItem('token', token.value)
        localStorage.setItem('user', JSON.stringify(user.value))
        
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
    } catch (error) {
      console.error('Error en logout:', error)
    } finally {
      token.value = null
      user.value = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
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
    isAuthenticated,
    userRole,
    login,
    logout,
    refreshToken
  }
})
