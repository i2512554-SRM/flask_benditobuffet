<template>
  <div class="login">
    <Transition name="card" appear>
      <div class="card">
        <img :src="logoSrc" class="logo stagger-1" alt="Logo Bendito Buffet" />
        <h2 class="stagger-2">Iniciar Sesión</h2>
        <p class="sub stagger-3">Sistema de Gestión Integral - Bendito Buffet</p>

        <form class="form stagger-4" @submit.prevent="handleLogin">
          <label>Usuario</label>
          <div class="field">
            <input
              v-model="usuario"
              type="text"
              autocomplete="off"
              placeholder="Tu usuario"
              :disabled="loading || success"
              required
            />
          </div>

          <label>Contraseña</label>
          <div class="field">
            <input
              v-model="contrasena"
              :type="showPassword ? 'text' : 'password'"
              autocomplete="current-password"
              placeholder="Tu contraseña"
              :disabled="loading || success"
              required
            />
            <button
              type="button"
              class="toggle-pass"
              :class="{ active: showPassword }"
              :aria-label="showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'"
              @click="showPassword = !showPassword"
            >
              <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
            </button>
          </div>

          <button
            type="submit"
            class="btn"
            :class="{ 'is-loading': loading, 'is-success': success }"
            :disabled="loading || success"
          >
            <span class="btn-content">
              <span v-if="loading" class="spinner" aria-hidden="true"></span>
              <span v-else-if="success" class="check" aria-hidden="true">✓</span>
              {{ success ? '¡Bienvenido!' : loading ? 'Ingresando…' : 'Ingresar' }}
            </span>
          </button>
        </form>

        <Transition name="error">
          <div v-if="errorMsg" :key="shakeKey" class="flash error" role="alert">
            <i class="fas fa-circle-exclamation"></i>
            <span>{{ errorMsg }}</span>
          </div>
        </Transition>

        <p class="olvide stagger-5">¿Olvidaste tu contraseña?</p>

        <hr class="stagger-6" />

        <p class="final stagger-6">Acceso exclusivo para trabajadores del restaurante.</p>
      </div>
    </Transition>
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
const success = ref(false)
const errorMsg = ref('')
const shakeKey = ref(0)
const showPassword = ref(false)

const handleLogin = async () => {
  loading.value = true
  errorMsg.value = ''
  try {
    await authStore.login({
      usuario: usuario.value,
      clave: contrasena.value
    })
    success.value = true
    setTimeout(() => router.push('/panel'), 650)
  } catch (error) {
    errorMsg.value = error?.response?.data?.error || 'Credenciales inválidas'
    shakeKey.value++
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
  padding: 24px;
  font-family: 'Lexend', sans-serif;
  background:
    radial-gradient(1200px 600px at 15% -10%, rgba(255, 123, 0, 0.10), transparent 55%),
    radial-gradient(900px 500px at 110% 110%, rgba(255, 123, 0, 0.08), transparent 60%),
    var(--bg-main, #f5f6f8);
}

/* ===== Card: glassmorphism sutil ===== */
.card {
  width: min(100%, 460px);
  padding: 44px 40px;
  border-radius: 24px;
  text-align: center;
  background: color-mix(in srgb, var(--bg-card, #ffffff) 82%, transparent);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border: 1px solid rgba(255, 123, 0, 0.16);
  box-shadow:
    0 2px 6px rgba(15, 23, 42, 0.04),
    0 24px 48px -12px rgba(15, 23, 42, 0.12);
}

/* ===== Entrada de la tarjeta ===== */
.card-enter-active {
  transition:
    opacity 0.6s cubic-bezier(0.22, 1, 0.36, 1),
    transform 0.6s cubic-bezier(0.22, 1, 0.36, 1);
}
.card-enter-from {
  opacity: 0;
  transform: translateY(28px) scale(0.97);
}

/* ===== Elementos internos con desfase ===== */
.stagger-1 { animation: rise 0.7s cubic-bezier(0.22, 1, 0.36, 1) 0.15s both; }
.stagger-2 { animation: rise 0.7s cubic-bezier(0.22, 1, 0.36, 1) 0.22s both; }
.stagger-3 { animation: rise 0.7s cubic-bezier(0.22, 1, 0.36, 1) 0.29s both; }
.stagger-4 { animation: rise 0.7s cubic-bezier(0.22, 1, 0.36, 1) 0.37s both; }
.stagger-5 { animation: rise 0.7s cubic-bezier(0.22, 1, 0.36, 1) 0.46s both; }
.stagger-6 { animation: rise 0.7s cubic-bezier(0.22, 1, 0.36, 1) 0.53s both; }

@keyframes rise {
  from { opacity: 0; transform: translateY(14px); }
  to   { opacity: 1; transform: translateY(0); }
}

.logo {
  width: 92px;
  margin: 0 auto 14px;
  display: block;
  filter: drop-shadow(0 6px 14px rgba(255, 123, 0, 0.18));
  transition: transform 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.logo:hover {
  transform: scale(1.06) rotate(-2deg);
}

h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  letter-spacing: -0.01em;
  color: var(--text-main, #111827);
}

.sub {
  color: var(--text-muted, #6b7280);
  margin: 6px 0 4px;
  font-size: 14px;
}

/* ===== Formulario ===== */
.form {
  text-align: left;
  margin-top: 6px;
}

.form label {
  display: block;
  margin-top: 16px;
  font-size: 13.5px;
  font-weight: 600;
  color: var(--text-main, #111827);
}

.field {
  position: relative;
  margin-top: 7px;
}

.field input {
  width: 100%;
  padding: 13px 44px 13px 14px;
  border: 1.5px solid var(--border-color, #e5e7eb);
  border-radius: 12px;
  background: var(--input-bg, #ffffff);
  color: var(--text-main, #111827);
  font-size: 14.5px;
  font-family: inherit;
  box-sizing: border-box;
  transition:
    border-color 0.25s cubic-bezier(0.4, 0, 0.2, 1),
    box-shadow 0.25s cubic-bezier(0.4, 0, 0.2, 1),
    transform 0.25s cubic-bezier(0.4, 0, 0.2, 1),
    opacity 0.2s ease;
}

.field input:hover:not(:disabled):not(:focus) {
  border-color: #f6b17a;
}

.field input:focus {
  outline: none;
  border-color: #ff7b00;
  box-shadow: 0 0 0 4px rgba(255, 123, 0, 0.12);
  transform: translateY(-1px);
}

.field input:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

/* Toggle mostrar/ocultar contraseña */
.toggle-pass {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  width: 34px;
  height: 34px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: var(--text-muted, #6b7280);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  transition:
    background-color 0.2s ease,
    color 0.2s ease,
    transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.toggle-pass:hover {
  background: rgba(255, 123, 0, 0.1);
  color: #ff7b00;
}
.toggle-pass:active {
  transform: translateY(-50%) scale(0.88);
}
.toggle-pass.active {
  color: #ff7b00;
}

/* ===== Botón principal ===== */
.btn {
  width: 100%;
  margin-top: 22px;
  padding: 14px;
  background: linear-gradient(135deg, #ff7a18 0%, #ffb259 130%);
  color: #ffffff;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  font-size: 15px;
  font-family: inherit;
  cursor: pointer;
  box-shadow: 0 6px 18px -4px rgba(255, 122, 24, 0.45);
  transition:
    transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1),
    box-shadow 0.3s ease,
    opacity 0.2s ease;
}

.btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 24px -4px rgba(255, 122, 24, 0.55);
}

.btn:active:not(:disabled) {
  transform: translateY(0) scale(0.985);
  box-shadow: 0 4px 12px -4px rgba(255, 122, 24, 0.4);
}

.btn:disabled {
  cursor: not-allowed;
  opacity: 0.8;
}

.btn.is-success {
  background: linear-gradient(135deg, #22c55e 0%, #86efac 140%);
  box-shadow: 0 6px 18px -4px rgba(34, 197, 94, 0.45);
}

.btn-content {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 9px;
}

/* Spinner del estado de carga */
.spinner {
  width: 16px;
  height: 16px;
  border: 2.5px solid rgba(255, 255, 255, 0.45);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Check de éxito con pop */
.check {
  font-weight: 700;
  animation: pop 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}
@keyframes pop {
  0%   { transform: scale(0); opacity: 0; }
  70%  { transform: scale(1.25); }
  100% { transform: scale(1); opacity: 1; }
}

/* ===== Mensajes de feedback ===== */
.flash {
  margin-top: 16px;
  padding: 12px 14px;
  border-radius: 12px;
  font-size: 13.5px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 9px;
  text-align: left;
}

.flash.error {
  background: rgba(239, 68, 68, 0.1);
  color: #b91c1c;
  border: 1px solid rgba(239, 68, 68, 0.25);
}

.flash.error i {
  flex-shrink: 0;
}

/* Entrada del error: desliza + shake */
.error-enter-active {
  transition:
    opacity 0.35s cubic-bezier(0.22, 1, 0.36, 1),
    transform 0.35s cubic-bezier(0.22, 1, 0.36, 1);
}
.error-enter-active {
  animation: shakeX 0.45s cubic-bezier(0.36, 0.07, 0.19, 0.97);
}
.error-enter-from {
  opacity: 0;
  transform: translateY(-8px);
}
.error-leave-active {
  transition: opacity 0.2s ease;
}
.error-leave-to {
  opacity: 0;
}

@keyframes shakeX {
  0%, 100% { transform: translateX(0); }
  20%      { transform: translateX(-8px); }
  40%      { transform: translateX(8px); }
  60%      { transform: translateX(-5px); }
  80%      { transform: translateX(4px); }
}

/* ===== Resto ===== */
.olvide {
  text-align: center;
  color: var(--text-muted, #6b7280);
  margin-top: 18px;
  font-size: 13.5px;
  transition: color 0.2s ease;
  cursor: pointer;
}
.olvide:hover {
  color: #ff7b00;
}

hr {
  border: none;
  border-top: 1px solid var(--border-color, #e5e7eb);
  margin: 18px 0;
}

.final {
  text-align: center;
  font-size: 13px;
  color: var(--text-muted, #6b7280);
}

/* ===== Responsive ===== */
@media (max-width: 540px) {
  .card {
    padding: 32px 22px;
    border-radius: 20px;
  }
  .logo {
    width: 78px;
  }
  h2 {
    font-size: 21px;
  }
}

@media (max-width: 360px) {
  .card {
    padding: 26px 16px;
  }
}

/* Respeta usuarios que piden menos movimiento */
@media (prefers-reduced-motion: reduce) {
  .card-enter-active,
  .stagger-1, .stagger-2, .stagger-3,
  .stagger-4, .stagger-5, .stagger-6,
  .error-enter-active {
    animation: none !important;
    transition-duration: 0.01s !important;
  }
}
</style>
