<template>
  <div class="caja-movimientos">
    <div class="page-hero">
      <div class="hero-left">
        <h1>Movimientos de Caja</h1>
        <p>Ingresos y egresos registrados, con acceso al histórico completo</p>
      </div>
      <router-link to="/caja" class="btn btn-outline">
        <i class="fa-solid fa-vault"></i> Ir al Control de Caja
      </router-link>
    </div>

    <div class="toolbar">
      <div class="segment">
        <button :disabled="$saving" class="seg-btn" :class="{ active: ambito === 'hoy' }" @click="ambito = 'hoy'">Hoy</button>
        <button :disabled="$saving" class="seg-btn" :class="{ active: ambito === 'historico' }" @click="ambito = 'historico'">Histórico</button>
      </div>
      <button :disabled="$saving" class="btn btn-outline btn-sm" @click="cargar">
        <i class="fa-solid fa-arrows-rotate"></i> Actualizar
      </button>
    </div>

    <div class="table-card">
      <DataTable :value="filas" :paginator="true" :rows="10" dataKey="id_transaccion" responsiveLayout="scroll" class="p-datatable-sm">
        <Column field="fecha" header="Fecha" style="max-width: 8rem;">
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
        <Column field="metodo_pago" header="Método" style="max-width: 7rem;">
          <template #body="slotProps">
            <span class="text-muted">{{ slotProps.data.metodo_pago || '—' }}</span>
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
            <span>{{ ambito === 'hoy' ? 'Aún no hay movimientos registrados hoy.' : 'No hay movimientos históricos.' }}</span>
          </div>
        </template>
      </DataTable>
    </div>

    <div class="loading-overlay" v-if="loading">
      <i class="fa-solid fa-spinner fa-spin"></i>
    </div>
  </div>
</template>

<script setup>
import { formatFecha as fechaLegible } from '../utils/format'
import { ref, computed, onMounted } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'
import api from '../config/axios'

const loading = ref(true)
const ambito = ref('hoy')
const data = ref({ transacciones: [], historico: [], ultimos_movimientos: [] })

const filas = computed(() =>
  ambito.value === 'hoy' ? data.value.transacciones : data.value.ultimos_movimientos
)

const formatMoney = (val) => Number(val || 0).toLocaleString('es-PE', { minimumFractionDigits: 2 })
const formatFecha = fechaLegible

const cargar = async () => {
  loading.value = true
  try {
    const res = await api.get('/caja/transacciones?historico=1&limit=100')
    if (res.data?.success) data.value = res.data.data
  } catch (err) {
    console.error('Error cargando movimientos:', err)
  } finally {
    loading.value = false
  }
}

onMounted(cargar)
</script>

<style scoped>
.page-hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin: 1rem 0 0;
}

.segment {
  display: inline-flex;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 999px;
  padding: 0.2rem;
  box-shadow: var(--shadow-soft);
}

.seg-btn {
  border: none;
  background: transparent;
  padding: 0.4rem 1rem;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}

.seg-btn.active {
  background: var(--btn-primary);
  color: #fff;
}

.btn-sm {
  padding: 0.45rem 0.9rem;
  font-size: 0.8rem;
}

.table-card {
  margin-top: 1rem;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  padding: 0.75rem;
  box-shadow: var(--shadow-soft);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.3rem;
  padding: 1.5rem;
  color: var(--text-muted);
  font-size: 0.85rem;
}

.empty-state i {
  font-size: 1.3rem;
  opacity: 0.4;
}

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