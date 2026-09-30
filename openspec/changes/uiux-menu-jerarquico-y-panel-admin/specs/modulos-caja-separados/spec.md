## Purpose

Define el subconjunto de módulos de Caja como navegación jerárquica con dashboard propio: `/caja/dashboard`, `/caja` (control), `/caja/movimientos`, `/caja/historial`, y respaldo con el backend histórico.

## ADDED Requirements

### Requirement: Rutas de Caja por función
- `/caja/dashboard` SHALL renderizar el panel-tipo-dashboard (bienvenida + resumen + acciones);
- `/caja` SHALL renderizar el módulo transaccional (Control de Caja);
- `/caja/movimientos` SHALL renderizar la lista de movimientos del día con toggle de histórico;
- `/caja/historial` SHALL renderizar la tabla de cierres cerrados con montos y saldo.

#### Scenario: homeForRole de Admin y Cajera
- **WHEN** un usuario de rol 1 o 2 inicia sesión
- **THEN** es dirigido a `/caja/dashboard`

### Requirement: Endpoint de histórico de caja
`GET /api/caja/transacciones?historico=1` SHALL devolver, además del día en curso, `historico` con los cierres (cabecera y saldo) y las últimas `N` transacciones de todas las fechas.

#### Scenario: Pedir histórico
- **WHEN** se llama con `?historico=1`
- **THEN** la respuesta incluye `historico: [ { cierre_id, cerrado, ventas, gastos, neto, fecha } ]` ordenado desc por fecha
- **AND** `transacciones` contiene los últimos movimientos históricos (no solo los del día)