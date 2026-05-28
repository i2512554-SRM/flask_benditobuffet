## Why

El sistema tiene 11 tablas distribuidas en 5 módulos, pero solo 3 de ellas (caja, pagos) tienen soporte responsive completo con conversión a cards. Las 8 restantes (empleados, inventario, perfil) son inusables en celular — especialmente empleados con 7 columnas y 3 botones de acción por fila. Además, inputs con `font-size: 14px` causan zoom forzado en iOS, no hay breakpoint para pantallas <540px, y los touch targets no cumplen WCAG (44px mínimos). Se requiere una auditoría y corrección profesional que garantice 100% de cobertura responsive.

## What Changes

- **Conversión a cards de TODAS las tablas** en ≤640px: agregar `data-label` a las 8 tablas que faltan y CSS unificado de card-conversion en `estilos.css`
- **Cerrar gaps de min-width**: eliminar `min-width` rígidos en `panel.css` (840px/720px), `caja.css` (760px), `inventario.css` (720px), `perfil.css` (520px)
- **iOS zoom fix**: cambiar inputs con `font-size < 16px` a `16px` en `empleados.css` y `caja.css`
- **Touch targets WCAG**: `min-height: 44px` en todos los botones para viewport ≤640px
- **Breakpoint xs**: `@media (max-width: 380px)` con padding reducido y font-size escalado
- **Tabla de empleados**: agregar overflow wrapper, `data-label`, y manejo de 3 botones de acción en mobile (stack vertical)
- **Stats grid**: 1 columna en ≤400px para inventario
- **Perfil**: botones de acciones con `min-width` adaptable en mobile

## Capabilities

### New Capabilities
- `responsive-tablas`: Conversión universal de tablas a cards en mobile con `data-label` y CSS unificado, cubriendo las 11 tablas del sistema
- `responsive-general`: Breakpoint xs, touch targets WCAG, iOS zoom fix, cierre de gaps min-width, overflow wrappers, stats grid, ajustes de formularios

### Modified Capabilities
<!-- Ninguna -->

## Impact

**Templates (5):**
- `templates/empleados.html` — `data-label` en 7 celdas, overflow wrapper, stack vertical de botones acción
- `templates/inventario.html` — `data-label` en 6 celdas (reemplazar `data-nombre`/`data-categoria`/`data-fecha`)
- `templates/perfil.html` — `data-label` en 8 celdas (2 tablas × 4 columnas)
- `templates/caja.html` — verificar `data-label` existentes (ya completo)
- `templates/pagos_personal.html`, `pagos_personal_detalle.html` — verificar `data-label` (ya completos)

**CSS (7):**
- `static/css/estilos.css` — card-conversion unificado, breakpoint xs, touch targets
- `static/css/panel.css` — eliminar `min-width: 840px` y `min-width: 720px`
- `static/css/caja.css` — eliminar `min-width: 760px`, iOS zoom fix (16px)
- `static/css/inventario.css` — eliminar `min-width: 720px`, card-conversion, stats 1-col
- `static/css/perfil.css` — eliminar `min-width: 520px`, card-conversion, min-width actions
- `static/css/empleados.css` — iOS zoom fix (16px), overflow wrapper, card-conversion
- `static/css/login.css` — touch target 44px
