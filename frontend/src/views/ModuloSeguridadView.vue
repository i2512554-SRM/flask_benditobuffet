<template>
  <div>
    <div class="page-hero">
      <router-link to="/panel" class="btn btn-outline btn-back">
        <i class="fa-solid fa-arrow-left"></i> Volver al Panel
      </router-link>
      <h1>Seguridad y Accesos</h1>
      <p>Control de usuarios, roles, accesos y actividad del sistema</p>
    </div>

    <div class="modulo-grid">
      <router-link to="/personal/empleados" class="seccion-card">
        <div class="seccion-icon ic-blue"><i class="fa-solid fa-users-gear"></i></div>
        <h3>Usuarios</h3>
        <p>Cuentas de acceso de empleados y administradores.</p>
      </router-link>
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
      <router-link to="/seguridad/actividad" class="seccion-card">
        <div class="seccion-icon ic-cyan"><i class="fa-solid fa-clock-rotate-left"></i></div>
        <h3>Historial de Actividad</h3>
        <p>Registro detallado de las acciones de los usuarios.</p>
      </router-link>
    </div>
  </div>
</template>