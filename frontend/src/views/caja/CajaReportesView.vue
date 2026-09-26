<template>
  <div>
    <VolverBtn :to="links.caja.control" />
    <div class="page-hero">
      <h1>Reportes Financieros</h1>
      <p>Ingresos, egresos, balance de caja y evolución por fechas</p>
    </div>
    <ReporteFinanciero />
  </div>
</template>
<script setup>
import VolverBtn from '../../components/ui/VolverBtn.vue'
import ReporteFinanciero from '../../components/charts/ReporteFinanciero.vue'
import { links } from '../../router/links'
</script>
