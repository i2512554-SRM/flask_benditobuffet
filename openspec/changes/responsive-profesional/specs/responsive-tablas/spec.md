## ADDED Requirements

### Requirement: Conversión universal de tablas a cards en ≤640px
Toda tabla del sistema SHALL convertirse a un layout de tipo card en viewports ≤640px, mostrando cada fila como una tarjeta independiente con etiquetas visibles para cada celda mediante el atributo `data-label`.

#### Scenario: Tabla de empleados con card conversion
- **WHEN** la página de empleados se visualiza en un viewport ≤640px
- **THEN** cada fila de la tabla SHALL renderizarse como una tarjeta con `data-label` para las 7 columnas (Nombre, DNI, Email, Teléfono, Rol, Estado, Acciones)
- **AND** los 3 botones de acción (Editar, Activar/Desactivar, Eliminar) SHALL apilarse verticalmente dentro de la tarjeta

#### Scenario: Tabla de inventario con card conversion
- **WHEN** la página de inventario se visualiza en un viewport ≤640px
- **THEN** cada fila de la tabla de productos SHALL renderizarse como tarjeta con `data-label` para las 6 columnas (Artículo, Categoría, Stock, Precio Unitario, Valor Total, Registrado)
- **AND** los atributos `data-nombre`/`data-categoria`/`data-fecha` SHALL ser reemplazados por `data-label` estándar

#### Scenario: Tablas de perfil con card conversion
- **WHEN** la página de perfil se visualiza en un viewport ≤640px
- **THEN** la tabla de pagos (4 columnas: Fecha, Monto, Descripción, Estado) SHALL renderizarse como tarjeta con `data-label`
- **AND** la tabla de adelantos (4 columnas: Fecha, Motivo, Monto, Estado) SHALL renderizarse como tarjeta con `data-label`

#### Scenario: Tablas existentes con data-label no se rompen
- **WHEN** las tablas de caja (2 tablas), pagos_personal (2 tablas) y pagos_personal_detalle (3 tablas) se visualizan en ≤640px
- **THEN** SHALL seguir funcionando correctamente con el CSS unificado de card-conversion
- **AND** su apariencia SHALL ser consistente con las tablas recién convertidas

#### Scenario: CSS unificado en estilos.css
- **WHEN** existe una regla CSS de card-conversion en `estilos.css`
- **THEN** SHALL aplicar a cualquier `td[data-label]` sin necesidad de CSS específico por módulo
- **AND** SHALL producir tarjetas con bordes redondeados (12px), padding interno de 16px, separación entre tarjetas de 12px, y etiquetas en mayúscula con color muted

### Requirement: data-label en cada celda de tabla
Toda celda `<td>` en una tabla SHALL tener un atributo `data-label` con el nombre legible de su columna para la conversión a cards.

#### Scenario: Formato de data-label
- **WHEN** se inspecciona un `<td>` en cualquier tabla
- **THEN** `data-label` SHALL contener el texto exacto del encabezado de columna (e.g., `data-label="Monto"`, `data-label="Fecha"`, `data-label="Estado"`)

### Requirement: Tabla de empleados con overflow wrapper
La tabla de empleados SHALL estar envuelta en un contenedor con `overflow-x: auto` para evitar desbordamiento horizontal.

#### Scenario: Overflow wrapper presente en empleados
- **WHEN** se inspecciona el HTML de la página de empleados
- **THEN** la tabla SHALL estar dentro de un `<div class="table-wrapper">` con `overflow-x: auto`
