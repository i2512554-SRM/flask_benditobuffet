## Purpose

Define el registro y persistencia del monto inicial de la caja: columna `monto_inicial` en `cierres_caja`, captura opcional al abrir la caja y despliegue en el resumen de caja del panel de la cajera.

## ADDED Requirements

### Requirement: Columna monto inicial en cierres de caja
La tabla de cierres de caja SHALL incluir el campo `monto_inicial` con valor por defecto `0`, persistido al abrir la caja y disponible para consultas posteriores.

#### Scenario: Apertura sin monto inicial
- **WHEN** se abre la caja sin especificar monto inicial
- **THEN** el cierre se guarda con `monto_inicial` igual a `0`

#### Scenario: Apertura con monto inicial
- **WHEN** se abre la caja indicando un monto inicial (p. ej. S/. 200)
- **THEN** el cierre se guarda con `monto_inicial` igual al valor indicado

### Requirement: Apertura de caja con monto inicial opcional
El endpoint de apertura de caja SHALL aceptar el monto inicial opcionalmente; el monto SHALL ser numérico no negativo, y la caja SHALL abrirse efectivamente con dicho valor.

#### Scenario: Apertura exitosa con monto inicial
- **WHEN** el usuario envía la apertura con `monto_inicial: 200`
- **THEN** la respuesta contiene el cierre con `monto_inicial` 200 y la caja queda abierta

#### Scenario: Apertura con monto no válido
- **WHEN** el usuario envía la apertura con `monto_inicial` negativo o no numérico
- **THEN** el endpoint rechaza la solicitud con un error claro y no abre la caja

### Requirement: Despliegue del monto inicial en el resumen de caja
El resumen de caja del panel de la cajera SHALL mostrar el monto inicial del cierre del día; si la caja aún no se abrió, se muestra el valor por defecto `0`.

#### Scenario: Caja abierta con monto inicial
- **WHEN** la caja del día está abierta con un monto inicial registrado
- **THEN** la tarjeta "Monto inicial / apertura" muestra el valor persistido del cierre

#### Scenario: Caja cerrada o sin apertura
- **WHEN** la caja no tiene un cierre abierto hoy
- **THEN** la tarjeta "Monto inicial / apertura" muestra `S/. 0.00`