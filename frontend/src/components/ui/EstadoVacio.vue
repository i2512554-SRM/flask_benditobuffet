<template>
  <div class="estado-vacio" :class="{ 'estado-vacio--compacto': compacto }" role="status">
    <OllitaMascota :expresion="expresion" :tamano="tamanoFinal" />
    <div class="estado-vacio__texto">
      <p class="estado-vacio__titulo">{{ titulo }}</p>
      <p v-if="mensaje" class="estado-vacio__mensaje">{{ mensaje }}</p>
    </div>
    <div v-if="$slots.default" class="estado-vacio__acciones">
      <slot />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import OllitaMascota from './OllitaMascota.vue'

const props = defineProps({
  titulo: { type: String, required: true },
  mensaje: { type: String, default: '' },
  expresion: { type: String, default: 'pensando' },
  tamano: { type: Number, default: 0 },
  compacto: { type: Boolean, default: false }
})

const tamanoFinal = computed(() => props.tamano || (props.compacto ? 72 : 110))
</script>

<style scoped>
.estado-vacio {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 1.75rem 1rem;
  text-align: center;
}

.estado-vacio--compacto {
  flex-direction: row;
  gap: 0.9rem;
  padding: 0.9rem 0.5rem;
  text-align: left;
  width: max-content;
  max-width: min(34rem, calc(100vw - 5rem));
  margin-inline: auto;
  position: sticky;
  left: 0.5rem;
  right: 0.5rem;
}

.estado-vacio__titulo {
  margin: 0;
  font-weight: 600;
  color: var(--text-main);
}

.estado-vacio__mensaje {
  margin: 0.2rem 0 0;
  font-size: 0.9rem;
  color: var(--text-muted);
  max-width: 34rem;
}

.estado-vacio__acciones {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  justify-content: center;
  margin-top: 0.35rem;
}
</style>
