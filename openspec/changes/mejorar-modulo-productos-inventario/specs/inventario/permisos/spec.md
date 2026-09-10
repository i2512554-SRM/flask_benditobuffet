## Purpose

Define las reglas de acceso por rol para las operaciones del módulo de inventario según el rol del usuario autenticado (administrador, cocinero, trabajador).

## ADDED Requirements

### Requirement: Acceso del administrador
El sistema SHALL permitir al rol administrador (rol 1) realizar todas las operaciones de inventario: crear productos, ver productos, editar productos, desactivar/reactivar productos, agregar stock, registrar salidas y consultar el historial de movimientos.

#### Scenario: Administrador accede a gestión completa
- **WHEN** un administrador autenticado accede al módulo de productos e inventario
- **THEN** el sistema le permite crear, editar, desactivar, agregar stock, registrar salidas y consultar movimientos

### Requirement: Acceso del cocinero
El sistema SHALL permitir al rol cocinero (rol 3) ver productos, consultar stock, agregar stock, registrar salidas/consumos y consultar movimientos de inventario. El sistema SHALL NOT permitir al cocinero crear, editar ni desactivar productos.

#### Scenario: Cocinero registra salida de insumos
- **WHEN** un cocinero autenticado registra una salida de un insumo en su pantalla de inventario
- **THEN** el sistema registra el movimiento de salida correctamente

#### Scenario: Cocinero intenta crear un producto
- **WHEN** un cocinero intenta crear, editar o desactivar un producto
- **THEN** el sistema rechaza la operación con error de acceso restringido (403)

### Requirement: Sin acceso para el trabajador
El sistema SHALL NOT exponer la gestión general del inventario al rol trabajador (rol 4). El trabajador SHALL NOT ver las opciones de gestión de productos, stock ni historial.

#### Scenario: Trabajador no ve gestión de inventario
- **WHEN** un trabajador autenticado navega por el sistema
- **THEN** el sistema no le muestra la sección de inventario ni le permite ejecutar operaciones de stock

### Requirement: Registro del responsable
El sistema SHALL registrar al usuario autenticado como responsable de cada movimiento de stock (entrada, salida, creación, compra o ajuste).

#### Scenario: Responsable en el movimiento
- **WHEN** un cocinero registra una salida
- **THEN** el historial de movimientos muestra al cocinero como responsable de esa operación