<template>
  <section class="reporte">
    <div class="filtros">
      <label>Periodo <select v-model="periodo" @change="cargar"><option value="dia">Día</option><option value="semana">Semana</option><option value="mes">Mes</option><option value="anio">Año</option></select></label>
      <button class="btn btn-outline" @click="mover(-1)" :disabled="loading" aria-label="Periodo anterior">←</button>
      <input type="date" v-model="fecha" @change="cargar" aria-label="Fecha del reporte" />
      <button class="btn btn-outline" @click="mover(1)" :disabled="loading" aria-label="Periodo siguiente">→</button>
      <button class="btn btn-outline" @click="cargar" :disabled="loading">Actualizar</button>
    </div>
    <p v-if="error" role="alert">{{ error }}</p>
    <p v-if="loading" role="status">Cargando reporte…</p>
    <template v-else-if="!error">
      <p>{{ formatFecha(datos.inicio) }} — {{ formatFecha(finVisible) }} · Hora de Lima</p>
      <div class="totales">
        <div><span>Ventas del periodo</span><strong>S/ {{ dinero(datos.ventas_mes) }}</strong></div>
        <div><span>Egresos del periodo</span><strong>S/ {{ dinero(datos.egresos_mes) }}</strong></div>
        <div><span>Balance de caja</span><strong>S/ {{ dinero(datos.neto_mes) }}</strong></div>
      </div>
      <LineChartFinanciero :puntos="datos.puntos || []" />
      <p class="nota">Cada movimiento se cuenta una sola vez. El balance es ventas menos egresos registrados; no representa la utilidad contable del restaurante.</p>
      <details open>
        <summary>Detalle de movimientos ({{ datos.transacciones?.length || 0 }})</summary>
        <DataTable :value="datos.transacciones || []" paginator :rows="10" stripedRows sortField="fecha" :sortOrder="-1">
          <Column field="fecha" header="Fecha y hora" sortable><template #body="{data}">{{ formatFecha(data.fecha) }}</template></Column>
          <Column field="tipo" header="Tipo" sortable />
          <Column field="metodo_pago" header="Método de pago" />
          <Column field="monto" header="Monto" sortable><template #body="{data}">S/ {{ dinero(data.monto) }}</template></Column>
          <Column field="descripcion" header="Descripción" />
          <template #empty>No hay movimientos en este periodo.</template>
        </DataTable>
      </details>
      <details>
        <summary>Cierres por apertura</summary>
        <p class="nota">Los importes se reconstruyen desde los movimientos entre apertura y cierre. Los registros originales se conservan.</p>
        <DataTable :value="datos.cierres || []" paginator :rows="10" stripedRows>
          <Column field="fecha" header="Apertura" sortable><template #body="{data}">{{ formatFecha(data.fecha) }}</template></Column>
          <Column field="fecha_cierre" header="Cierre"><template #body="{data}">{{ formatFecha(data.fecha_cierre) }}</template></Column>
          <Column field="total_ventas" header="Ventas"><template #body="{data}">S/ {{ dinero(data.total_ventas) }}</template></Column>
          <Column field="total_gastos" header="Gastos"><template #body="{data}">S/ {{ dinero(data.total_gastos) }}</template></Column>
          <Column field="neto" header="Balance"><template #body="{data}">S/ {{ dinero(data.neto) }}</template></Column>
          <Column field="estado" header="Estado" />
          <template #empty>No hay aperturas en este periodo.</template>
        </DataTable>
      </details>
    </template>
  </section>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import LineChartFinanciero from './LineChartFinanciero.vue'
import { formatFecha, fechaLocal } from '../../utils/format'
import api from '../../config/axios'
const periodo=ref('mes'), fecha=ref(fechaLocal()), datos=ref({}), loading=ref(false), error=ref('')
const dinero=v=>Number(v || 0).toLocaleString('es-PE',{minimumFractionDigits:2, maximumFractionDigits:2})
const finVisible=computed(()=>datos.value.fin ? new Date(new Date(datos.value.fin).getTime()-1000).toISOString() : null)
let solicitud=0
async function cargar() {
  if (!fecha.value) return
  const id=++solicitud
  loading.value=true; error.value=''
  try { const res=await api.get('/caja/reportes',{params:{periodo:periodo.value,fecha:fecha.value}}); if(id===solicitud) datos.value=res.data.data }
  catch(e) { if(id===solicitud) error.value=e.response?.data?.error || 'No se pudo cargar el reporte. Intenta nuevamente.' }
  finally { if(id===solicitud) loading.value=false }
}
function mover(paso) {
  const d=new Date(fecha.value+'T12:00:00')
  if(periodo.value==='mes') { d.setDate(1); d.setMonth(d.getMonth()+paso) }
  else if(periodo.value==='anio') { d.setMonth(0,1); d.setFullYear(d.getFullYear()+paso) }
  else d.setDate(d.getDate()+paso*(periodo.value==='semana'?7:1))
  fecha.value=fechaLocal(d); cargar()
}
onMounted(cargar)
</script>
<style scoped>
.reporte { margin-top:1rem; padding:1.25rem; border:1px solid var(--border-color); background:var(--bg-card); border-radius:14px; }
.filtros { display:flex; align-items:center; gap:.7rem; flex-wrap:wrap; }
.filtros label { display:flex; align-items:center; gap:.5rem; width:auto; margin:0; }
.filtros input { width:auto; max-width:100%; flex:0 1 180px; margin:0; }
.filtros select { width:auto; }
input,select { padding:.65rem; border:1px solid var(--border-color); border-radius:8px; background:var(--bg-card); color:var(--text-main); font:inherit; }
.totales { display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:1rem; margin:1.5rem 0; }
.totales div { display:grid; gap:.35rem; } .totales strong { font-size:1.5rem; }
.nota { font-size:.9rem; color:var(--text-muted); margin:1rem 0; }
summary { cursor:pointer; padding:1rem 0; font-weight:600; }
</style>
