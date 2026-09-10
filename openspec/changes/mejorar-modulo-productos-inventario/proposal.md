## Why

El módulo actual de inventario mezcla la creación de productos con el ingreso de stock bajo un único botón "Agregar producto", por lo que se generan duplicados (hoy la BD ya tiene dos registros "Arroz") y no existe un historial completo de movimientos con trazabilidad (stock anterior/posterior, motivo, unidad). Se necesita separar claramente producto, entrada, salida e historial, además de diferenciar permisos por rol.

## What Changes

- **Nuevo modelo de producto**: se agrega `unidad_medida` (Kg, Un, Lt), `descripcion` (opcional) y `estado` (activo/inactivo) a la tabla `productos`. La categoría se conserva como agrupación opcional.
- **Prevención de duplicados**: al crear un producto se valida en servidor (y en cliente) la existencia de otro producto con el mismo nombre ignorando mayúsculas/minúsculas. Si existe, no se crea y se muestra el mensaje con acceso a "Agregar stock".
- **Separación de acciones** en la pantalla de inventario: `[+ Nuevo producto]`, `[+ Agregar stock]`, `[− Registrar salida]` (se elimina el botón ambiguo "Agregar producto").
- **Agregar stock**: entrada a un producto existente (selector/buscador), registra movimiento de tipo "Entrada" con stock anterior/posterior y sin permitir editar nombre/unidad del producto.
- **Registrar salida**: consumo/uso de un producto con motivo obligatorio, validación de que no se retiren más unidades que el stock disponible y rechazo de stock negativo.
- **Historial de movimientos completo**: cada operación (creación, entrada, salida, ajuste, compra, anulación) registra producto, tipo, cantidad, unidad, stock anterior, stock posterior, motivo, usuario y fecha/hora. No se agrupan movimientos.
- **CRUD de productos**: editar solo información descriptiva (nombre, unidad, descripción, estado) — el stock se modifica únicamente vía "Agregar stock" o "Registrar salida". Eliminación lógica (desactivar) cuando el producto tiene movimientos; un producto inactivo no aparece para nuevas entradas/salidas y conserva su historial.
- **Deduplicado de datos existentes**: se fusiona el producto duplicado "Arroz" (suma de stock, consolidación de movimientos) como migración dirigida.
- **Permisos por rol**: el administrador tiene control total; el cocinero puede ver productos/stock, agregar stock, registrar salidas y consultar movimientos, pero no crear, editar ni desactivar productos. El trabajador no accede a la gestión de inventario.
- **BREAKING**: `DELETE /inventario/productos/<id>` deja de eliminar físicamente y pasa a desactivar el producto (con validación). Los esquemas de producto y movimiento incorporan los nuevos campos.

## Capabilities

### New Capabilities
- `inventario/productos`: CRUD de productos con unidad de medida (Kg/Un/Lt), descripción y estado; prevención de duplicados por nombre sin distinguir mayúsculas; desactivación lógica y conservación del historial.
- `inventario/stock`: gestión de stock por movimientos — entrada ("Agregar stock") a producto existente y salida ("Registrar salida") con validaciones de stock suficiente y motivo; el stock nunca queda negativo.
- `inventario/movimientos`: historial independiente por movimiento con producto, tipo, cantidad, unidad, stock anterior/posterior, motivo, usuario y fecha; consulta y filtros.
- `inventario/permisos`: reglas de acceso por rol para las operaciones de inventario (administrador vs cocinero vs trabajador).

### Modified Capabilities
- Ninguna: `openspec/specs/` no contiene capacidades consolidadas todavía; este cambio introduce las primeras.

## Impact

- **Backend**: `models.py` (Producto: unidad_medida, descripcion, estado; InventarioMovimiento: stock_anterior, stock_posterior, motivo), `schemas/inventario.py`, `api/inventario.py` (nuevos/ajustados endpoints y decoradores de permiso), `api/cocina.py` (serialización con unidad y solo productos activos para cocina).
- **Base de datos (Supabase/PostgreSQL)**: nuevo script de migración idempotente (patrón `automatizacion_caja/crear_indices.py`) para `ALTER TABLE` con columnas nuevas y deduplicación del "Arroz".
- **Frontend**: `InventarioView.vue` (reestructuración en acciones claras: nuevo producto / agregar stock / registrar salida + listado con stock, unidad y estado), `ModuloInventarioView.vue` (enlaces), `CocinaInventarioView.vue` (muestra unidad y estado activo), `router/index.js` y `AppDrawer.vue` si aplica.
- **Compatibilidad**: se conservan columnas `precio` y `id_categoria` (requeridas por el esquema actual); el precio queda como dato descriptivo y la categoría como agrupación.