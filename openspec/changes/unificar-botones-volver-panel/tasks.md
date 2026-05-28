## 1. Base CSS

- [x] 1.1 Add `.btn-back` base class to `static/css/variables.css` (42×42px, icon, hover, aria-label support, text variant)

## 2. Templates — Icon-only back buttons (currently inline inside `<h1>`)

- [x] 2.1 Update `templates/caja.html` — replace inline `.btn-outline` with standalone `.btn-back` before `<h1>`, remove inline `font-size: 16px`
- [x] 2.2 Update `templates/inventario.html` — same pattern
- [x] 2.3 Update `templates/pagos_personal_detalle.html` — same pattern
- [x] 2.4 Update `templates/empleados.html` — add `.btn-back` class to unstyled `<a>`, move outside `<h1>`
- [x] 2.5 Update `templates/empleados_form.html` — same pattern (navega a `empleados`)

## 3. Templates — Icon-only already standalone

- [x] 3.1 Update `templates/perfil.html` — replace `.back-profile` with `.btn-back`

## 4. Templates — Back buttons with text

- [x] 4.1 Update `templates/pagos_personal.html` — replace `.btn-outline` + text with `.btn-back` + text
- [x] 4.2 Update `templates/inventario_compra_detalle.html` — replace `.btn-secondary` (right side) with `.btn-back` + text (left side, standalone)
- [x] 4.3 Update `templates/login.html` — replace `.volver` with `.btn-back` + text

## 5. CSS Cleanup

- [x] 5.1 Remove `.back-profile` class from `static/css/perfil.css`
- [x] 5.2 Remove `.volver` class from `static/css/login.css`
- [x] 5.3 Remove `.link-back` class (dead code) from `static/css/inventario.css`
- [x] 5.4 Remove redundant `a.btn-outline` rules from `static/css/caja.css` (if no longer used for navigation)
- [x] 5.5 Clean up inline `font-size: 16px` from all templates

## 6. Verification

- [ ] 6.1 Open each module in browser and verify button renders correctly
- [ ] 6.2 Verify dark mode toggles correctly on new `.btn-back` button
- [ ] 6.3 Verify responsive behavior at ≤640px — button maintains size, cards don't shift
