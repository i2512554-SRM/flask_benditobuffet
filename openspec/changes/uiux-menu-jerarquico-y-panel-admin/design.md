## Context

- Frontend Vue 3 + PrimeVue 5 + Pinia (`frontend/src`), servido estático desde Flask (`frontend/dist`). Sin `npm proxy` de dev.
- `AppDrawer.vue` ya existe con menú jerárquico por rol (change anterior) pero: la apertura/cierre la fuerza `AppLayout.vue` (drawer(s) autoabriéndose), el menú no tiene interacción visual afinada (flechas, indización, hover, estado activo) ni chips de métricas, y la estructura por rol quedó a medias (categoría "Caja" incompleta, secciones "Mi Área" hipotéticas).
- Backend Flask + SQLAlchemy sobre Supabase/Postgres. `api/caja.py` ya tiene `GET /api/caja/transacciones` (solo movimientos del día y del cierre actual); `api/admin.py` tiene `GET /api/admin/alertas-resumen`, `GET /api/admin/actividad` (basada en `actividad_logs` = logins, query "logins recientes") y `GET /api/admin/resumen`.
- Modelos existentes con datos suficientes para una actividad "operacional": `Pago`, `SolicitudAdelanto`, `SolicitudMaterial`/`SolicitudInsumo`, `OperacionInversion`, `CierreCaja`, `TransaccionCaja`, `TurnoPersonal`, `MovimientoInventario`.
- `homeForRole` actual: Admin → `/admin`, Cajera → `/caja`, Cocinero → `/panel-cocinero`, Trabajador → `/panel-trabajador`. decidido: Admin y Cajera → `/caja/dashboard`.

## Goals / Non-Goals

**Goals:**
- Menú hamburguesa con interacción manual, jerarquía real por rol, indización visual, estado activo e indicador, métricas en chips, sin sidebar.
- `/caja/dashboard` como panel-tipo-dashboard y `/caja`, `/caja/movimientos`, `/caja/historial` como módulos de control/datos; `homeForRole` actualizado.
- `/api/caja/transacciones?historico=1` para movimientos y cierres históricos (backfill).
- Panel Admin: notificaciones con chips de tipo/prioridad/fecha, actividad reciente operacional (no logins), todo el panel leído en una sola visita.

**Non-Goals:**
- No cambiar CajaReportesView, CajaView (`?accion=`), No rediseñar identidad. No crear tablas nuevas. No tocar la lógica de pagos/adelantos en sí.

## Decisions

### D1. Estructura de menú declarativa por rol (dato, no template)
Se define una sola constante `MENU_POR_ROL` en `AppDrawer.vue` con la forma:
`{ id, label, to?, children? }[]`. Las categorías ("Caja", "Personal", "Inventario e Inversión", "Seguridad", "Mi Área", "Cocina") son nodos con `children`; los ítems reciben `to`. Cada ítem puede llevar `metric:{ key }` para renderizar el chip. Los nodos van ocultos si el conjunto resultante para el rol queda vacío (filter de children).

D1.1 **Admin**: Panel Principal (`/admin`), Caja→[Dashboard de Caja `/caja/dashboard`, Control de Caja `/caja` (chip ventas), Movimientos `/caja/movimientos`, Historial de Cierres `/caja/historial`], Personal→[Empleados `/admin/personal`, Pagos `/admin/pagos`, Turnos `/admin/turnos`, Adelantos `/admin/adelantos`, Solicitudes `/admin/solicitudes`, Salarios `/admin/salarios`], Inventario e Inversión→[Módulo `/admin/inventario`, Operaciones `/admin/operaciones`, Reportes `/admin/reportes`], Seguridad→[Monitoreo `/admin/monitoreo`, Roles `/admin/roles`, Actividad `/admin/actividad`], IA Predictiva `/admin/ia-predictiva`.
D1.2 **Cajera**: Panel Principal `/panel-cajera`, Caja→[Dashboard de Caja `/caja/dashboard`, Control de Caja `/caja`, Movimientos `/caja/movimientos`, Historial de Cierres `/caja/historial`], Mi Área→[Información `/cajera/informacion`, Turnos `/cajera/turnos`, Pagos `/cajera/pagos`, Notificaciones `/cajera/notificaciones`].
D1.3 **Cocinero**: Panel Principal `/panel-cocinero`, Cocina→[Insumos `/admin/inventario`, Solicitudes `/cocinero/solicitudes`, Alertas `/cocinero/alertas`], Mi Área→ídem Cajera.
D1.4 **Trabajador**: Panel Principal `/panel-trabajador`, Mi Área→ídem.

### D2. Interacción y estilo del drawer
- Layout: `AppLayout.vue` deja de abrir el drawer automáticamente (quita el `open="true"`/watch por guard); `AppDrawer.vue` expone `open(value)` para que `AppLayout` (o el botón ☰ global) solo invierta el estado. El drawer mantiene su pin físico al topbar.
- Cada categoría es un botón con flecha `▸`/`▾` (lado izquierdo) — flecha rota 90° con transición. Sub-ítems anidados con indentación creciente (12px por nivel), tipografía un punto menor por nivel.
- Ítem activo: fondo `primary` tinte 8%, texto en `--primary-color`, y barra vertical de 3px izquierda rotulada con `--primary-color`. Hover suave. Transición en stagger (~30ms por nivel) al abrir categorías; no hay animación al cerrar hacia arriba (inmediato, menos mareo).
- Estado de apertura por categoría en `Set` local; se abre la visita inicial a `Caja`.
- Clic en ítem cierra el drawer.

### D3. Chips de métricas en el menú
Dentro del drawer, al abrirse, `onMounted` dispara fetch en paralelo: `GET /panel/resumen` y `GET /caja/actual` (si role ∈ {1,2,3}). Mapeo: `Panel Principal` → resumen.caja.monto_inicial o resumen contable por rol; `Control de Caja` → `S/. <ventas>` / `Saldo: <neto>` si la caja está abierta y `Caja cerrada` en gris si no. Formato compacto (`Intl.NumberFormat('es-PE')`) y chip a la derecha con color por estado. Reintento único; si falla, no se muestra el chip (nunca bloquea la navegación).

### D4. Rutas de Caja
Se crean 3 vistas: `CajaDashboardView.vue` (bienvenida + 4 tarjetas de resumen + acciones rápidas + guiño al graph existente con Chart en `/caja/reportes`), `CajaMovimientosView.vue` (tabla con DataTable movimientos del día + historial toggle), `CajaHistorialView.vue` (tabla de cierres con montos y saldo). `homeForRole` → Admin y Cajera a `/caja/dashboard`. Los "Acciones en Caja" de AppDrawer, PanelAdminView y PanelCajeraView enlazarán a estas rutas.

### D5. `/caja/transacciones?historico=1`
El endpoint ya devuelve `transacciones` del día. Con `?historico=1` devuelve `historico`: lista de `{ cierre_id, cerrado, ventas, gastos, neto, fecha }` para todos los cierres (desc), además de `transacciones`: última `limit` de `TransaccionCaja` (todas las fechas). Compatible con el serializador de cierre existente.

### D6. Panel Admin refinado
- Notificaciones/alertas: el bloque deja de ser texto plano → chips. Se toma `/admin/alertas-resumen` existente (={admin:..., logistica:..., ...}) y se renderiza cada alerta como tarjeta pequeña con icono por tipo, "pill" de prioridad (Alta=roja, Media=ámbar, Baja=azul) y fecha legible (relativa o `dd/MM/yyyy`). Si el backend no entrega prioridad se asigna heurística según sección (p.ej. agotado→Alta, stock bajo→Media, solicitudes→Media).
- Actividad reciente: nuevo endpoint `GET /api/admin/actividad-reciente?limit=10` que une `Pago` (aprobado/pendiente), `CierreCaja` + `TransaccionCaja` (cierre diario), `SolicitudAdelanto` (estado), `SolicitudMaterial` (pendiente/aprobada), `OperacionInversion` (registro). Devuelve `[{ id, tipo, titulo, descripcion, fecha, icono }]` ordenado desc por fecha. El panel lo usa y mantiene el feed de actividad de logins solo en `/admin/actividad`.
- Layout del panel: fila 1 bienvenida + fecha + botones rápidos; fila 2 grid 4 tarjetas resumen (ventas, egresos, ganancia, caja); fila 3 grid 2 columnas (gráfico rendimiento | notificaciones+actividad con scroll independiente). Se afloja el grid rígido actual.

### D7. Bienvenidas por rol
Constante `WELCOME_*` por panel con emoji discreto, nombre y subtexto contextual (p.ej. Admin: "Resumen operativo" / Cajera "Bienvenida" / Cocinero "Tu cocina a un vistazo" / Trabajador "Tu espacio personal"). Solo retocar textos y layout de cabecera, sin tocar la lógica de fetch de cada vista.

## Risks

- **R1** Cambio de reducir columnas en `TransaccionCaja`.fecha con Pandas: el backend usa SQLAlchemy, no Pandas; la agregación `?historico=1` es de arranque y agrupa con SQL (`func.date`) — riesgo menor. El planing anterior descartó pandas.
- **R2** Editar `AppLayout.vue` (apertura del drawer) puede romper el flujo de "autoabrir tras login" de versiones anteriores; el guard ya coloca al usuario en su home, por lo que quitar la apertura automática es seguro y deseado.
- **R3** `PanelCajeraView.vue` y `PanelAdminView.vue` se editan en dos changes (este y el anterior); merge manual restringido a bloques (cabecera y acción) sin tocar fetch.