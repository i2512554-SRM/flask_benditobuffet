## Purpose

Backend Flask modificado para exponer API REST en lugar de renderizar templates Jinja2.

## MODIFIED Requirements

### Requirement: Endpoints de autenticación
El sistema SHALL proporcionar endpoints RESTful para autenticación con JWT.

#### Scenario: Login via API
- **WHEN** el cliente envía POST /api/auth/login con credenciales
- **THEN** el backend retorna token JWT y datos de usuario en JSON

#### Scenario: Logout via API
- **WHEN** el cliente envía POST /api/auth/logout con token válido
- **THEN** el backend invalida el token

### Requirement: Endpoints de caja
El sistema SHALL exponer API REST para operaciones de caja.

#### Scenario: Abrir caja via API
- **WHEN** el cliente envía POST /api/caja/abrir con monto_inicial
- **THEN** el backend crea registro y retorna JSON

#### Scenario: Registrar transacción via API
- **WHEN** el cliente envía POST /api/caja/transaccion
- **THEN** el backend registra y retorna transacción creada

### Requirement: Endpoints de personal
El sistema SHALL exponer API REST para gestión de personal.

#### Scenario: CRUD empleados via API
- **WHEN** el cliente envía requests a /api/personal/empleados
- **THEN** el backend procesa CRUD y retorna JSON

### Requirement: Endpoints de inventario
El sistema SHALL exponer API REST para gestión de inventario.

#### Scenario: CRUD productos via API
- **WHEN** el cliente envía requests a /api/inventario/productos
- **THEN** el backend procesa CRUD y retorna JSON

### Requirement: CORS habilitado
El sistema SHALL permitir requests cross-origin desde el frontend Vue.js.

#### Scenario: Request desde Vue.js
- **WHEN** el frontend Vue.js envía request al backend Flask
- **THEN** el backend procesa normalmente sin bloqueo CORS

### Requirement: Serialización JSON
El sistema SHALL retornar respuestas en formato JSON con estructura consistente.

#### Scenario: Respuesta exitosa
- **WHEN** el backend procesa request exitoso
- **THEN** retorna { "success": true, "data": {...} }

#### Scenario: Respuesta de error
- **WHEN** el backend encuentra error
- **THEN** retorna { "success": false, "error": "mensaje" }

### Requirement: Validación de datos
El sistema SHALL validar datos de entrada en endpoints API.

#### Scenario: Datos inválidos
- **WHEN** el cliente envía datos con campos requeridos faltantes
- **THEN** el backend retorna error 400 con detalles de validación
