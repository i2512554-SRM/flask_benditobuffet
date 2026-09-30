## Why

La aplicación funciona pero los dashboards por rol tienen desperdicio de espacio, el menú hamburguesa muestra opciones planas sin jerarquía, la Cajera es enviada directamente al Control de Caja en vez de a un panel interactivo, y no existe un gráfico de rendimiento financiero. Se requiere una mejora final de UI/UX que consolide el sistema como una herramienta profesional manteniendo el estilo minimalista, moderno y compacto actual (sin sidebar fijo ni cambio de identidad visual).

## What Changes

- **Menú hamburguesa jerárquico**: el menú (☰) se abre/cierra manualmente y agrupa las opciones en categorías desplegables con flecha ▸/▾. Las subcategorías solo aparecen con la categoría abierta. Solo se muestran categorías/funciones permitidas para el rol autenticado.
- **Dashboard por rol reforzado**: todos los roles inician en su propio dashboard con bienvenida personalizada (nombre + rol), fecha actual, resumen, acciones rápidas, notificaciones y actividad relevante, adaptadas a sus permisos.
- **Panel de Cajera interactivo**: la Cajera ya NO es enviada al Control de Caja al iniciar sesión. Su panel muestra bienvenida, resumen de caja (estado, monto inicial, ingresos, egresos, saldo), acciones rápidas. "Abrir Caja", "Registrar Ingreso" y "Registrar Egreso" abren el modal correspondiente DENTRO del panel (sin navegar); solo "Control de Caja" navega al módulo completo.
- **Monto inicial de caja**: la tabla `cierres_caja` gana la columna `monto_inicial`; `POST /api/caja/abrir` la recibe y persiste, y el resumen de caja muestra el valor registrado.
- **Rendimiento financiero (gráfico de líneas)**: apartado en los dashboards de Administrador (financiero general) y Cajera (su gestión de caja), con filtros Día/Semana/Mes/Año que recalculan el gráfico. Nuevo endpoint de agregación que usa las transacciones/cierres existentes de la BD (sin historial duplicado). Opcionalmente se pueden mostrar/ocultar Ingresos, Egresos y Ganancia.
- **Dashboard de Administrador**: distribución equilibrada bienvenida → resumen financiero (ventas, egresos, ganancia neta) → rendimiento financiero → notificaciones → acciones rápidas → actividad reciente, aprovechando el espacio horizontal sin agregar tarjetas de relleno.
- **Panel del Cocinero**: se mantiene su dashboard personalizado (bienvenida, resumen, stock bajo, agotados, solicitudes, notificaciones, acciones rápidas).
- **Panel del Trabajador**: solo información propia (próximo turno, último pago, estado de solicitudes, adelantos permitidos, notificaciones). Reforzar que no vea datos de otros trabajadores.
- **Permisos estrictos por rol**: el menú y las acciones solo exponen funciones permitidas (Admin: general; Cajera: dashboard + caja; Cocinero: dashboard + insumos/productos/stock/solicitudes; Trabajador: dashboard + su información/pagos/turnos/adelantos/solicitudes).
- **Estilo visual**: tarjetas pequeñas, iconos pequeños, sombras suaves, bordes redondeados, tipografía clara, animaciones suaves, responsive, sin zonas vacías grandes y sin excesos de tarjetas.

## Capabilities

### New Capabilities
- `menu-hamburguesa-jerarquico`: comportamiento del menú hamburguesa con categorías desplegables por rol.
- `dashboard-por-rol`: estructura y contenido de los dashboards personalizados por rol (bienvenida, resumen, acciones, notificaciones, actividad).
- `rendimiento-financiero`: gráfico de líneas con filtros Día/Semana/Mes/Año y endpoint de agregación sobre datos existentes.
- `monto-inicial-caja`: columna `monto_inicial`, apertura/cierre con monto inicial y despliegue en resumen de caja.

### Modified Capabilities
- (ninguna: `openspec/specs/` principal está vacía; el proyecto define capacidades dentro de cada cambio como deltas autónomos)

## Impact

- **Frontend** (`frontend/src/`): `components/layout/AppDrawer.vue` (menú jerárquico), `views/PanelAdminView.vue`, `views/PanelCajeraView.vue` (modales de apertura/ingreso/egreso en el panel + gráfico), vistas de Cocinero y Trabajador, nuevo componente `charts/LineChartFinanciero.vue`, nueva dependencia npm `chart.js` + `vue-chartjs`.
- **API** (`api/`): `caja.py` (`/abrir` acepta `monto_inicial`, `/actual` lo devuelve, nuevo endpoint de rendimiento por periodo), `admin.py`/`api` (endpoint de rendimiento financiero general), migración `ALTER TABLE cierres_caja ADD COLUMN monto_inicial` en Supabase (Postgres).
- **Modelo** (`models.py`): `CierreCaja.monto_inicial`.
- **Base de datos**: Supabase/Postgres — nueva columna `monto_inicial` con valor por defecto `0` y migración aplicada manualmente (el proyecto no tiene sistema de migraciones).
- **Dependencias**: `chart.js` y `vue-chartjs` (requieren `npm install`).
- **Router**: sin cambios de rutas; los dashboards ya son el destino por rol (`homeForRole`).