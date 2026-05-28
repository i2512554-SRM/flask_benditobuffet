## 1. Renombrar "Salir" → "Cerrar Sesión"

- [x] 1.1 `panel_admin.html` línea 14 — cambiar texto "Salir" → "Cerrar Sesión"
- [x] 1.2 `pagos_personal_detalle.html` línea 26 — cambiar texto "Salir" → "Cerrar Sesión"

## 2. Agregar botón en paneles principales

- [x] 2.1 `panel_cajero.html` — agregar `<a href="{{ url_for('logout') }}" class="btn-outline">Cerrar Sesión</a>` en `.header-buttons` después del botón Mi Perfil (línea 13)
- [x] 2.2 `pagos_personal.html` — agregar botón Cerrar Sesión en `.header-buttons` después del botón 🌙 toggle (línea 21)

## 3. Agregar botón en módulos de gestión

- [x] 3.1 `caja.html` — agregar botón Cerrar Sesión en `.header-actions` después del botón Cerrar Caja (línea 35)
- [x] 3.2 `inventario.html` — agregar botón Cerrar Sesión en `.header-actions` después del botón Registrar inversión (línea 29)
- [x] 3.3 `inventario_compra_detalle.html` — agregar botón Cerrar Sesión en `.header-actions` después del botón Volver al Inventario (línea 17)

## 4. Agregar botón en empleados y perfil

- [x] 4.1 `empleados.html` — agregar botón Cerrar Sesión dentro del `<div>` del header (después del `<p>` línea 16)
- [x] 4.2 `empleados_form.html` — agregar botón Cerrar Sesión dentro del `<div>` del header (después del `<p>` línea 17)
- [x] 4.3 `perfil.html` — agregar botón Cerrar Sesión en `.header-actions` después del botón Editar perfil (línea 24)

## 5. Verificación

- [x] 5.1 Verificar que los 10 templates protegidos tienen botón Cerrar Sesión visible
- [x] 5.2 Verificar que todos usan `btn-outline` y `{{ url_for('logout') }}`
- [x] 5.3 Verificar que la ruta `/logout` existe y funciona (session.clear + redirect login)
