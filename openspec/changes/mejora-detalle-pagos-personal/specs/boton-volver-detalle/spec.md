## ADDED Requirements

### Requirement: Botón de volver estilizado
El botón de retroceso DEBE usar la clase `btn-outline` del sistema, con el texto "Volver" y el icono de flecha izquierda, y DEBE enlazar a la página de Pagos al Personal.

#### Scenario: Botón visible con estilo correcto
- **WHEN** un usuario accede al detalle de pagos de un empleado
- **THEN** DEBE ver un botón con clase `btn-outline`, texto "Volver", icono `fa-arrow-left`, y enlace a `url_for('pagos_personal')`

### Requirement: Texto "Historial" en tabla de empleados
El botón de acción en la tabla de empleados de `pagos_personal.html` DEBE mostrar el texto "Historial" en lugar de "Ver".

#### Scenario: Texto actualizado en la tabla
- **WHEN** un usuario ve la tabla de empleados en Pagos al Personal
- **THEN** el botón en la columna Acción DEBE decir "Historial"
