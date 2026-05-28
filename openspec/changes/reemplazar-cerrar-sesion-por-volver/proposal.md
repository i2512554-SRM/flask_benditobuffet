## Why

El botón "Cerrar Sesión" en la esquina superior derecha de `pagos_personal_detalle.html` es redundante (el header del sistema ya ofrece esa opción) y ocupa espacio que podría usarse para la navegación principal de retroceso. El botón "Volver" está actualmente en la esquina superior izquierda mezclado con el título, lo que rompe la jerarquía visual del header.

## What Changes

- Eliminar el botón "Cerrar Sesión" del `header-buttons` (esquina superior derecha)
- Mover el botón "Volver" desde la esquina superior izquierda al `header-buttons` (esquina superior derecha)
- Mantener el botón de alternar modo noche en `header-buttons`

## Capabilities

### New Capabilities
- `boton-volver-header-derecha`: Botón "Volver" reubicado en la esquina superior derecha del header, reemplazando a "Cerrar Sesión"

### Modified Capabilities

*(ninguna)*

## Impact

- `templates/pagos_personal_detalle.html`: mover el `<a>` de Volver de la izquierda al `header-buttons` y eliminar el `<a>` de Cerrar Sesión
