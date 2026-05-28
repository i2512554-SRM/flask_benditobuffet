## ADDED Requirements

### Requirement: Tablas centradas horizontalmente en Pagos al Personal
La tabla visible (empleados o historial) DEBE aparecer centrada horizontalmente con igual distancia a ambos lados del contenedor, independientemente del tamaño de pantalla.

#### Scenario: Tabla centrada en escritorio (>=900px)
- **WHEN** un usuario hace clic en "Empleados" o "Historial" en una pantalla de escritorio
- **THEN** la tabla visible DEBE estar centrada horizontalmente con igual espacio a izquierda y derecha

#### Scenario: Tabla centrada en tablet/mobile (<900px)
- **WHEN** un usuario hace clic en "Empleados" o "Historial" en una pantalla menor a 900px
- **THEN** la tabla visible DEBE ocupar el ancho disponible con padding uniforme a izquierda y derecha, y el contenido estar centrado

### Requirement: Botones de alternar vista centrados
Los botones "Empleados" e "Historial" DEBEN estar centrados horizontalmente sobre las tablas.

#### Scenario: Botones visibles centrados
- **WHEN** un usuario accede a la página de Pagos al Personal
- **THEN** los botones "Empleados" e "Historial" DEBEN aparecer centrados horizontalmente en su contenedor
