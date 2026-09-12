<template>
  <div>
    <div class="page-hero">
      <VolverBtn to="/panel" />
      <h1>Seguridad y Accesos</h1>
      <p>Roles y accesos al sistema</p>
    </div>

    <div class="modulo-grid">
      <router-link to="/seguridad/roles" class="seccion-card">
        <div class="seccion-icon ic-purple"><i class="fa-solid fa-user-shield"></i></div>
        <h3>Roles</h3>
        <p>Roles del sistema y usuarios asignados.</p>
      </router-link>
      <router-link to="/seguridad/monitoreo" class="seccion-card">
        <div class="seccion-icon ic-red"><i class="fa-solid fa-shield-halved"></i></div>
        <h3>Accesos</h3>
        <p>Intentos de inicio de sesión, bloqueos y desbloqueos.</p>
      </router-link>
    </div>
  </div>
</template>