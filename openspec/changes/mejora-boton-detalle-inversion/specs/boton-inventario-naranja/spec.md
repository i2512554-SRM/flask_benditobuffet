## ADDED Requirements

### Requirement: Botón "Volver al Inventario" en naranja
El botón de navegación "Volver al Inventario" DEBE usar el color naranja principal del sistema.

#### Scenario: Botón visible con color naranja
- **WHEN** un usuario accede a la página de detalle de inversión
- **THEN** el botón "Volver al Inventario" DEBE mostrar el color naranja del sistema (`#ff7b00`) como color de fondo

### Requirement: Botón "Cerrar Sesión" eliminado
El botón "Cerrar Sesión" NO DEBE aparecer en la vista de detalle de inversión.

#### Scenario: Botón de cerrar sesión ausente
- **WHEN** un usuario accede a la página de detalle de inversión
- **THEN** el botón "Cerrar Sesión" NO DEBE estar presente en el DOM
