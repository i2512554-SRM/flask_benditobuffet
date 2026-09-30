## Purpose

Mantiene un historial de inventario por movimiento donde cada operación (entrada, salida, creación, compra, ajuste) queda registrada de forma independiente con stock anterior, stock posterior, motivo, usuario, unidad y fecha.

## ADDED Requirements

### Requirement: Cada operación genera su propio movimiento
El sistema SHALL registrar cada operación de stock como un movimiento individual e independiente en `inventario_movimientos`. El historial SHALL NOT agrupar operaciones en un único registro. Cada movimiento SHALL conservar: producto, tipo de movimiento, cantidad (con su signo), unidad, stock anterior, stock posterior, motivo, usuario y fecha/hora.

#### Scenario: Múltiples operaciones del mismo producto
- **WHEN** sobre "Arroz" se realizan una entrada de +20 Kg, luego una entrada de +10 Kg y luego una salida de -5 Kg
- **THEN** el historial contiene tres movimientos separados y ordenados por fecha, y el stock actual del producto es 25 Kg

#### Scenario: Los movimientos no cambian al variar el stock
- **WHEN** después de varios movimientos se agrega más stock
- **THEN** los movimientos anteriores conservan sus valores de stock anterior/posterior tal como ocurrieron

#### Scenario: Creación de producto con stock inicial
- **WHEN** se crea un producto con stock inicial mayor a cero
- **THEN** el sistema registra un movimiento "Entrada" inicial con el stock inicial y stock anterior 0

### Requirement: Consulta del historial con trazabilidad
El sistema SHALL permitir consultar el historial de movimientos por producto y por tipo de movimiento. Cada registro SHALL mostrar producto, tipo, cantidad, unidad, stock anterior, stock posterior, motivo, responsable y fecha/hora.

#### Scenario: Filtrar historial por producto
- **WHEN** un usuario consulta el historial con filtro de producto "Arroz"
- **THEN** el sistema devuelve únicamente los movimientos de "Arroz" con sus stocks anterior y posterior

#### Scenario: Filtrar por tipo
- **WHEN** un usuario filtra el historial por tipo "Salida"
- **THEN** el sistema devuelve únicamente los movimientos de tipo "Salida"