<template>
  <div class="panel-view">
    <div class="page-hero">
      <div class="hero-left">
        <h1>¡Hola, {{ nombre }}! 👋</h1>
        <p>Resumen operativo del negocio de Bendito Buffet</p>
        <div class="hero-badges">
          <span class="rol-badge"><i class="fa-solid fa-user-shield"></i> Administrador</span>
          <span class="fecha-badge"><i class="fa-regular fa-calendar"></i> {{ fechaHoy }}</span>
        </div>
      </div>
      <button class="btn btn-outline" @click="cargar">
        <i class="fa-solid fa-arrows-rotate"></i> Actualizar
      </button>
    </div>

    <!-- Resumen -->
    <h2 class="seccion-title">Resumen general</h2>
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon positive">
          <i class="fa-solid fa-arrow-trend-up"></i>
        </div>
        <div class="stat-content">
          <span class="stat-label">Ventas del mes</span>
          <span class="stat-value">S/. {{ formatMoney(stats.ventas_mes) }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon negative">
          <i class="fa-solid fa-arrow-trend-down"></i>
        </div>
        <div class="stat-content">
          <span class="stat-label">Egresos del mes</span>
          <span class="stat-value">S/. {{ formatMoney(stats.egresos_mes) }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" :class="stats.neto_mes >= 0 ? 'positive' : 'negative'">
          <i class="fa-solid fa-scale-balanced"></i>
        </div>
        <div class="stat-content">
          <span class="stat-label">Ganancia neta</span>
          <span class="stat-value">S/. {{ formatMoney(stats.neto_mes) }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple">
          <i class="fa-solid fa-boxes-stacked"></i>
        </div>
        <div class="stat-content">
          <span class="stat-label">Valor de inventario</span>
          <span class="stat-value">S/. {{ formatMoney(resumenInv.valor_total) }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon amber">
          <i class="fa-solid fa-inbox"></i>
        </div>
        <div class="stat-content">
          <span class="stat-label">Solicitudes pendientes</span>
          <span class="stat-value">{{ alertas.adelantos_pendientes + alertas.solicitudes_pendientes }}</span>
        </div>
      </div>
    </div>

    <div class="panel-grid">
      <div class="col-main">
        <!-- Rendimiento financiero -->
        <h2 class="seccion-title">Rendimiento financiero</h2>
        <div class="chart-card">
          <div class="filtros-bar">
            <div class="periodo-tabs">
              <button
                v-for="p in periodos"
                :key="p.key"
                class="filtro-btn"
                :class="{ active: periodo === p.key }"
                @click="cambiarPeriodo(p.key)"
              >
                {{ p.label }}
              </button>
            </div>
            <div class="serie-toggles">
              <button
                v-for="s in series"
                :key="s.key"
                class="serie-toggle"
                :class="{ active: seriesVisibles[s.key], [s.key]: true }"
                @click="toggleSerie(s.key)"
              >
                <span class="dot"></span>{{ s.label }}
              </button>
            </div>
          </div>
          <LineChartFinanciero :puntos="rendimientoPuntos" :series="seriesActivas" />
        </div>
      </div>

      <div class="col-side">
        <!-- Notificaciones -->
        <h2 class="seccion-title">Notificaciones</h2>
        <div class="notif-card">
          <div v-if="!notificaciones.length" class="notif-empty">
            <i class="fa-solid fa-circle-check"></i>
            <span>Todo en orden. No hay alertas pendientes.</span>
          </div>
          <div v-for="(n, i) in notificaciones" :key="i" class="notif-item" :class="'notif-' + n.tipo">
            <i :class="n.icono"></i>
            <div class="notif-body">
              <span class="notif-titulo">{{ n.titulo }}</span>
              <div class="notif-meta">
                <span class="prio-pill" :class="'prio-' + n.prioridad">{{ n.prioridad }}</span>
                <span class="notif-fecha">{{ n.fecha }}</span>
                <router-link v-if="n.link" :to="n.link" class="notif-link">Revisar →</router-link>
              </div>
            </div>
          </div>
        </div>

        <!-- Acciones rápidas -->
        <h2 class="seccion-title">Acciones rápidas</h2>
        <div class="acciones-grid">
          <router-link to="/caja/dashboard" class="accion-chip">
            <i class="fa-solid fa-cash-register"></i> Ir a Caja
          </router-link>
          <router-link to="/personal/empleados" class="accion-chip">
            <i class="fa-solid fa-users"></i> Gestionar Personal
          </router-link>
          <router-link to="/inventario/operaciones" class="accion-chip">
            <i class="fa-solid fa-boxes-stacked"></i> Ver Inventario
          </router-link>
          <router-link to="/personal/pagos" class="accion-chip">
            <i class="fa-solid fa-money-bill-wave"></i> Registrar Pago
          </router-link>
          <router-link to="/personal/solicitudes" class="accion-chip">
            <i class="fa-solid fa-clipboard-list"></i> Revisar Solicitudes
          </router-link>
        </div>

        <!-- Actividad reciente -->
        <h2 class="seccion-title">Actividad reciente</h2>
        <div class="activity-card">
          <div v-if="!actividad.length" class="actividad-empty">
            <i class="fa-solid fa-receipt"></i>
            <span>Sin actividad registrada.</span>
          </div>
          <div v-for="(a, i) in actividad" :key="i" class="activity-item">
            <div class="activity-icon" :class="'act-' + a.tipo">
              <i :class="actividadIconos[a.tipo] || 'fa-solid fa-circle-info'"></i>
            </div>
            <div class="activity-body">
              <span class="activity-user">{{ a.titulo }}</span>
              <span class="activity-accion">{{ a.descripcion }}</span>
            </div>
            <span class="activity-fecha">{{ a.fecha }}</span>
          </div>
          <router-link to="/seguridad/actividad" class="activity-link">Ver actividad de accesos →</router-link>
        </div>
      </div>
    </div>

    <div class="loading-overlay" v-if="loading">
      <i class="fa-solid fa-spinner fa-spin"></i>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import LineChartFinanciero from '../components/charts/LineChartFinanciero.vue'
import api from '../config/axios'

const authStore = useAuthStore()
const loading = ref(true)
const stats = ref({ ventas_mes: 0, egresos_mes: 0, neto_mes: 0 })
const resumenInv = ref({ valor_total: 0 })
const actividad = ref([])
const alertas = ref({
  stock_bajo: 0,
  agotados: 0,
  adelantos_pendientes: 0,
  solicitudes_pendientes: 0,
  pagos_pendientes: 0,
  bloqueos_activos: 0,
  movimientos_hoy: 0
})

const periodos = [
  { key: 'dia', label: 'Día' },
  { key: 'semana', label: 'Semana' },
  { key: 'mes', label: 'Mes' },
  { key: 'anio', label: 'Año' }
]
const series = [
  { key: 'ingresos', label: 'Ingresos' },
  { key: 'egresos', label: 'Egresos' },
  { key: 'ganancia', label: 'Ganancia' }
]
const periodo = ref('dia')
const seriesVisibles = ref({ ingresos: true, egresos: true, ganancia: true })
const rendimientoPuntos = ref([])

const seriesActivas = computed(() => series.filter((s) => seriesVisibles.value[s.key]).map((s) => s.key))

const cambiarPeriodo = (key) => {
  periodo.value = key
  cargarRendimiento()
}

const toggleSerie = (key) => {
  seriesVisibles.value[key] = !seriesVisibles.value[key]
}

const cargarRendimiento = async () => {
  try {
    const res = await api.get(`/rendimiento?periodo=${periodo.value}`)
    if (res.data.success) rendimientoPuntos.value = res.data.data || []
  } catch (err) {
    console.error('Error cargando rendimiento:', err)
    rendimientoPuntos.value = []
  }
}

const nombre = computed(() => authStore.user?.nombre || 'Administrador')
const fechaHoy = computed(() => {
  return new Intl.DateTimeFormat('es-PE', {
    weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'
  }).format(new Date())
})

const formatMoney = (val) => Number(val || 0).toLocaleString('es-PE', { minimumFractionDigits: 2 })

const notificaciones = computed(() => {
  const a = alertas.value
  const items = []
  const hoy = new Intl.DateTimeFormat('es-PE', { day: '2-digit', month: '2-digit' }).format(new Date())
  if (a.adelantos_pendientes > 0) {
    items.push({ tipo: 'warn', icono: 'fa-solid fa-file-invoice-dollar', titulo: `Hay ${a.adelantos_pendientes} adelanto(s) pendientes de revisión`, link: '/personal/adelantos', prioridad: 'Media', fecha: hoy })
  }
  if (a.solicitudes_pendientes > 0) {
    items.push({ tipo: 'warn', icono: 'fa-solid fa-clipboard-list', titulo: `Hay ${a.solicitudes_pendientes} solicitud(es) de insumos pendientes`, link: '/personal/solicitudes', prioridad: 'Media', fecha: hoy })
  }
  if (a.stock_bajo > 0) {
    items.push({ tipo: 'warn', icono: 'fa-solid fa-fill-drip', titulo: `${a.stock_bajo} producto(s) con stock bajo`, link: '/inventario/operaciones?vista=productos', prioridad: 'Media', fecha: hoy })
  }
  if (a.agotados > 0) {
    items.push({ tipo: 'error', icono: 'fa-solid fa-triangle-exclamation', titulo: `${a.agotados} producto(s) agotados`, link: '/inventario/operaciones?vista=productos', prioridad: 'Alta', fecha: hoy })
  }
  if (a.pagos_pendientes > 0) {
    items.push({ tipo: 'warn', icono: 'fa-solid fa-money-bill-wave', titulo: `Hay ${a.pagos_pendientes} pago(s) pendientes`, link: '/personal/pagos', prioridad: 'Media', fecha: hoy })
  }
  if (a.bloqueos_activos > 0) {
    items.push({ tipo: 'error', icono: 'fa-solid fa-shield-halved', titulo: `${a.bloqueos_activos} cuenta(s) bloqueada(s) por seguridad`, link: '/seguridad/monitoreo', prioridad: 'Alta', fecha: hoy })
  }
  if (a.movimientos_hoy > 0) {
    items.push({ tipo: 'info', icono: 'fa-solid fa-cash-register', titulo: `Se registraron ${a.movimientos_hoy} movimiento(s) de caja hoy`, link: '/caja/movimientos', prioridad: 'Baja', fecha: hoy })
  }
  return items
})

const actividadIconos = {
  pago: 'fa-solid fa-money-check-dollar',
  cierre_caja: 'fa-solid fa-cash-register',
  adelanto: 'fa-solid fa-piggy-bank',
  solicitud_insumo: 'fa-solid fa-box-open',
  inversion: 'fa-solid fa-chart-line'
}

const cargar = async () => {
  loading.value = true
  try {
    const [statsRes, alertasRes, invRes, actRes] = await Promise.all([
      api.get('/admin/panel-stats'),
      api.get('/admin/alertas-resumen'),
      api.get('/inventario/resumen'),
      api.get('/admin/actividad-reciente?limit=8')
    ])
    if (statsRes.data.success) stats.value = statsRes.data.data
    if (alertasRes.data.success) alertas.value = alertasRes.data.data
    if (invRes.data.success) resumenInv.value = invRes.data.data
    if (actRes.data.success) actividad.value = actRes.data.data
  } catch (err) {
    console.error('Error cargando panel admin:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  cargar()
  cargarRendimiento()
})
</script>

<style scoped>
.panel-view {
  padding: 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.9rem;
  margin-top: 1rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 0.9rem;
  padding: 1rem 1.1rem;
  background: var(--bg-card);
  border-radius: 14px;
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-soft);
}

.stat-icon {
  width: 44px;
  height: 44px;
  border-radius: 11px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.05rem;
  flex-shrink: 0;
}

.stat-icon.positive { background: rgba(22, 163, 74, 0.1); color: var(--color-verde-fuerte); }
.stat-icon.negative { background: rgba(220, 38, 38, 0.1); color: var(--color-rojo); }
.stat-icon.purple { background: rgba(139, 92, 246, 0.1); color: #8b5cf6; }
.stat-icon.amber { background: rgba(245, 158, 11, 0.12); color: #d97706; }

.stat-content { display: flex; flex-direction: column; }
.stat-label { font-size: 0.72rem; color: var(--text-muted); }
.stat-value { font-size: 1.2rem; font-weight: 700; color: var(--text-main); }

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

.rol-badge {
  background: rgba(255, 122, 0, 0.1);
  color: var(--btn-primary);
}

.fecha-badge {
  background: var(--bg-secondary);
  color: var(--text-muted);
}

.page-hero .hero-left {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.page-hero {
  flex-direction: row;
  justify-content: space-between;
  align-items: flex-start;
}

.acciones-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  margin-top: 1rem;
}

.accion-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.55rem 1rem;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--text-main);
  text-decoration: none;
  transition: all 0.18s ease;
  box-shadow: var(--shadow-soft);
}

.accion-chip i {
  color: var(--btn-primary);
}

.accion-chip:hover {
  border-color: var(--btn-primary);
  color: var(--btn-primary);
  transform: translateY(-1px);
}

.notif-card {
  margin-top: 1rem;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  padding: 0.75rem;
  box-shadow: var(--shadow-soft);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.notif-empty {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.6rem 0.75rem;
  color: var(--color-verde-fuerte);
  font-size: 0.85rem;
}

.notif-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.6rem 0.75rem;
  border-radius: 10px;
  font-size: 0.83rem;
  background: var(--bg-secondary);
}

.notif-item > i {
  margin-top: 0.2rem;
}

.notif-item i {
  font-size: 0.95rem;
  flex-shrink: 0;
}

.notif-item.notif-warn { color: #b45309; background: rgba(245, 158, 11, 0.08); }
.notif-item.notif-error { color: var(--color-rojo); background: rgba(220, 38, 38, 0.06); }
.notif-item.notif-info { color: #2563eb; background: rgba(59, 130, 246, 0.08); }

.notif-titulo {
  color: var(--text-main);
  font-weight: 500;
  margin-right: 0.6rem;
}

.notif-link {
  font-size: 0.75rem;
  font-weight: 600;
  color: inherit;
  text-decoration: none;
}

.notif-body {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  flex: 1;
  min-width: 0;
}

.notif-meta {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  flex-wrap: wrap;
}

.prio-pill {
  font-size: 0.62rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  padding: 0.1rem 0.45rem;
  border-radius: 999px;
}

.prio-Alta { background: rgba(220, 38, 38, 0.14); color: var(--color-rojo); }
.prio-Media { background: rgba(245, 158, 11, 0.16); color: #b45309; }
.prio-Baja { background: rgba(59, 130, 246, 0.12); color: #2563eb; }

.notif-fecha {
  font-size: 0.68rem;
  color: var(--text-muted);
}

.loading-overlay {
  display: flex;
  justify-content: center;
  padding: 2rem;
  color: var(--btn-primary);
  font-size: 1.5rem;
}

.chart-card {
  margin-top: 1rem;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  padding: 1rem;
  box-shadow: var(--shadow-soft);
}

.filtros-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.periodo-tabs,
.serie-toggles {
  display: flex;
  gap: 0.4rem;
  flex-wrap: wrap;
}

.filtro-btn {
  padding: 0.35rem 0.8rem;
  border-radius: 999px;
  border: 1px solid var(--border-color);
  background: var(--bg-secondary);
  color: var(--text-muted);
  font-size: 0.76rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.filtro-btn:hover {
  border-color: var(--btn-primary);
  color: var(--btn-primary);
}

.filtro-btn.active {
  background: var(--btn-primary);
  border-color: var(--btn-primary);
  color: #fff;
}

.serie-toggle {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.35rem 0.8rem;
  border-radius: 999px;
  border: 1px solid var(--border-color);
  background: var(--bg-secondary);
  color: var(--text-muted);
  font-size: 0.76rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.serie-toggle.active {
  border-color: currentColor;
}

.serie-toggle .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
}

.serie-toggle.ingresos { color: #16a34a; }
.serie-toggle.egresos { color: #dc2626; }
.serie-toggle.ganancia { color: #ff7b00; }

.panel-grid {
  display: grid;
  grid-template-columns: 1.6fr 1fr;
  gap: 1.5rem;
  margin-top: 0.25rem;
  align-items: start;
}

.col-main,
.col-side {
  min-width: 0;
}

.activity-card {
  margin-top: 1rem;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  padding: 0.75rem;
  box-shadow: var(--shadow-soft);
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.actividad-empty {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.6rem 0.75rem;
  color: var(--text-muted);
  font-size: 0.85rem;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  padding: 0.55rem 0.75rem;
  border-radius: 10px;
  background: var(--bg-secondary);
  font-size: 0.8rem;
}

.activity-icon {
  width: 32px;
  height: 32px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(59, 130, 246, 0.12);
  color: #3b82f6;
  font-size: 0.8rem;
  flex-shrink: 0;
}

.act-pago { background: rgba(22, 163, 74, 0.12); color: #16a34a; }
.act-cierre_caja { background: rgba(59, 130, 246, 0.12); color: #2563eb; }
.act-adelanto { background: rgba(255, 123, 0, 0.14); color: var(--btn-primary); }
.act-solicitud_insumo { background: rgba(139, 92, 246, 0.12); color: #8b5cf6; }
.act-inversion { background: rgba(6, 182, 212, 0.12); color: #06b6d4; }

.activity-body {
  display: flex;
  flex-direction: column;
  min-width: 0;
  flex: 1;
}

.activity-user {
  font-weight: 600;
  color: var(--text-main);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.activity-accion {
  color: var(--text-muted);
  font-size: 0.75rem;
}

.activity-fecha {
  font-size: 0.7rem;
  color: var(--text-muted);
  white-space: nowrap;
}

.activity-link {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 0.75rem;
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--btn-primary);
  text-decoration: none;
}

.activity-link:hover {
  text-decoration: underline;
}

@media (max-width: 1024px) {
  .panel-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .page-hero {
    flex-direction: column;
    gap: 0.75rem;
  }
}
</style>