## Why

Actualmente cada módulo implementa el botón de "volver al panel" de forma distinta: clases diferentes (`.btn-outline`, `.back-profile`, `.btn-secondary`, `.volver`, o ninguna), tamaños dispares, posiciones inconsistentes dentro del header, y algunas sin estilar. Esto genera fricción visual al navegar entre módulos y dificulta el mantenimiento. Unificarlos mejora la experiencia de usuario y reduce la deuda técnica.

## What Changes

- Crear una clase compartida `.btn-back` con un tamaño y estilo base unificado (fixed-size, icono `fa-arrow-left`)
- Reemplazar todos los botones de "volver al panel" en los 9 templates con la nueva clase
- Ajustar el CSS específico de cada módulo solo para variaciones de color/tema, no para tamaño/estructura
- Eliminar clases y CSS muerto (`.link-back` en inventario.css, `.volver` en login.css)
- Mantener la posición del botón consistente en todos los headers (fuera del `<h1>`, standalone, para no afectar el layout del título ni mover las cards)
- El botón de cierre de overlays/modales NO entra en este cambio (son funcionalmente distintos)

## Capabilities

### New Capabilities
- `back-button`: Componente de botón de retroceso unificado con icono `fa-arrow-left`, tamaño fijo, posicionamiento consistente en el header, y soporte para tema claro/oscuro.

### Modified Capabilities
<!-- Ninguna -- no hay cambios en requisitos existentes de specs -->

## Impact

**Templates afectados (9):**
- `templates/caja.html` — reemplazar `.btn-outline` inline
- `templates/inventario.html` — reemplazar `.btn-outline` inline
- `templates/inventario_compra_detalle.html` — reemplazar `.btn-secondary` (Volver al Inventario)
- `templates/perfil.html` — reemplazar `.back-profile`
- `templates/empleados.html` — agregar clase al `<a>` sin clase
- `templates/empleados_form.html` — agregar clase al `<a>` sin clase
- `templates/pagos_personal.html` — reemplazar `.btn-outline` (Volver al Panel, con texto)
- `templates/pagos_personal_detalle.html` — reemplazar `.btn-outline` inline
- `templates/login.html` — reemplazar `.volver` (Volver al inicio)

**CSS afectados (8):**
- `static/css/variables.css` — agregar `.btn-back` base
- `static/css/panel.css` — remover reglas redundantes si se unifican
- `static/css/caja.css` — remover `a.btn-outline` específico si aplica
- `static/css/inventario.css` — remover `.link-back` (dead code), remover reglas redundantes
- `static/css/perfil.css` — remover `.back-profile`
- `static/css/empleados.css` — agregar variante de color si es necesario
- `static/css/login.css` — remover `.volver`
- `static/css/estilos.css` — posible regla global si aplica
