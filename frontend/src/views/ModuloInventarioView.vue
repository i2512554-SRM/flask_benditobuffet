<template>
  <div>
    <div class="page-hero">
      <VolverBtn to="/panel" />
      <h1>Inventario e Inversión</h1>
      <p>Control de productos, compras, inversiones y movimientos de almacén</p>
    </div>

    <div class="modulo-grid">
      <router-link to="/inventario/operaciones?vista=productos" class="seccion-card">
        <div class="seccion-icon ic-orange"><i class="fa-solid fa-box-open"></i></div>
        <h3>Productos</h3>
        <p>Registro, edición y desactivación de productos con sus unidades.</p>
        <span class="go-arrow"><i class="fa-solid fa-arrow-right"></i> Ingresar</span>
      </router-link>
      <router-link to="/inventario/operaciones?vista=productos&accion=entrada" class="seccion-card">
        <div class="seccion-icon ic-blue"><i class="fa-solid fa-right-left"></i></div>
        <h3>Entradas y Salidas</h3>
        <p>Agregar stock y registrar salidas de los productos del almacén.</p>
        <span class="go-arrow"><i class="fa-solid fa-arrow-right"></i> Ingresar</span>
      </router-link>
      <router-link to="/inventario/operaciones?vista=movimientos" class="seccion-card">
        <div class="seccion-icon ic-cyan"><i class="fa-solid fa-clock-rotate-left"></i></div>
        <h3>Movimientos</h3>
        <p>Historial con stock anterior/posterior, motivo y responsable.</p>
        <span class="go-arrow"><i class="fa-solid fa-arrow-right"></i> Ingresar</span>
      </router-link>
      <router-link v-if="auth.userRole === 1" to="/inventario/operaciones?vista=compras" class="seccion-card">
        <div class="seccion-icon ic-green"><i class="fa-solid fa-cart-shopping"></i></div>
        <h3>Inversiones (compras)</h3>
        <p>Compra de productos con cantidad y precio; proveedor opcional.</p>
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
<script setup>
import { useAuthStore } from '../stores/auth'
const auth = useAuthStore()
</script>
