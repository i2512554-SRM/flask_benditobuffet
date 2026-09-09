import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('../views/HomeView.vue')
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/LoginView.vue')
  },
  {
    path: '/panel',
    name: 'panel',
    component: () => import('../views/PanelAdminView.vue'),
    meta: { requiresAuth: true, adminOnly: true }
  },
  {
    path: '/cocinero',
    name: 'cocinero',
    component: () => import('../views/CocinaDashboardView.vue'),
    meta: { requiresAuth: true, roles: [3] }
  },
  {
    path: '/cocinero/inventario',
    name: 'cocina-inventario',
    component: () => import('../views/CocinaInventarioView.vue'),
    meta: { requiresAuth: true, roles: [3] }
  },
  {
    path: '/cocinero/solicitudes',
    name: 'cocina-solicitudes',
    component: () => import('../views/CocinaSolicitudesView.vue'),
    meta: { requiresAuth: true, roles: [3] }
  },
  {
    path: '/cocinero/alertas',
    name: 'cocina-alertas',
    component: () => import('../views/CocinaAlertasView.vue'),
    meta: { requiresAuth: true, roles: [3] }
  },
  {
    path: '/trabajador',
    name: 'trabajador',
    component: () => import('../views/TrabajadorDashboardView.vue'),
    meta: { requiresAuth: true, roles: [2, 3, 4] }
  },
  {
    path: '/trabajador/info',
    name: 'trabajador-info',
    component: () => import('../views/TrabajadorInfoView.vue'),
    meta: { requiresAuth: true, roles: [2, 3, 4] }
  },
  {
    path: '/trabajador/turnos',
    name: 'trabajador-turnos',
    component: () => import('../views/TrabajadorTurnosView.vue'),
    meta: { requiresAuth: true, roles: [2, 3, 4] }
  },
  {
    path: '/trabajador/pagos',
    name: 'trabajador-pagos',
    component: () => import('../views/TrabajadorPagosView.vue'),
    meta: { requiresAuth: true, roles: [2, 3, 4] }
  },
  {
    path: '/trabajador/notificaciones',
    name: 'trabajador-notificaciones',
    component: () => import('../views/TrabajadorNotificacionesView.vue'),
    meta: { requiresAuth: true, roles: [2, 3, 4] }
  },
  {
    path: '/perfil',
    name: 'perfil',
    component: () => import('../views/PerfilView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/panel-cajera',
    name: 'panel-cajera',
    component: () => import('../views/PanelCajeraView.vue'),
    meta: { requiresAuth: true, roles: [2] }
  },
  {
    path: '/caja',
    name: 'caja',
    component: () => import('../views/CajaView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/caja/reportes',
    name: 'caja-reportes',
    component: () => import('../views/CajaReportesView.vue'),
    meta: { requiresAuth: true, adminOnly: true }
  },
  {
    path: '/personal',
    name: 'personal',
    component: () => import('../views/ModuloPersonalView.vue'),
    meta: { requiresAuth: true, adminOnly: true }
  },
  {
    path: '/personal/empleados',
    name: 'empleados',
    component: () => import('../views/EmpleadosView.vue'),
    meta: { requiresAuth: true, adminOnly: true }
  },
  {
    path: '/personal/pagos',
    name: 'pagos',
    component: () => import('../views/PagosView.vue'),
    meta: { requiresAuth: true, adminOnly: true }
  },
  {
    path: '/personal/pagos/empleado/:id',
    name: 'pago-detalle',
    component: () => import('../views/DetallePagosView.vue'),
    meta: { requiresAuth: true, adminOnly: true }
  },
  {
    path: '/personal/turnos',
    name: 'turnos',
    component: () => import('../views/TurnosView.vue'),
    meta: { requiresAuth: true, adminOnly: true }
  },
  {
    path: '/personal/adelantos',
    name: 'adelantos',
    component: () => import('../views/AdelantosView.vue'),
    meta: { requiresAuth: true, adminOnly: true }
  },
  {
    path: '/personal/salarios',
    name: 'salarios',
    component: () => import('../views/SalariosView.vue'),
    meta: { requiresAuth: true, adminOnly: true }
  },
  {
    path: '/personal/solicitudes',
    name: 'solicitudes',
    component: () => import('../views/SolicitudesView.vue'),
    meta: { requiresAuth: true, adminOnly: true }
  },
  {
    path: '/inventario',
    name: 'inventario',
    component: () => import('../views/ModuloInventarioView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/inventario/operaciones',
    name: 'inventario-operaciones',
    component: () => import('../views/InventarioView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/inventario/reportes',
    name: 'inventario-reportes',
    component: () => import('../views/InventarioReportesView.vue'),
    meta: { requiresAuth: true, adminOnly: true }
  },
  {
    path: '/seguridad',
    name: 'seguridad',
    component: () => import('../views/ModuloSeguridadView.vue'),
    meta: { requiresAuth: true, adminOnly: true }
  },
  {
    path: '/seguridad/monitoreo',
    name: 'seguridad-monitoreo',
    component: () => import('../views/SeguridadView.vue'),
    meta: { requiresAuth: true, adminOnly: true }
  },
  {
    path: '/seguridad/roles',
    name: 'seguridad-roles',
    component: () => import('../views/RolesView.vue'),
    meta: { requiresAuth: true, adminOnly: true }
  },
  {
    path: '/seguridad/actividad',
    name: 'seguridad-actividad',
    component: () => import('../views/ActividadView.vue'),
    meta: { requiresAuth: true, adminOnly: true }
  },
  {
    path: '/ia',
    name: 'ia',
    component: () => import('../views/IAPredictivaView.vue'),
    meta: { requiresAuth: true, adminOnly: true }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

function homeForRole(rol) {
  if (rol === 1) return '/panel'
  if (rol === 3) return '/cocinero'
  if (rol === 2) return '/panel-cajera'
  if (rol === 4) return '/trabajador'
  return '/'
}

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const rol = authStore.user?.rol
  const home = homeForRole(rol)

  if (!authStore.isAuthenticated) {
    next(to.meta.requiresAuth ? '/login' : undefined)
    return
  }

  if (to.name === 'login') {
    next(home)
    return
  }

  if (to.meta.adminOnly && rol !== 1) {
    next(home)
    return
  }

  if (to.meta.roles && !to.meta.roles.includes(rol)) {
    next(home)
    return
  }

  next()
})

export default router
