## ADDED Requirements

### Requirement: Envío asíncrono de formularios de pago y adelanto

El sistema DEBE interceptar el evento `submit` de los formularios de pago y adelanto en la página de Pagos al Personal y enviarlos mediante `fetch()` con header `X-Requested-With: XMLHttpRequest`.

#### Scenario: Envío exitoso de pago
- **WHEN** el usuario completa el formulario de pago y hace clic en "Registrar Pago"
- **THEN** el formulario se envía mediante fetch al endpoint `/pagos-personal/pago`
- **THEN** si el servidor responde con `{ success: true, ... }`, se actualizan las cards de estadísticas, la tabla de empleados y la tabla de historial sin recargar la página
- **THEN** se cierra el overlay de registro

#### Scenario: Envío exitoso de adelanto
- **WHEN** el usuario completa el formulario de adelanto y hace clic en "Registrar Adelanto"
- **THEN** el formulario se envía mediante fetch al endpoint `/pagos-personal/adelanto`
- **THEN** si el servidor responde con `{ success: true, ... }`, se actualizan las cards de estadísticas, la tabla de empleados y la tabla de historial sin recargar la página
- **THEN** se cierra el overlay de registro

#### Scenario: Error del servidor
- **WHEN** el servidor responde con `{ success: false, message: "..." }`
- **THEN** se muestra el mensaje de error en la página sin recargar
- **THEN** el overlay permanece abierto para que el usuario corrija

#### Scenario: Fallback sin JavaScript
- **WHEN** JavaScript está deshabilitado o el fetch falla
- **THEN** el formulario se envía mediante POST tradicional (comportamiento por defecto del HTML)
- **THEN** el servidor redirige de vuelta a la página de Pagos al Personal (flujo original)

### Requirement: Actualización dinámica del DOM

El frontend DEBE actualizar los siguientes elementos del DOM con los datos recibidos en la respuesta JSON:
- Cards de estadísticas (Total Pagado, Total Adelantos, Neto)
- Tabla de resumen por empleado (tbody)
- Tabla de historial de pagos (tbody)

#### Scenario: Actualización de cards de estadísticas
- **WHEN** se recibe una respuesta JSON exitosa
- **THEN** el contenido de cada `<h2>` en las cards se actualiza con el nuevo valor numérico

#### Scenario: Actualización de tabla de empleados
- **WHEN** se recibe una respuesta JSON exitosa
- **THEN** se reconstruye el `<tbody>` de la tabla de empleados con las filas actualizadas
- **THEN** se muestran los nombres, total pagado, total adelantos, neto y enlace a detalle

#### Scenario: Actualización de tabla de historial
- **WHEN** se recibe una respuesta JSON exitosa
- **THEN** se reconstruye el `<tbody>` de la tabla de historial con las filas actualizadas
- **THEN** se muestran la fecha, empleado, monto y estado de cada pago
