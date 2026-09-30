## Purpose

Gestiona el stock mediante dos operaciones separadas: "Agregar stock" (entrada a un producto existente) y "Registrar salida" (consumo o uso), con unidad coherente al producto y validaciones que impiden stock negativo.

## ADDED Requirements

### Requirement: Agregar stock a un producto existente
El sistema SHALL ofrecer una operación "Agregar stock" que NO crea productos nuevos: requiere seleccionar un producto existente (activo) mediante buscador/selector y una cantidad a ingresar. El sistema SHALL mostrar el stock actual del producto y SHALL NOT permitir modificar nombre ni unidad del producto desde esta operación.

#### Scenario: Entrada exitosa con stock anterior y posterior
- **WHEN** el producto "Arroz" tiene 20 Kg y un usuario autorizado agrega 10 Kg
- **THEN** el sistema registra el movimiento "Entrada" de +10 Kg con stock anterior 20 y stock posterior 30, y el stock actual del producto pasa a 30 Kg

#### Scenario: La unidad se hereda del producto
- **WHEN** se agrega stock a un producto cuya unidad es "Kg"
- **THEN** el sistema usa la unidad del producto y rechaza el ingreso si se envía una cantidad con unidad distinta

#### Scenario: Producto inactivo no disponible
- **WHEN** un producto está desactivado
- **THEN** el sistema no permite seleccionarlo para agregar stock

#### Scenario: Cantidad inválida
- **WHEN** un usuario envía una cantidad a agregar menor o igual a cero
- **THEN** el sistema rechaza la operación con un mensaje de error

### Requirement: Registrar salida de stock
El sistema SHALL ofrecer un operación "Registrar salida" para descontar stock por consumo o uso. La salida SHALL requerir seleccionar un producto existente (activo), una cantidad y un motivo. El sistema SHALL NOT eliminar el producto al registrar la salida; sólo cambia su cantidad disponible.

#### Scenario: Salida exitosa
- **WHEN** el producto "Arroz" tiene 30 Kg y un usuario registra una salida de 5 Kg con motivo "Preparación"
- **THEN** el sistema registra el movimiento "Salida" de -5 Kg con stock anterior 30 y stock posterior 25, y el stock del producto pasa a 25 Kg

#### Scenario: Salida mayor al stock disponible
- **WHEN** el producto tiene 5 Kg y un usuario intenta registrar una salida de 8 Kg
- **THEN** el sistema rechaza la salida con el error "No hay suficiente stock disponible" y no modifica el stock ni crea movimientos

#### Scenario: Salida con motivo vacío
- **WHEN** un usuario intenta registrar una salida sin motivo
- **THEN** el sistema rechaza la operación solicitando el motivo

### Requirement: Stock nunca negativo
El sistema SHALL garantizar que el stock de un producto nunca quede en valores negativos como resultado de ninguna operación.

#### Scenario: Stock exacto a cero
- **WHEN** el producto tiene 5 Kg y se registra una salida de exactamente 5 Kg
- **THEN** el sistema permite la salida y el stock queda en 0 Kg

#### Scenario: Rechazo de stock negativo
- **WHEN** cualquier operación intentaría dejar el stock en valor negativo
- **THEN** el sistema la rechaza antes de persistir y mantiene el stock anterior