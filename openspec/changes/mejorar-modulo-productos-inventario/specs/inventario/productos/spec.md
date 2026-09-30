## Purpose

Define el ciclo de vida de los productos del inventario: creación sin duplicados, unidad de medida, descripción y estado, edición descriptiva y desactivación lógica conservando el historial.

## ADDED Requirements

### Requirement: Crear un producto nuevo
El sistema SHALL permitir crear un producto nuevo con nombre, unidad de medida (Kilogramos "Kg", Unidades "Un" o Litros "Lt"), stock inicial, descripción opcional y estado. Cada producto SHALL almacenar su unidad de medida asociada.

#### Scenario: Creación exitosa
- **WHEN** un usuario autorizado crea "Arroz" con unidad "Kg", stock inicial 20 y estado activo
- **THEN** el sistema crea un único registro y devuelve los datos del producto con stock 20 y unidad "Kg"

#### Scenario: Unidad inválida
- **WHEN** un usuario envía un producto con una unidad de medida no contemplada (por ejemplo "cm")
- **THEN** el sistema rechaza la creación con un mensaje de error de unidad no válida

#### Scenario: Stock inicial cero
- **WHEN** un usuario crea un producto con stock inicial 0
- **THEN** el sistema permite crearlo sin generar un movimiento de entrada

### Requirement: Prevenir productos duplicados
Antes de crear un producto, el sistema SHALL verificar si existe otro producto con el mismo nombre ignorando mayúsculas y minúsculas. Si existe, el sistema SHALL NOT crearlo y SHALL devolver un mensaje de error que indique que el producto ya existe y que para aumentar su cantidad debe usarse "Agregar stock".

#### Scenario: Nombre con variación de mayúsculas
- **WHEN** ya existe "Arroz" en el sistema y un usuario intenta crear "arroz" o "ARROZ"
- **THEN** el sistema no crea un nuevo registro y muestra el error "El producto ya existe en el sistema. Si deseas aumentar su cantidad, utiliza la opción 'Agregar stock'"

#### Scenario: Nombres distintos
- **WHEN** ya existe "Arroz" y el usuario crea "Papa"
- **THEN** el sistema crea el nuevo producto "Papa" sin conflicto

### Requirement: Editar producto
El sistema SHALL permitir editar únicamente información descriptiva del producto: nombre, unidad de medida, descripción y estado. El sistema SHALL NOT permitir modificar el stock mediante la edición.

#### Scenario: Editar nombre, unidad y descripción
- **WHEN** un usuario edita "Arroz" cambiando su nombre, unidad o descripción
- **THEN** el sistema guarda los cambios descriptivos y conserva el stock y los movimientos existentes

#### Scenario: Edición con nombre duplicado
- **WHEN** un usuario intenta renombrar un producto a un nombre que ya existe en otro producto activo
- **THEN** el sistema rechaza el cambio con el error de producto duplicado

### Requirement: Desactivar producto
El sistema SHALL NOT eliminar físicamente un producto que tenga movimientos registrados. En su lugar, el sistema SHALL desactivarlo (estado "inactivo"). Un producto desactivado SHALL NOT aparecer como opción para nuevas entradas ni salidas, pero su historial de movimientos y sus registros anteriores SHALL permanecer intactos.

#### Scenario: Desactivar producto con movimientos
- **WHEN** un usuario desactiva "Arroz" que tiene movimientos históricos
- **THEN** el producto queda con estado inactivo, deja de listarse como disponible para agregar stock o registrar salidas, y su historial se conserva completo

#### Scenario: Re-activar producto
- **WHEN** un usuario vuelve a activar un producto inactivo
- **THEN** el producto reaparece como disponible manteniendo su stock y su historial previo