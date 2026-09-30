## Why

El menú hamburguesa jerárquico quedó funcional pero sin la interacción depurada (apertura forzada, filtración plana, secciones vacías) y el Panel del Administrador aún muestra las notificaciones como texto plano sin tipo/prioridad/fecha y actividad basada en inicios de sesión. Además, "Caja" abarca dos vistas muy distintas bajo una sola ruta base (dashboard interactivo vs. control transaccional) que conviene separar con navegación propia, y el Panel de Cajera necesita el mismo submenú para no quedar huérfano respecto de sus dashboards. Se refina la UI/UX de cierre del ciclo manteniendo el estilo minimalista actual.

## What Changes

- **AppDrawer.vue**: reescritura de la interacción del menú — apertura manual estatal por botón/cierre (sin abrirse automáticamente por guard/apertura), flechas ▸/▾, indización visual por niveles, indicador vertical de la sección activa, hover/transiciones suaves, y estructura declarativa por rol (Panel Principal + categorías jerárquicas reales por rol, incluyendo Caja: Dashboard de Caja / Control de Caja / Movimientos / Historial de Cierres para Admin y Cajera).
- **Caché de métricas en el menú**: lema "La información está en el menú" — chips de métricas en vivo sobre los ítems de menú (panel y Control de Caja) usando endpoints existentes (`/panel/resumen`, `/caja/actual`), en formato moneda/entero compacto, coloreado por estado (`Monto inicial`, `Ventas`, `Saldo`).
- **Jerarquía de módulos de Caja**: nueva ruta base `/caja/dashboard` con `homeForRole` actualizado (Admin y Cajera llegan al Dashboard de Caja); vista `CajaDashboardView.vue` (bienvenida + resumen + acciones; solo tipo dashboard) y `CajaMovimientosView.vue` + `CajaHistorialView.vue` con datos desde `GET /api/caja/transacciones?historico=1` (backfill implícito por aperturas históricas). `/caja` queda como el módulo transaccional; `PanelCajeraView.vue` adopta el mismo submenú de Caja.
- **Panel de Administrador refinado**: notificaciones con chips de tipo/prioridad y fecha legible, actividad reciente operacional (pagos, cierres de caja, solicitudes, inversiones) desde `GET /api/admin/actividad-reciente` y distribucion en columnas; bienvenidas personalizadas por rol en todos los paneles.
- **Backend**: endpoint `GET /api/caja/transacciones` gana `?historico=1` para agregar movimientos históricos agrupados al detalle del día, y `GET /api/admin/actividad-reciente` agrega eventos operacionales de las tablas reales (orden por fecha, límite configurable).

## Capabilities

### New Capabilities
- `menu-hamburguesa-interactivo`: interacción completa del drawer (apertura manual, flechas, indización, estado activo, transiciones) y estructuras de menú declarativas por rol.
- `metricas-en-menu`: chips de métricas en vivo sobre ítems de menú con formato y color por estado.
- `modulos-caja-separados`: rutas `/caja/dashboard`, `/caja/movimientos`, `/caja/historial`, API `?historico=1` y navegación en panel/sidebar.
- `panel-admin-refinado`: notificaciones enriquecidas y actividad reciente operacional para el panel del Administrador.

### Modified Capabilities
- (ninguna: `openspec/specs/` principal está vacía; el proyecto define capacidades dentro de cada cambio como deltas autónomos)

## Impact

- **Frontend** (`frontend/src/`): `components/layout/AppDrawer.vue` (reescritura de interacción + estructuras + chips), `layouts/AppLayout.vue` (izquierda libre para que el menú maneje su apertura; apertura por ítem), `router/index.js` (`cajaBaseRoute`/`homeForRole`, rutas nuevas), `views/CajaDashboardView.vue`, `views/CajaMovimientosView.vue`, `views/CajaHistorialView.vue`, `views/PanelAdminView.vue`, `views/PanelCajeraView.vue`.
- **API** (`api/`): `caja.py` (`?historico=1`), `admin.py` (`/actividad-reciente`).
- **Router**: `homeForRole` de Admin y Cajera apuntan a `/caja/dashboard`.
- Sin cambios de esquema de base de datos ni dependencias nuevas.