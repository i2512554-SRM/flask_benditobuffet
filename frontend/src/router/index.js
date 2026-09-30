import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { links, homeForRole } from './links'
import { ROLES, ROLES_CAJA, ROLES_INVENTARIO, ROLES_TRABAJADOR } from '../config/roles'

const routes = [
  {
    path: links.home,
    name: 'home',
    component: () => import('../views/auth/HomeView.vue')
  },
  {
    path: links.login,
    name: 'login',
    component: () => import('../views/auth/LoginView.vue')
  },
  {
    path: links.panel.admin,
    name: 'panel',
    component: () => import('../views/panel/PanelAdminView.vue'),
    meta: { requiresAuth: true, adminOnly: true }
  },
  {
    path: links.panel.kpis,
    name: 'indicadores',
    component: () => import('../views/panel/IndicadoresView.vue'),
    meta: { requiresAuth: true, adminOnly: true }
  },
  {
    path: links.panel.cocinero,
    name: 'cocinero',
    component: () => import('../views/cocina/CocinaDashboardView.vue'),
    meta: { requiresAuth: true, roles: [ROLES.COCINA] }
  },
  {
    path: links.cocina.inventarioDetalle,
    name: 'cocina-inventario',
    component: () => import('../views/cocina/CocinaInventarioView.vue'),
    meta: { requiresAuth: true, roles: [ROLES.COCINA] }
  },
  {
    path: links.cocina.solicitudes,
    name: 'cocina-solicitudes',
    component: () => import('../views/cocina/CocinaSolicitudesView.vue'),
    meta: { requiresAuth: true, roles: [ROLES.COCINA] }
  },
  {
    path: links.cocina.alertas,
    name: 'cocina-alertas',
    component: () => import('../views/cocina/CocinaAlertasView.vue'),
    meta: { requiresAuth: true, roles: [ROLES.COCINA] }
  },
  {
    path: links.trabajador.dashboard,
    name: 'trabajador',
    component: () => import('../views/trabajador/TrabajadorDashboardView.vue'),
    meta: { requiresAuth: true, roles: ROLES_TRABAJADOR }
  },
  {
    path: links.trabajador.info,
    name: 'trabajador-info',
    component: () => import('../views/trabajador/TrabajadorInfoView.vue'),
    meta: { requiresAuth: true, roles: ROLES_TRABAJADOR }
  },
  {
    path: links.trabajador.turnos,
    name: 'trabajador-turnos',
    component: () => import('../views/trabajador/TrabajadorTurnosView.vue'),
    meta: { requiresAuth: true, roles: ROLES_TRABAJADOR }
  },
  {
    path: links.trabajador.pagos,
    name: 'trabajador-pagos',
    component: () => import('../views/trabajador/TrabajadorPagosView.vue'),
    meta: { requiresAuth: true, roles: ROLES_TRABAJADOR }
  },
  {
    path: links.trabajador.notificaciones,
    name: 'trabajador-notificaciones',
    component: () => import('../views/trabajador/TrabajadorNotificacionesView.vue'),
    meta: { requiresAuth: true, roles: ROLES_TRABAJADOR }
  },
  {
    path: links.perfil,
    name: 'perfil',
    component: () => import('../views/PerfilView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: links.panel.cajera,
    name: 'panel-cajera',
    component: () => import('../views/cajera/PanelCajeraView.vue'),
    meta: { requiresAuth: true, roles: [ROLES.CAJERA] }
  },
  {
    path: links.caja.control,
    name: 'caja',
    component: () => import('../views/caja/CajaControlView.vue'),
    meta: { requiresAuth: true, roles: ROLES_CAJA }
  },
  {
    path: links.caja.resumen,
    name: 'caja-resumen',
    component: () => import('../views/caja/CajaResumenView.vue'),
    meta: { requiresAuth: true, roles: ROLES_CAJA }
  },
  {
    path: links.caja.movimientos,
    name: 'caja-movimientos',
    component: () => import('../views/caja/CajaMovimientosView.vue'),
    meta: { requiresAuth: true, roles: ROLES_CAJA }
  },
  {
    path: links.caja.historial,
    name: 'caja-historial',
    component: () => import('../views/caja/CajaHistorialView.vue'),
    meta: { requiresAuth: true, roles: ROLES_CAJA }
  },
  {
    path: links.caja.reportes,
    name: 'caja-reportes',
    component: () => import('../views/caja/CajaReportesView.vue'),
    meta: { requiresAuth: true, roles: ROLES_CAJA }
  },
  {
    path: links.personal.modulo,
    name: 'personal',
    component: () => import('../views/personal/ModuloPersonalView.vue'),
    meta: { requiresAuth: true, adminOnly: true }
  },
  {
    path: links.personal.empleados,
    name: 'empleados',
    component: () => import('../views/personal/EmpleadosView.vue'),
    meta: { requiresAuth: true, adminOnly: true }
  },
  {
    path: links.personal.pagos,
    name: 'pagos',
    component: () => import('../views/personal/PagosView.vue'),
    meta: { requiresAuth: true, adminOnly: true }
  },
  {
    path: links.personal.pagoDetalle(':id'),
    name: 'pago-detalle',
    component: () => import('../views/personal/DetallePagosView.vue'),
    meta: { requiresAuth: true, adminOnly: true }
  },
  {
    path: links.personal.turnos,
    name: 'turnos',
    component: () => import('../views/personal/TurnosView.vue'),
    meta: { requiresAuth: true, adminOnly: true }
  },
  {
    path: links.personal.adelantos,
    name: 'adelantos',
    component: () => import('../views/personal/AdelantosView.vue'),
    meta: { requiresAuth: true, adminOnly: true }
  },
  {
    path: links.personal.salarios,
    name: 'salarios',
    component: () => import('../views/personal/SalariosView.vue'),
    meta: { requiresAuth: true, adminOnly: true }
  },
  {
    path: links.personal.solicitudes,
    name: 'solicitudes',
    component: () => import('../views/personal/SolicitudesView.vue'),
    meta: { requiresAuth: true, adminOnly: true }
  },
  {
    path: links.inventario.modulo,
    name: 'inventario',
    component: () => import('../views/inventario/ModuloInventarioView.vue'),
    meta: { requiresAuth: true, roles: ROLES_INVENTARIO }
  },
  {
    path: links.inventario.operaciones,
    name: 'inventario-operaciones',
    component: () => import('../views/inventario/InventarioOperacionesView.vue'),
    meta: { requiresAuth: true, roles: ROLES_INVENTARIO }
  },
  {
    path: links.inventario.reportes,
    name: 'inventario-reportes',
    component: () => import('../views/inventario/InventarioReportesView.vue'),
    meta: { requiresAuth: true, roles: ROLES_INVENTARIO }
  },
  {
    path: links.seguridad.modulo,
    name: 'seguridad',
    component: () => import('../views/seguridad/ModuloSeguridadView.vue'),
    meta: { requiresAuth: true, adminOnly: true }
  },
  {
    path: links.seguridad.monitoreo,
    name: 'seguridad-monitoreo',
    component: () => import('../views/seguridad/MonitoreoView.vue'),
    meta: { requiresAuth: true, adminOnly: true }
  },
  {
    path: links.seguridad.roles,
    name: 'seguridad-roles',
    component: () => import('../views/seguridad/RolesView.vue'),
    meta: { requiresAuth: true, adminOnly: true }
  },
  {
    path: links.seguridad.actividad,
    name: 'seguridad-actividad',
    component: () => import('../views/seguridad/ActividadView.vue'),
    meta: { requiresAuth: true, adminOnly: true }
  },
  {
    path: links.ia,
    name: 'ia',
    component: () => import('../views/IAPredictivaView.vue'),
    meta: { requiresAuth: true, adminOnly: true }
  },
  {
    path: links.notFound,
    redirect: links.home
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to) => {
  const authStore = useAuthStore()

  if (authStore.token && !authStore.sessionChecked) {
    const ok = await authStore.checkSession()
    if (!ok && to.meta.requiresAuth) return { path: links.login }
  }

  const rol = authStore.user?.rol
  const home = homeForRole(rol)

  if (!authStore.isAuthenticated) {
    if (to.meta.requiresAuth) return { path: links.login }
    return true
  }

  if (to.name === 'login') return { path: home }

  if (to.meta.adminOnly && rol !== ROLES.ADMIN) return { path: home }
  if (to.meta.roles && !to.meta.roles.includes(rol)) return { path: home }

  return true
})

export default router
