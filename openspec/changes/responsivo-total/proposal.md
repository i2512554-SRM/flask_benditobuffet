## Why

El sistema actual es funcional en desktop pero su soporte mobile es incompleto. Tablas como la de empleados (7 columnas, 3 botones de acción) son inusables en celular. Hay 8 breakpoints distintos pero ninguno por debajo de 540px, y 4 tablas carecen de conversión a cards. En pantallas de 360-414px (iPhone SE, Galaxy S24) los textos y cards no escalan adecuadamente, haciendo la experiencia pobre.

## What Changes

- **Conversión universal de tablas a cards** en ≤640px: agregar atributos `data-label` a todas las tablas que faltan (empleados, inventario, perfil) y unificar el CSS de card-conversion
- **Cerrar gaps de min-width**: eliminar `min-width` rígidos en `panel.css` (840px), `caja.css` (760px), `inventario.css` (720px), `perfil.css` (520px) que causan overflow incluso cuando existe card-conversion
- **Agregar breakpoint xs (≤380px)**: reducir padding general, tamaños de fuente, y márgenes para pantallas muy pequeñas
- **Touch targets**: botones y elementos interactivos deben tener mínimo 44px de altura en mobile (WCAG)
- **Grillas de stats**: evitar que se vean apretadas en mobile (inventario 2-column stats en 360px)
- **Empleados**: agregar overflow wrapper a la tabla, es el único módulo sin uno
- **Tipografía responsive**: usar `clamp()` en títulos principales donde sea práctico

## Capabilities

### New Capabilities
- `responsive-tablas`: Conversión de tablas a cards en mobile con `data-label` y CSS unificado, para todos los módulos
- `responsive-general`: Breakpoint xs (≤380px), touch targets, cierre de gaps min-width, grillas, overflow wrappers

### Modified Capabilities
<!-- Ninguna — no hay specs existentes en openspec/specs/ -->

## Impact

**Templates (6):**
- `templates/empleados.html` — agregar `data-label` a `<td>`, wrapper overflow
- `templates/inventario.html` — reemplazar `data-nombre`/`data-categoria`/`data-fecha` por `data-label`
- `templates/perfil.html` — agregar `data-label` a tablas de pagos y adelantos
- `templates/caja.html` — verificar `data-label` existentes (ya tiene)
- `templates/pagos_personal.html` — verificar `data-label` existentes
- `templates/pagos_personal_detalle.html` — verificar `data-label` existentes

**CSS (7):**
- `static/css/estilos.css` — breakpoint xs, reglas universales card-conversion
- `static/css/panel.css` — eliminar `min-width: 840px` en `.table-card`, `min-width: 720px` en `table`
- `static/css/caja.css` — eliminar `min-width: 760px` en `table`
- `static/css/inventario.css` — eliminar `min-width: 720px` en `table`, ajustar grilla stats
- `static/css/perfil.css` — eliminar `min-width: 520px` en `table`
- `static/css/empleados.css` — wrapper overflow, card-conversion, touch targets
- `static/css/login.css` — touch target mínimo 44px en botón
