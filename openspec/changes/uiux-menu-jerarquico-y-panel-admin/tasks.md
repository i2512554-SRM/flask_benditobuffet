# Tareas UX/Caja/Admin — Menú jerárquico, métricas y panel admin

## Frontend — Menú (AppDrawer v2)

- [x] **`F1` AppDrawer.vue — estructura declarativa por rol**: `MENU_POR_ROL` (D1.1–D1.4) con `children`, `to` y `chip` opcional.
- [x] **`F2` Interacción**: apertura por botón (estado en App.vue), flechas ▸ animadas (rotación 90°), indización creciente, stagger 30ms, clic en ítem cierra, colapso por categoría con badge de conteo.
- [x] **`F3` Estado activo + indicador vertical** (`::before` 3px) y tinte primario.
- [x] **`F4` Chips de métricas**: fetch `/caja/actual` al abrir (roles 1/2), formato es-PE, tono ok/neutral/warn, no bloquea nav.
- [x] **`F5` App.vue**: ya controlaba apertura manual (`menuOpen`); sin cambios requeridos.

## Frontend — Caja

- [x] **`F6` Router**: `homeForRole` Admin/Cajera → `/caja/dashboard`; rutas `cajaDashboard`, `cajaMovimientos`, `cajaHistorial`.
- [x] **`F7` CajaDashboardView.vue** (bienvenida por rol + resumen + módulos de caja).
- [x] **`F8` CajaMovimientosView.vue** (DataTable + toggle Hoy/Histórico).
- [x] **`F9` CajaHistorialView.vue** (resumen y tabla de cierres).
- [x] **`F10` Acciones de caja**: PanelAdmin y PanelCajera apuntan a rutas nuevas; drawer incluye Dashboard/Movimientos/Historial.

## Frontend — Panel Admin

- [x] **`F11` Notificaciones con chips**: prioridad (Alta/Media/Baja) + fecha + enlace.
- [x] **`F12` Actividad reciente operacional** consumiendo `/admin/actividad-reciente`.
- [x] **`F13` Rebalancear grid**: gráfico a la izquierda; notificaciones + acciones + actividad a la derecha.
- [x] **`F14` Bienvenidas por rol**: textos de Admin, Cajera, Cocinero y Trabajador.

## Backend

- [x] **`F15` `GET /api/caja/transacciones?historico=1`**: `historico` (cierres desc) + `ultimos_movimientos`.
- [x] **`F16` `GET /api/admin/actividad-reciente?limit=N`** (pagos, cierres, adelantos, solicitudes, inversiones).

## Verificación

- [x] **`F17`** Build frontend (`npm run build`) sin errores.
- [x] **`F18`** Flask importa OK; rutas `/api/admin/actividad-reciente` y `/api/caja/transacciones` registradas.
- [ ] **`F19`** Revisión manual de estructuras de menú por los 4 roles (queda para el usuario).