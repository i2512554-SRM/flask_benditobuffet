## Why

La vista de detalle de inversión en el módulo de inventario tiene una presentación básica y sin centrado, lo que rompe la cohesión visual del sistema. Un diseño centrado tipo card con los estilos modernos del proyecto mejorará la experiencia del usuario al revisar inversiones.

## What Changes

- El template `inventario_compra_detalle.html` se reestructura para envolver el contenido en un contenedor centrado
- Los datos de la inversión (monto, proveedor, fecha) se presentan en un layout tipo card con mejor jerarquía visual
- Se actualizan los estilos en `inventario.css` para la clase `.detalle-card` y sus elementos internos, usando los tokens de diseño existentes
- No se modifica ninguna ruta, lógica de negocio ni otro template

## Capabilities

### New Capabilities
- `detalle-inversion`: Vista de detalle de inversión con diseño centrado tipo card, consistente con el sistema

### Modified Capabilities

*(ninguna — solo cambio visual, sin cambios en requerimientos)*

## Impact

- `templates/inventario_compra_detalle.html`: reestructuración del markup
- `static/css/inventario.css`: actualización de estilos `.detalle-card`, `.detalle-grid`, `.detalle-meta`
- Sin impacto en rutas, modelos, lógica de negocio, ni otros templates
