## Context

El módulo actual (ver proposal.md) usa `productos` con solo nombre/precio/stock/id_categoria/fechas, `inventario_movimientos` con tipo/cantidad/observación, y un único flujo "Agregar producto" que permite duplicados (la BD ya tiene dos "Arroz" — ids 9 y 10). No hay unidad de medida, estado ni stocks anterior/posterior. La BD es PostgreSQL remota (Supabase), por lo que los cambios de esquema no se propagan con `db.create_all()`; el proyecto ya usa el patrón de scripts idempotentes (`automatizacion_caja/crear_indices.py`).

Roles vigentes (numéricos): 1 administrador, 2 cajera, 3 cocinero, 4 trabajador. El frontend es Vue 3 + PrimeVue servido desde `frontend/dist`.

## Goals / Non-Goals

**Goals:**
- Separación conceptual y funcional entre producto, entrada, salida e historial.
- Unidad de medida asociada al producto y stock nunca negativo.
- Prevención de duplicados (case-insensitive) y deduplicación del "Arroz" existente.
- Historial con trazabilidad completa (stock anterior/posterior, motivo, usuario).
- Permisos diferenciados: admin (gestión total) y cocinero (ver, agregar stock, salidas, historial); trabajador sin acceso.

**Non-Goals:**
- No se introduce costo/origen de inventario por proveedor, ni recetas/desglose de recetas (requiere referencia a ventas).
- No se replica la gestión en el panel de caja.
- No se reescribe el módulo de compras/inversiones/reportes; solo se ajusta su serialización de stock para alimentar el historial.

## Decisions

### D1. Cambios de esquema en `productos` e `inventario_movimientos`
- `productos`: `unidad_medida VARCHAR(10) NOT NULL DEFAULT 'Un'`, `descripcion VARCHAR(255)`, `estado BOOLEAN NOT NULL DEFAULT TRUE`.
- `inventario_movimientos`: `stock_anterior NUMERIC`, `stock_posterior NUMERIC`, `motivo VARCHAR(255)`.
- Se conservan `precio` e `id_categoria` (esquema actual los exige NOT NULL). La categoría se mantiene como agrupación; `precio` se conserva para no romper el valor económico del inventario (`productos.precio * stock`).
- Alternativa considerada: nueva tabla `unidades_medida` normalizada. Se descarta por simplicidad (solo 3 valores fijos y validados en aplicación).

### D2. Migración dirigida y deduplicación
Nuevo script `automatizacion_caja/migrar_inventario.py` (idempotente, mismo patrón que `crear_indices.py`):
1. `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` para las columnas nuevas (Postgres).
2. Normaliza `productos.nombre` existentes (trileado) y detecta duplicados case-insensitive.
3. Para cada grupo duplicado: conserva el `id_producto` de menor id como "maestro", suma los stocks, reasigna a él los `inventario_movimientos`, `detalle_compras_inventario` y referencias de otras tablas que apunten al duplicado, y elimina el registro sobrante. Verifica que ninguna tabla con FK a `productos` conserve referencias huérfanas.
4. Relena `stock_anterior/stock_posterior` de los movimientos existentes (recalculando acumulando por producto) cuando sea posible.

### D3. Permisos por endpoint mediante decoradores
- `_solo_admin`: rol 1 → crear/editar/desactivar productos, categorías, proveedores, compras, inversiones, ajuste manual.
- `_inventario_stock`: roles [1, 3] → `GET /productos`, `GET /productos/<id>`, `GET /movimientos`, `POST` entrada y salida.
- El acceso del trabajador se bloquea en frontend (router/drawer) y en backend (los decoradores rechazan rol 4).

### D4. API de stock separada de la creación
- `POST /inventario/productos` → crea producto; valida duplicado case-insensitive; si existe responde `409` con `{ error: "El producto ya existe...", existe: true }` y el `id_producto` del existente (para navegar directo a "Agregar stock"). Con stock inicial > 0 crea el primer movimiento "Entrada" (stock_anterior=0, posterior=stock inicial).
- `POST /inventario/productos/<id>/stock/entrada`: body `{ cantidad }`. Valida producto activo y cantidad > 0; registra "Entrada" con stock_anterior/posterior y motivo "Ingreso de stock".
- `POST /inventario/productos/<id>/stock/salida`: body `{ cantidad, motivo }`. Valida producto activo, cantidad > 0, motivo no vacío y `stock - cantidad >= 0`; responde `400` "No hay suficiente stock disponible" en caso contrario; registra "Salida" con stocks anterior/posterior.
- `DELETE /inventario/productos/<id>` → si el producto tiene movimientos se desactiva (lógico); si no tiene ninguno se elimina físicamente. `PUT /productos/<id>` solo acepta nombre/unidad/descripción/estado/categoría/precio e ignora `stock`.
- Se mantiene `PUT /productos/<id>/stock` (ajuste manual, admin) por compatibilidad, pero el nuevo frontend no lo usa.

### D5. Compra/anulación alimentan el historial
`POST /compras` y `DELETE /compras/<id>` (anulación) seguirán actualizando stock, pero ahora escriben `stock_anterior/stock_posterior`/`motivo` en cada `InventarioMovimiento` generado. La anulación usa tipo "Salida" con motivo "Anulación de compra …".

### D6. Frontend
- `InventarioView.vue` reestructurado: barra de acciones `[+ Nuevo producto] [+ Agregar stock] [− Registrar salida]`, listado con columnas Producto / Unidad / Stock actual (con unidad) / Estado / acciones (`Ver`, `Editar`, `Agregar stock`, `Registrar salida`, `Desactivar`/`Activar`). Dialog de creación con validación de duplicado (cliente consulta el 409 y ofrece ir a "Agregar stock"). El historial conserva la pestaña existente y agrega columnas unidad/stock anterior/posterior/motivo.
- `CocinaInventarioView.vue`: muestra unidad y estado activo; para rol 3 habilita "Agregar stock" y "Registrar salida" (llama a los mismos endpoints) y un acceso al historial de movimientos.
- `ModuloInventarioView.vue` y `AppDrawer.vue`: se actualizan textos para diferenciar "Productos", "Entradas/Salidas" y "Movimientos".

### D7. Serialización y cocina
- `schemas/inventario.py`: ProductoSchema e InventarioMovimientoSchema incluyen los nuevos campos.
- `api/cocina.py`: `_serializar_producto` agrega `unidad_medida` y excluye productos inactivos.

## Risks / Trade-offs

- **Deduplicación en BD viva** → hacer backup/las cuentas antes de correr, script de un solo sentido y verificación de FKs huérfanas posterior.
- **`precio` e `id_categoria` fuera del formulario propuesto por el usuario** → se conservan como campos del modelo (requeridos por el esquema actual); el form admite categoría y precio opcional para no romper el valor del inventario.
- **Cocina toca stock directamente** → el motivo es obligatorio y el responsable queda registrado; mitigado por permisos backend.
- **Cambio de comportamiento DELETE** (de físico a lógico) → visible en la UI (botón "Desactivar"/"Activar") y en el 409/descripción de la API.
- **`dist` desactualizado / servidor no reiniciado** → se debe rebuildear el frontend y reiniciar Flask para ver los cambios.

## Migration Plan

1. Correr `automatizacion_caja/migrar_inventario.py` (agrega columnas + deduplica + relena stocks históricos).
2. Aplicar cambios de backend (models, schemas, api) y rebuildear frontend (`npm run build`).
3. Prueba funcional por rol (admin y cocinero) con login real.
4. Rollback: solo se propaga como ALTER TABLE ADD; no es destructivo. La deduplicación se revierte restaurando el backup de las tablas afectadas.

## Open Questions

Ninguna que cambie specs/approach/tareas.