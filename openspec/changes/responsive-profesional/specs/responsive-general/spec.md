## ADDED Requirements

### Requirement: Breakpoint para pantallas muy pequeñas (≤380px)
El sistema SHALL tener un breakpoint `@media (max-width: 380px)` que ajuste paddings, fuentes y márgenes para dispositivos con pantalla de 360-380px (iPhone SE, Galaxy S24).

#### Scenario: Padding reducido en ≤380px
- **WHEN** el viewport es ≤380px
- **THEN** el padding de cards y contenedores SHALL reducirse a 8px (mitad del valor típico en 640px)

#### Scenario: Títulos escalados en ≤380px
- **WHEN** el viewport es ≤380px
- **THEN** los `<h1>` SHALL usar `font-size: 1.25rem` y `<h2>` `font-size: 1.1rem`

### Requirement: Touch targets WCAG 2.1 (44px mínimos)
Todos los botones y elementos interactivos SHALL tener un área táctil mínima de 44px de altura en viewports ≤640px, cumpliendo criterio WCAG 2.5.5 (Target Size).

#### Scenario: Botones con altura mínima en mobile
- **WHEN** un `<button>` o `<a>` con clase `btn-*` se visualiza en viewport ≤640px
- **THEN** su altura SHALL ser al menos 44px (incluyendo padding)

#### Scenario: Botones de acción en tabla empleados
- **WHEN** los botones `.btn-edit`, `.btn-delete`, `.btn-activar`, `.btn-desactivar` se visualizan en viewport ≤640px
- **THEN** su altura SHALL ser al menos 44px

### Requirement: iOS zoom fix en inputs
Ningún input, select o textarea SHALL tener `font-size` menor a 16px en el CSS del proyecto, para evitar el auto-zoom de iOS Safari al enfocar el campo.

#### Scenario: Inputs en empleados con 16px
- **WHEN** un input en `empleados.html` o `empleados_form.html` recibe foco en iOS Safari
- **THEN** su `font-size` SHALL ser 16px (no 14px como está actualmente en `empleados.css`)

#### Scenario: Inputs en caja con 16px
- **WHEN** un input en `caja.html` recibe foco en iOS Safari
- **THEN** su `font-size` SHALL ser 16px (no 14px como está actualmente en `caja.css`)

### Requirement: Sin min-width rígido en contenedores de tabla
Ningún contenedor de tabla o tabla SHALL tener `min-width` fijo en píxeles que impida el reflujo natural.

#### Scenario: panel.css sin min-width
- **WHEN** se visualiza `.table-card` en `panel.css` en viewport <840px
- **THEN** NO SHALL tener `min-width: 840px`
- **AND** las tablas dentro SHALL tener `min-width: auto`

#### Scenario: caja.css sin min-width
- **WHEN** se visualiza `table` en `caja.css` en viewport <760px
- **THEN** NO SHALL tener `min-width: 760px`

#### Scenario: inventario.css sin min-width
- **WHEN** se visualiza `table` en `inventario.css` en viewport <720px
- **THEN** NO SHALL tener `min-width: 720px`

#### Scenario: perfil.css sin min-width
- **WHEN** se visualiza `table` en `perfil.css`
- **THEN** NO SHALL tener `min-width: 520px`

### Requirement: Stats grid responsive
Las grillas de estadísticas SHALL adaptar sus columnas según el viewport para no comprimir el contenido.

#### Scenario: Stats de inventario en 1 columna
- **WHEN** el viewport es ≤400px
- **THEN** `.inventario-stats` SHALL mostrar 1 columna

#### Scenario: Profile actions buttons en mobile
- **WHEN** el viewport es ≤400px
- **THEN** `.profile-actions button` SHALL tener `min-width: auto` o `width: 100%` en lugar de los 170px fijos
