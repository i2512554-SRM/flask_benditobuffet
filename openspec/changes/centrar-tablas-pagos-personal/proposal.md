## Why

En la vista de Pagos al Personal, las tablas de empleados e historial no se muestran centradas horizontalmente. En pantallas de escritorio (>900px) el grid `.tables` usa dos columnas (`1.5fr 1fr`), pero solo una tabla se muestra a la vez, quedando desplazada hacia la izquierda. Los botones de alternar vista ("Empleados" / "Historial") también están alineados a la izquierda, acentuando la falta de simetría.

## What Changes

- Se agrega la clase `.tables--single` a la sección `.tables` en `pagos_personal.html` para forzar una columna única
- Se añade la regla CSS `.tables--single { grid-template-columns: minmax(0, 1fr); }` en `panel.css`
- Se centran los botones `.view-toggle` con `justify-content: center`
- No se modifican rutas, lógica de negocio, ni otros templates

## Capabilities

### New Capabilities
- `tablas-centradas`: Tablas de empleados e historial centradas horizontalmente en la vista de Pagos al Personal

### Modified Capabilities

*(ninguna)*

## Impact

- `templates/pagos_personal.html`: agregar clase `tables--single` al `<section class="tables">`
- `static/css/panel.css`: agregar regla `.tables--single` y centrar `.view-toggle`
