## ADDED Requirements

### Requirement: Conversión universal de tablas a cards en mobile
Toda tabla del sistema SHALL convertirse a un layout de tipo card en viewports ≤640px, mostrando cada fila como una tarjeta independiente con etiquetas visibles para cada celda.

#### Scenario: Tabla de empleados con card conversion
- **WHEN** la página de empleados se visualiza en un viewport ≤640px
- **THEN** cada fila de la tabla SHALL renderizarse como una tarjeta apilada, con `data-label` mostrando el nombre de cada columna antes del valor

#### Scenario: Tabla de inventario con card conversion
- **WHEN** la página de inventario se visualiza en un viewport ≤640px
- **THEN** cada fila de la tabla de productos SHALL renderizarse como tarjeta, usando `data-label` en lugar de los atributos `data-nombre`/`data-categoria`/`data-fecha` actuales

#### Scenario: Tablas de perfil con card conversion
- **WHEN** la página de perfil se visualiza en un viewport ≤640px
- **THEN** las tablas de pagos y adelantos SHALL renderizarse como tarjetas, usando `data-label` en cada `<td>`

#### Scenario: data-label en cada celda
- **WHEN** una tabla tiene card conversion en ≤640px
- **THEN** cada `<td>` SHALL tener un atributo `data-label` con el nombre legible de su columna (e.g., `data-label="Monto"`, `data-label="Fecha"`)

#### Scenario: Tablas existentes con data-label no se rompen
- **WHEN** las tablas de caja, pagos_personal y pagos_personal_detalle (que ya tienen `data-label`) se visualizan en ≤640px
- **THEN** SHALL seguir funcionando correctamente con el CSS unificado de card-conversion

#### Scenario: CSS unificado en estilos.css
- **WHEN** existe una regla CSS de card-conversion en `estilos.css` aplicable a cualquier tabla
- **THEN** las reglas SHALL aplicar a toda tabla que tenga celdas con `data-label`, sin necesidad de CSS específico por módulo

### Requirement: Tabla de empleados con overflow wrapper
La tabla de empleados SHALL estar envuelta en un contenedor con `overflow-x: auto` para evitar desbordamiento horizontal en cualquier viewport.

#### Scenario: Overflow wrapper presente
- **WHEN** se inspecciona el HTML de la página de empleados
- **THEN** la tabla SHALL estar dentro de un `<div class="table-wrapper">` o similar con `overflow-x: auto`
