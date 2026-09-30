## Purpose

API REST para el módulo de inventario e inversiones, permitiendo gestionar productos, compras, categorías y proveedores.

## ADDED Requirements

### Requirement: CRUD de productos
El sistema SHALL permitir crear, leer, actualizar y eliminar productos del inventario.

#### Scenario: Crear producto
- **WHEN** el admin envía POST /api/inventario/productos con nombre, categoría, stock, precio
- **THEN** el sistema crea el producto y retorna sus datos

#### Scenario: Listar productos
- **WHEN** el admin envía GET /api/inventario/productos
- **THEN** el sistema retorna lista paginada de productos

#### Scenario: Actualizar stock
- **WHEN** el admin envía PUT /api/inventario/productos/{id}/stock con cantidad
- **THEN** el sistema actualiza el stock del producto

### Requirement: Registro de compras
El sistema SHALL permitir registrar compras de productos con detalle de proveedor y montos.

#### Scenario: Registrar compra
- **WHEN** el admin envía POST /api/inventario/compras con producto_id, cantidad, monto, proveedor
- **THEN** el sistema registra la compra y actualiza stock

#### Scenario: Consultar historial de compras
- **WHEN** el admin envía GET /api/inventario/compras?producto_id=X
- **THEN** el sistema retorna historial de compras del producto

### Requirement: Gestión de categorías
El sistema SHALL permitir administrar categorías de productos.

#### Scenario: Crear categoría
- **WHEN** el admin envía POST /api/inventario/categorias con nombre
- **THEN** el sistema crea la categoría

#### Scenario: Listar categorías
- **WHEN** el admin envía GET /api/inventario/categorias
- **THEN** el sistema retorna todas las categorías

### Requirement: Gestión de proveedores
El sistema SHALL permitir administrar proveedores de productos.

#### Scenario: Crear proveedor
- **WHEN** el admin envía POST /api/inventario/proveedores con datos
- **THEN** el sistema crea el proveedor

#### Scenario: Listar proveedores
- **WHEN** el admin envía GET /api/inventario/proveedores
- **THEN** el sistema retorna todos los proveedores

### Requirement: Inversiones y equipamiento
El sistema SHALL permitir registrar inversiones en equipamiento y activos fijos.

#### Scenario: Registrar inversión
- **WHEN** el admin envía POST /api/inversiones con descripción, monto, fecha
- **THEN** el sistema registra la inversión

#### Scenario: Consultar historial de inversiones
- **WHEN** el admin envía GET /api/inversiones?fecha_inicio=X&fecha_fin=Y
- **THEN** el sistema retorna inversiones en ese rango
