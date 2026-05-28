## 1. CSS Foundation — estilos.css

- [x] 1.1 Agregar CSS unificado de card-conversion en `estilos.css` dentro de `@media (max-width: 640px)`: selector `td[data-label]::before`, ocultar `<thead>`, filas como flex-column cards con border-radius 12px, padding 16px, gap 12px
- [x] 1.2 Agregar breakpoint `@media (max-width: 380px)` en `estilos.css`: padding de cards a 8px, h1→1.25rem, h2→1.1rem
- [x] 1.3 Agregar `min-height: 44px` a `button, .btn-*, a.btn-*` dentro de `@media (max-width: 640px)` en `estilos.css`

## 2. Eliminar min-width rígidos

- [x] 2.1 `panel.css` línea 267 — eliminar `min-width: 840px` en `.table-card`
- [x] 2.2 `panel.css` línea 275 — eliminar `min-width: 720px` en `table`
- [x] 2.3 `caja.css` línea 197 — eliminar `min-width: 760px` en `table`
- [x] 2.4 `inventario.css` línea 220 — eliminar `min-width: 720px` en `table`
- [x] 2.5 `perfil.css` línea 272 — eliminar `min-width: 520px` en `table`

## 3. iOS zoom fix — font-size 16px en inputs

- [x] 3.1 `empleados.css` — cambiar `font-size: 14px` a `font-size: 16px` en la regla `input, select` (línea 88)
- [x] 3.2 `caja.css` — cambiar `font-size: 14px` a `font-size: 16px` en la regla `.form-group input, .form-group select, .form-group textarea` (línea 157)

## 4. Templates — data-label

- [x] 4.1 `empleados.html` — agregar `data-label` a cada `<td>` en tabla de empleados (7 columnas: Nombres, DNI, Email, Teléfono, Rol, Estado, Acciones) líneas 75-88
- [x] 4.2 `inventario.html` — reemplazar `data-nombre`, `data-categoria`, `data-fecha` por `data-label` en tabla de productos (6 columnas: Artículo, Categoría, Stock, Precio Unitario, Valor Total, Registrado) líneas 113-118
- [x] 4.3 `perfil.html` — agregar `data-label` a cada `<td>` en tabla de pagos (Fecha, Monto, Descripción, Estado) líneas 121-124
- [x] 4.4 `perfil.html` — agregar `data-label` a cada `<td>` en tabla de adelantos (Fecha, Motivo, Monto, Estado) líneas 174-177

## 5. Empleados — overflow wrapper y botones de acción en mobile

- [x] 5.1 `empleados.html` — envolver la tabla (línea 60) en `<div class="table-wrapper">`
- [x] 5.2 `empleados.css` — agregar regla `.table-wrapper { overflow-x: auto; }` si no existe
- [x] 5.3 `empleados.css` — dentro de `@media (max-width: 640px)` agregar stack vertical para `.btn-edit, .btn-delete, .btn-state` con `display: flex; flex-direction: column; gap: 8px; width: 100%` en el contenedor de acciones de la tabla

## 6. Stats grid y ajustes específicos

- [x] 6.1 `inventario.css` — agregar `@media (max-width: 400px)` con `.inventario-stats { grid-template-columns: 1fr }`
- [x] 6.2 `perfil.css` — agregar `@media (max-width: 400px)` con `.profile-actions button { min-width: auto; width: 100% }`

## 7. Verificación profesional

- [x] 7.1 Verificar viewport ≤640px: TODAS las tablas (11) se convierten a cards con `data-label` visible
- [x] 7.2 Verificar viewport ≤380px: padding reducido, títulos escalados
- [x] 7.3 Verificar touch targets: todos los botones miden ≥44px de alto en mobile
- [x] 7.4 Verificar iOS zoom: inputs en empleados y caja no causan zoom al focus (font-size 16px)
- [x] 7.5 Verificar sin overflow horizontal inesperado en ningún módulo
- [x] 7.6 Verificar tabla de empleados: 3 botones de acción apilados verticalmente, sin solapamiento
- [x] 7.7 Verificar dark mode en mobile: cards y botones mantienen contraste
- [x] 7.8 Verificar que las tablas existentes con data-label (caja, pagos) siguen funcionando
