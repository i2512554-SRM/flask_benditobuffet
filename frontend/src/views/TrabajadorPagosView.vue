<template>
  <div class="trabajador-view">
    <VolverBtn to="/trabajador" />
    <div class="page-header">
      <div>
        <h1>Mis pagos</h1>
        <p>Historial de pagos y solicitudes de adelanto</p>
      </div>
      <router-link to="/perfil" class="btn btn-outline">
        <i class="fa-solid fa-hand-holding-dollar"></i> Solicitar adelanto
      </router-link>
    </div>

    <div class="table-card">
      <h2 class="section-title"><i class="fa-solid fa-money-check-dollar"></i> Pagos registrados</h2>
      <DataTable :value="data.pagos || []" :paginator="true" :rows="10" dataKey="id_pago" responsiveLayout="scroll">
        <Column field="fecha" header="Fecha" sortable></Column>
        <Column field="monto" header="Monto">
          <template #body="slotProps">
            <strong>S/. {{ formatMoney(slotProps.data.monto) }}</strong>
          </template>
        </Column>
        <Column field="descripcion" header="Concepto">
          <template #body="slotProps">
            <span class="text-muted">{{ slotProps.data.descripcion }}</span>
          </template>
        </Column>
        <Column field="estado" header="Estado" sortable>
          <template #body="slotProps">
            <Tag :value="slotProps.data.estado" :severity="severidadPago(slotProps.data.estado)" />
          </template>
        </Column>
        <template #empty>
          <div class="empty-state small">
            <i class="fa-solid fa-wallet"></i>
            <span>No tienes pagos registrados todavía.</span>
          </div>
        </template>
      </DataTable>
    </div>

    <div class="table-card">
      <h2 class="section-title"><i class="fa-solid fa-file-invoice-dollar"></i> Adelantos</h2>
      <DataTable :value="data.adelantos || []" :paginator="true" :rows="10" dataKey="id_adelanto" responsiveLayout="scroll">
        <Column field="fecha" header="Fecha" sortable></Column>
        <Column field="motivo" header="Motivo"></Column>
        <Column field="monto" header="Monto">
          <template #body="slotProps">
            <strong>S/. {{ formatMoney(slotProps.data.monto) }}</strong>
          </template>
        </Column>
        <Column field="estado" header="Estado" sortable>
          <template #body="slotProps">
            <Tag :value="slotProps.data.estado" :severity="severidadAdelanto(slotProps.data.estado)" />
          </template>
        </Column>
        <Column field="respuesta" header="Respuesta">
          <template #body="slotProps">
            <span class="text-muted">{{ slotProps.data.respuesta || '—' }}</span>
          </template>
        </Column>
        <template #empty>
          <div class="empty-state small">
            <i class="fa-solid fa-hand-holding-dollar"></i>
            <span>No tienes adelantos solicitados.</span>
          </div>
        </template>
      </DataTable>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import VolverBtn from '../components/ui/VolverBtn.vue'
import api from '../config/axios'

const data = ref({})

const formatMoney = (v) => Number(v || 0).toLocaleString('es-PE', { minimumFractionDigits: 2 })
const severidadPago = (e) => (e === 'Pagado' ? 'success' : 'warning')
const severidadAdelanto = (e) => (e === 'Aprobado' ? 'success' : e === 'Rechazado' ? 'danger' : 'warning')

const load = async () => {
  try {
    const res = await api.get('/trabajador/pagos')
    if (res.data.success) data.value = res.data.data
  } catch (e) {
    console.error('Error cargando pagos:', e)
  }
}

onMounted(load)
</script>

<style scoped>
.trabajador-view {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-color);
}

.page-header h1 {
  margin: 0;
  font-size: 1.5rem;
  color: var(--text-main);
}

.page-header p {
  margin: 0.25rem 0 0;
  font-size: 0.85rem;
  color: var(--text-muted);
}

.table-card {
  margin: 1.5rem 2rem 0;
  background: var(--bg-card);
  border-radius: 14px;
  border: 1px solid var(--border-color);
  padding: 1rem;
  box-shadow: var(--shadow-soft);
}

.table-card:last-of-type {
  margin-bottom: 2rem;
}

.section-title {
  margin: 0 0 0.75rem;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-main);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.empty-state.small { padding: 2rem; }

@media (max-width: 768px) {
  .page-header { flex-direction: column; gap: 1rem; align-items: flex-start; }
  .table-card { margin: 1rem; }
}
</style>