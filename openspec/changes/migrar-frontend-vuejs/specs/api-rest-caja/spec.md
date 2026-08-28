## Purpose

API REST para el módulo de gestión de caja, permitiendo operaciones de apertura, cierre, transacciones y reportes diarios.

## ADDED Requirements

### Requirement: Apertura de caja
El sistema SHALL permitir abrir la caja del día con un monto inicial.

#### Scenario: Apertura exitosa
- **WHEN** el cajero envía POST /api/caja/abrir con monto_inicial
- **THEN** el sistema crea un registro de apertura y retorna los datos de la caja abierta

#### Scenario: Caja ya abierta
- **WHEN** el cajero intenta abrir caja cuando ya existe una abierta
- **THEN** el sistema retorna error 400 "Ya existe una caja abierta"

### Requirement: Registro de transacciones
El sistema SHALL permitir registrar ingresos y egresos en la caja.

#### Scenario: Registrar ingreso
- **WHEN** el cajero envía POST /api/caja/transaccion con tipo="ingreso", monto, descripción
- **THEN** el sistema registra la transacción y actualiza el saldo

#### Scenario: Registrar egreso
- **WHEN** el cajero envía POST /api/caja/transaccion con tipo="egreso", monto, descripción
- **THEN** el sistema registra la transacción y actualiza el saldo

### Requirement: Cierre de caja
El sistema SHALL permitir cerrar la caja del día con resumen de transacciones.

#### Scenario: Cierre exitoso
- **WHEN** el cajero envía POST /api/caja/cerrar
- **THEN** el sistema calcula totales, crea registro de cierre, y retorna resumen

### Requirement: Consulta de historial
El sistema SHALL permitir consultar el historial de transacciones por rango de fechas.

#### Scenario: Consulta por fecha
- **WHEN** el usuario envía GET /api/caja/historial?fecha_inicio=X&fecha_fin=Y
- **THEN** el sistema retorna lista de transacciones en ese rango

### Requirement: Reportes de caja
El sistema SHALL generar reportes de caja diarios, semanales y mensuales.

#### Scenario: Reporte diario
- **WHEN** el usuario solicita GET /api/caja/reporte/diario?fecha=X
- **THEN** el sistema retorna resumen de ingresos, egresos y balance del día
