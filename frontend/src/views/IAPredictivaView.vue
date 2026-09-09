<template>
  <div>
    <div class="page-hero">
      <router-link to="/panel" class="btn btn-outline btn-back">
        <i class="fa-solid fa-arrow-left"></i> Volver al Panel
      </router-link>
      <h1>IA Predictiva</h1>
      <p>Análisis avanzado de los datos del restaurante</p>
    </div>

    <div class="modulo-grid">
      <div class="seccion-card">
        <div class="seccion-icon ic-blue"><i class="fa-solid fa-chart-line"></i></div>
        <h3>Predicción de Ventas</h3>
        <p>Proyección de ventas por día y por mes según el historial de la caja.</p>
      </div>
      <div class="seccion-card">
        <div class="seccion-icon ic-purple"><i class="fa-solid fa-boxes-stacked"></i></div>
        <h3>Demanda de Insumos</h3>
        <p>Estimación de consumo y recomendaciones de reabastecimiento.</p>
      </div>
      <div class="seccion-card">
        <div class="seccion-icon ic-green"><i class="fa-solid fa-coins"></i></div>
        <h3>Rentabilidad Proyectada</h3>
        <p>Cálculo de rentabilidad y detección de tendencias del negocio.</p>
      </div>
      <div class="seccion-card">
        <div class="seccion-icon ic-orange"><i class="fa-solid fa-users"></i></div>
        <h3>Análisis de Personal</h3>
        <p>Comportamiento de pagos, turnos y adelantos del equipo.</p>
      </div>
    </div>

    <div class="ia-nota">
      <i class="fa-solid fa-microchip"></i>
      <div>
        <strong>Módulo en integración</strong>
        <p>Los análisis predictivos se habilitarán progresivamente conforme se acumulen datos históricos en el sistema.</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.ia-nota {
  display: flex;
  align-items: flex-start;
  gap: 0.9rem;
  margin-top: 1.5rem;
  padding: 1.25rem;
  border-radius: 14px;
  border: 1px dashed var(--border-color);
  background: var(--bg-card);
  color: var(--text-muted);
  font-size: 0.85rem;
}

.ia-nota i {
  font-size: 1.3rem;
  color: var(--btn-primary);
  margin-top: 0.15rem;
}

.ia-nota strong {
  display: block;
  color: var(--text-main);
  margin-bottom: 0.25rem;
}

.ia-nota p {
  margin: 0;
  line-height: 1.5;
}
</style>