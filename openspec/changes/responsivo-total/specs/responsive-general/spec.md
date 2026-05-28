## ADDED Requirements

### Requirement: Breakpoint para pantallas muy pequeñas (≤380px)
El sistema SHALL tener un breakpoint `@media (max-width: 380px)` que ajuste paddings, fuentes y márgenes para dispositivos con pantalla de 360-380px de ancho (iPhone SE, Galaxy S24, etc.).

#### Scenario: Padding reducido en pantalla muy pequeña
- **WHEN** el viewport es ≤380px
- **THEN** el padding general de las cards y contenedores SHALL reducirse a la mitad del valor en 640px (mínimo 8px)

#### Scenario: Títulos más pequeños en pantalla muy pequeña
- **WHEN** el viewport es ≤380px
- **THEN** los `<h1>` SHALL usar `font-size: 1.25rem` y los `<h2>` `font-size: 1.1rem`

### Requirement: Touch targets mínimos de 44px en mobile
Todos los botones y elementos interactivos SHALL tener un área táctil mínima de 44px de altura en viewports ≤640px.

#### Scenario: Botones con altura mínima
- **WHEN** un `<button>` o `<a>` con clase `btn-*` se visualiza en viewport ≤640px
- **THEN** su altura SHALL ser al menos 44px (incluyendo padding)

#### Scenario: Botones de acción en tabla de empleados
- **WHEN** los botones `.btn-edit`, `.btn-delete`, `.btn-activar`, `.btn-desactivar` se visualizan en viewport ≤640px
- **THEN** su altura SHALL ser al menos 44px

### Requirement: Sin min-width rígido en contenedores de tabla
Ningún contenedor de tabla SHALL tener un `min-width` fijo en píxeles que impida el reflujo natural en viewports intermedios.

#### Scenario: panel.css sin min-width en table-card
- **WHEN** se visualiza `.table-card` en `panel.css` en un viewport entre 640px y 840px
- **THEN** NO SHALL tener `min-width: 840px` que fuerce overflow horizontal

#### Scenario: caja.css sin min-width en table
- **WHEN** se visualiza `table` en `caja.css` en un viewport entre 640px y 760px
- **THEN** NO SHALL tener `min-width: 760px`

#### Scenario: inventario.css sin min-width en table
- **WHEN** se visualiza `table` en `inventario.css` en un viewport entre 700px y 720px
- **THEN** NO SHALL tener `min-width: 720px`

#### Scenario: perfil.css sin min-width en table
- **WHEN** se visualiza `table` en `perfil.css`
- **THEN** NO SHALL tener `min-width: 520px`

### Requirement: Stats grid no se aprieta en mobile
Las grillas de estadísticas SHALL evitar mostrar más de 2 columnas en viewports ≤640px, y 1 columna en ≤400px.

#### Scenario: Stats de inventario en 1 columna en mobile estrecho
- **WHEN** el viewport es ≤400px
- **THEN** `.inventario-stats` SHALL mostrar 1 columna
