## ADDED Requirements

### Requirement: Título dinámico con nombre del empleado
El título principal del detalle de pagos DEBE mostrar "Historial de [nombre] [apellido]" según el empleado que se está consultando.

#### Scenario: Título muestra el nombre del empleado
- **WHEN** un usuario accede al detalle de pagos de un empleado específico
- **THEN** el `<h1>` del header DEBE mostrar "Historial de [nombres] [apellido]" correspondiente a ese empleado

### Requirement: Subtítulo contextual
El subtítulo del header DEBE describir el contenido de la página de forma precisa.

#### Scenario: Subtítulo visible
- **WHEN** un usuario accede al detalle de pagos
- **THEN** el subtítulo DEBE decir "Historial de pagos, adelantos y movimientos"
