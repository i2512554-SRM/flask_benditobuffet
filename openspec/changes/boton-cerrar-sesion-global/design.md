## Context

Actualmente solo 2 de 10 templates protegidos tienen botón de logout: `panel_admin.html` ("Salir") y `pagos_personal_detalle.html` ("Salir"). Los 8 restantes obligan al usuario a navegar manualmente a `/logout`.

## Decisions

### 1. Patrón único para todos los templates

**Decisión:** Todos los botones usan el mismo HTML exacto:

```html
<a href="{{ url_for('logout') }}" class="btn-outline">Cerrar Sesión</a>
```

La clase `btn-outline` ya existe en todos los CSS modulares y tiene el mismo estilo visual (transparente con borde).

### 2. Ubicación del botón por template

| Template | Contenedor | Insertar después de |
|----------|-----------|-------------------|
| `panel_admin.html` `.header-buttons` | Renombrar "Salir" → "Cerrar Sesión" (existe) |
| `panel_cajero.html` `.header-buttons` | Botón Mi Perfil |
| `caja.html` `.header-actions` | Botón Cerrar Caja |
| `inventario.html` `.header-actions` | Botón Registrar inversión |
| `inventario_compra_detalle.html` `.header-actions` | Botón Volver al Inventario |
| `empleados.html` `.header-empleados` | Dentro del `<div>` del `<h1>`, después del `<p>` |
| `empleados_form.html` `.header-empleados` | Dentro del `<div>` del `<h1>`, después del `<p>` |
| `perfil.html` `.header-actions` | Botón Editar perfil |
| `pagos_personal.html` `.header-buttons` | Botón 🌙 toggle |
| `pagos_personal_detalle.html` `.header-buttons` | Renombrar "Salir" → "Cerrar Sesión" (existe) |

### 3. Sin cambios de backend ni CSS

La ruta `@app.route("/logout")` ya existe en `app.py` y hace `session.clear()` + redirect a login. La clase `btn-outline` ya está definida en todos los CSS. Zero cambios de backend o CSS.

## Riesgos

| Riesgo | Mitigación |
|--------|-----------|
| El botón en `empleados.html` y `empleados_form.html` queda fuera del flujo visual del header | Se inserta dentro del `div` contenedor del título, después del subtítulo, usando la misma clase `btn-outline` |
| `pagos_personal_detalle.html` tiene estructura de header atípica (header-actions vacíos + header-buttons) | Solo se renombra el texto del enlace existente, no se toca la estructura |
