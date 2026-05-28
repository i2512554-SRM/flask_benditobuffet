## ADDED Requirements

### Requirement: Vista de detalle centrada con card moderna
La vista de detalle de inversión DEBE mostrar la información en una tarjeta centrada horizontalmente con un max-width que garantice legibilidad.

#### Scenario: La tarjeta de detalle se muestra centrada en desktop
- **WHEN** un usuario accede a la página de detalle de una inversión en una pantalla de escritorio (>900px)
- **THEN** la tarjeta de detalle DEBE aparecer centrada horizontalmente con un max-width de 800px y margen automático

#### Scenario: La tarjeta de detalle se adapta en mobile
- **WHEN** un usuario accede a la página de detalle en una pantalla de menos de 700px
- **THEN** los metadatos (monto, proveedor, fecha) DEBEN apilarse verticalmente en una sola columna

### Requirement: Metadatos organizados en grid
Los campos de información de la inversión (monto, proveedor, fecha) DEBEN presentarse en un grid visual con etiqueta sobre el valor para facilitar la lectura rápida.

#### Scenario: Metadatos visibles con etiquetas
- **WHEN** la página de detalle se renderiza
- **THEN** cada campo DEBE mostrar una etiqueta semitransparente (label) arriba y el valor abajo en un grid de 3 columnas

### Requirement: Badge para número de inversión
El identificador único de la inversión DEBE mostrarse como un badge/píldora destacado visualmente.

#### Scenario: ID de inversión como badge
- **WHEN** se renderiza el encabezado del detalle
- **THEN** el texto "Inversión #<id>" DEBE aparecer como un badge con fondo semitransparente y bordes redondeados

### Requirement: Separación visual entre secciones
Las secciones de metadatos y descripción/notas DEBEN estar separadas visualmente con una línea divisoria sutil.

#### Scenario: Separador entre metadatos y descripción
- **WHEN** la página muestra tanto metadatos como descripción
- **THEN** DEBE haber una línea horizontal sutil entre ambas secciones

### Requirement: Consistencia con tokens de diseño existentes
Todos los estilos nuevos DEBEN reutilizar las variables CSS del módulo inventario (`--inventario-*`) para mantener consistencia visual.

#### Scenario: Diseño consistente con otras vistas
- **WHEN** se inspeccionan los estilos de la página de detalle
- **THEN** los colores, bordes y sombras DEBEN usar las variables `--inventario-card`, `--inventario-border`, `--inventario-muted`, `--inventario-accent` y similares
