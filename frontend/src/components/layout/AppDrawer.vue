<template>
  <div v-if="open" class="drawer-root">
    <div class="drawer-backdrop" @click="emit('close')"></div>
    <aside class="app-drawer">
      <div class="drawer-header">
        <img :src="logoSrc" alt="Logo" class="drawer-logo" />
        <div>
          <h2>Bendito Buffet</h2>
          <span class="drawer-subtitle">{{ subtitle }}</span>
        </div>
      </div>

      <nav class="drawer-nav">
        <template v-for="entry in menu" :key="entry.id">
          <!-- Ítem directo (no plegable) -->
          <router-link
            v-if="entry.item"
            :to="entry.item.to"
            class="drawer-item main-item"
            :class="{ active: isExact(entry.item.to) }"
            @click="emit('close')"
          >
            <span class="nav-tick"></span>
            <span class="item-icon-shell" :class="entry.item.iconCls || 'ic-orange'">
              <i :class="entry.item.icon"></i>
            </span>
            <span class="item-label">{{ entry.item.label }}</span>
            <span v-if="chip(entry.item.chip)" class="menu-chip" :class="'chip-' + chipTone(entry.item.chip)">
              {{ chip(entry.item.chip) }}
            </span>
          </router-link>

          <!-- Categoría desplegable -->
          <template v-else>
            <button
              class="drawer-cat"
              :class="{ 'cat-open': abiertas[entry.id], 'cat-active': isSectionActive(entry) }"
              @click="toggleCat(entry.id)"
            >
              <span class="cat-arrow" :class="{ open: abiertas[entry.id] }">▸</span>
              <span class="item-icon-shell" :class="entry.iconCls">
                <i :class="entry.icon"></i>
              </span>
              <span class="cat-titulo">{{ entry.label }}</span>
              <span class="cat-badge">{{ entry.children.length }}</span>
            </button>

            <transition-group v-if="abiertas[entry.id]" tag="div" name="subcat" class="drawer-subcat">
              <router-link
                v-for="(child, idx) in entry.children"
                :key="child.to"
                :to="child.to"
                class="drawer-item sub-item"
                :class="{ active: isExact(child.to) }"
                :style="{ transitionDelay: idx * 30 + 'ms' }"
                @click="emit('close')"
              >
                <span class="sub-indent" :style="{ paddingLeft: (11 + 14) + 'px' }">
                  <i :class="child.icon"></i>
                </span>
                <span class="item-label">{{ child.label }}</span>
                <span v-if="chip(child.chip)" class="menu-chip" :class="'chip-' + chipTone(child.chip)">
                  {{ chip(child.chip) }}
                </span>
              </router-link>
            </transition-group>
          </template>
        </template>
      </nav>

      <div class="drawer-footer">
        <button class="drawer-logout" @click="confirmarCierre">
          <i class="fa-solid fa-right-from-bracket"></i>
          <span>Cerrar sesión</span>
        </button>
      </div>
    </aside>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { useLogout } from '../../composables/useLogout'
import api from '../../config/axios'
import logoSrc from '../../assets/logo.png'

const props = defineProps({
  open: { type: Boolean, default: false }
})
const emit = defineEmits(['close'])

const { confirmarCierre } = useLogout()
const authStore = useAuthStore()
const route = useRoute()

const rol = computed(() => authStore.user?.rol)
const subtitle = computed(() => {
  const r = rol.value
  if (r === 1) return 'Panel Administrativo'
  if (r === 3) return 'Área de Cocina'
  if (r === 2) return 'Área de Caja'
  return 'Área del Colaborador'
})

const areaItems = [
  { to: '/trabajador/info', icon: 'fa-solid fa-id-card', label: 'Mi Información' },
  { to: '/trabajador/turnos', icon: 'fa-solid fa-calendar-days', label: 'Mis Turnos' },
  { to: '/trabajador/pagos', icon: 'fa-solid fa-money-check-dollar', label: 'Mis Pagos' },
  { to: '/trabajador/notificaciones', icon: 'fa-solid fa-bell', label: 'Notificaciones' }
]

const MENU_POR_ROL = {
  1: [
    { id: 'principal', item: { to: '/panel', label: 'Panel Principal', icon: 'fa-solid fa-gauge-high', iconCls: 'ic-orange' } },
    {
      id: 'caja',
      label: 'Caja',
      icon: 'fa-solid fa-cash-register',
      iconCls: 'ic-green',
      children: [
        { to: '/caja/dashboard', icon: 'fa-solid fa-chart-pie', label: 'Dashboard de Caja' },
        { to: '/caja', icon: 'fa-solid fa-cash-register', label: 'Control de Caja', chip: 'caja-control' },
        { to: '/caja/movimientos', icon: 'fa-solid fa-arrows-rotate', label: 'Movimientos' },
        { to: '/caja/historial', icon: 'fa-solid fa-clock-rotate-left', label: 'Historial de Cierres' },
        { to: '/caja/reportes', icon: 'fa-solid fa-chart-line', label: 'Reportes Financieros' }
      ]
    },
    {
      id: 'personal',
      label: 'Personal',
      icon: 'fa-solid fa-users',
      iconCls: 'ic-blue',
      children: [
        { to: '/personal', icon: 'fa-solid fa-users', label: 'Gestión del Personal' },
        { to: '/personal/empleados', icon: 'fa-solid fa-id-badge', label: 'Empleados' },
        { to: '/personal/pagos', icon: 'fa-solid fa-money-check-dollar', label: 'Pagos' },
        { to: '/personal/turnos', icon: 'fa-solid fa-calendar-days', label: 'Turnos' },
        { to: '/personal/adelantos', icon: 'fa-solid fa-piggy-bank', label: 'Adelantos' },
        { to: '/personal/solicitudes', icon: 'fa-solid fa-file-lines', label: 'Solicitudes' },
        { to: '/personal/salarios', icon: 'fa-solid fa-sack-dollar', label: 'Salarios' }
      ]
    },
    {
      id: 'inversiones',
      label: 'Inventario e Inversión',
      icon: 'fa-solid fa-cubes-stacked',
      iconCls: 'ic-purple',
      children: [
        { to: '/inventario', icon: 'fa-solid fa-boxes-stacked', label: 'Módulo' },
        { to: '/inventario/operaciones', icon: 'fa-solid fa-arrows-rotate', label: 'Operaciones' },
        { to: '/inventario/reportes', icon: 'fa-solid fa-chart-column', label: 'Reportes' }
      ]
    },
    {
      id: 'seguridad',
      label: 'Seguridad',
      icon: 'fa-solid fa-shield-halved',
      iconCls: 'ic-red',
      children: [
        { to: '/seguridad', icon: 'fa-solid fa-shield-halved', label: 'Seguridad y Accesos' },
        { to: '/seguridad/monitoreo', icon: 'fa-solid fa-eye', label: 'Monitoreo' },
        { to: '/seguridad/roles', icon: 'fa-solid fa-user-shield', label: 'Roles' },
        { to: '/seguridad/actividad', icon: 'fa-solid fa-list-check', label: 'Actividad' }
      ]
    },
    { id: 'ia', item: { to: '/ia', label: 'IA Predictiva', icon: 'fa-solid fa-brain', iconCls: 'ic-cyan' } }
  ],
  2: [
    { id: 'principal', item: { to: '/panel-cajera', label: 'Mi Panel', icon: 'fa-solid fa-gauge-high', iconCls: 'ic-orange', chip: 'caja-saldo' } },
    {
      id: 'caja',
      label: 'Caja',
      icon: 'fa-solid fa-cash-register',
      iconCls: 'ic-green',
      children: [
        { to: '/caja/dashboard', icon: 'fa-solid fa-chart-pie', label: 'Dashboard de Caja' },
        { to: '/caja', icon: 'fa-solid fa-cash-register', label: 'Control de Caja', chip: 'caja-control' },
        { to: '/caja/movimientos', icon: 'fa-solid fa-arrows-rotate', label: 'Movimientos' },
        { to: '/caja/historial', icon: 'fa-solid fa-clock-rotate-left', label: 'Historial de Cierres' }
      ]
    },
    { id: 'miarea', label: 'Mi Área', icon: 'fa-solid fa-user', iconCls: 'ic-blue', children: areaItems }
  ],
  3: [
    { id: 'principal', item: { to: '/cocinero', label: 'Mi Panel', icon: 'fa-solid fa-gauge-high', iconCls: 'ic-orange' } },
    {
      id: 'cocina',
      label: 'Cocina',
      icon: 'fa-solid fa-utensils',
      iconCls: 'ic-orange',
      children: [
        { to: '/cocinero/inventario', icon: 'fa-solid fa-boxes-stacked', label: 'Insumos' },
        { to: '/cocinero/solicitudes', icon: 'fa-solid fa-list-check', label: 'Mis Solicitudes' },
        { to: '/cocinero/alertas', icon: 'fa-solid fa-triangle-exclamation', label: 'Alertas' }
      ]
    },
    { id: 'miarea', label: 'Mi Área', icon: 'fa-solid fa-user', iconCls: 'ic-blue', children: areaItems }
  ],
  4: [
    { id: 'principal', item: { to: '/trabajador', label: 'Mi Panel', icon: 'fa-solid fa-gauge-high', iconCls: 'ic-orange' } },
    { id: 'miarea', label: 'Mi Área', icon: 'fa-solid fa-user', iconCls: 'ic-blue', children: areaItems }
  ]
}

const menu = computed(() => {
  const estructura = MENU_POR_ROL[rol.value] || MENU_POR_ROL[4]
  return estructura
    .map((e) => ({ ...e, children: e.children ? [...e.children] : undefined }))
    .filter((e) => !e.children || e.children.length > 0)
})

// Apertura por categoría: el estado es local al drawer y se reinicia en cada apertura
const abiertas = ref({ caja: true })

const toggleCat = (key) => {
  abiertas.value[key] = !abiertas.value[key]
}

// Indicador de la sección activa
const isExact = (path) => route.path === path
const isSectionActive = (entry) =>
  (entry.children || []).some((c) => route.path === c.to || route.path.startsWith(c.to + '/'))

// Métricas en vivo del menú (lema: la información está en el menú)
const chips = ref(null)

watch(
  () => props.open,
  (val) => {
    if (!val) return
    abiertas.value = { caja: true }
    if (rol.value === 1 || rol.value === 2) cargarChips()
  }
)

const cargarChips = async () => {
  try {
    const res = await api.get('/caja/actual')
    if (res.data?.success) chips.value = res.data.data
  } catch (err) {
    chips.value = null
  }
}

const fmtMoney = (val) =>
  Number(val || 0).toLocaleString('es-PE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

const chip = (ck) => {
  if (!chips.value) return null
  if (ck === 'caja-control') {
    return chips.value.abierta ? `S/. ${fmtMoney(chips.value.ventas_dia)}` : 'Cerrada'
  }
  if (ck === 'caja-saldo') {
    return chips.value.abierta ? `S/. ${fmtMoney(chips.value.neto_dia)}` : 'Cerrada'
  }
  return null
}

const chipTone = (ck) => {
  if (!chips.value) return 'neutral'
  if (ck === 'caja-control' && !chips.value.abierta) return 'neutral'
  if (chips.value.abierta && (chips.value.ventas_dia ?? 0) <= 0 && ck === 'caja-control') return 'warn'
  return 'ok'
}
</script>

<style scoped>
.drawer-root {
  position: fixed;
  inset: 0;
  z-index: 200;
}

.drawer-backdrop {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(2px);
  animation: fadeIn 0.2s ease;
}

.app-drawer {
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  width: 300px;
  max-width: 88vw;
  background: var(--bg-card);
  box-shadow: var(--shadow-medium);
  display: flex;
  flex-direction: column;
  animation: slideIn 0.25s ease;
}

@keyframes slideIn {
  from { transform: translateX(-100%); }
  to { transform: translateX(0); }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.drawer-header {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 1.25rem 1.25rem 1rem;
  border-bottom: 1px solid var(--border-color);
}

.drawer-logo {
  width: 40px;
  height: 40px;
  object-fit: contain;
}

.drawer-header h2 {
  margin: 0;
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-main);
}

.drawer-subtitle {
  font-size: 0.7rem;
  color: var(--text-muted);
  letter-spacing: 0.05em;
}

.drawer-nav {
  flex: 1;
  overflow-y: auto;
  padding: 0.75rem 0.75rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

/* ------------------------------------------------------------------ */
/* Ítems                                                                */
/* ------------------------------------------------------------------ */
.drawer-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.7rem;
  padding: 0.6rem 0.75rem;
  border-radius: 12px;
  text-decoration: none;
  color: var(--text-muted);
  font-size: 0.84rem;
  font-weight: 500;
  transition: background 0.18s ease, color 0.18s ease;
}

.drawer-item:hover {
  background: var(--hover-color);
  color: var(--btn-primary);
}

.drawer-item.active {
  background: rgba(255, 123, 0, 0.08);
  color: var(--btn-primary);
  font-weight: 600;
}

/* Indicador vertical de la sección activa */
.drawer-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 22%;
  bottom: 22%;
  width: 3px;
  border-radius: 3px;
  background: var(--btn-primary);
}

.nav-tick {
  width: 0px;
  flex-shrink: 0;
}

.item-icon-shell {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: 9px;
  font-size: 0.82rem;
  flex-shrink: 0;
}

.ic-orange { background: rgba(255, 123, 0, 0.15); color: var(--btn-primary); }
.ic-green { background: rgba(22, 163, 74, 0.15); color: #16a34a; }
.ic-blue { background: rgba(59, 130, 246, 0.15); color: #3b82f6; }
.ic-purple { background: rgba(139, 92, 246, 0.15); color: #8b5cf6; }
.ic-red { background: rgba(220, 38, 38, 0.15); color: #dc2626; }
.ic-cyan { background: rgba(6, 182, 212, 0.15); color: #06b6d4; }

.item-label {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ------------------------------------------------------------------ */
/* Sub-ítems                                                           */
/* ------------------------------------------------------------------ */
.sub-item {
  padding: 0.5rem 0.75rem;
  font-size: 0.8rem;
}

.sub-item .sub-indent {
  display: flex;
  align-items: center;
  flex-shrink: 0;
  color: inherit;
}

.sub-item i {
  font-size: 0.72rem;
  opacity: 0.85;
}

/* transición escalonada al abrir la categoría */
.drawer-subcat {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin: 2px 0 2px;
}

.subcat-enter-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
}

.subcat-enter-from {
  opacity: 0;
  transform: translateX(-6px);
}

/* ------------------------------------------------------------------ */
/* Categorías                                                          */
/* ------------------------------------------------------------------ */
.drawer-cat {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  width: 100%;
  padding: 0.6rem 0.75rem;
  margin-top: 0.35rem;
  border: none;
  background: transparent;
  border-radius: 12px;
  cursor: pointer;
  text-align: left;
  color: var(--text-main);
  font-size: 0.84rem;
  font-weight: 600;
  transition: background 0.18s ease;
}

.drawer-cat:hover {
  background: var(--hover-color);
}

.drawer-cat.cat-active {
  color: var(--btn-primary);
}

.cat-arrow {
  width: 14px;
  flex-shrink: 0;
  font-size: 0.7rem;
  color: var(--text-muted);
  transition: transform 0.18s ease;
}

.cat-arrow.open {
  transform: rotate(90deg);
  color: var(--btn-primary);
}

.cat-titulo {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.cat-badge {
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  border-radius: 999px;
  background: var(--bg-secondary);
  color: var(--text-muted);
  font-size: 0.66rem;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.cat-open .cat-badge {
  background: rgba(255, 123, 0, 0.12);
  color: var(--btn-primary);
}

/* ------------------------------------------------------------------ */
/* Chips de métricas                                                   */
/* ------------------------------------------------------------------ */
.menu-chip {
  margin-left: auto;
  flex-shrink: 0;
  font-size: 0.62rem;
  font-weight: 700;
  padding: 0.16rem 0.5rem;
  border-radius: 999px;
  white-space: nowrap;
  letter-spacing: 0.02em;
}

.chip-ok { background: rgba(22, 163, 74, 0.12); color: #16a34a; }
.chip-warn { background: rgba(255, 123, 0, 0.14); color: var(--btn-primary); }
.chip-neutral { background: var(--bg-secondary); color: var(--text-muted); }

/* ------------------------------------------------------------------ */
/* Footer                                                              */
/* ------------------------------------------------------------------ */
.drawer-footer {
  padding: 1rem;
  border-top: 1px solid var(--border-color);
}

.drawer-logout {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.6rem;
  width: 100%;
  padding: 0.7rem;
  border-radius: 12px;
  border: 1px solid var(--border-color);
  background: var(--bg-secondary);
  color: var(--color-rojo);
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 600;
  transition: all 0.18s ease;
}

.drawer-logout:hover {
  border-color: var(--color-rojo);
  background: rgba(220, 38, 38, 0.08);
}
</style>