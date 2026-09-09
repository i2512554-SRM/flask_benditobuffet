import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Interceptor para agregar token a las peticiones
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Refresh automático: si el access token expira, intenta renovarlo una vez
let refreshingPromise = null

async function renovarToken() {
  if (!refreshingPromise) {
    const refreshToken = localStorage.getItem('refresh_token')
    if (!refreshToken) return false
    refreshingPromise = axios
      .post(
        '/api/auth/refresh',
        {},
        { headers: { Authorization: `Bearer ${refreshToken}` } }
      )
      .then((res) => {
        const nuevo = res.data?.data?.token
        if (nuevo) {
          localStorage.setItem('token', nuevo)
          return true
        }
        return false
      })
      .catch(() => false)
      .finally(() => {
        refreshingPromise = null
      })
  }
  return refreshingPromise
}

// Interceptor para manejar errores de respuesta
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config
    if (
      error.response?.status === 401 &&
      !original._reintento &&
      !original.url.includes('/auth/login') &&
      !original.url.includes('/auth/refresh')
    ) {
      original._reintento = true
      const renovado = await renovarToken()
      if (renovado) {
        return api(original)
      }
      localStorage.removeItem('token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
