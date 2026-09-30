## Purpose

Sistema de autenticación JWT para la API REST de Flask, que permite a los usuarios autenticarse y mantener sesiones Stateless mediante tokens de acceso.

## ADDED Requirements

### Requirement: Login de usuario
El sistema SHALL permitir a los usuarios autenticarse mediante credenciales (usuario/contraseña) y retornar un token JWT de acceso.

#### Scenario: Login exitoso
- **WHEN** el usuario envía POST /api/auth/login con credenciales válidas
- **THEN** el sistema retorna un token JWT de acceso, refresh token, y datos del usuario (id, nombre, rol)

#### Scenario: Credenciales inválidas
- **WHEN** el usuario envía POST /api/auth/login con credenciales incorrectas
- **THEN** el sistema retorna error 401 con mensaje "Credenciales inválidas"

### Requirement: Cierre de sesión
El sistema SHALL permitir a los usuarios cerrar sesión invalidando el token actual.

#### Scenario: Logout exitoso
- **WHEN** el usuario envía POST /api/auth/logout con token válido
- **THEN** el sistema invalida el token y retorna confirmación

### Requirement: Renovación de token
El sistema SHALL permitir renovar el token de acceso antes de que expire utilizando el refresh token.

#### Scenario: Renovación exitosa
- **WHEN** el usuario envía POST /api/auth/refresh con refresh token válido
- **THEN** el sistema retorna un nuevo token de acceso

#### Scenario: Refresh token expirado
- **WHEN** el usuario envía POST /api/auth/refresh con refresh token expirado
- **THEN** el sistema retorna error 401 y requiere login nuevamente

### Requirement: Verificación de sesión
El sistema SHALL verificar la validez del token en cada request autenticado.

#### Scenario: Token válido
- **WHEN** el usuario envía request con header Authorization: Bearer <token_válido>
- **THEN** el sistema procesa la solicitud normalmente

#### Scenario: Token inválido o expirado
- **WHEN** el usuario envía request con token inválido o expirado
- **THEN** el sistema retorna error 401

### Requirement: Control de acceso por roles
El sistema SHALL controlar el acceso a endpoints según el rol del usuario (administrador, cajero, cocina, trabajador).

#### Scenario: Acceso autorizado
- **WHEN** el usuario tiene el rol requerido para el endpoint
- **THEN** el sistema permite el acceso

#### Scenario: Acceso denegado
- **WHEN** el usuario no tiene el rol requerido
- **THEN** el sistema retorna error 403
