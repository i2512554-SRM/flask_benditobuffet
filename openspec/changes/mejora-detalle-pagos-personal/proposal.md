## Why

La vista de detalle de pagos al personal (`pagos_personal_detalle.html`) tiene problemas de UX: muestra las tres tablas (pagos registrados, pagos personal, adelantos) apiladas sin posibilidad de navegar entre ellas, el botón de volver tiene un texto placeholder (`#sebas`) sin estilos CSS, y el enlace apunta al panel en vez de a pagos al personal. Además, el botón "Ver" en la tabla de empleados (`pagos_personal.html`) debería decir "Historial" para ser más descriptivo.

## What Changes

- Cambiar texto "Ver" a "Historial" en la columna Acción de la tabla de empleados en `pagos_personal.html`
- En `pagos_personal_detalle.html`:
  - Corregir botón de volver: enlace a `url_for('pagos_personal')`, clase `btn-outline`, texto "Volver" + icono flecha
  - Agregar botones de alternar vista (Pagos Registrados / Pagos Personal / Adelantos) para mostrar una tabla a la vez
  - Agregar IDs a cada `.table-card` y clase `hidden` inicial
  - Agregar JavaScript para alternar visibilidad de las tablas
  - Limpiar los `header-actions` vacíos

## Capabilities

### New Capabilities
- `navegacion-tablas-detalle`: Botones de alternar vista entre pagos registrados, pagos personal y adelantos en el detalle de pagos al personal
- `boton-volver-detalle`: Botón de retroceso estilizado con clase del sistema y texto "Volver"

### Modified Capabilities

*(ninguna)*

## Impact

- `templates/pagos_personal.html`: cambiar texto "Ver" a "Historial" (1 línea)
- `templates/pagos_personal_detalle.html`: reestructuración completa del header y las tablas con toggle buttons + JS
