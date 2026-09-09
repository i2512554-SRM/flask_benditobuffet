<template>
  <div class="trabajador-view">
    <VolverBtn to="/trabajador" />

    <div class="page-header">
      <div>
        <h1>Mis turnos</h1>
        <p>Turno y jornada asignada</p>
      </div>
      <span class="estado-chip" :class="turnos.estado_laboral === 'Activo' ? 'ok' : 'off'">
        <i class="fa-solid fa-user-check"></i> {{ turnos.estado_laboral }}
      </span>
    </div>

    <div v-if="loading" class="loading-overlay">
      <i class="fa-solid fa-spinner fa-spin"></i>
    </div>

    <template v-else>
      <div class="summary-strip">
        <div class="sum-item">
          <span class="sum-label">Turno(s) asignado(s)</span>
          <div class="sum-value turnos">
            <span v-for="t in turnos.turnos" :key="t" class="turno-chip">{{ t }}</span>
            <span v-if="!turnos.turnos.length" class="text-muted">Sin turno asignado</span>
          </div>
        </div>
        <div class="sum-item">
          <span class="sum-label">Horario general</span>
          <span class="sum-value">{{ turnos.horario || 'No definido' }}</span>
        </div>
      </div>

      <div class="section-block">
        <h2 class="seccion-title">Turnos de esta semana</h2>
        <div class="week-grid">
          <div v-for="d in turnos.semana" :key="d.dia"
            class="day-card" :class="{ descanso: !d.laboral, hoy: esHoy(d.fecha) }">
            <div class="day-head">
              <span class="day-name">{{ d.dia }}</span>
              <Tag :value="d.estado" :severity="d.laboral ? 'success' : 'secondary'" />
            </div>
            <div class="day-fecha">{{ d.fecha }}</div>
            <div v-if="d.turnos.length" class="day-turnos">
              <div v-for="t in d.turnos" :key="t.nombre" class="day-turno">
                <span class="dt-nombre">{{ t.nombre }}</span>
                <span class="dt-horas">
                  <i class="fa-regular fa-clock"></i> {{ t.hora_entrada }} – {{ t.hora_salida }}
                </span>
              </div>
            </div>
            <div v-else class="day-descanso">
              <i class="fa-solid fa-moon"></i> Descanso
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Tag from 'primevue/tag'
import VolverBtn from '../components/ui/VolverBtn.vue'
import api from '../config/axios'

const loading = ref(true)
const turnos = ref({ turnos: [], horario: null, estado_laboral: 'Activo', semana: [] })

const esHoy = (fecha) => {
  const hoy = new Date().toLocaleDateString('es-PE')
  return fecha === hoy
}

const load = async () => {
  loading.value = true
  try {
    const res = await api.get('/trabajador/turnos')
    if (res.data.success) turnos.value = res.data.data
  } catch (e) {
    console.error('Error cargando turnos:', e)
  } finally {
    loading.value = false
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
  border-radius: 14px 14px 0 0;
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

.estado-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.35rem 0.9rem;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 600;
}

.estado-chip.ok { background: rgba(22, 163, 74, 0.1); color: var(--color-verde-fuerte); }
.estado-chip.off { background: rgba(220, 38, 38, 0.08); color: var(--color-rojo); }

.summary-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin: 1.5rem 2rem 0;
  padding: 1rem 1.25rem;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  box-shadow: var(--shadow-soft);
}

.sum-item {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  min-width: 200px;
}

.sum-label {
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
}

.sum-value.turnos { display: flex; flex-wrap: wrap; gap: 0.4rem; }
.sum-value { font-size: 0.95rem; font-weight: 600; color: var(--text-main); }

.turno-chip {
  padding: 0.18rem 0.65rem;
  border-radius: 999px;
  background: rgba(245, 158, 11, 0.12);
  color: #d97706;
  font-size: 0.78rem;
  font-weight: 600;
}

.section-block { margin: 1rem 2rem 2rem; }
.seccion-title { font-size: 1rem; color: var(--text-main); }

.week-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.day-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  padding: 1rem 1.1rem;
  box-shadow: var(--shadow-soft);
  transition: all 0.18s ease;
}

.day-card.hoy {
  border-color: var(--btn-primary);
  box-shadow: 0 0 0 2px rgba(255, 122, 0, 0.15);
}

.day-card.descanso { opacity: 0.7; }

.day-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.25rem;
}

.day-name { font-size: 0.9rem; font-weight: 700; color: var(--text-main); }
.day-fecha { font-size: 0.75rem; color: var(--text-muted); margin-bottom: 0.6rem; }

.day-turnos { display: flex; flex-direction: column; gap: 0.45rem; }

.day-turno {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.3rem;
  padding: 0.45rem 0.6rem;
  background: var(--bg-secondary);
  border-radius: 10px;
}

.dt-nombre { font-size: 0.8rem; font-weight: 600; color: var(--btn-primary); }
.dt-horas { font-size: 0.75rem; color: var(--text-muted); }
.dt-horas i { margin-right: 0.25rem; }

.day-descanso {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.8rem;
  color: var(--text-muted);
}

.loading-overlay {
  display: flex;
  justify-content: center;
  padding: 3rem;
  color: var(--btn-primary);
  font-size: 1.5rem;
}

@media (max-width: 768px) {
  .page-header { flex-direction: column; gap: 1rem; align-items: flex-start; }
  .summary-strip { margin: 1rem; flex-direction: column; }
  .section-block { margin: 1rem; }
}
</style>