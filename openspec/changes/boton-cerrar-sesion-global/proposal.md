## Why

Actualmente solo 2 de 10 páginas protegidas tienen un botón para cerrar sesión (`panel_admin.html` y `pagos_personal_detalle.html`, con texto "Salir"). Las demás páginas (panel cajero, caja, inventario, empleados, perfil, etc.) no permiten al usuario cerrar sesión sin navegar manualmente — obligan a escribir `/logout` en la URL o volver al panel admin. Esto es un problema de UX y seguridad: un usuario en un módulo no puede salir sin dar múltiples pasos.

## What Changes

- **Renombrar "Salir" → "Cerrar Sesión"** en `panel_admin.html` y `pagos_personal_detalle.html` (mismo estilo, mismo ruta `url_for('logout')`)
- **Agregar botón "Cerrar Sesión"** en todas las páginas protegidas que no lo tienen: `panel_cajero.html`, `caja.html`, `inventario.html`, `inventario_compra_detalle.html`, `empleados.html`, `empleados_form.html`, `perfil.html`, `pagos_personal.html`
- Todos los botones usan la misma clase `btn-outline` y apuntan a `{{ url_for('logout') }}` para mantener consistencia visual

## Capabilities

### New Capabilities
- `logout-global`: Botón de cerrar sesión visible y accesible desde cualquier página protegida del sistema

### Modified Capabilities
- *(ninguna)*

## Impact

**10 templates modificados:**
- `panel_admin.html` — cambiar texto "Salir" → "Cerrar Sesión" (línea 14)
- `panel_cajero.html` — agregar botón Cerrar Sesión en header (junto a Mi Perfil)
- `caja.html` — agregar botón Cerrar Sesión en `.header-actions`
- `inventario.html` — agregar botón Cerrar Sesión en `.header-actions`
- `inventario_compra_detalle.html` — agregar botón Cerrar Sesión en header
- `empleados.html` — agregar botón Cerrar Sesión en `.header-empleados`
- `empleados_form.html` — agregar botón Cerrar Sesión en header
- `perfil.html` — agregar botón Cerrar Sesión en `.header-actions`
- `pagos_personal.html` — agregar botón Cerrar Sesión en `.header-actions`
- `pagos_personal_detalle.html` — cambiar texto "Salir" → "Cerrar Sesión" (línea 26)

**Zero cambios de backend** — la ruta `/logout` ya existe y funciona.
