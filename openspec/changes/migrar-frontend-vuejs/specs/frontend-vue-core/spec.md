## Purpose

Framework Vue.js base con router, stores Pinia, y layout principal para la aplicación frontend SPA.

## ADDED Requirements

### Requirement: Navegación SPA
El sistema SHALL proporcionar navegación entre vistas sin recarga de página completa.

#### Scenario: Navegación entre vistas
- **WHEN** el usuario hace clic en un enlace de navegación
- **THEN** el sistema carga la vista solicitada sin recargar la página

#### Scenario: URL del navegador
- **WHEN** el usuario navega a una vista
- **THEN** la URL del navegador se actualiza correctamente

### Requirement: Layout principal
El sistema SHALL proporcionar un layout base con header, sidebar y área de contenido.

#### Scenario: Layout consistente
- **WHEN** el usuario navega entre vistas
- **THEN** el layout (header, sidebar) se mantiene consistente

#### Scenario: Sidebar colapsable
- **WHEN** el usuario hace clic en botón de colapsar sidebar
- **THEN** el sidebar se contrae mostrando solo iconos

### Requirement: State management con Pinia
El sistema SHALL manejar estado global mediante stores Pinia.

#### Scenario: Store de autenticación
- **WHEN** el usuario inicia sesión
- **THEN** el store auth guarda token, datos de usuario y rol

#### Scenario: Persistencia de sesión
- **WHEN** el usuario recarga la página
- **THEN** el store recupera sesión de localStorage y mantiene estado

### Requirement: Rutas protegidas
El sistema SHALL proteger rutas según el rol del usuario.

#### Scenario: Acceso no autenticado
- **WHEN** un usuario no autenticado intenta acceder a ruta protegida
- **THEN** el sistema redirige a login

#### Scenario: Acceso con rol incorrecto
- **WHEN** un usuario intenta acceder a ruta de otro rol
- **THEN** el sistema muestra mensaje de acceso denegado

### Requirement: Tema oscuro/claro
El sistema SHALL permitir alternar entre tema oscuro y claro.

#### Scenario: Cambio de tema
- **WHEN** el usuario hace clic en botón de tema
- **THEN** el sistema cambia la apariencia visual y guarda preferencia

### Requirement: Loading states
El sistema SHALL mostrar indicadores de carga durante operaciones asíncronas.

#### Scenario: Carga de datos
- **WHEN** el frontend solicita datos al backend
- **THEN** muestra indicador de carga hasta completar la operación
