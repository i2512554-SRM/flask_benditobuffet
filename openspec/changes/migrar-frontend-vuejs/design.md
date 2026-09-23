## Context

El proyecto "Bendito Buffet" es un sistema de gestión de restaurante que actualmente utiliza Flask con Jinja2 templates para server-side rendering. El frontend es JavaScript vanilla con 19 templates HTML y 5 archivos JS. La arquitectura actual genera recargas completas de página en cada interacción y dificulta la escalabilidad.

Se necesita migrar a una arquitectura SPA con Vue.js como frontend y Flask como backend API REST, manteniendo la base de datos PostgreSQL existente en Supabase.

## Goals / Non-Goals

**Goals:**
- Crear una SPA moderna con Vue.js 3 y PrimeVue
- Implementar autenticación JWT para stateless auth
- Desarrollar endpoints RESTful para todos los módulos
- Mantener la funcionalidad existente durante la migración
- Lograr un frontend mantenible y escalable

**Non-Goals:**
- Cambiar la base de datos PostgreSQL existente
- Modificar los modelos de datos actuales
- Implementar nuevas funcionalidades no existentes
- Migrar a otro backend framework

## Decisions

### 1. Arquitectura SPA con Vue.js 3

**Decisión**: Usar Vue.js 3 con Composition API y Vite como build tool.

**Alternativas consideradas**:
- **React**: Más popular pero Vue es más simple para este proyecto existente
- **Angular**: Más pesado, overkill para este tamaño de aplicación
- **Nuxt.js**: SSR innecesario, SPA es suficiente

**Razón**: Vue.js 3 Composition API es ideal para componentes reutilizables y lógica compleja. Vite proporciona build rápido y HMR excelente.

### 2. Comunicación REST con Axios

**Decisión**: Usar Axios para comunicación HTTP entre Vue.js y Flask.

**Alternativas consideradas**:
- **fetch API nativa**: Sin interceptors ni manejo automático de errores
- **vue-resource**: Obsoleto, no recomendado

**Razón**: Axios ofrece interceptors para JWT automático, manejo de errores, y cancelación de requests.

### 3. JWT para Autenticación

**Decisión**: Implementar JWT con access tokens de 15 minutos y refresh tokens de 7 días.

**Alternativas consideradas**:
- **Sesiones Flask**: Requiere estado en servidor, no escalable
- **OAuth2**: Overkill para aplicación interna

**Razón**: JWT es stateless, escalable, y estándar para APIs REST. Los refresh tokens permiten sesiones largas sin comprometer seguridad.

### 4. PrimeVue como UI Framework

**Decisión**: Usar PrimeVue 4 con tema Lara para componentes de interfaz.

**Alternativas consideradas**:
- **Vuetify**: Más opinionado, menos flexible
- **BootstrapVue**: Menos moderno, menos componentes
- **Tailwind CSS**: Requiere construir componentes desde cero

**Razón**: PrimeVue ofrece componentes ricos (DataTable, Calendar, Dropdown) con theming personalizable y soporte LTS.

### 5. Estructura de Carpetas

**Decisión**: Organizar frontend en src/views, src/components, src/stores, src/composables.

**Alternativas consideradas**:
- **Feature-based**: Más complejo para este tamaño
- **Flat structure**: Difícil de mantener

**Razón**: Estructura basada en tipos es simple y clara para proyecto de este tamaño.

### 6. CORS y Seguridad

**Decisión**: Usar flask-cors con configuración específica para desarrollo y producción.

**Configuración**:
```python
from flask_cors import CORS
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173"]}})
```

**Razón**: Permite desarrollo local con Vite y producción con dominio específico.

## Risks / Trade-offs

### Riesgos

1. **Breaking changes en rutas**: Todas las rutas Flask cambian de render HTML a JSON
   - **Mitigación**: Implementar gradualmente, mantener compatibilidad temporal

2. **Autenticación JWT**: Requiere manejo de token expiration
   - **Mitigación**: Implementar refresh tokens y auto-renewal

3. **CORS en desarrollo**: Configuración entre Vite (5173) y Flask (5000)
   - **Mitigación**: Usar proxy de Vite o flask-cors configurado

4. **Estado de UI**: Complejidad de sincronizar estado entre componentes
   - **Mitigación**: Pinia para state management centralizado

### Trade-offs

1. **SEO**: SPA no es indexable por motores de búsqueda
   - **Aceptado**: Aplicación interna, no necesita SEO

2. **JavaScript required**: Sin JS no funciona la aplicación
   - **Aceptado**: Todos los usuarios tienen navegador moderno

3. **Bundle size**: PrimeVue agrega ~200KB al bundle
   - **Aceptado**: Tree-shaking y lazy loading mitigan esto

## Migration Plan

### Fase 1: Setup Base
1. Crear proyecto Vue.js con Vite
2. Instalar PrimeVue y configurar temas
3. Configurar flask-cors en backend
4. Implementar endpoints de auth

### Fase 2: Migración Gradual
1. Migrar login (más simple)
2. Migrar panel admin
3. Migrar módulo caja
4. Migrar módulo personal
5. Migrar módulo inventario

### Fase 3: Limpieza
1. Eliminar templates Jinja2
2. Eliminar código JS legacy
3. Optimizar bundle
4. Testing y validación

### Rollback
- Mantener templates Jinja2 en branch separado
- Si Vue falla, revertir a Flask templates
- Configurar feature flag para switches

## Open Questions

1. **Deploy**: ¿Cómo se desplegará? ¿Separado o junto con Flask?
2. **Ambientes**: ¿Cuántos ambientes (dev, staging, production)?
3. **Testing**: ¿Qué framework de testing se usará?
4. **CI/CD**: ¿Pipeline de deploy automatizado?
