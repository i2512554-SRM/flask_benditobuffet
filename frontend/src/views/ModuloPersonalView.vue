<template>
  <div>
    <div class="page-hero">
      <router-link to="/panel" class="btn btn-outline btn-back">
        <i class="fa-solid fa-arrow-left"></i> Volver al Panel
      </router-link>
      <h1>Gestión del Personal</h1>
      <p>Administra a tu equipo: empleados, pagos, turnos, adelantos y solicitudes</p>
    </div>

    <div class="modulo-grid">
      <router-link to="/personal/empleados" class="seccion-card">
        <div class="seccion-icon ic-blue"><i class="fa-solid fa-users"></i></div>
        <h3>Empleados</h3>
        <p>Registro, edición y estado del personal del restaurante.</p>
        <span class="go-arrow"><i class="fa-solid fa-arrow-right"></i> Ingresar</span>
      </router-link>
      <router-link to="/personal/pagos" class="seccion-card">
        <div class="seccion-icon ic-green"><i class="fa-solid fa-money-bill-wave"></i></div>
        <h3>Pagos</h3>
        <p>Registro de pagos, boletas y penalizaciones del personal.</p>
        <span class="go-arrow"><i class="fa-solid fa-arrow-right"></i> Ingresar</span>
      </router-link>
      <router-link to="/personal/turnos" class="seccion-card">
        <div class="seccion-icon ic-indigo"><i class="fa-solid fa-calendar-days"></i></div>
        <h3>Turnos</h3>
        <p>Asignación y edición de turnos de trabajo del equipo.</p>
        <span class="go-arrow"><i class="fa-solid fa-arrow-right"></i> Ingresar</span>
      </router-link>
      <router-link to="/personal/adelantos" class="seccion-card">
        <div class="seccion-icon ic-amber"><i class="fa-solid fa-file-invoice-dollar"></i></div>
        <h3>Adelantos</h3>
        <p>Solicitudes de adelanto de sueldo y su gestión.</p>
        <span class="go-arrow"><i class="fa-solid fa-arrow-right"></i> Ingresar</span>
      </router-link>
      <router-link to="/personal/solicitudes" class="seccion-card">
        <div class="seccion-icon ic-purple"><i class="fa-solid fa-file-pen"></i></div>
        <h3>Solicitudes</h3>
        <p>Solicitudes de insumos y peticiones del personal.</p>
        <span class="go-arrow"><i class="fa-solid fa-arrow-right"></i> Ingresar</span>
      </router-link>
      <router-link to="/personal/salarios" class="seccion-card">
        <div class="seccion-icon ic-cyan"><i class="fa-solid fa-coins"></i></div>
        <h3>Salarios</h3>
        <p>Planillas, sueldos y detalle de salarios del mes.</p>
        <span class="go-arrow"><i class="fa-solid fa-arrow-right"></i> Ingresar</span>
      </router-link>
      <router-link to="/seguridad/roles" class="seccion-card">
        <div class="seccion-icon ic-red"><i class="fa-solid fa-user-shield"></i></div>
        <h3>Roles</h3>
        <p>Roles del sistema y usuarios asignados a cada uno.</p>
        <span class="go-arrow"><i class="fa-solid fa-arrow-right"></i> Ingresar</span>
      </router-link>
    </div>
  </div>
</template>