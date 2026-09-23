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
    meta: { requiresAuth: true }
  },
  {
    path: '/perfil',
    name: 'perfil',
    component: () => import('../views/PerfilView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/caja',
    name: 'caja',
    component: () => import('../views/CajaView.vue'),
    meta: { requiresAuth: true }
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
    component: () => import('../views/InventarioView.vue'),
    meta: { requiresAuth: true }
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

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.meta.adminOnly && authStore.user?.rol !== 1) {
    next('/panel')
  } else {
    next()
  }
})

export default router
