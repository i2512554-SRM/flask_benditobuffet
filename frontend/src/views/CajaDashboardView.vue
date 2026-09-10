<template>
  <div class="caja-dashboard">
    <div class="page-hero">
      <div class="hero-left">
        <h1>{{ rol === 1 ? '¡Hola, ' + nombre + '! 🧾' : '¡Hola, ' + nombre + '! 🛎️' }}</h1>
        <p>{{ rol === 1 ? 'Resumen general de la caja para la administración' : 'Tu caja del día, todo en un solo vistazo' }}</p>
        <div class="hero-badges">
          <span class="rol-badge">
            <i class="fa-solid fa-cash-register"></i> {{ rol === 1 ? 'Administrador' : 'Cajera' }}
          </span>
          <span class="fecha-badge"><i class="fa-regular fa-calendar"></i> {{ fechaHoy }}</span>
        </div>
      </div>
      <router-link to="/caja" class="btn btn-outline">
        <i class="fa-solid fa-vault"></i> Ir al Control de Caja
      </router-link>
    </div>

    <!-- Resumen de caja -->
    <h2 class="seccion-title">Resumen de caja</h2>
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon" :class="caja.abierta ? 'positive' : 'negative'">
          <i :class="caja.abierta ? 'fa-solid fa-lock-open' : 'fa-solid fa-lock'"></i>
        </div>
        <div class="stat-content">
          <span class="stat-label">Estado</span>
          <span class="stat-value">{{ caja.abierta ? 'Abierta' : 'Cerrada' }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon blue">
          <i class="fa-solid fa-clock"></i>
        </div>
        <div class="stat-content">
          <span class="stat-label">Monto inicial</span>
          <span class="stat-value">S/. {{ formatMoney(caja.cierre?.monto_inicial) }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon positive">
          <i class="fa-solid fa-arrow-trend-up"></i>
        </div>
        <div class="stat-content">
          <span class="stat-label">Ingresos del día</span>
          <span class="stat-value">S/. {{ formatMoney(caja.ventas_dia) }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon negative">
          <i class="fa-solid fa-arrow-trend-down"></i>
        </div>
        <div class="stat-content">
          <span class="stat-label">Egresos del día</span>
          <span class="stat-value">S/. {{ formatMoney(caja.gastos_dia) }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" :class="(caja.neto_dia ?? 0) >= 0 ? 'positive' : 'negative'">
          <i class="fa-solid fa-scale-balanced"></i>
        </div>
        <div class="stat-content">
          <span class="stat-label">Saldo actual</span>
          <span class="stat-value">S/. {{ formatMoney(caja.neto_dia) }}</span>
        </div>
      </div>
    </div>

    <!-- Módulos de caja -->
    <h2 class="seccion-title">Módulos de caja</h2>
    <div class="modulos-grid">
      <router-link to="/caja" class="modulo-card">
        <div class="modulo-icon ic-green"><i class="fa-solid fa-cash-register"></i></div>
        <div>
          <span class="modulo-titulo">Control de Caja</span>
          <span class="modulo-desc">Abre, opera y cierra la caja del día</span>
        </div>
        <i class="fa-solid fa-chevron-right modulo-arrow"></i>
      </router-link>
      <router-link to="/caja/movimientos" class="modulo-card">
        <div class="modulo-icon ic-blue"><i class="fa-solid fa-arrows-rotate"></i></div>
        <div>
          <span class="modulo-titulo">Movimientos</span>
          <span class="modulo-desc">Revisa ingresos y egresos con histórico</span>
        </div>
        <i class="fa-solid fa-chevron-right modulo-arrow"></i>
      </router-link>
      <router-link to="/caja/historial" class="modulo-card">
        <div class="modulo-icon ic-purple"><i class="fa-solid fa-clock-rotate-left"></i></div>
        <div>
          <span class="modulo-titulo">Historial de Cierres</span>
          <span class="modulo-desc">Cierres anteriores con sus montos</span>
        </div>
        <i class="fa-solid fa-chevron-right modulo-arrow"></i>
      </router-link>
      <router-link v-if="rol === 1" to="/caja/reportes" class="modulo-card">
        <div class="modulo-icon ic-orange"><i class="fa-solid fa-chart-line"></i></div>
        <div>
          <span class="modulo-titulo">Reportes Financieros</span>
          <span class="modulo-desc">Gráficos y rendimiento financiero</span>
        </div>
        <i class="fa-solid fa-chevron-right modulo-arrow"></i>
      </router-link>
    </div>

    <div class="loading-overlay" v-if="loading">
      <i class="fa-solid fa-spinner fa-spin"></i>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import api from '../config/axios'

const authStore = useAuthStore()
const rol = computed(() => authStore.user?.rol)
const nombre = computed(() => authStore.user?.nombre || (rol.value === 1 ? 'Administrador' : 'Cajera'))
const loading = ref(true)
const caja = ref({ abierta: false, ventas_dia: 0, gastos_dia: 0, neto_dia: 0, cierre: null })

const fechaHoy = computed(() =>
  new Intl.DateTimeFormat('es-PE', {
    weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'
  }).format(new Date())
)

const formatMoney = (val) => Number(val || 0).toLocaleString('es-PE', { minimumFractionDigits: 2 })

let timer = null

const cargar = async () => {
  try {
    const res = await api.get('/caja/actual')
    if (res.data?.success) caja.value = res.data.data
  } catch (err) {
    console.error('Error cargando dashboard de caja:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  cargar()
  timer = setInterval(cargar, 30000)
})

onUnmounted(() => clearInterval(timer))
</script>

<style scoped>
.page-hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.hero-badges {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.6rem;
  flex-wrap: wrap;
}

.rol-badge,
.fecha-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.72rem;
  font-weight: 600;
  padding: 0.3rem 0.7rem;
  border-radius: 999px;
}

.rol-badge { background: rgba(16, 185, 129, 0.1); color: #059669; }
.fecha-badge { background: var(--bg-secondary); color: var(--text-muted); }

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
  gap: 0.9rem;
  margin-top: 1rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 0.9rem;
  padding: 1rem 1.05rem;
  background: var(--bg-card);
  border-radius: 14px;
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-soft);
}

.stat-icon {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  flex-shrink: 0;
}

.stat-icon.positive { background: rgba(22, 163, 74, 0.1); color: var(--color-verde-fuerte); }
.stat-icon.negative { background: rgba(220, 38, 38, 0.1); color: var(--color-rojo); }
.stat-icon.blue { background: rgba(59, 130, 246, 0.1); color: #2563eb; }

.stat-content { display: flex; flex-direction: column; }
.stat-label { font-size: 0.72rem; color: var(--text-muted); margin-bottom: 0.1rem; }
.stat-value { font-size: 1.15rem; font-weight: 700; color: var(--text-main); }

.modulos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 0.9rem;
  margin-top: 1rem;
}

.modulo-card {
  display: flex;
  align-items: center;
  gap: 0.9rem;
  padding: 1rem;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  box-shadow: var(--shadow-soft);
  text-decoration: none;
  color: var(--text-main);
  transition: all 0.18s ease;
}

.modulo-card:hover {
  border-color: var(--btn-primary);
  transform: translateY(-2px);
}

.modulo-icon {
  width: 42px;
  height: 42px;
  border-radius: 11px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  flex-shrink: 0;
}

.ic-green { background: rgba(22, 163, 74, 0.1); color: #16a34a; }
.ic-blue { background: rgba(59, 130, 246, 0.1); color: #3b82f6; }
.ic-purple { background: rgba(139, 92, 246, 0.1); color: #8b5cf6; }
.ic-orange { background: rgba(255, 123, 0, 0.12); color: var(--btn-primary); }

.modulo-card > div:nth-child(2) {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
}

.modulo-titulo { font-weight: 600; font-size: 0.88rem; }
.modulo-desc { font-size: 0.74rem; color: var(--text-muted); }
.modulo-arrow { color: var(--text-muted); font-size: 0.8rem; opacity: 0.6; }

.loading-overlay {
  display: flex;
  justify-content: center;
  padding: 2rem;
  color: var(--btn-primary);
  font-size: 1.5rem;
}

@media (max-width: 768px) {
  .page-hero { flex-direction: column; }
}
</style>