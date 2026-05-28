## Why

Actualmente, al registrar un pago o adelanto en el módulo de Pagos al Personal, el formulario se envía mediante POST tradicional y el servidor redirige de vuelta, provocando una recarga completa de la página. Esto rompe la fluidez de la experiencia: las cards de estadísticas y las tablas de empleados e historial deberían actualizarse al instante sin recargar, dando feedback inmediato al usuario.

## What Changes

- Los formularios de registro de pago y adelanto se envían mediante `fetch()` (AJAX) en lugar de POST tradicional
- Las rutas `/pagos-personal/pago` y `/pagos-personal/adelanto` detectan peticiones AJAX y devuelven JSON con los datos actualizados
- Las cards de estadísticas (Total Pagado, Total Adelantos, Neto, Próximo Pago) se actualizan dinámicamente sin recargar
- La tabla de empleados (resumen por empleado) se actualiza dinámicamente al registrar un pago
- La tabla de historial se actualiza dinámicamente al registrar un pago
- El flujo tradicional (POST + redirect) se mantiene como fallback para navegadores sin JS
- No se rompe ninguna funcionalidad existente

## Capabilities

### New Capabilities
- `registro-pago-ajax`: Envío asíncrono de formularios de pago y adelanto con actualización dinámica del DOM
- `api-resumen-pagos`: Endpoints que devuelven datos actualizados de estadísticas y tablas en formato JSON

### Modified Capabilities

*(ninguna)*

## Impact

- `app.py`: modificar rutas `registrar_pago_personal` y `registrar_adelanto_personal` para soportar AJAX + JSON
- `app.py`: agregar helper `_get_resumen_pagos_data(inicio, fin)` para calcular datos actualizados
- `templates/pagos_personal.html`: agregar IDs a elementos del DOM para actualización JS, interceptar envío de formularios con fetch, agregar funciones de actualización de cards y tablas
