import { ROLES } from '../config/roles'

export const links = {
  home: '/',
  login: '/login',
  perfil: '/perfil',
  ia: '/ia',
  notFound: '/:pathMatch(.*)*',

  panel: {
    admin: '/panel',
    kpis: '/panel/indicadores',
    cajera: '/panel-cajera',
    cocinero: '/cocinero',
    trabajador: '/trabajador'
  },

  caja: {
    control: '/caja',
    resumen: '/caja/resumen',
    movimientos: '/caja/movimientos',
    historial: '/caja/historial',
    reportes: '/caja/reportes'
  },

  personal: {
    modulo: '/personal',
    empleados: '/personal/empleados',
    pagos: '/personal/pagos',
    pagoDetalle: (id) => `/personal/pagos/empleado/${id}`,
    turnos: '/personal/turnos',
    adelantos: '/personal/adelantos',
    salarios: '/personal/salarios',
    solicitudes: '/personal/solicitudes'
  },

  inventario: {
    modulo: '/inventario',
    operaciones: '/inventario/operaciones',
    productoStock: '/inventario/operaciones?vista=productos',
    entrada: '/inventario/operaciones?vista=productos&accion=entrada',
    compras: '/inventario/operaciones?vista=compras',
    inversiones: '/inventario/operaciones?vista=inversiones',
    nuevo: '/inventario/operaciones?accion=nuevo',
    movimientosHistorico: '/inventario/operaciones?vista=movimientos',
    reportes: '/inventario/reportes'
  },

  seguridad: {
    modulo: '/seguridad',
    monitoreo: '/seguridad/monitoreo',
    roles: '/seguridad/roles',
    actividad: '/seguridad/actividad'
  },

  cocina: {
    dashboard: '/cocinero',
    inventario: '/inventario',
    inventarioDetalle: '/cocinero/inventario',
    solicitudes: '/cocinero/solicitudes',
    alertas: '/cocinero/alertas'
  },

  trabajador: {
    dashboard: '/trabajador',
    info: '/trabajador/info',
    turnos: '/trabajador/turnos',
    pagos: '/trabajador/pagos',
    pagosAdelantos: '/trabajador/pagos?vista=adelantos',
    notificaciones: '/trabajador/notificaciones'
  }
}

export const homeForRole = (rol) => {
  if (rol === ROLES.ADMIN) return links.panel.admin
  if (rol === ROLES.CAJERA) return links.panel.cajera
  if (rol === ROLES.COCINA) return links.panel.cocinero
  if (rol === ROLES.TRABAJADOR) return links.panel.trabajador
  return links.home
}
