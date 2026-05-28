## ADDED Requirements

### Requirement: Botones para alternar entre tablas
La vista de detalle DEBE mostrar botones (Pagos Registrados / Pagos Personal / Adelantos) que permitan al usuario elegir qué tabla ver, mostrando solo una a la vez.

#### Scenario: Botones visibles al cargar la página
- **WHEN** un usuario accede al detalle de pagos de un empleado
- **THEN** DEBEN verse tres botones: "Pagos Registrados", "Pagos Personal" y "Adelantos"

#### Scenario: Alternar entre tablas
- **WHEN** un usuario hace clic en "Pagos Personal"
- **THEN** la tabla de Pagos Personal DEBE mostrarse y las otras dos DEBEN ocultarse

### Requirement: Una tabla visible a la vez
Solo una tabla DEBE ser visible en cualquier momento.

#### Scenario: Primera tabla visible por defecto
- **WHEN** la página se carga por primera vez
- **THEN** la tabla "Pagos Registrados" DEBE estar visible y las demás ocultas

#### Scenario: Botón activo resaltado
- **WHEN** una tabla está visible
- **THEN** el botón correspondiente DEBE tener la clase `active` para resaltar visualmente cuál está seleccionado
