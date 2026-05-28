## ADDED Requirements

### Requirement: Respuesta JSON en rutas de pago y adelanto

Las rutas `/pagos-personal/pago` y `/pagos-personal/adelanto` DEBEN detectar si la petición incluye el header `X-Requested-With: XMLHttpRequest` y, en ese caso, devolver una respuesta JSON en lugar de redirigir.

#### Scenario: Petición AJAX a registrar_pago_personal
- **WHEN** el servidor recibe un POST a `/pagos-personal/pago` con header `X-Requested-With: XMLHttpRequest`
- **THEN** procesa el pago normalmente
- **THEN** calcula los datos actualizados de estadísticas, empleados e historial
- **THEN** devuelve `{ success: true, message: "...", stats: {...}, empleados: [...], historial: [...] }`

#### Scenario: Petición AJAX a registrar_adelanto_personal
- **WHEN** el servidor recibe un POST a `/pagos-personal/adelanto` con header `X-Requested-With: XMLHttpRequest`
- **THEN** procesa el adelanto normalmente
- **THEN** calcula los datos actualizados de estadísticas, empleados e historial
- **THEN** devuelve `{ success: true, message: "...", stats: {...}, empleados: [...], historial: [...] }`

#### Scenario: Error de validación en petición AJAX
- **WHEN** ocurre un error de validación (ej: monto inválido, campos faltantes)
- **THEN** devuelve `{ success: false, message: "..." }` con el código de estado HTTP apropiado

#### Scenario: Petición POST tradicional sin AJAX
- **WHEN** el servidor recibe un POST sin header `X-Requested-With: XMLHttpRequest`
- **THEN** procesa y redirige con `redirect(url_for('pagos_personal'))` (comportamiento original)

### Requirement: Función helper de resumen

El backend DEBE proporcionar una función auxiliar `_get_resumen_pagos_data(inicio, fin)` que calcule y devuelva todos los datos necesarios para la vista de Pagos al Personal en un diccionario.

#### Scenario: Cálculo de datos de resumen
- **WHEN** se invoca `_get_resumen_pagos_data(inicio, fin)` con un rango de fechas
- **THEN** devuelve un dict con: `total_pagado_mes`, `total_adelantos_mes`, `neto_mes`, `empleados_activos`, `proximo_pago_dias`, `empleados` (lista de dicts con id, nombre, totals), `historial` (lista de dicts con fecha, empleado, monto, estado)

#### Scenario: Datos consistentes con la vista principal
- **WHEN** se comparan los datos devueltos por el helper con los que renderiza `pagos_personal()`
- **THEN** DEBEN ser equivalentes (mismas consultas y filtros)
