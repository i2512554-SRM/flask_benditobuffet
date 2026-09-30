## Why

El frontend actual utiliza Jinja2 templates con JavaScript vanilla, lo que genera páginas completas con recargas totales en cada interacción, experiencia de usuario pobre, y difícil escalabilidad. Se necesita migrar a Vue.js con PrimeVue para lograr una SPA moderna con interactividad en tiempo real, mejor UX, y código frontend mantenible y modular.

## What Changes

- **Migración completa del frontend**: De Jinja2 templates a Vue.js 3 (Composition API) con Vue Router para navegación SPA
- **API REST**: Flask expondrá endpoints RESTful para comunicación con el frontend, eliminando render_template()
- **Autenticación JWT**: Reemplazo de sesiones Flask por tokens JWT para autenticación Stateless
- **UI Framework**: Implementación de PrimeVue para componentes UI profesionales (tablas, formularios, botones, etc.)
- **State Management**: Pinia para manejo de estado global (autenticación, tema, datos de usuario)
- **CORS**: Configuración de flask-cors para permitir requests desde Vue.js
- **Estructura modular**: Organización de código en componentes reutilizables y composables

## Capabilities

### New Capabilities
- `api-rest-auth`: Sistema de autenticación JWT con endpoints REST (login, logout, refresh token, verificación de sesión)
- `api-rest-caja`: API REST para módulo de caja (apertura, cierre, transacciones, reportes)
- `api-rest-personal`: API REST para gestión de personal (empleados, pagos, turnos, adelantos, salarios)
- `api-rest-inventario`: API REST para módulo de inventario e inversiones (productos, compras, categorías)
- `frontend-vue-core`: Framework Vue.js base con router, stores, y layout principal
- `frontend-ui-primevue`: Integración de PrimeVue como UI framework con theming

### Modified Capabilities
- `backend-flask-core`: Flask se modifica para exponer API REST en lugar de renderizar templates (requiere flask-cors, flask-jwt-extended, marshmallow)

## Impact

### Code Changes
- **app.py**: Se eliminan todas las rutas render_template, se agregan rutas API con prefijo /api/
- **api/**: Nuevo módulo con rutas organizadas por dominio (auth, caja, personal, inventario, ia)
- **schemas/**: Nuevo módulo para serialización JSON (marshmallow)
- **frontend/**: Nueva carpeta con app Vue.js completa

### Dependencies
- **Nuevas (backend)**: flask-cors, flask-jwt-extended, flask-marshmallow, marshmallow-sqlalchemy
- **Nuevas (frontend)**: vue, vue-router, pinia, primevue, primeicons, axios, vite
- **Eliminadas**: Flask-WTF CSRF (se reemplaza por JWT), dependencias de Jinja2 templates

### Systems
- **Autenticación**: Sesiones Flask → JWT tokens
- **Comunicación**: render_template() → REST API + fetch/axios
- **Estado**: Stateful (Flask session) → Stateless (JWT)
- **Desarrollo**: Full-page reloads → SPA navigation

### Breakpoints
- **BREAKING**: Todas las rutas actuales de Flask que retornan HTML cambian a retornar JSON
- **BREAKING**: Frontend ya no se sirve desde Flask, se construye con Vite
- **BREAKING**: Sistema de autenticación completamente nuevo
