<template>
  <Dialog
    :visible="visible"
    modal
    maximizable
    dismissableMask
    :style="{ width: '860px' }"
    :breakpoints="{ '960px': '94vw' }"
    @update:visible="$emit('update:visible', $event)"
  >
    <template #header>
      <div v-if="kpi" class="detalle-titulo">
        <span class="detalle-icono" :class="`estado-${estado}`"><i :class="info.icono"></i></span>
        <div>
          <h2>{{ info.nombre }}</h2>
          <p>{{ info.pregunta }}</p>
        </div>
      </div>
    </template>

    <div v-if="kpi" class="detalle">
      <section class="detalle-resumen">
        <div class="detalle-valor-bloque">
          <span class="estado-pill" :class="`estado-${estado}`">
            <i :class="ESTADOS[estado].icono"></i> {{ ESTADOS[estado].etiqueta }}
          </span>
          <div class="detalle-valor">{{ valorIndicador(kpi) }}</div>
          <p v-if="motivo" class="detalle-motivo"><i class="fa-solid fa-circle-info"></i> {{ motivo }}</p>
          <p v-if="anterior" class="detalle-anterior">{{ comparacionParcial ? 'Mismo tramo del periodo anterior' : 'Periodo anterior' }}: <strong>{{ anterior }}</strong></p>
          <p v-if="periodoTexto" class="detalle-periodo"><i class="fa-solid fa-calendar-days"></i> {{ periodoTexto }}</p>
          <template v-if="limites">
            <p class="detalle-meta"><i class="fa-solid fa-bullseye"></i> Meta: {{ textoMeta(kpi) }}</p>
            <p v-if="limites.personalizada" class="detalle-meta-autor">
              Ajustada<template v-if="limites.actualizado_por"> por {{ limites.actualizado_por }}</template> el {{ soloFecha(limites.actualizado_en) }}
            </p>
            <button v-if="!editando" type="button" class="detalle-ajustar" @click="abrirEdicion">
              <i class="fa-solid fa-sliders"></i> Ajustar meta
            </button>
          </template>
        </div>
        <div class="detalle-consejo">
          <OllitaMascota :expresion="ESTADOS[estado].ollita" :tamano="92" />
          <div>
            <h3>¿Qué puedo hacer?</h3>
            <p>{{ info.acciones?.[estado] || kpi.alerta || 'Revisa el detalle del periodo.' }}</p>
          </div>
        </div>
      </section>

      <section v-if="editando && limites" ref="seccionMetas" class="detalle-bloque detalle-metas" aria-labelledby="titulo-ajustar-meta">
        <h3 id="titulo-ajustar-meta"><i class="fa-solid fa-sliders"></i> Ajustar meta</h3>
        <p class="detalle-metas__ayuda">
          Elige desde qué valor el indicador se ve en verde y desde cuál pide revisión. Entre ambos queda en «Atención».
        </p>
        <div class="detalle-metas__campos">
          <div class="detalle-metas__campo">
            <label for="meta-atencion"><i class="fa-solid fa-circle-check estado-texto-bien"></i> {{ etiquetas.atencion }}</label>
            <InputNumber
              v-model="borrador.atencion"
              input-id="meta-atencion"
              highlight-on-focus
              locale="es-PE"
              :min="limites.minimo"
              :max="limites.maximo"
              :max-fraction-digits="2"
              :suffix="sufijo"
              fluid
              @input="borrador.atencion = $event.value"
            />
          </div>
          <div class="detalle-metas__campo">
            <label for="meta-revisar"><i class="fa-solid fa-triangle-exclamation estado-texto-revisar"></i> {{ etiquetas.revisar }}</label>
            <InputNumber
              v-model="borrador.revisar"
              input-id="meta-revisar"
              highlight-on-focus
              locale="es-PE"
              :min="limites.minimo"
              :max="limites.maximo"
              :max-fraction-digits="2"
              :suffix="sufijo"
              fluid
              @input="borrador.revisar = $event.value"
            />
          </div>
        </div>
        <p v-if="errorBorrador" class="detalle-alerta" role="alert">{{ errorBorrador }}</p>
        <template v-else-if="kpi.valor !== null && kpi.valor !== undefined">
          <p class="detalle-metas__vista">
            Con esta meta, el valor actual ({{ valorIndicador(kpi) }}) se vería como
            <span class="estado-pill" :class="`estado-${estadoPrevio}`">
              <i :class="ESTADOS[estadoPrevio].icono"></i> {{ ESTADOS[estadoPrevio].etiqueta }}
            </span>
          </p>
          <p v-if="motivoPrevio" class="detalle-motivo detalle-metas__motivo"><i class="fa-solid fa-circle-info"></i> {{ motivoPrevio }}</p>
        </template>
        <p class="detalle-metas__sugerida">Meta sugerida: {{ textoMeta(kpi, limites.sugerido) }}</p>
        <div class="detalle-metas__acciones">
          <Button
            v-if="limites.personalizada"
            label="Volver a la sugerida"
            icon="pi pi-replay"
            severity="secondary"
            text
            :loading="guardando === 'restaurar'"
            :disabled="Boolean(guardando)"
            @click="restaurar"
          />
          <Button label="Cancelar" severity="secondary" outlined :disabled="Boolean(guardando)" @click="editando = false" />
          <Button
            label="Guardar meta"
            icon="pi pi-check"
            :loading="guardando === 'guardar'"
            :disabled="Boolean(guardando) || Boolean(errorBorrador) || !hayCambios"
            @click="guardar"
          />
        </div>
      </section>

      <section class="detalle-bloque">
        <KpiGrafico :kpi="kpi" :altura="300" />
      </section>

      <section class="detalle-textos">
        <div v-if="kpi.descripcion">
          <h3>¿Qué significa?</h3>
          <p>{{ kpi.descripcion }}</p>
        </div>
        <div v-if="calculo">
          <h3>¿De dónde sale este número?</h3>
          <p>{{ calculo }}</p>
        </div>
      </section>

      <p v-if="kpi.alerta" class="detalle-alerta" role="status">
        <i class="fa-solid fa-triangle-exclamation"></i> {{ kpi.alerta }}
      </p>

      <section v-if="info.desglose && filas.length" class="detalle-bloque">
        <h3>{{ info.desglose.titulo }}</h3>
        <div class="detalle-tabla">
          <table>
            <thead>
              <tr>
                <th v-for="[campo, titulo, tipo] in info.desglose.columnas" :key="campo" :class="{ numero: tipo }">{{ titulo }}</th>
                <th v-if="info.desglose.accion"><span class="sr-only">Acción</span></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(fila, indice) in filas" :key="indice">
                <td v-for="[campo, , tipo] in info.desglose.columnas" :key="campo" :class="{ numero: tipo }">{{ formatoCelda(fila[campo], tipo) }}</td>
                <td v-if="info.desglose.accion" class="celda-accion">
                  <router-link v-if="info.desglose.accion.mostrar(fila, kpi)" :to="info.desglose.accion.ruta(fila)" class="accion-fila">
                    <i :class="info.desglose.accion.icono"></i> {{ info.desglose.accion.etiqueta }}
                  </router-link>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <p v-if="kpi.nota || kpi.estimado" class="detalle-nota">
        <i class="fa-solid fa-circle-info"></i>
        <span><strong v-if="kpi.estimado">Valor estimado.</strong> {{ kpi.nota }}</span>
      </p>
    </div>

    <template #footer>
      <Button label="Cerrar" severity="secondary" @click="$emit('update:visible', false)" />
    </template>
  </Dialog>
</template>

<script setup>
import { computed, nextTick, ref, watch } from 'vue'
import { useToast } from 'primevue/usetoast'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import InputNumber from 'primevue/inputnumber'
import KpiGrafico from '../charts/KpiGrafico.vue'
import api from '../../config/axios'
import { soloFecha } from '../../utils/format'
import {
  ESTADOS, infoIndicador, valorIndicador, estadoIndicador, calculoIndicador, anteriorIndicador, formatoCelda,
  etiquetasLimites, sufijoLimite, textoMeta, errorLimites, motivoEstado
} from '../../config/indicadores'

const props = defineProps({
  kpi: { type: Object, default: null },
  visible: { type: Boolean, default: false },
  periodoTexto: { type: String, default: '' },
  comparacionParcial: { type: Boolean, default: false }
})

const emit = defineEmits(['update:visible', 'meta-actualizada'])

const toast = useToast()

const info = computed(() => (props.kpi ? infoIndicador(props.kpi.codigo) : {}))
const estado = computed(() => (props.kpi ? estadoIndicador(props.kpi) : 'sin_datos'))
const calculo = computed(() => (props.kpi ? calculoIndicador(props.kpi) : ''))
const anterior = computed(() => (props.kpi ? anteriorIndicador(props.kpi) : ''))
const filas = computed(() => (props.kpi?.serie || []).filter((fila) => fila && Object.values(fila).some((v) => v !== null && v !== undefined)))

const limites = computed(() => props.kpi?.limites || null)
const etiquetas = computed(() => etiquetasLimites(limites.value))
const sufijo = computed(() => (props.kpi ? sufijoLimite(props.kpi.codigo) : ''))

const editando = ref(false)
const guardando = ref('')
const errorServidor = ref('')
const borrador = ref({ atencion: null, revisar: null })

const errorBorrador = computed(() => errorServidor.value || (limites.value ? errorLimites(limites.value, borrador.value) : ''))
const hayCambios = computed(() => Boolean(limites.value) && (
  borrador.value.atencion !== limites.value.atencion || borrador.value.revisar !== limites.value.revisar))
const limitesPrevios = computed(() => (limites.value ? { ...limites.value, ...borrador.value } : null))
const estadoPrevio = computed(() => (props.kpi && limitesPrevios.value ? estadoIndicador(props.kpi, limitesPrevios.value) : 'sin_datos'))
const motivo = computed(() => (props.kpi && limites.value ? motivoEstado(props.kpi) : ''))
const motivoPrevio = computed(() => (props.kpi && limitesPrevios.value ? motivoEstado(props.kpi, limitesPrevios.value) : ''))

watch(borrador, () => { errorServidor.value = '' }, { deep: true })
watch([() => props.kpi?.codigo, () => props.visible], () => { editando.value = false })

const seccionMetas = ref(null)

const abrirEdicion = async () => {
  borrador.value = { atencion: limites.value.atencion, revisar: limites.value.revisar }
  errorServidor.value = ''
  editando.value = true
  await nextTick()
  seccionMetas.value?.scrollIntoView({ behavior: 'smooth', block: 'center' })
  document.getElementById('meta-atencion')?.focus({ preventScroll: true })
}

const enviar = async (accion, peticion) => {
  guardando.value = accion
  try {
    const res = await peticion()
    emit('meta-actualizada', props.kpi.codigo, res.data.data)
    editando.value = false
    toast.add({ severity: 'success', summary: res.data.message, detail: info.value.nombre, life: 3000 })
  } catch (err) {
    errorServidor.value = err.response?.data?.error || 'No se pudo guardar la meta. Intenta nuevamente.'
  } finally {
    guardando.value = ''
  }
}

const guardar = () => {
  if (errorBorrador.value) return
  enviar('guardar', () => api.put(`/indicadores/metas/${props.kpi.codigo}`, borrador.value))
}

const restaurar = () => enviar('restaurar', () => api.delete(`/indicadores/metas/${props.kpi.codigo}`))
</script>

<style scoped>
.detalle-titulo {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.detalle-titulo h2 {
  margin: 0;
  font-size: 1.2rem;
  color: var(--text-main);
}

.detalle-titulo p {
  margin: 0.15rem 0 0;
  font-size: 0.85rem;
  color: var(--text-muted);
}

.detalle-icono {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  font-size: 1.1rem;
  flex-shrink: 0;
}

.detalle {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.detalle-resumen {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1.2fr);
  gap: 1rem;
}

.detalle-valor-bloque,
.detalle-consejo,
.detalle-bloque {
  padding: 1rem 1.1rem;
  border: 1px solid var(--border-color);
  border-radius: 14px;
  background: var(--bg-secondary);
}

.detalle-valor {
  margin: 0.6rem 0 0.35rem;
  font-size: 2rem;
  font-weight: 700;
  line-height: 1.15;
  color: var(--text-main);
}

.detalle-anterior,
.detalle-periodo,
.detalle-meta {
  margin: 0.25rem 0 0;
  font-size: 0.85rem;
  color: var(--text-muted);
}

.detalle-periodo i,
.detalle-meta i {
  color: var(--btn-primary);
  margin-right: 0.3rem;
}

.detalle-motivo {
  margin: 0.35rem 0 0.2rem;
  display: flex;
  gap: 0.4rem;
  font-size: 0.83rem;
  line-height: 1.45;
  color: #b45309;
}

.detalle-motivo i {
  margin-top: 0.2rem;
}

.detalle-metas__motivo {
  margin: -0.2rem 0 0.5rem;
}

.detalle-meta-autor {
  margin: 0.15rem 0 0 1.45rem;
  font-size: 0.78rem;
  color: var(--text-muted);
}

.detalle-ajustar {
  margin-top: 0.65rem;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.35rem 0.8rem;
  border: 1px solid var(--btn-primary);
  border-radius: 999px;
  background: transparent;
  color: var(--btn-primary);
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
}

.detalle-ajustar:hover,
.detalle-ajustar:focus-visible {
  background: color-mix(in srgb, var(--btn-primary) 10%, transparent);
}

.detalle-metas h3 i {
  color: var(--btn-primary);
  margin-right: 0.3rem;
}

.detalle-metas__ayuda,
.detalle-metas__sugerida {
  margin: 0;
  font-size: 0.85rem;
  line-height: 1.5;
  color: var(--text-muted);
}

.detalle-metas__campos {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 0.9rem;
  margin: 0.9rem 0;
}

.detalle-metas__campo {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.detalle-metas__campo label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-main);
}

.detalle-metas__campo label i {
  margin-right: 0.3rem;
}

.estado-texto-bien { color: #16a34a; }
.estado-texto-revisar { color: var(--color-rojo); }

.detalle-metas__vista {
  margin: 0 0 0.5rem;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.88rem;
  color: var(--text-main);
}

.detalle-metas .detalle-alerta {
  margin-bottom: 0.5rem;
}

.detalle-metas__acciones {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 0.9rem;
}

.detalle-consejo {
  display: flex;
  align-items: center;
  gap: 0.9rem;
}

.detalle h3 {
  margin: 0 0 0.35rem;
  font-size: 0.95rem;
  color: var(--text-main);
}

.detalle-consejo p,
.detalle-textos p {
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.55;
  color: var(--text-main);
}

.detalle-textos {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1rem;
}

.detalle-alerta {
  margin: 0;
  padding: 0.75rem 1rem;
  border-radius: 10px;
  font-size: 0.88rem;
  color: var(--color-rojo);
  background: color-mix(in srgb, var(--color-rojo) 10%, transparent);
}

.detalle-tabla {
  max-height: 280px;
  overflow: auto;
}

.detalle-tabla table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.86rem;
}

.detalle-tabla th,
.detalle-tabla td {
  padding: 0.45rem 0.6rem;
  border-bottom: 1px solid var(--border-color);
  text-align: left;
  color: var(--text-main);
}

.detalle-tabla th {
  position: sticky;
  top: 0;
  background: var(--bg-secondary);
  font-size: 0.78rem;
  color: var(--text-muted);
}

.detalle-tabla .numero {
  text-align: right;
  white-space: nowrap;
}

.celda-accion {
  text-align: right;
  white-space: nowrap;
}

.accion-fila {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.25rem 0.65rem;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 600;
  color: #fff;
  background: var(--btn-primary);
  text-decoration: none;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
}

.detalle-nota {
  margin: 0;
  display: flex;
  gap: 0.5rem;
  font-size: 0.8rem;
  line-height: 1.5;
  color: var(--text-muted);
}

.detalle-nota i {
  margin-top: 0.2rem;
  color: var(--btn-primary);
}

.estado-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.25rem 0.7rem;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 700;
}

.estado-bien { color: #15803d; background: color-mix(in srgb, #16a34a 14%, transparent); }
.estado-atencion { color: #b45309; background: color-mix(in srgb, #f59e0b 18%, transparent); }
.estado-revisar { color: var(--color-rojo); background: color-mix(in srgb, var(--color-rojo) 14%, transparent); }
.estado-sin_datos { color: var(--text-muted); background: color-mix(in srgb, var(--text-muted) 14%, transparent); }

@media (max-width: 720px) {
  .detalle-resumen {
    grid-template-columns: 1fr;
  }

  .detalle-consejo {
    flex-direction: column;
    text-align: center;
  }
}
</style>
