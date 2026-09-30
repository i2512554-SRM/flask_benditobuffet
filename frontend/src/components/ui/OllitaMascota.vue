<template>
  <svg
    class="ollita"
    :class="[`ollita--${expresion}`, { 'ollita--animada': animada }]"
    :width="tamano"
    :height="tamano"
    viewBox="-120 8 240 240"
    :role="titulo ? 'img' : undefined"
    :aria-label="titulo || undefined"
    :aria-hidden="titulo ? undefined : 'true'"
    focusable="false"
  >
    <ellipse cx="0" cy="240" rx="58" ry="6" fill="#B4B2A9" opacity="0.35" />

    <g class="ollita__vapor" fill="none" stroke="#B4B2A9" stroke-linecap="round">
      <template v-if="expresion === 'pensando'">
        <path d="M-12 70 q0 -16 14 -16 q14 0 14 14 q0 10 -12 14 q-4 2 -4 10" stroke-width="4" />
        <circle cx="2" cy="99" r="3" fill="#B4B2A9" stroke="none" />
      </template>
      <template v-else-if="expresion === 'preocupada'">
        <path d="M-10 104 q-7 -10 0 -20 q7 -10 0 -20" stroke-width="3" opacity="0.7" />
        <path d="M12 104 q-7 -10 0 -20 q7 -10 0 -20" stroke-width="3" opacity="0.7" />
      </template>
      <template v-else-if="expresion === 'celebrando'">
        <path d="M-20 104 q-11 -13 0 -26 q11 -13 0 -26" stroke-width="4.5" />
        <path d="M0 102 q-11 -13 0 -26 q11 -13 0 -26" stroke-width="4.5" />
        <path d="M20 104 q-11 -13 0 -26 q11 -13 0 -26" stroke-width="4.5" />
      </template>
      <template v-else>
        <path d="M-18 104 q-10 -12 0 -24 q10 -12 0 -24" stroke-width="4" />
        <path d="M0 102 q-10 -12 0 -24 q10 -12 0 -24" stroke-width="4" />
        <path d="M18 104 q-10 -12 0 -24 q10 -12 0 -24" stroke-width="4" />
      </template>
    </g>

    <g class="ollita__aureola" fill="none" stroke="#EF9F27">
      <ellipse v-if="expresion === 'pensando'" cx="0" cy="40" rx="26" ry="6" stroke-width="4" opacity="0.55" />
      <ellipse v-else-if="expresion === 'preocupada'" cx="6" cy="46" rx="28" ry="6" stroke-width="4" opacity="0.8" transform="rotate(-14 6 46)" />
      <ellipse v-else-if="expresion === 'celebrando'" cx="0" cy="42" rx="32" ry="7" stroke-width="6" />
      <ellipse v-else cx="0" cy="44" rx="30" ry="7" stroke-width="5" />
    </g>

    <g v-if="expresion === 'celebrando'" class="ollita__confeti">
      <rect x="-70" y="36" width="7" height="12" rx="1" fill="#FF7B00" transform="rotate(-25 -66 42)" />
      <circle cx="68" cy="38" r="4.5" fill="#1D9E75" />
      <circle cx="-102" cy="74" r="4" fill="#EF9F27" />
      <rect x="96" y="70" width="7" height="12" rx="1" fill="#D4537E" transform="rotate(30 100 76)" />
      <circle cx="0" cy="18" r="3.5" fill="#5DCAA5" />
      <rect x="-112" y="128" width="6" height="10" rx="1" fill="#7F77DD" transform="rotate(20 -109 133)" />
      <circle cx="110" cy="130" r="3.5" fill="#FF7B00" />
    </g>

    <g fill="none" stroke="#993C1D" stroke-width="7" stroke-linecap="round">
      <path v-if="expresion === 'feliz'" d="M-40 176 Q-78 182 -86 194" />
      <path v-if="expresion === 'pensando'" d="M-40 176 Q-74 184 -80 194" />
      <template v-if="expresion === 'celebrando'">
        <path d="M-40 160 Q-90 134 -84 100" />
        <path d="M40 160 Q90 134 84 100" />
      </template>
    </g>
    <g v-if="expresion === 'feliz'" class="ollita__saludo">
      <path d="M40 160 Q84 146 90 110" fill="none" stroke="#993C1D" stroke-width="7" stroke-linecap="round" />
      <ellipse cx="90" cy="100" rx="10" ry="12" fill="#FF7B00" stroke="#D85A30" stroke-width="1.5" />
      <ellipse cx="100" cy="104" rx="4" ry="6" fill="#FF7B00" stroke="#D85A30" stroke-width="1.5" />
      <path d="M108 84 q6 6 4 14 M114 76 q9 9 6 22" fill="none" stroke="#B4B2A9" stroke-width="2.5" stroke-linecap="round" />
    </g>

    <ellipse cx="-24" cy="226" rx="13" ry="7" fill="#993C1D" />
    <ellipse cx="24" cy="226" rx="13" ry="7" fill="#993C1D" />
    <ellipse cx="0" cy="170" rx="62" ry="56" fill="#D85A30" />
    <path d="M-50 114 q-15 0 -15 11 q0 9 12 10" fill="none" stroke="#993C1D" stroke-width="6" stroke-linecap="round" />
    <path d="M50 114 q15 0 15 11 q0 9 -12 10" fill="none" stroke="#993C1D" stroke-width="6" stroke-linecap="round" />
    <rect x="-52" y="108" width="104" height="18" rx="9" fill="#993C1D" />
    <path d="M-48 204 l8 -8 l8 8 l8 -8 l8 8 l8 -8 l8 8 l8 -8 l8 8 l8 -8 l8 8 l8 -8 l8 8" fill="none" stroke="#FAC775" stroke-width="3" stroke-linejoin="round" />

    <g v-if="expresion === 'pensando'">
      <path d="M-24 146 Q-16 142 -8 146" fill="none" stroke="#412402" stroke-width="2.5" stroke-linecap="round" />
      <path d="M12 140 Q20 133 28 139" fill="none" stroke="#412402" stroke-width="2.5" stroke-linecap="round" />
      <ellipse cx="-13" cy="157" rx="5" ry="6" fill="#412402" />
      <ellipse cx="23" cy="155" rx="5" ry="6" fill="#412402" />
      <circle cx="-11" cy="154.5" r="1.6" fill="#FFFFFF" />
      <circle cx="25" cy="152.5" r="1.6" fill="#FFFFFF" />
      <path d="M-6 180 Q4 176 12 180" fill="none" stroke="#412402" stroke-width="2.5" stroke-linecap="round" />
    </g>
    <g v-else-if="expresion === 'preocupada'">
      <path d="M-27 147 L-10 141 M10 141 L27 147" fill="none" stroke="#412402" stroke-width="2.5" stroke-linecap="round" />
      <ellipse cx="-18" cy="160" rx="5" ry="6" fill="#412402" />
      <ellipse cx="18" cy="160" rx="5" ry="6" fill="#412402" />
      <circle cx="-16.5" cy="158" r="1.6" fill="#FFFFFF" />
      <circle cx="19.5" cy="158" r="1.6" fill="#FFFFFF" />
      <path d="M-14 186 q4.5 -5 9 0 q4.5 5 9 0 q4.5 -5 9 0" fill="none" stroke="#412402" stroke-width="2.5" stroke-linecap="round" />
      <path class="ollita__gota" d="M52 128 q-8 11 0 15 q8 -4 0 -15 Z" fill="#85B7EB" />
    </g>
    <g v-else-if="expresion === 'celebrando'">
      <path d="M-25 162 Q-18 152 -11 162 M11 162 Q18 152 25 162" fill="none" stroke="#412402" stroke-width="3" stroke-linecap="round" />
      <ellipse cx="-32" cy="174" rx="7" ry="4" fill="#F0997B" />
      <ellipse cx="32" cy="174" rx="7" ry="4" fill="#F0997B" />
      <path d="M-15 175 Q0 198 15 175 Z" fill="#412402" />
      <ellipse cx="0" cy="187" rx="6" ry="3" fill="#F0997B" />
    </g>
    <g v-else>
      <ellipse cx="-18" cy="160" rx="5" ry="6" fill="#412402" />
      <ellipse cx="18" cy="160" rx="5" ry="6" fill="#412402" />
      <circle cx="-16.5" cy="158" r="1.6" fill="#FFFFFF" />
      <circle cx="19.5" cy="158" r="1.6" fill="#FFFFFF" />
      <ellipse cx="-30" cy="176" rx="7" ry="4" fill="#F0997B" />
      <ellipse cx="30" cy="176" rx="7" ry="4" fill="#F0997B" />
      <path d="M-13 177 Q0 190 13 177" fill="none" stroke="#412402" stroke-width="2.5" stroke-linecap="round" />
    </g>

    <g v-if="expresion === 'pensando'">
      <path d="M58 172 Q58 198 26 194" fill="none" stroke="#993C1D" stroke-width="7" stroke-linecap="round" />
    </g>
    <g v-if="expresion === 'preocupada'" fill="none" stroke="#993C1D" stroke-width="7" stroke-linecap="round">
      <path d="M-58 158 Q-66 178 -44 178" />
      <path d="M58 158 Q66 178 44 178" />
    </g>

    <g fill="#FF7B00" stroke="#D85A30" stroke-width="1.5">
      <template v-if="expresion === 'feliz'">
        <ellipse cx="-86" cy="202" rx="10" ry="12" />
        <ellipse cx="-96" cy="198" rx="4" ry="6" />
      </template>
      <template v-else-if="expresion === 'pensando'">
        <ellipse cx="18" cy="194" rx="10" ry="12" />
        <ellipse cx="10" cy="186" rx="4" ry="6" />
        <ellipse cx="-80" cy="202" rx="10" ry="12" />
        <ellipse cx="-90" cy="198" rx="4" ry="6" />
      </template>
      <template v-else-if="expresion === 'preocupada'">
        <ellipse cx="-38" cy="178" rx="10" ry="12" />
        <ellipse cx="-30" cy="172" rx="4" ry="6" />
        <ellipse cx="38" cy="178" rx="10" ry="12" />
        <ellipse cx="30" cy="172" rx="4" ry="6" />
      </template>
      <template v-else>
        <ellipse cx="-84" cy="92" rx="10" ry="12" />
        <ellipse cx="-94" cy="96" rx="4" ry="6" />
        <ellipse cx="84" cy="92" rx="10" ry="12" />
        <ellipse cx="94" cy="96" rx="4" ry="6" />
      </template>
    </g>
  </svg>
</template>

<script setup>
defineProps({
  expresion: {
    type: String,
    default: 'feliz',
    validator: (valor) => ['feliz', 'pensando', 'preocupada', 'celebrando'].includes(valor)
  },
  tamano: { type: Number, default: 120 },
  animada: { type: Boolean, default: true },
  titulo: { type: String, default: '' }
})
</script>

<style scoped>
.ollita {
  display: block;
  flex-shrink: 0;
  overflow: visible;
}

.ollita--animada .ollita__vapor {
  animation: ollita-vapor 2.6s ease-in-out infinite;
}

.ollita--animada .ollita__aureola {
  animation: ollita-flotar 3.2s ease-in-out infinite;
}

.ollita--animada .ollita__saludo {
  transform-box: fill-box;
  transform-origin: 8% 92%;
  animation: ollita-saludo 1.6s ease-in-out infinite;
}

.ollita--animada.ollita--celebrando {
  animation: ollita-salto 0.9s ease-in-out infinite;
}

.ollita--animada .ollita__confeti {
  animation: ollita-brillo 1.2s ease-in-out infinite alternate;
}

.ollita--animada .ollita__gota {
  animation: ollita-gota 1.8s ease-in infinite;
}

.ollita--animada.ollita--pensando .ollita__vapor {
  animation: ollita-duda 2.4s ease-in-out infinite;
}

@keyframes ollita-vapor {
  0%, 100% { transform: translateY(0); opacity: 1; }
  50% { transform: translateY(-5px); opacity: 0.55; }
}

@keyframes ollita-flotar {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}

@keyframes ollita-saludo {
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(-12deg); }
  75% { transform: rotate(8deg); }
}

@keyframes ollita-salto {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6%); }
}

@keyframes ollita-brillo {
  from { opacity: 0.55; }
  to { opacity: 1; }
}

@keyframes ollita-gota {
  0% { transform: translateY(0); opacity: 1; }
  80% { transform: translateY(10px); opacity: 0.2; }
  100% { transform: translateY(10px); opacity: 0; }
}

@keyframes ollita-duda {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.45; }
}

@media (prefers-reduced-motion: reduce) {
  .ollita,
  .ollita * {
    animation: none !important;
  }
}
</style>
