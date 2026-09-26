<template>
  <div class="panel-view">
    <div class="page-hero">
      <div class="hero-left">
        <h1>¡Hola, {{ nombre }}! 👋</h1>
        <p>Resumen general de Bendito Buffet</p>
        <div class="hero-badges">
          <span class="rol-badge"><i class="fa-solid fa-user-shield"></i> Rol: Administrador</span>
          <span class="fecha-badge"><i class="fa-regular fa-calendar"></i> {{ fechaHoy }}</span>
        </div>
      </div>
      <div class="hero-right">
        <span v-if="estadoAct === 'cargando'" class="estado-actualizar">
          <i class="fa-solid fa-spinner fa-spin"></i> Actualizando información...
        </span>
        <span v-else-if="estadoAct === 'ok'" class="estado-actualizar ok">
          <i class="fa-solid fa-circle-check"></i> Información actualizada correctamente
        </span>
        <button :disabled="$saving || estadoAct === 'cargando'" class="btn btn-outline" @click="cargar">
          <i class="fa-solid fa-arrows-rotate" :class="{ 'fa-spin': estadoAct === 'cargando' }"></i> Actualizar
        </button>
      </div>
    </div>

    <!-- Resumen general -->
    <h2 class="seccion-title">Resumen general</h2>
    <div class="stats-grid">
      <router-link :to="links.caja.reportes" class="stat-card" title="Ver reporte de ventas">
        <div class="stat-icon positive">
          <i class="fa-solid fa-arrow-trend-up"></i>
        </div>
        <div class="stat-content">
          <span class="stat-label">Ventas del mes</span>
          <span class="stat-value">S/. {{ formatMoney(stats.ventas_mes) }}</span>
        </div>
        <i class="fa-solid fa-chevron-right stat-arrow"></i>
      </router-link>
      <router-link :to="{ path: links.caja.movimientos, query: { filtro: 'egresos' } }" class="stat-card" title="Ver egresos del mes">
        <div class="stat-icon negative">
          <i class="fa-solid fa-arrow-trend-down"></i>
        </div>
        <div class="stat-content">
          <span class="stat-label">Egresos del mes</span>
          <span class="stat-value">S/. {{ formatMoney(stats.egresos_mes) }}</span>
        </div>
        <i class="fa-solid fa-chevron-right stat-arrow"></i>
      </router-link>
      <router-link :to="links.caja.reportes" class="stat-card" title="Ver reporte financiero del mes">
        <div class="stat-icon" :class="stats.neto_mes >= 0 ? 'positive' : 'negative'">
          <i class="fa-solid fa-scale-balanced"></i>
        </div>
        <div class="stat-content">
          <span class="stat-label">Balance del mes</span>
          <span class="stat-value">S/. {{ formatMoney(stats.neto_mes) }}</span>
        </div>
        <i class="fa-solid fa-chevron-right stat-arrow"></i>
      </router-link>
      <router-link :to="links.inventario.operaciones" class="stat-card" title="Ver inventario">
        <div class="stat-icon purple">
          <i class="fa-solid fa-boxes-stacked"></i>
        </div>
        <div class="stat-content">
          <span class="stat-label">Valor del inventario</span>
          <span class="stat-value">S/. {{ formatMoney(resumenInv.valor_total) }}</span>
        </div>
        <i class="fa-solid fa-chevron-right stat-arrow"></i>
      </router-link>
      <router-link :to="links.personal.solicitudes" class="stat-card" title="Revisar solicitudes y tareas pendientes">
        <div class="stat-icon amber">
          <i class="fa-solid fa-inbox"></i>
        </div>
        <div class="stat-content">
          <span class="stat-label">Pendientes</span>
          <span class="stat-value">{{ pendientes }}</span>
        </div>
        <i class="fa-solid fa-chevron-right stat-arrow"></i>
      </router-link>
      <router-link :to="links.panel.kpis" class="stat-card" title="Ver indicadores clave del negocio">
        <div class="stat-icon cyan">
          <i class="fa-solid fa-chart-simple"></i>
        </div>
        <div class="stat-content">
          <span class="stat-label">Indicadores</span>
          <span class="stat-value">Ver panel</span>
        </div>
        <i class="fa-solid fa-chevron-right stat-arrow"></i>
      </router-link>
    </div>

    <div class="panel-grid">
      <div class="panel-col">
        <!-- Ventas recientes -->
        <h2 class="seccion-title">Ventas recientes</h2>
        <div class="chart-card">
          <div class="filtros-bar">
            <div class="periodo-tabs">
              <button
                :disabled="$saving"
                v-for="p in periodos"
                :key="p.key"
                class="filtro-btn"
                :class="{ active: periodo === p.key }"
                @click="cambiarPeriodo(p.key)"
              >
                {{ p.label }}
              </button>
            </div>
            <router-link :to="links.caja.reportes" class="btn btn-outline btn-sm">Ver reporte completo <i class="fa-solid fa-arrow-right"></i></router-link>
          </div>
          <LineChartFinanciero :puntos="rendimientoPuntos" :series="['ingresos']" />
        </div>

        <!-- Personal -->
        <h2 class="seccion-title">Personal</h2>
        <div class="info-card">
          <div class="sub-grid">
            <div class="sub-stat">
              <span class="sub-stat-icon ic-green"><i class="fa-solid fa-users"></i></span>
              <div class="sub-stat-body">
                <span class="stat-label">Trabajadores activos</span>
                <span class="stat-value">{{ alertas.empleados_activos }}</span>
              </div>
            </div>
            <div class="sub-stat">
              <span class="sub-stat-icon ic-red"><i class="fa-solid fa-money-bill-wave"></i></span>
              <div class="sub-stat-body">
                <span class="stat-label">Pagos pendientes</span>
                <span class="stat-value">{{ alertas.pagos_pendientes }}</span>
              </div>
            </div>
            <div class="sub-stat">
              <span class="sub-stat-icon ic-orange"><i class="fa-solid fa-piggy-bank"></i></span>
              <div class="sub-stat-body">
                <span class="stat-label">Adelantos pendientes</span>
                <span class="stat-value">{{ alertas.adelantos_pendientes }}</span>
              </div>
            </div>
            <div class="sub-stat">
              <span class="sub-stat-icon ic-blue"><i class="fa-solid fa-file-invoice-dollar"></i></span>
              <div class="sub-stat-body">
                <span class="stat-label">Pagos este mes</span>
                <span class="stat-value">{{ alertas.pagos_mes }}</span>
              </div>
            </div>
          </div>
          <div class="card-footer">
            <router-link :to="links.personal.empleados" class="btn btn-outline btn-sm">Gestionar personal <i class="fa-solid fa-arrow-right"></i></router-link>
          </div>
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
              <div class="activity-top">
                <span class="act-tipo">{{ tipoLabel(a.tipo) }}</span>
                <router-link :to="destinoActividad(a.tipo)" class="activity-user">{{ a.titulo }}</router-link>
              </div>
              <span class="activity-accion">{{ a.descripcion }}</span>
            </div>
            <span class="activity-fecha">{{ formatFecha(a.fecha) }}</span>
          </div>
        </div>
      </div>

      <div class="panel-col">
        <!-- Estado del inventario -->
        <h2 class="seccion-title">Estado del inventario</h2>
        <div class="info-card">
          <div class="sub-grid">
            <div class="sub-stat">
              <span class="sub-stat-icon ic-purple"><i class="fa-solid fa-box-open"></i></span>
              <div class="sub-stat-body">
                <span class="stat-label">Total productos</span>
                <span class="stat-value">{{ resumenInv.articulos_registrados }}</span>
              </div>
            </div>
            <div class="sub-stat">
              <span class="sub-stat-icon ic-cyan"><i class="fa-solid fa-circle-check"></i></span>
              <div class="sub-stat-body">
                <span class="stat-label">Disponibles</span>
                <span class="stat-value">{{ disponibles }}</span>
              </div>
            </div>
            <router-link :to="{ path: links.inventario.operaciones, query: { vista: 'productos', stock: 'bajo' } }" class="sub-stat clickable" title="Ver productos con stock bajo">
              <span class="sub-stat-icon ic-amber"><i class="fa-solid fa-fill-drip"></i></span>
              <div class="sub-stat-body">
                <span class="stat-label">Stock bajo</span>
                <span class="stat-value">{{ alertas.stock_bajo }}</span>
              </div>
            </router-link>
            <router-link :to="{ path: links.inventario.operaciones, query: { vista: 'productos', stock: 'agotados' } }" class="sub-stat clickable" title="Ver productos agotados">
              <span class="sub-stat-icon ic-red"><i class="fa-solid fa-triangle-exclamation"></i></span>
              <div class="sub-stat-body">
                <span class="stat-label">Agotados</span>
                <span class="stat-value">{{ alertas.agotados }}</span>
              </div>
            </router-link>
          </div>
          <div class="card-footer">
            <router-link :to="links.inventario.operaciones" class="btn btn-outline btn-sm">Ver inventario <i class="fa-solid fa-arrow-right"></i></router-link>
          </div>
        </div>

        <!-- Inversiones -->
        <h2 class="seccion-title">Inversiones</h2>
        <div class="info-card">
          <div class="sub-grid">
            <div class="sub-stat">
              <span class="sub-stat-icon ic-green"><i class="fa-solid fa-chart-line"></i></span>
              <div class="sub-stat-body">
                <span class="stat-label">Invertido del mes</span>
                <span class="stat-value">S/. {{ formatMoney(resumenInv.inversiones_mes) }}</span>
              </div>
            </div>
            <div class="sub-stat">
              <span class="sub-stat-icon ic-blue"><i class="fa-solid fa-layer-group"></i></span>
              <div class="sub-stat-body">
                <span class="stat-label">Inversiones del mes</span>
                <span class="stat-value">{{ resumenInv.inversiones_mes_cantidad }}</span>
              </div>
            </div>
            <div class="sub-stat ultima-inv">
              <span class="sub-stat-icon ic-orange"><i class="fa-solid fa-clock-rotate-left"></i></span>
              <div class="sub-stat-body">
                <span class="stat-label">Última inversión</span>
                <span v-if="ultimaInv" class="ultima-line">
                  {{ ultimaInv.descripcion || 'Inversión registrada' }}
                  <strong>S/. {{ formatMoney(ultimaInv.monto) }}</strong>
                  <em v-if="ultimaInv.fecha">{{ soloFecha(ultimaInv.fecha) }}</em>
                </span>
                <span v-else class="text-muted">Sin inversiones registradas.</span>
              </div>
            </div>
          </div>
          <div class="card-footer">
            <router-link :to="{ path: links.inventario.operaciones, query: { vista: 'compras' } }" class="btn btn-outline btn-sm">Ver inversiones <i class="fa-solid fa-arrow-right"></i></router-link>
          </div>
        </div>

        <!-- Notificaciones -->
        <h2 class="seccion-title">Notificaciones</h2>
        <div class="notif-card">
          <div v-if="!notificaciones.length" class="notif-empty">
            <i class="fa-solid fa-circle-check"></i>
            <span>Todo en orden. No hay alertas importantes.</span>
          </div>
          <div v-for="(n, i) in notificaciones" :key="i" class="notif-item" :class="'notif-' + n.tipo">
            <i :class="n.icono"></i>
            <div class="notif-body">
              <span class="notif-titulo">{{ n.titulo }}</span>
              <div class="notif-meta">
                <router-link :to="n.link" class="notif-link">Revisar</router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Acciones rápidas -->
    <h2 class="seccion-title">Acciones rápidas</h2>
    <div class="acciones-grid">
      <router-link :to="links.caja.control" class="accion-chip">
        <i class="fa-solid fa-cash-register"></i> Ir a Caja
      </router-link>
      <router-link :to="links.personal.empleados" class="accion-chip">
        <i class="fa-solid fa-users"></i> Gestionar Personal
      </router-link>
      <router-link :to="links.inventario.operaciones" class="accion-chip">
        <i class="fa-solid fa-boxes-stacked"></i> Ver Inventario
      </router-link>
      <router-link :to="{ path: links.personal.pagos, query: { accion: 'nuevo' } }" class="accion-chip">
        <i class="fa-solid fa-money-bill-wave"></i> Registrar Pago
      </router-link>
      <router-link :to="links.personal.solicitudes" class="accion-chip">
        <i class="fa-solid fa-clipboard-list"></i> Revisar Solicitudes
      </router-link>
      <router-link :to="{ path: links.inventario.operaciones, query: { vista: 'compras', accion: 'nueva-compra' } }" class="accion-chip">
        <i class="fa-solid fa-chart-line"></i> Registrar Inversión
      </router-link>
    </div>

    <div class="loading-overlay" v-if="loading">
      <i class="fa-solid fa-spinner fa-spin"></i>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { links } from '../../router/links'
import LineChartFinanciero from '../../components/charts/LineChartFinanciero.vue'
import { formatFecha, soloFecha } from '../../utils/format'
import api from '../../config/axios'

const authStore = useAuthStore()
const loading = ref(true)
const estadoAct = ref('')
let timeoutId = null
const stats = ref({ ventas_mes: 0, egresos_mes: 0, neto_mes: 0 })
const resumenInv = ref({ valor_total: 0, inversiones_mes: 0, articulos_registrados: 0, inversiones_mes_cantidad: 0, ultima_inversion: null })
const alertas = ref({
  stock_bajo: 0,
  agotados: 0,
  adelantos_pendientes: 0,
  solicitudes_pendientes: 0,
  pagos_pendientes: 0,
  empleados_activos: 0,
  pagos_mes: 0,
  caja_pendiente_cierre: false
})
const actividad = ref([])
const rendimientoPuntos = ref([])

const periodos = [
  { key: 'semana', label: 'Semana' },
  { key: 'mes', label: 'Mes' }
]
const periodo = ref('semana')

const ultimaInv = computed(() => resumenInv.value.ultima_inversion || null)
const pendientes = computed(() => alertas.value.adelantos_pendientes + alertas.value.solicitudes_pendientes)
const disponibles = computed(() =>
  Math.max(0, Number(resumenInv.value.articulos_registrados || 0) - Number(alertas.value.stock_bajo || 0) - Number(alertas.value.agotados || 0))
)

const cambiarPeriodo = (key) => {
  periodo.value = key
  cargarRendimiento()
}

const cargarRendimiento = async () => {
  try {
    const res = await api.get('/rendimiento', { params: { periodo: periodo.value } })
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
  if (a.adelantos_pendientes > 0) {
    items.push({ tipo: 'warn', icono: 'fa-solid fa-file-invoice-dollar', titulo: `${a.adelantos_pendientes} adelanto(s) pendiente(s) de revisión`, link: links.personal.adelantos })
  }
  if (a.stock_bajo > 0) {
    items.push({ tipo: 'warn', icono: 'fa-solid fa-fill-drip', titulo: `${a.stock_bajo} producto(s) con stock bajo`, link: `${links.inventario.productoStock}&stock=bajo` })
  }
  if (a.agotados > 0) {
    items.push({ tipo: 'error', icono: 'fa-solid fa-triangle-exclamation', titulo: `${a.agotados} producto(s) agotados`, link: `${links.inventario.productoStock}&stock=agotados` })
  }
  if (a.caja_pendiente_cierre) {
    items.push({ tipo: 'info', icono: 'fa-solid fa-cash-register', titulo: 'Caja abierta pendiente de cerrar', link: links.caja.control })
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

const tipoLabel = (tipo) => ({
  pago: 'Pago',
  cierre_caja: 'Caja',
  adelanto: 'Adelanto',
  solicitud_insumo: 'Solicitud',
  inversion: 'Inversión'
}[tipo] || 'Registro')

const destinoActividad = (tipo) => ({
  pago: links.personal.pagos,
  cierre_caja: links.caja.historial,
  adelanto: links.personal.solicitudes,
  solicitud_insumo: links.inventario.productoStock,
  inversion: links.inventario.inversiones
}[tipo] || links.panel.admin)

const cargar = async () => {
  if (estadoAct.value === 'cargando') return
  loading.value = true
  estadoAct.value = 'cargando'
  if (timeoutId) clearTimeout(timeoutId)
  try {
    const [statsRes, alertasRes, invRes, actRes] = await Promise.all([
      api.get('/admin/panel-stats'),
      api.get('/admin/alertas-resumen'),
      api.get('/inventario/resumen'),
      api.get('/admin/actividad-reciente?limit=7')
    ])
    if (statsRes.data.success) stats.value = statsRes.data.data
    if (alertasRes.data.success) alertas.value = alertasRes.data.data
    if (invRes.data.success) resumenInv.value = invRes.data.data
    if (actRes.data.success) actividad.value = actRes.data.data
    await cargarRendimiento()
    estadoAct.value = 'ok'
    timeoutId = setTimeout(() => { estadoAct.value = '' }, 3000)
  } catch (err) {
    console.error('Error cargando panel admin:', err)
    estadoAct.value = ''
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  cargar()
})
</script>

<style scoped>
.panel-view {
  padding: 0;
}

.page-hero {
  flex-direction: row;
  justify-content: space-between;
  align-items: flex-start;
}

.hero-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.5rem;
}

.estado-actualizar {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--text-muted);
}

.estado-actualizar.ok {
  color: var(--color-verde-fuerte);
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
  color: var(--text-main);
  text-decoration: none;
  transition: border-color 0.18s ease, transform 0.18s ease;
  cursor: pointer;
}

.stat-card:hover {
  border-color: var(--btn-primary);
  transform: translateY(-1px);
}

.stat-arrow {
  margin-left: auto;
  font-size: 0.7rem;
  color: var(--text-muted);
  opacity: 0;
  transition: opacity 0.18s ease;
}

.stat-card:hover .stat-arrow {
  opacity: 1;
  color: var(--btn-primary);
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
.stat-icon.cyan { background: rgba(6, 182, 212, 0.12); color: #0e7490; }

.stat-content { display: flex; flex-direction: column; min-width: 0; }
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

.panel-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-top: 0.25rem;
  align-items: start;
}

.panel-col {
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.panel-col .seccion-title {
  margin-top: 1.5rem;
}

.chart-card,
.info-card {
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

.periodo-tabs {
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

.sub-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.6rem;
}

.sub-stat {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.7rem 0.75rem;
  background: var(--bg-secondary);
  border: 1px solid transparent;
  border-radius: 10px;
  text-decoration: none;
  color: var(--text-main);
}

.sub-stat.clickable {
  cursor: pointer;
  transition: border-color 0.18s ease, transform 0.18s ease;
}

.sub-stat.clickable:hover {
  border-color: var(--btn-primary);
  transform: translateY(-1px);
}

.ultima-inv {
  grid-column: 1 / -1;
}

.sub-stat-icon {
  width: 34px;
  height: 34px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  flex-shrink: 0;
}

.sub-stat-icon.ic-green { background: rgba(22, 163, 74, 0.1); color: #16a34a; }
.sub-stat-icon.ic-red { background: rgba(220, 38, 38, 0.1); color: #dc2626; }
.sub-stat-icon.ic-orange { background: rgba(255, 123, 0, 0.12); color: var(--btn-primary); }
.sub-stat-icon.ic-blue { background: rgba(59, 130, 246, 0.12); color: #3b82f6; }
.sub-stat-icon.ic-purple { background: rgba(139, 92, 246, 0.12); color: #8b5cf6; }
.sub-stat-icon.ic-cyan { background: rgba(6, 182, 212, 0.12); color: #06b6d4; }
.sub-stat-icon.ic-amber { background: rgba(245, 158, 11, 0.14); color: #d97706; }

.sub-stat-body {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.sub-stat .stat-value {
  font-size: 1.05rem;
}

.ultima-line {
  font-size: 0.8rem;
  color: var(--text-main);
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.ultima-line strong {
  font-weight: 700;
}

.ultima-line em {
  color: var(--text-muted);
  font-style: normal;
  font-size: 0.72rem;
}

.card-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 0.75rem;
}

.btn-sm {
  padding: 0.45rem 0.9rem;
  font-size: 0.8rem;
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
  font-size: 0.95rem;
  flex-shrink: 0;
}

.notif-item.notif-warn { color: #b45309; background: rgba(245, 158, 11, 0.08); }
.notif-item.notif-error { color: var(--color-rojo); background: rgba(220, 38, 38, 0.06); }
.notif-item.notif-info { color: #2563eb; background: rgba(59, 130, 246, 0.08); }

.notif-titulo {
  color: var(--text-main);
  font-weight: 500;
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

.notif-link {
  display: inline-flex;
  align-items: center;
  font-size: 0.72rem;
  font-weight: 700;
  color: inherit;
  background: rgba(255, 255, 255, 0.55);
  border: 1px solid currentColor;
  border-radius: 999px;
  padding: 0.18rem 0.7rem;
  text-decoration: none;
  transition: all 0.15s ease;
  align-self: flex-start;
}

.notif-link:hover {
  background: currentColor;
  color: #fff;
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

.activity-top {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 0;
}

.act-tipo {
  font-size: 0.62rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-muted);
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 999px;
  padding: 0.1rem 0.45rem;
  flex-shrink: 0;
}

.activity-user {
  font-weight: 600;
  color: var(--text-main);
  text-decoration: none;
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

.loading-overlay {
  display: flex;
  justify-content: center;
  padding: 2rem;
  color: var(--btn-primary);
  font-size: 1.5rem;
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

  .hero-right {
    align-items: flex-start;
  }
}

@media (max-width: 520px) {
  .sub-grid {
    grid-template-columns: 1fr;
  }

  .ultima-inv {
    grid-column: auto;
  }
}
</style>
