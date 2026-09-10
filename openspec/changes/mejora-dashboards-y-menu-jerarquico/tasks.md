## 1. Migración de BD: monto inicial

- [x] 1.1 Añadir `monto_inicial` al modelo `CierreCaja` (`models.py:227`, `Float`, `nullable=False`, `server_default='0'`, `default=0`) y verificar que aparece en `schemas/caja.py` (dump automático) sin romper el build
- [x] 1.2 Aplicar en Supabase `ALTER TABLE cierres_caja ADD COLUMN IF NOT EXISTS monto_inicial DOUBLE PRECISION NOT NULL DEFAULT 0;` y verificar con `SELECT monto_inicial FROM cierres_caja LIMIT 1`

## 2. Backend: apertura con monto inicial y resumen

- [x] 2.1 En `api/caja.py`, `POST /abrir` acepta `monto_inicial` opcional (float >= 0; error 400 si es negativo o no numérico) y lo persiste; verificar vía API abriendo caja con y sin monto
- [x] 2.2 `GET /actual` devuelve `monto_inicial` del cierre del día y `POST /cerrar` conserva el valor; verificar que el resumen responde incluyendo `monto_inicial`
- [x] 2.3 `PanelCajeraView.vue` muestra la tarjeta "Monto inicial / apertura" con el valor real persistido (no el fijo `S/. 0.00`); verificar que refleja el valor al abrir caja

## 3. Backend: endpoint de rendimiento financiero

- [x] 3.1 Crear `api/rendimiento.py` (blueprint `/api/rendimiento`) con acceso roles 1 y 2: agrega `TransaccionCaja` por periodo (`dia|semana|mes|anio`) y devuelve `[{ etiqueta, ingresos, egresos, ganancia }]`; Cajera filtra `id_usuario` propio
- [x] 3.2 Registrar blueprint en `app.py` y probar vía API (admin y cajera) que responde `200 success=True` para cada periodo y que no se crean tablas ni registros nuevos
- [x] 3.3 Verificar restricción por rol: un token de Cajera NO devuelve movimientos de otros usuarios en el gráfico

## 4. Frontend: gráfico de líneas

- [x] 4.1 Instalar `chart.js` y `vue-chartjs` (`npm install chart.js vue-chartjs`) y verificar que `npm run build` sigue compilando
- [x] 4.2 Crear `frontend/src/components/charts/LineChartFinanciero.vue` (chart de líneas, hasta 3 series Ingresos/Egresos/Ganancia, estilos minimalistas) y verificar que se renderiza sin errores de consola
- [x] 4.3 Integrar el componente con filtros Día/Semana/Mes/Año y checkboxes de indicadores (Ingresos/Egresos/Ganancia) en PanelAdmin y PanelCajera; verificar que al cambiar filtro se consume el nuevo periodo y el gráfico se actualiza

## 5. Frontend: menú hamburguesa jerárquico

- [x] 5.1 Reestructurar `AppDrawer.vue` con categorías desplegables: estado local de categorías abiertas, flecha ▸/▾ y subcategorías solo cuando la categoría está abierta; verificar el comportamiento de apertura/cierre y navegación
- [x] 5.2 Definir el mapa de menú por rol (Admin: Caja/Personal/Inventario/Seguridad/IA; Cajera: Caja + Mi Área; Cocinero: Cocina + Mi Área; Trabajador: Mi Área) y verificar en cada rol que solo se muestran sus opciones y todas sus rutas existen en el router

## 6. Frontend: Panel de Cajera con modales y gráfico

- [x] 6.1 Agregar Dialog de apertura con InputNumber de monto inicial que llama a `POST /api/caja/abrir` y refresca el resumen; verificar que abre caja sin salir del panel
- [x] 6.2 Agregar Dialog de ingreso y Dialog de egreso (tipo/monto/descripción) que llaman a `POST /api/caja/transacciones` y refrescan el panel; reemplazar los `router-link ?accion=` de estas tres acciones y dejar "Control de Caja" como único enlace a `/caja`; verificar que no ocurre navegación al abrir modales
- [x] 6.3 Añadir el apartado "Rendimiento financiero" (gráfico + filtros) al Panel de Cajera usando el endpoint de rendimiento; verificar pantalla en `900px` y versiones móvil

## 7. Frontend: Panel de Administrador

- [x] 7.1 Reorganizar `PanelAdminView.vue`: Bienvenida → Resumen financiero (ventas/egresos/ganancia neta) → Rendimiento financiero con gráfico → Acciones rápidas → Notificaciones → Actividad reciente (`/admin/actividad?limit=8`), en grid de 2 columnas sin grilla de "Módulos"; verificar que se aprovecha el espacio horizontal sin agregar tarjetas de relleno
- [x] 7.2 Verificar responsive (versión tablet 900px y móvil) y que el panel sigue mostrando las notificaciones existentes con enlaces válidos

## 8. Paneles Cocinero y Trabajador

- [x] 8.1 Verificar `CocinaDashboardView.vue` cumple con bienvenida + resumen + stock bajo/agotados + solicitudes + notificaciones + acciones rápidas (Insumos/Productos/Stock/Solicitudes); ajustar accesos del menú jerárquico y verificar el flujo por rol
- [x] 8.2 Verificar `TrabajadorDashboardView.vue` muestra solo información propia (próximo turno, último pago, estado de solicitudes, adelantos, notificaciones) y que no expone datos de otros trabajadores ni opciones no permitidas; Ajustar si el menú dejaba ver opciones de otros roles

## 9. Integración y verificación final

- [x] 9.1 `npm run build` compila sin errores y el servidor Flask sirve la app actualizada; verificar `GET /` y login de los 4 roles vía API
- [x] 9.2 Prueba integral en vivo: login de admin/cajera/cocinero/mozo, apertura de caja con monto inicial, registro de ingreso/egreso desde el panel de cajera, consulta de `/api/rendimiento` por periodo y estados de los dashboards (`success=True`); documentar resultados
  - Resultados (09/09/2026): logins OK en los 4 roles; `POST /caja/abrir {monto_inicial:100.50}` → `success=True`, persistido en `cierre.monto_inicial`; ingreso (Venta 45) y egreso (Gasto 12) registrados con `success=True`; `GET /caja/actual` refleja `monto_inicial=100.5, ventas=45, gastos=12, neto=33`; `/api/rendimiento` responde `success=True` para `dia|semana|mes|anio` (24/7/9/12 puntos); filtrado por rol: admin ve semana ingresos=57.5 (incluye venta propia 12.5 + cajera 45) y cajera1 solo ve lo suyo (ingresos=45, egresos=12); dashboards `cocina/dashboard` y `trabajador/dashboard` con `success=True`; cierre de caja posterior conserva `monto_inicial` y deja el entorno listo. La UI (modales/dialogs) consume los mismos endpoints verificados.
- [x] 9.3 Revisar que no queden referencias a `?accion=` en el panel de cajera ni opciones de menú de roles ajenos; corrección de cualquier inconsistencia detectada