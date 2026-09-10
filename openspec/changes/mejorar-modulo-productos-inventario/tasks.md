## 1. Migración de base de datos

- [x] 1.1 Crear `automatizacion_caja/migrar_inventario.py` (idempotente) que agregue `productos.unidad_medida` (default 'Un'), `productos.descripcion`, `productos.estado` (default true), e `inventario_movimientos.stock_anterior`, `stock_posterior` y `motivo` (verificar con `SELECT column_name ... information_schema` tras ejecutar)
- [x] 1.2 Agregar al script la relenado de `stock_anterior/stock_posterior` de movimientos existentes recalculando acumulado por producto (verificar: ningún movimiento activo con stock_anterior NULL)
- [x] 1.3 Agregar al script la deduplicación case-insensitive de productos (suma de stock, reasignación de `inventario_movimientos` y referencias FK, baja del sobrante) y verificar que no queden duplicados (`SELECT lower(nombre), count(*) ... HAVING count(*) > 1` devuelve 0 filas) ni FKs huérfanas
- [x] 1.4 Ejecutar el script contra la BD de Supabase y verificar conteos antes/después (productos, movimientos)

## 2. Backend: modelos, esquemas y API

- [x] 2.1 Agregar `unidad_medida`, `descripcion`, `estado` al modelo `Producto`; agregar `stock_anterior`, `stock_posterior`, `motivo` a `InventarioMovimiento` (verificar import correcto en `models.py`)
- [x] 2.2 Actualizar `schemas/inventario.py` para exponer los nuevos campos en producto y movimiento (verificar dump con cliente de prueba)
- [x] 2.3 Agregar decoradores de permiso en `api/inventario.py`: `_solo_admin` (rol 1) y `_inventario_stock` (roles 1 y 3), y aplicarlos: admin a gestión (crear/editar/desactivar/categorías/proveedores/compras/inversiones/ajuste), staff a consulta y stock (verificar 403 para cocinero en gestión y 200/201 en stock)
- [x] 2.4 `POST /inventario/productos`: validar duplicado case-insensitive (409 con `existe: true` e id del existente), unidad válida (Kg/Un/Lt), crear movimiento "Entrada" inicial cuando stock > 0 (verificar con `test_client`: crear "Arroz" dos veces → segundo devuelve 409)
- [x] 2.5 `PUT /inventario/productos/<id>`: editar solo nombre/unidad/descripción/estado (ignorar `stock`), validar duplicado al renombrar (verificar que stock no cambia tras el PUT)
- [x] 2.6 `DELETE /inventario/productos/<id>`: si tiene movimientos → desactivar; si no → eliminar físicamente (verificar comportamiento de ambos casos)
- [x] 2.7 `POST /inventario/productos/<id>/stock/entrada`: validar producto activo y cantidad > 0; registrar movimiento "Entrada" con stock_anterior/posterior y motivo (verificar que stock pasa de 20 a 30)
- [x] 2.8 `POST /inventario/productos/<id>/stock/salida`: validar motivo obligatorio, cantidad > 0 y stock suficiente; rechazo con "No hay suficiente stock disponible" cuando `cantidad > stock` y stock nunca negativo (verificar 400 y sin cambios)
- [x] 2.9 Ajustar `POST /compras`, `DELETE /compras/<id>` y `crear_producto` para escribir `stock_anterior/stock_posterior`/`motivo` en cada movimiento (verificar dump del historial tras registrar/ anular una compra)

## 3. Backend: cocina y endpoints de consulta

- [x] 3.1 Actualizar `api/cocina.py` `_serializar_producto` para incluir `unidad_medida` y excluir productos inactivos (verificar con `test_client` como rol 3)
- [x] 3.2 Asegurar `GET /inventario/productos` y `GET /inventario/productos/<id>` accesibles a roles 1 y 3 y que el listado permita filtrar solo activos mediante parámetro `activos=1` (verificar por rol)

## 4. Frontend: módulo de inventario (admin)

- [x] 4.1 Reestructurar `InventarioView.vue`: barra `[+ Nuevo producto] [+ Agregar stock] [− Registrar salida]` (eliminar "Agregar producto"), listado con columnas Producto/Unidad/Stock (con unidad)/Estado y acciones por fila (Ver, Editar, Agregar stock, Registrar salida, Desactivar/Activar) (verificar render y carga contra API)
- [x] 4.2 Dialog de Nuevo producto con nombre, unidad (Kg/Un/Lt), stock inicial, descripción, estado y manejo del 409: al existir nombre muestra "El producto ya existe..." con botón ir a "Agregar stock" (verificar flujo completo en navegador)
- [x] 4.3 Dialog de Agregar stock: buscador/selector de productos activos, muestra unidad y stock actual, NO permite editar nombre/unidad (verificar comportamiento)
- [x] 4.4 Dialog de Registrar salida: selector de producto activo, cantidad, motivo obligatorio y validación de stock suficiente (verificar mensaje y rechazo)
- [x] 4.5 Pestaña Movimientos: agregar columnas Unidad, Stock anterior, Stock posterior y Motivo, manteniendo filtros por producto/tipo (verificar datos mostrados)

## 5. Frontend: cocina, módulo y navegación

- [x] 5.1 `CocinaInventarioView.vue`: mostrar unidad en la cantidad (ej. "20 Kg"), aplicar acciones "Agregar stock"/"Registrar salida" para rol 3 y acceso al historial (verificar permisos y render)
- [x] 5.2 Actualizar `ModuloInventarioView.vue` y textos del `AppDrawer.vue` para diferenciar Productos / Entradas y Salidas / Movimientos (verificar navegación)
- [x] 5.3 Asegurar que el trabajador (rol 4) no vea enlaces ni rutas de inventario (verificar router guard y drawer)

## 6. Integración y verificación final

- [x] 6.1 Rebuilded del frontend (`npm run build` en `frontend/`) y reinicio de Flask; verificar carga de `http://localhost:5000`
- [ ] 6.2 Prueba funcional con login real de admin y de cocinero: crear producto, detectar duplicado, agregar stock, registrar salida, consultar historial y desactivar producto (verificar cada escenario de los specs)
- [x] 6.3 Comprobación de que el stock nunca queda negativo y que el historial conserva stock_anterior/posterior tras varios movimientos (verificado por suite de integración con `test_client`: salida > stock da 400 sin cambios; historial conserva 0→20→30→25)