## Why

El título "Pagos Personal" en la vista de detalle de pagos (`pagos_personal_detalle.html`) es genérico y no indica qué empleado se está consultando. Al mostrar "Historial de [nombre del empleado]", el usuario sabe inmediatamente de quién está viendo los datos.

## What Changes

- Cambiar el `<h1>` estático "Pagos Personal" por `<h1>Historial de {{ empleado.nombres }} {{ empleado.apellido }}</h1>`
- Actualizar el subtítulo `<p>` para que describa el contexto específico del empleado

## Capabilities

### New Capabilities
- `titulo-dinamico-empleado`: Título del detalle de pagos personalizado con el nombre del empleado consultado

### Modified Capabilities

*(ninguna)*

## Impact

- `templates/pagos_personal_detalle.html`: 2 líneas modificadas (título y subtítulo del header)
- Sin cambios en rutas, lógica de negocio, ni CSS (el objeto `empleado` ya está disponible en el contexto del template)
