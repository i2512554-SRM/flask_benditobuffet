## Context

- Frontend Vue 3 + PrimeVue 5 + Pinia, servido como estático desde Flask (`frontend/dist`); sin proxy de dev; sin librería de gráficos instalada.
- Backend Flask + SQLAlchemy sobre Supabase/Postgres (`bd.py`, `app.py`). No existe sistema de migraciones (sin Alembic ni scripts SQL); las tablas ya existen en Supabase. `app.py` no llama `db.create_all()`.
- `CierreCaja` (`models.py:227`) no tiene `monto_inicial`; `/api/caja/abrir` abre en 0; `/api/caja/actual` devuelve `abierta, cierre, ventas_dia, gastos_dia, neto_dia, transacciones`.
- `TransaccionCaja` es la fuente histórica de movimientos (tipo Venta/Gasto, monto, fecha) y `CierreCaja` guarda totales por cierre. Son los únicos datos para el gráfico (sin duplicados).
- El menú actual (`AppDrawer.vue`) es plano con secciones; los dashboards ya reciben el destino por rol (`homeForRole` en `router/index.js`).
- Ver ref. `proposal.md` para motivación y `specs/` para el contrato de comportamiento.

## Goals / Non-Goals

**Goals:**
- Menú jerárquico por rol en `AppDrawer.vue` sin volver a un sidebar.
- Panel de Cajera con modales propios (apertura con monto inicial, ingreso, egreso) y gráfico.
- Panel de Admin con resumen financiero, gráfico, notificaciones, acciones y actividad reciente, mejor uso del espacio.
- Endpoint único de rendimiento por periodo para Admin y Cajera.
- Persistir `monto_inicial` en Supabase con una migración mínima y defensiva.

**Non-Goals:**
- No rediseñar la identidad visual, no sidebar fijo, no reorganizar rutas del router.
- No crear tablas ni historiales nuevos para alimentar el gráfico.
- No cambiar el gráfico de "Reportes Financieros" existente (`CajaReportesView`).
- No tocar la lógica de permisos del guard/router salvo que el menú lo requiera para ocultar opciones.

## Decisions

### D1. Endpoint de rendimiento financiero (nuevo, compartido)
Se crea `GET /api/rendimiento?periodo=dia|semana|mes|anio` accesible por roles 1 y 2 (Admin ve todas las transacciones; Cajera ve solo las suyas). Agrupa `TransaccionCaja` por tramo de tiempo (hora del día / día / semana / mes) y devuelve `[{ etiqueta, ingresos, egresos, ganancia }]`. La data sale de los movimientos existentes (la cajera además recibe el cierre del día para no duplicar).
- **Alternativa**: endpoint separado por rol (`/admin/rendimiento`, `/caja/rendimiento`). Se descarta para reutilizar la misma serialización y reducir código; la autorización se resuelve con el identidad del JWT.
- Sitio propuesto: nuevo módulo `api/rendimiento.py` o reutilizar `api/caja.py`; se decide por **nuevo blueprint `api/rendimiento.py`** para no inflar `caja.py` y centralizar la agregación.

### D2. Gráfico de líneas con chart.js + vue-chartjs
Se instala `chart.js` y `vue-chartjs` (decisión del usuario) y se crea `frontend/src/components/charts/LineChartFinanciero.vue` que recibe `{ data, indicadores }` y dibuja hasta 3 series (Ingresos, Egresos, Ganancia) con checkboxes independientes. Configuración minimalista (sin grid agresivo, tooltips en es-PE, colores de la paleta existente).
- **Alternativa**: SVG propio (menos dependencias) — descartada por elección explícita del usuario.

### D3. `monto_inicial` en `cierres_caja`
- `models.py`: añadir `monto_inicial = db.Column(db.Float, nullable=False, server_default='0', default=0)`.
- Migración: `ALTER TABLE cierres_caja ADD COLUMN IF NOT EXISTS monto_inicial DOUBLE PRECISION NOT NULL DEFAULT 0;` ejecutada contra Supabase (psql/smart client). Se hace idempotente (`IF NOT EXISTS`).
- `POST /api/caja/abrir` acepta `monto_inicial` opcional (float >= 0); `GET /api/caja/actual` incluye `monto_inicial` del cierre; el cierre (`cerrar`) lo conserva.
- Defensa en runtime: si por cualquier razón la columna no existiera (migración pendiente), el alta de caja con monto inicial falle claramente y el panel muestre 0 (ver Riesgos R1).
- **Alternativa**: solo modal sin persistencia — descartada por decisión del usuario.

### D4. Panel de Cajera con modales propios
`PanelCajeraView.vue` incorpora los Dialog de PrimeVue (Apertura con InputNumber de monto inicial; Ingreso y Egreso con tipo + monto + descripción) que llaman a `/api/caja/abrir` y `POST /api/caja/transacciones` y refrescan el panel. Se retiran los `router-link` con `?accion=...` para las tres primeras acciones (se mantiene la ruta `/caja?accion=` en `CajaView.vue`, sin cambios). "Control de Caja" conserva su enlace a `/caja`. El resumen muestra `monto_inicial` real del cierre en vez del valor fijo `S/. 0.00`.

### D5. Panel de Admin rebalanceado
`PanelAdminView.vue` se reorganiza a 2 columnas principales (grid `1fr 1.2fr`): columna de resumen/gráfico y columna de notificaciones/actividad; debajo acciones rápidas y actividad reciente (usa `/admin/actividad?limit=8` existente). Se elimina la grilla de "Módulos" de relleno, manteniendo el orden Bienvenida → Resumen → Gráfico → Acciones → Notificaciones/Actividad.

### D6. Menú jerárquico por rol
`AppDrawer.vue` se reestructura con estado `abiertas` (set de categorías expandidas) y un mapa de menú por rol:
- Admin: `Panel Principal` (link) + categorías `Caja` (Control de Caja, Reportes Financieros), `Personal` (Empleados, Pagos, Turnos, Adelantos, Solicitudes, Salarios), `Inventario e Inversión` (Módulo, Operaciones, Reportes), `Seguridad` (Monitoreo, Roles, Actividad), `IA Predictiva` (link).
- Cajera: su panel + `Caja` (Control de Caja) + `Mi Área` (Información, Turnos, Pagos, Notificaciones).
- Cocinero: su panel + `Cocina` (Insumos, Productos*, Stock*, Solicitudes, Alertas) + `Mi Área`.
  - *Productos/Stock viven dentro de `CocinaInventarioView`; el ítem "Insumos" es el único path; se mapean "Productos" y "Stock" a la misma ruta con ancla/vista si aplica, si no se omiten como ítems duplicados y se deja "Insumos + Stock + Solicitudes" (se valida contra la vista real en implementación).
- Trabajador: su panel + `Mi Área` (Información, Turnos, Pagos, Notificaciones).
Flecha ▸/▾ por categoría; solo subcategorías visibles si la categoría está abierta; el estado de apertura es local al drawer (se reinicia al abrir el menú para UX predecible).

### D7. Notificaciones y actividad recurrentes
Se reutilizan los endpoints existentes (`/admin/alertas-resumen`, `/admin/actividad`) y la notificación client-side de cada vista; no se crean servicios nuevos.

## Risks / Trade-offs

- **[R1] Migración de BD sin sistema de migraciones** → `ALTER TABLE ... IF NOT EXISTS` idempotente; el código tolera ausencia (monto inicial 0) y se documenta el SQL en el PR. Prueba con un `SELECT` tras aplicar.
- **[R2] chart.js incrementa el bundle** → se importa solo el componente de línea (tree-shaking) y la vista lo carga lazy por la ruta; bundle final sigue siendo aceptable.
- **[R3] Cajera ve solo sus movimientos en el gráfico** → restricción por `id_usuario` en el endpoint; verificar con credenciales distintas en pruebas.
- **[R4] Cambiar la tarjeta "Monto inicial" fija** → al añadir el valor real, datos históricos previos muestran 0 (valor por defecto), coherente con el comportamiento anterior.
- **[R5] Duplicación semántica "Control de Caja" (ruta + modal)** → se mantiene el flujo único de `CajaView.vue` inalterado; el panel solo abre modales propios, evitando estados duplicados.

## Migration Plan

1. Aplicar migración SQL en Supabase: `ALTER TABLE cierres_caja ADD COLUMN IF NOT EXISTS monto_inicial DOUBLE PRECISION NOT NULL DEFAULT 0;`
2. Desplegar backend (modelo + endpoints) y frontend (`npm install chart.js vue-chartjs`, `npm run build`).
3. Verificar: abrir caja con y sin monto inicial; resumir en panel; consultar `/api/rendimiento?periodo=mes` como admin y cajera.

## Open Questions

- Ninguna que cambie specs/approach: mientras que la carpeta exacta de Productos/Stock dentro de `CocinaInventarioView` (D6) se resuelve en implementación sin afectar el comportamiento especificado.