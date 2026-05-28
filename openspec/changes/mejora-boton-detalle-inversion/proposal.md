## Why

El botón "Volver al Inventario" en la vista de detalle de inversión usa el color blanco/genérico de `btn-secondary`, que no sigue la identidad visual del sistema (naranja `#ff7b00`). Además, el botón "Cerrar Sesión" es redundante en esta vista ya que el header principal del sistema ya incluye esa opción.

## What Changes

- El botón "Volver al Inventario" cambia de `btn-secondary` (blanco) a usar el color naranja del sistema
- El botón "Cerrar Sesión" se elimina de `inventario_compra_detalle.html`
- No se modifican rutas, lógica de negocio, ni otros templates

## Capabilities

### New Capabilities
- `boton-inventario-naranja`: Botón de navegación "Volver al Inventario" con el color naranja principal del sistema

### Modified Capabilities

*(ninguna)*

## Impact

- `templates/inventario_compra_detalle.html`: cambio de clase en el botón y eliminación del botón de cerrar sesión
