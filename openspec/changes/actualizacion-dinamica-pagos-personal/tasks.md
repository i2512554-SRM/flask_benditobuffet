## 1. Helper function para datos de resumen

- [ ] 1.1 Crear función `_get_resumen_pagos_data(inicio, fin)` en `app.py` que ejecute las mismas consultas que `pagos_personal()` y devuelva un dict con: `total_pagado_mes`, `total_adelantos_mes`, `neto_mes`, `empleados_activos`, `proximo_pago_dias`, `empleados` (lista de dicts), `historial` (lista de dicts)

## 2. Respuesta JSON en rutas de pago y adelanto

- [ ] 2.1 Modificar `registrar_pago_personal` para detectar `X-Requested-With: XMLHttpRequest` y devolver JSON con datos de resumen, o redirect si no es AJAX
- [ ] 2.2 Modificar `registrar_adelanto_personal` para detectar `X-Requested-With: XMLHttpRequest` y devolver JSON con datos de resumen, o redirect si no es AJAX
- [ ] 2.3 Actualizar ruta `/pagos-personal/pago` para que también maneje peticiones GET (redirigir a pagos_personal) y validar campos vacíos

## 3. IDs y estructura en el template

- [ ] 3.1 Agregar IDs a los `<h2>` de las cards de estadísticas: `totalPagadoValue`, `totalAdelantosValue`, `netoMesValue`
- [ ] 3.2 Agregar ID `empleadosTableBody` al `<tbody>` de la tabla de empleados
- [ ] 3.3 Agregar ID `historialTableBody` al `<tbody>` de la tabla de historial
- [ ] 3.4 Agregar IDs a los formularios de pago (`formPago`) y adelanto (`formAdelanto`) y a los overlays (`overlayPago`, `overlayAdelanto`)

## 4. JavaScript de envío asíncrono

- [ ] 4.1 Agregar función `actualizarStats(stats)` que actualice los `<h2>` de las cards
- [ ] 4.2 Agregar función `actualizarTablaEmpleados(empleados)` que reconstruya `empleadosTableBody`
- [ ] 4.3 Agregar función `actualizarHistorial(historial)` que reconstruya `historialTableBody`
- [ ] 4.4 Agregar función `enviarFormulario(form, url)` que use fetch con FormData y maneje success/error
- [ ] 4.5 Vincular `enviarFormulario` al evento `submit` de ambos formularios
