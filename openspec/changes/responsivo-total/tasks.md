## 1. CSS Foundation — estilos.css

- [ ] 1.1 Agregar CSS unificado de card-conversion en `estilos.css` dentro de `@media (max-width: 640px)` — selector `td[data-label]::before`, ocultar `<thead>`, filas como flex-column cards
- [ ] 1.2 Agregar breakpoint `@media (max-width: 380px)` en `estilos.css` — reducir padding de cards a 8px, font-size de h1→1.25rem, h2→1.1rem
- [ ] 1.3 Agregar `min-height: 44px` en botones para viewport ≤640px en `estilos.css`

## 2. Eliminar min-width rígidos

- [ ] 2.1 `panel.css` — eliminar `min-width: 840px` en `.table-card` (línea 267) y `min-width: 720px` en `table` (línea 275)
- [ ] 2.2 `caja.css` — eliminar `min-width: 760px` en `table` (línea 197)
- [ ] 2.3 `inventario.css` — eliminar `min-width: 720px` en `table` (línea 220)
- [ ] 2.4 `perfil.css` — eliminar `min-width: 520px` en `table` (línea 272)

## 3. Templates — data-label

- [ ] 3.1 `empleados.html` — agregar atributo `data-label` a cada `<td>` en la tabla de empleados (7 columnas: nombres, cargo, teléfono, email, salario, fecha, acciones)
- [ ] 3.2 `inventario.html` — reemplazar `data-nombre`, `data-categoria`, `data-fecha` por `data-label` en la tabla de productos
- [ ] 3.3 `perfil.html` — agregar `data-label` a cada `<td>` en la tabla de pagos y tabla de adelantos

## 4. Empleados — overflow wrapper

- [ ] 4.1 `empleados.html` — envolver la tabla en `<div class="table-wrapper">` (o similar con overflow-x: auto)
- [ ] 4.2 `empleados.css` — agregar regla `.table-wrapper { overflow-x: auto; }` si no existe

## 5. Stats grid

- [ ] 5.1 `inventario.css` — en `@media (max-width: 400px)` cambiar `.inventario-stats` a 1 columna
- [ ] 5.2 `inventario.css` — en `@media (max-width: 640px)` ajustar a 2 columnas si es necesario

## 6. Verification

- [ ] 6.1 Abrir cada módulo (caja, inventario, perfil, empleados, pagos) en viewport ≤640px y verificar que las tablas se convierten a cards
- [ ] 6.2 Verificar viewport ≤380px — padding reducido, fuentes más pequeñas
- [ ] 6.3 Verificar touch targets — botones miden al menos 44px de alto en mobile
- [ ] 6.4 Verificar que no hay overflow horizontal inesperado en ningún módulo
- [ ] 6.5 Verificar dark mode en mobile
