## ADDED Requirements

### Requirement: Botón de cerrar sesión en toda página protegida
Toda página que requiera autenticación SHALL tener un botón "Cerrar Sesión" visible en el header, usando la clase `btn-outline` y apuntando a `{{ url_for('logout') }}`.

#### Scenario: Admin panel muestra Cerrar Sesión
- **GIVEN** un usuario administrador autenticado
- **WHEN** visualiza `panel_admin.html`
- **THEN** SHALL ver un botón con texto "Cerrar Sesión" y clase `btn-outline` en `.header-buttons`
- **AND** el botón SHALL enlazar a `{{ url_for('logout') }}`

#### Scenario: Cajero panel muestra Cerrar Sesión
- **GIVEN** un usuario cajero autenticado
- **WHEN** visualiza `panel_cajero.html`
- **THEN** SHALL ver un botón "Cerrar Sesión" con clase `btn-outline` en `.header-buttons`

#### Scenario: Módulos de gestión muestran Cerrar Sesión
- **GIVEN** un usuario autenticado
- **WHEN** visualiza cualquiera de: `caja.html`, `inventario.html`, `inventario_compra_detalle.html`, `empleados.html`, `empleados_form.html`, `perfil.html`, `pagos_personal.html`
- **THEN** SHALL ver un botón "Cerrar Sesión" con clase `btn-outline` en el contenedor de acciones del header

#### Scenario: Botón Salir renombrado a Cerrar Sesión
- **GIVEN** un usuario autenticado
- **WHEN** visualiza `panel_admin.html` o `pagos_personal_detalle.html`
- **THEN** el texto del botón de logout SHALL ser "Cerrar Sesión" (no "Salir")
- **AND** el estilo, clase y ruta SHALL ser idénticos al original

### Requirement: Consistencia visual
Todos los botones de cerrar sesión SHALL usar la misma clase `btn-outline` y el mismo patrón `<a href="{{ url_for('logout') }}" class="btn-outline">Cerrar Sesión</a>` para mantener consistencia visual en todo el sistema.
