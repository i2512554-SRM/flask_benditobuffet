<template>
  <div class="login">
    <div class="card">
      <img :src="logoSrc" class="logo" alt="Logo Bendito Buffet" />
      <h2>Iniciar Sesion</h2>
      <p class="sub">Sistema de Gestion Integral - Bendito Buffet</p>
      <p class="sub2">Selecciona tu rol para acceder al sistema</p>

      <div class="roles">
        <div class="rol" :class="{ activo: rol === 'administrador' }" @click="cambiarRol('administrador')">
          <i class="fa-solid fa-shield"></i> Administrador
        </div>
        <div class="rol" :class="{ activo: rol === 'cajero' }" @click="cambiarRol('cajero')">
          <i class="fa-solid fa-dollar-sign"></i> Cajero
        </div>
      </div>

      <div class="info">
        <i :class="infoRol.icono"></i>
        <div>
          <h4>{{ infoRol.titulo }}</h4>
          <p>{{ infoRol.desc }}</p>
        </div>
      </div>

      <form class="form" @submit.prevent="handleLogin">
        <label>Usuario</label>
        <input
          type="text"
          v-model="usuario"
          autocomplete="off"
          placeholder="Tu usuario"
          required
        />

        <label>Contrasena</label>
        <input
          type="password"
          v-model="contrasena"
          autocomplete="new-password"
          placeholder="Tu contrasena"
          required
        />

        <button type="submit" class="btn" :disabled="loading">
          {{ loading ? 'Ingresando...' : 'Entrar como ' + infoRol.titulo }}
        </button>
      </form>

      <div v-if="errorMsg" class="flash error">{{ errorMsg }}</div>

      <p class="olvide">Olvidaste tu contrasena?</p>

      <hr />

      <p class="final">Acceso exclusivo para trabajadores del restaurante.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import logoSrc from '../assets/logo.png'

const router = useRouter()
const authStore = useAuthStore()

const usuario = ref('')
const contrasena = ref('')
const rol = ref('administrador')
const loading = ref(false)
const errorMsg = ref('')

const rolesInfo = {
  administrador: {
    titulo: 'Administrador',
    desc: 'Acceso completo a todos los modulos del sistema.',
    icono: 'fa-solid fa-shield'
  },
  cajero: {
    titulo: 'Cajero',
    desc: 'Acceso a modulo de caja e inventario.',
    icono: 'fa-solid fa-dollar-sign'
  }
}

const infoRol = computed(() => rolesInfo[rol.value])

const cambiarRol = (nuevoRol) => {
  rol.value = nuevoRol
}

const handleLogin = async () => {
  loading.value = true
  errorMsg.value = ''
  try {
    await authStore.login({
      usuario: usuario.value,
      clave: contrasena.value
    })
    router.push('/panel')
  } catch (error) {
    errorMsg.value = error?.response?.data?.error || 'Credenciales invalidas'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Lexend:wght@100..900&display=swap');

.login {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 30px;
  background: var(--bg-main, #f5f6f8);
  font-family: 'Lexend', sans-serif;
}

.card {
  width: min(100%, 520px);
  background: var(--bg-card, #ffffff);
  padding: 40px;
  border-radius: 20px;
  border: 1px solid rgba(255, 123, 0, 0.12);
  text-align: center;
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.04);
}

.logo {
  width: 100px;
  margin: 0 auto 10px;
  display: block;
}

h2 {
  margin: 0;
  font-size: 22px;
  color: var(--text-main, #111827);
}

.sub {
  color: var(--text-muted, #6b7280);
  margin: 5px 0;
  font-size: 14px;
}

.sub2 {
  color: var(--text-muted, #6b7280);
  font-size: 14px;
  margin-bottom: 20px;
}

.roles {
  display: flex;
  justify-content: space-between;
  background: var(--bg-secondary, #f7f8fb);
  border-radius: 12px;
  padding: 5px;
  margin-bottom: 20px;
}

.rol {
  flex: 1;
  padding: 10px;
  cursor: pointer;
  border-radius: 10px;
  font-size: 14px;
  text-align: center;
  color: var(--text-main, #111827);
  transition: all 0.18s ease;
}

.rol i {
  margin-right: 5px;
}

.rol.activo {
  background: var(--bg-card, #ffffff);
  border: 1px solid var(--border-color, #e5e7eb);
  font-weight: 600;
}

.info {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255, 123, 0, 0.12);
  border: 1px solid #ff7b00;
  border-radius: 12px;
  padding: 15px;
  text-align: left;
  margin-bottom: 20px;
}

.info i {
  background: #ff7b00;
  color: var(--bg-card, #ffffff);
  padding: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.info h4 {
  margin: 0;
  font-size: 14px;
  color: var(--text-main, #111827);
}

.info p {
  margin: 2px 0 0;
  font-size: 13px;
  color: var(--text-muted, #6b7280);
}

.form {
  text-align: left;
}

.form label {
  display: block;
  margin-top: 12px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-main, #111827);
}

.form input {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 10px;
  margin-top: 5px;
  background: var(--input-bg, #ffffff);
  color: var(--text-main, #111827);
  font-size: 14px;
  box-sizing: border-box;
}

.form input:focus {
  outline: none;
  border: 1px solid #ff7b00;
  box-shadow: 0 0 0 3px rgba(255, 123, 0, 0.1);
}

.btn {
  width: 100%;
  margin-top: 20px;
  padding: 14px;
  background: linear-gradient(135deg, #ff7a18 0%, #ffb259 100%);
  color: #ffffff;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  font-size: 15px;
  cursor: pointer;
  transition: opacity 0.18s ease;
}

.btn:hover:not(:disabled) {
  opacity: 0.9;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.flash {
  margin-top: 12px;
  padding: 10px;
  border-radius: 8px;
  font-size: 14px;
}

.flash.error {
  background: #f8d7da;
  color: #721c24;
}

.flash.success {
  background: #d4edda;
  color: #155724;
}

.olvide {
  text-align: center;
  color: var(--text-muted, #6b7280);
  margin-top: 15px;
  font-size: 14px;
}

hr {
  border: none;
  border-top: 1px solid var(--border-color, #e5e7eb);
  margin: 15px 0;
}

.final {
  text-align: center;
  font-size: 13px;
  color: var(--text-muted, #6b7280);
}

@media (max-width: 540px) {
  .card {
    padding: 24px 16px;
  }
  .roles {
    gap: 10px;
  }
}
</style>
