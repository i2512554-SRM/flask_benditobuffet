<template>
  <div>
    <div class="page-hero">
      <router-link to="/panel" class="btn btn-outline btn-back">
        <i class="fa-solid fa-arrow-left"></i> Volver al Panel
      </router-link>
      <h1>Inventario e Inversión</h1>
      <p>Control de productos, compras, inversiones y movimientos de almacén</p>
    </div>

    <div class="modulo-grid">
      <router-link to="/inventario/operaciones?vista=productos" class="seccion-card">
        <div class="seccion-icon ic-orange"><i class="fa-solid fa-box-open"></i></div>
        <h3>Productos</h3>
        <p>Registro y edición de productos y equipamiento.</p>
        <span class="go-arrow"><i class="fa-solid fa-arrow-right"></i> Ingresar</span>
      </router-link>
      <router-link to="/inventario/operaciones?vista=productos" class="seccion-card">
        <div class="seccion-icon ic-blue"><i class="fa-solid fa-warehouse"></i></div>
        <h3>Stock</h3>
        <p>Stock actual, precios y valor total del almacén.</p>
      </router-link>
      <router-link to="/inventario/operaciones?vista=movimientos" class="seccion-card">
        <div class="seccion-icon ic-cyan"><i class="fa-solid fa-arrows-rotate"></i></div>
        <h3>Movimientos de Inventario</h3>
        <p>Entradas y salidas de productos y su trazabilidad.</p>
        <span class="go-arrow"><i class="fa-solid fa-arrow-right"></i> Ingresar</span>
      </router-link>
      <router-link to="/inventario/operaciones?vista=compras" class="seccion-card">
        <div class="seccion-icon ic-green"><i class="fa-solid fa-cart-shopping"></i></div>
        <h3>Compras</h3>
        <p>Registro de compras a proveedores con detalle.</p>
        <span class="go-arrow"><i class="fa-solid fa-arrow-right"></i> Ingresar</span>
      </router-link>
      <router-link to="/inventario/operaciones?vista=inversiones" class="seccion-card">
        <div class="seccion-icon ic-purple"><i class="fa-solid fa-chart-pie"></i></div>
        <h3>Inversiones</h3>
        <p>Registro y seguimiento de inversiones realizadas.</p>
        <span class="go-arrow"><i class="fa-solid fa-arrow-right"></i> Ingresar</span>
      </router-link>
      <router-link to="/inventario/reportes" class="seccion-card">
        <div class="seccion-icon ic-indigo"><i class="fa-solid fa-chart-column"></i></div>
        <h3>Reportes</h3>
        <p>Resumen del valor de inventario y tendencias del mes.</p>
        <span class="go-arrow"><i class="fa-solid fa-arrow-right"></i> Ingresar</span>
      </router-link>
    </div>
  </div>
</template>