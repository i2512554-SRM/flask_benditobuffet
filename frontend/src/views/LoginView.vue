<template>
  <div class="login">
    <div class="card">
      <img :src="logoSrc" class="logo" alt="Logo Bendito Buffet" />
      <h2>Iniciar Sesion</h2>
      <p class="sub">Sistema de Gestion Integral - Bendito Buffet</p>

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
          {{ loading ? 'Ingresando...' : 'Ingresar' }}
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
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import logoSrc from '../assets/logo.png'

const router = useRouter()
const authStore = useAuthStore()

const usuario = ref('')
const contrasena = ref('')
const loading = ref(false)
const errorMsg = ref('')

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
}
</style>
