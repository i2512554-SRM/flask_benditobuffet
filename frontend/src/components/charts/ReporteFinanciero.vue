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
        <div><span>Ingresos</span><strong>S/ {{ dinero(datos.ventas_mes) }}</strong></div>
        <div><span>Egresos</span><strong>S/ {{ dinero(datos.egresos_mes) }}</strong></div>
        <div><span>Balance de caja</span><strong>S/ {{ dinero(datos.neto_mes) }}</strong></div>
        <div><span>Cantidad de movimientos</span><strong>{{ datos.transacciones?.length || 0 }}</strong></div>
      </div>
      <LineChartFinanciero :puntos="datos.puntos || []" />
      <div v-if="metodosPago.length" class="metodos">
        <h3>Distribución de ingresos por método de pago</h3>
        <DonaChart :items="metodosPago" :altura="230" />
      </div>
      <p class="nota">Cada movimiento se cuenta una sola vez. El balance es ventas menos egresos registrados; no representa la utilidad contable del restaurante.</p>
      <details open>
        <summary>Detalle de movimientos ({{ datos.transacciones?.length || 0 }})</summary>
        <DataTable :value="datos.transacciones || []" paginator :rows="10" stripedRows sortField="fecha" :sortOrder="-1">
          <Column field="fecha" header="Fecha y hora" sortable><template #body="{data}">{{ formatFecha(data.fecha) }}</template></Column>
          <Column field="tipo" header="Tipo" sortable><template #body="{data}">{{ tipoLabel(data.tipo) }}</template></Column>
          <Column field="metodo_pago" header="Método de pago" />
          <Column field="monto" header="Monto" sortable><template #body="{data}">S/ {{ dinero(data.monto) }}</template></Column>
          <Column field="descripcion" header="Descripción" />
          <template #empty><EstadoVacio v-if="cargandoDatos" compacto titulo="Revolviendo los datos…" expresion="pensando" /><EstadoVacio v-else compacto titulo="Sin movimientos en este periodo" mensaje="Prueba con otro rango de fechas." expresion="pensando" /></template>
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
          <template #empty><EstadoVacio v-if="cargandoDatos" compacto titulo="Revolviendo los datos…" expresion="pensando" /><EstadoVacio v-else compacto titulo="Sin aperturas de caja en este periodo" expresion="pensando" /></template>
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
import DonaChart from './DonaChart.vue'
import { formatFecha, fechaLocal } from '../../utils/format'
import api from '../../config/axios'

const cargandoDatos = ref(true)
const periodo=ref('mes'), fecha=ref(fechaLocal()), datos=ref({}), loading=ref(false), error=ref('')
const dinero=v=>Number(v || 0).toLocaleString('es-PE',{minimumFractionDigits:2, maximumFractionDigits:2})
const tipoLabel=tipo=>tipo==='Venta'?'Ingreso':tipo==='Gasto'?'Egreso':tipo || '—'
const finVisible=computed(()=>datos.value.fin ? new Date(new Date(datos.value.fin).getTime()-1000).toISOString() : null)
const metodosPago=computed(()=>{
  const agrupados={}
  for (const t of datos.value.transacciones || []) {
    if (t.tipo !== 'Venta') continue
    const metodo=t.metodo_pago || 'No especificado'
    agrupados[metodo]=(agrupados[metodo] || 0)+Number(t.monto || 0)
  }
  const colores={Efectivo:'#16a34a',Yape:'#3b82f6',Tarjeta:'#f59e0b','No especificado':'#94a3b8'}
  return Object.entries(agrupados).map(([etiqueta,valor])=>({etiqueta,valor,color:colores[etiqueta]}))
})
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
  const [anio,mes,dia]=fecha.value.split('-').map(Number)
  const d=new Date(Date.UTC(anio,mes-1,dia,12))
  if(periodo.value==='mes') { d.setUTCDate(1); d.setUTCMonth(d.getUTCMonth()+paso) }
  else if(periodo.value==='anio') { d.setUTCMonth(0,1); d.setUTCFullYear(d.getUTCFullYear()+paso) }
  else d.setUTCDate(d.getUTCDate()+paso*(periodo.value==='semana'?7:1))
  fecha.value=d.toISOString().slice(0,10); cargar()
}
onMounted(async () => { try { await cargar() } finally { cargandoDatos.value = false } })
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
.metodos { margin-top:1.5rem; padding-top:1.25rem; border-top:1px solid var(--border-color); }
.metodos h3 { font-size:1rem; margin:0 0 .75rem; }
summary { cursor:pointer; padding:1rem 0; font-weight:600; }
</style>
