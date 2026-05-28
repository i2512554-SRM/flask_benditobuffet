## ADDED Requirements

### Requirement: Botón "Volver" en header-derecha
El botón de retroceso "Volver" DEBE ubicarse en la esquina superior derecha del header (`header-buttons`), reemplazando al botón "Cerrar Sesión".

#### Scenario: Botón Volver visible en la derecha
- **WHEN** un usuario accede al detalle de pagos de un empleado
- **THEN** DEBE ver el botón "Volver" con clase `btn-outline` e icono `fa-arrow-left` en la esquina superior derecha del header

### Requirement: Botón "Cerrar Sesión" eliminado
El botón "Cerrar Sesión" NO DEBE aparecer en la vista de detalle de pagos al personal.

#### Scenario: Logout ausente del header
- **WHEN** un usuario accede al detalle de pagos de un empleado
- **THEN** el botón "Cerrar Sesión" NO DEBE estar presente en el DOM

### Requirement: Título sin botón Volver a la izquierda
El área izquierda del header DEBE contener solo el título "Pagos Personal" y su subtítulo, sin el botón de retroceso.

#### Scenario: Header izquierdo limpio
- **WHEN** un usuario accede al detalle de pagos de un empleado
- **THEN** el lado izquierdo del header DEBE mostrar solo el título y subtítulo, sin enlaces de navegación
