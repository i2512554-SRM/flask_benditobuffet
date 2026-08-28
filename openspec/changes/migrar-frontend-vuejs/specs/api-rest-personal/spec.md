## Purpose

API REST para el módulo de gestión de personal, incluyendo empleados, pagos, turnos, adelantos y salarios.

## ADDED Requirements

### Requirement: CRUD de empleados
El sistema SHALL permitir crear, leer, actualizar y eliminar registros de empleados.

#### Scenario: Crear empleado
- **WHEN** el admin envía POST /api/personal/empleados con datos válidos
- **THEN** el sistema crea el empleado y retorna sus datos

#### Scenario: Listar empleados
- **WHEN** el admin envía GET /api/personal/empleados
- **THEN** el sistema retorna lista paginada de empleados

#### Scenario: Actualizar empleado
- **WHEN** el admin envía PUT /api/personal/empleados/{id}
- **THEN** el sistema actualiza los datos y retorna empleado actualizado

#### Scenario: Eliminar empleado
- **WHEN** el admin envía DELETE /api/personal/empleados/{id}
- **THEN** el sistema elimina el empleado lógicamente

### Requirement: Gestión de pagos
El sistema SHALL permitir registrar y consultar pagos a empleados.

#### Scenario: Registrar pago
- **WHEN** el admin envía POST /api/personal/pagos con empleado_id, monto, período
- **THEN** el sistema registra el pago y actualiza el historial

#### Scenario: Consultar pagos por empleado
- **WHEN** el admin envía GET /api/personal/pagos?empleado_id=X
- **THEN** el sistema retorna historial de pagos del empleado

### Requirement: Gestión de turnos
El sistema SHALL permitir asignar y consultar turnos de trabajo.

#### Scenario: Asignar turno
- **WHEN** el admin envía POST /api/personal/turnos con empleado_id, fecha, hora_inicio, hora_fin
- **THEN** el sistema crea el turno

#### Scenario: Consultar turnos por fecha
- **WHEN** el admin envía GET /api/personal/turnos?fecha=X
- **THEN** el sistema retorna turnos asignados para esa fecha

### Requirement: Gestión de adelantos
El sistema SHALL permitir registrar adelantos de salario a empleados.

#### Scenario: Registrar adelanto
- **WHEN** el admin envía POST /api/personal/adelantos con empleado_id, monto
- **THEN** el sistema registra el adelanto y actualiza saldo pendiente

#### Scenario: Consultar adelantos pendientes
- **WHEN** el admin envía GET /api/personal/adelantos?empleado_id=X&pendientes=true
- **THEN** el sistema retorna adelantos sin descontar

### Requirement: Cálculo de salarios
El sistema SHALL calcular automáticamente el salario de cada empleado según horas trabajadas y bonificaciones.

#### Scenario: Calcular salario mensual
- **WHEN** el admin solicita GET /api/personal/salarios?mes=X&año=Y
- **THEN** el sistema retorna cálculo detallado por empleado
