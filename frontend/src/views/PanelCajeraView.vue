<template>
  <div class="cajera-panel">
    <div class="page-hero">
      <div class="hero-left">
        <h1>¡Hola, {{ nombre }}! 👋</h1>
        <p>Bienvenida a tu panel de Caja</p>
        <div class="hero-badges">
          <span class="rol-badge" style="background: rgba(16, 185, 129, 0.1); color: #059669;">
            <i class="fa-solid fa-cash-register"></i> Cajera
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
          <span class="stat-value" style="text-transform: capitalize;">{{ caja.abierta ? 'Abierta' : 'Cerrada' }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon blue">
          <i class="fa-solid fa-clock"></i>
        </div>
        <div class="stat-content">
          <span class="stat-label">Monto inicial / apertura</span>
          <span class="stat-value">S/. 0.00</span>
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

    <!-- Acciones rápidas -->
    <h2 class="seccion-title">Acciones rápidas</h2>
    <div class="acciones-grid">
      <router-link to="/caja?accion=apertura" class="accion-chip"
        :class="{ primary: !caja.abierta }">
        <i class="fa-solid fa-door-open"></i> Abrir Caja
      </router-link>
      <router-link to="/caja?accion=ingreso" class="accion-chip">
        <i class="fa-solid fa-circle-plus"></i> Registrar Ingreso
      </router-link>
      <router-link to="/caja?accion=egreso" class="accion-chip">
        <i class="fa-solid fa-circle-minus"></i> Registrar Egreso
      </router-link>
      <router-link to="/caja" class="accion-chip">
        <i class="fa-solid fa-vault"></i> Ir al Control de Caja
      </router-link>
    </div>

    <div class="panel-columns">
      <!-- Movimientos recientes -->
      <div class="col-block">
        <h2 class="seccion-title">Movimientos recientes</h2>
        <div class="table-card">
          <DataTable :value="caja.transacciones || []" :paginator="true" :rows="6" dataKey="id_transaccion" responsiveLayout="scroll" class="p-datatable-sm">
            <Column field="fecha" header="Fecha" style="max-width: 9rem;">
              <template #body="slotProps">
                <span class="text-muted">{{ formatFecha(slotProps.data.fecha) }}</span>
              </template>
            </Column>
            <Column field="tipo" header="Tipo">
              <template #body="slotProps">
                <Tag :value="slotProps.data.tipo === 'Venta' ? 'Ingreso' : 'Egreso'"
                  :severity="slotProps.data.tipo === 'Venta' ? 'success' : 'danger'" />
              </template>
            </Column>
            <Column field="monto" header="Monto">
              <template #body="slotProps">
                <strong>S/. {{ formatMoney(slotProps.data.monto) }}</strong>
              </template>
            </Column>
            <Column field="descripcion" header="Descripción">
              <template #body="slotProps">
                <span class="text-muted">{{ slotProps.data.descripcion || '—' }}</span>
              </template>
            </Column>
            <template #empty>
              <div class="empty-state">
                <i class="fa-solid fa-receipt"></i>
                <span>Aún no hay movimientos registrados hoy.</span>
              </div>
            </template>
          </DataTable>
        </div>
      </div>

      <!-- Notificaciones -->
      <div class="col-block">
        <h2 class="seccion-title">Notificaciones</h2>
        <div class="notif-card">
          <div v-for="(n, i) in notificaciones" :key="i" class="notif-item" :class="'notif-' + n.tipo">
            <i :class="n.icono"></i>
            <div>
              <span class="notif-texto">{{ n.titulo }}</span>
            </div>
          </div>
          <div v-if="!notificaciones.length" class="notif-empty">
            <i class="fa-solid fa-circle-check"></i>
            <span>Todo en orden por ahora.</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'
import api from '../config/axios'

const authStore = useAuthStore()
const loading = ref(true)
const caja = ref({ abierta: false, ventas_dia: 0, gastos_dia: 0, neto_dia: 0, transacciones: [] })

const nombre = computed(() => authStore.user?.nombre || 'Cajera')
const fechaHoy = computed(() => new Intl.DateTimeFormat('es-PE', {
  weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'
}).format(new Date()))

const notificaciones = computed(() => {
  const items = []
  if (!caja.value.abierta) {
    items.push({ tipo: 'error', icono: 'fa-solid fa-lock', titulo: 'La caja está pendiente de apertura.' })
  } else {
    items.push({ tipo: 'info', icono: 'fa-solid fa-lock-open', titulo: 'Tienes una caja abierta actualmente.' })
  }
  if ((caja.value.transacciones || []).length > 0) {
    items.push({ tipo: 'ok', icono: 'fa-solid fa-check', titulo: `Se registró(n) ${caja.value.transacciones.length} movimiento(s) hoy.` })
  }
  if (caja.value.abierta && (caja.value.transacciones || []).length === 0) {
    items.push({ tipo: 'warn', icono: 'fa-solid fa-circle-info', titulo: 'Aún no hay movimientos registrados hoy.' })
  }
  if (caja.value.abierta) {
    items.push({ tipo: 'info', icono: 'fa-solid fa-key', titulo: 'Recuerda realizar el cierre de caja al finalizar el turno.' })
  }
  return items
})

const formatMoney = (val) => Number(val || 0).toLocaleString('es-PE', { minimumFractionDigits: 2 })
const formatFecha = (val) => {
  if (!val) return '-'
  return String(val).slice(0, 16).replace('T', ' ').slice(11)
}

const cargar = async () => {
  loading.value = true
  try {
    const res = await api.get('/caja/actual')
    if (res.data.success) caja.value = res.data.data
  } catch (err) {
    console.error('Error cargando panel cajera:', err)
  } finally {
    loading.value = false
  }
}

onMounted(cargar)
</script>

<style scoped>
.cajera-panel {
  padding: 0;
}

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

.accion-chip.primary {
  background: var(--btn-primary);
  color: white;
  border-color: var(--btn-primary);
}

.accion-chip.primary i {
  color: white;
}

.accion-chip:hover {
  border-color: var(--btn-primary);
  transform: translateY(-1px);
}

.panel-columns {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 1.5rem;
  margin-top: 0.5rem;
}

.col-block {
  min-width: 0;
}

.table-card {
  margin-top: 1rem;
  background: var(--bg-card);
  border-radius: 14px;
  border: 1px solid var(--border-color);
  padding: 0.75rem;
  box-shadow: var(--shadow-soft);
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

.notif-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.6rem 0.75rem;
  border-radius: 10px;
  font-size: 0.83rem;
  background: var(--bg-secondary);
}

.notif-item i {
  font-size: 0.95rem;
  flex-shrink: 0;
}

.notif-item.notif-ok { color: var(--color-verde-fuerte); background: rgba(22, 163, 74, 0.06); }
.notif-item.notif-warn { color: #b45309; background: rgba(245, 158, 11, 0.08); }
.notif-item.notif-error { color: var(--color-rojo); background: rgba(220, 38, 38, 0.06); }
.notif-item.notif-info { color: #2563eb; background: rgba(59, 130, 246, 0.08); }

.notif-texto {
  color: var(--text-main);
  font-weight: 500;
}

.notif-empty {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.6rem 0.75rem;
  color: var(--color-verde-fuerte);
  font-size: 0.85rem;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.3rem;
  padding: 1.25rem;
  color: var(--text-muted);
  font-size: 0.85rem;
}

.empty-state i {
  font-size: 1.3rem;
  opacity: 0.4;
}

@media (max-width: 900px) {
  .panel-columns {
    grid-template-columns: 1fr;
  }
  .page-hero { flex-direction: column; }
}
</style>