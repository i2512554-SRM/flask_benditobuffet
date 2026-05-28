## Why

El proyecto tiene 8 CSS modulares con **duplicación masiva**: cada módulo redeclara botones, tabs, modales, tablas, cards y formularios con valores ligeramente distintos. Hay 2 fuentes inconsistentes (Inter vs Lexend), 2 estilos de botón primario (gradiente vs sólido), 3 patrones de modal diferentes, y valores hardcodeados que rompen dark mode (ej: `rgba(0,0,0,0.55)` en panel.css). El resultado visual es funcional pero carece de cohesión profesional — se nota que es un proyecto construido por capas sin un sistema de diseño unificado.

## What Changes

**Sistema de Diseño Unificado (breaking change visual):**
- Refactor completo de `variables.css` con paleta cromática profesional: naranja primario (`#ff6b00`), verde petróleo secundario (`#0a2e2f`), escalas neutrales, sistema de spacing 4px, tipografía solo Inter, sombras con 3 niveles, border-radius tokens
- **Componentes compartidos** extraídos a `componentes.css`: botones (`.btn` variants), cards (`.card` variants), modales, tabs, tablas, formularios, badges, loading states — TODO módulo los importa eliminando las declaraciones duplicadas en cada CSS
- **Modernización visual completa**: glassmorphism en cards (`backdrop-filter: blur`), gradientes sutiles en headers, micro-interacciones (hover con transform + shadow, focus rings, ripple effect en botones), refinamiento de border-radius (12px/16px/24px), tipografía fluida con `clamp()`
- **Dark mode pulido**: overlay usa `--overlay-bg`, inputs y selects dark-mode corregidos, scrollbar custom unificado, sin valores hardcodeados
- **Consolidación de carga de Font Awesome**: CDN unificado en `base.html`, eliminar cargas locales duplicadas

## Capabilities

### New Capabilities
- `sistema-diseno`: Tokens de diseño unificados — paleta, tipografía, spacing, elevation, border-radius, transiciones
- `componentes-compartidos`: Biblioteca de componentes CSS compartidos (botones, cards, modales, tabs, tablas, formularios, badges, loading) en `componentes.css`
- `modernizacion-visual`: Micro-interacciones, glassmorphism, glass nav, animaciones sutiles, tipografía fluida, refinamiento visual completo

### Modified Capabilities
<!-- Ninguna - es creación de nuevo sistema de diseño -->

## Impact

**CSS (9 archivos modificados, 1 creado, 7 simplificados):**
- `variables.css` — refactor completo: nueva paleta, spacing scale, elevation tokens, tipografía
- `componentes.css` — **NUEVO**: componentes compartidos (botones, cards, modales, tabs, tablas, formularios, badges)
- `panel.css` — eliminar ~200 líneas duplicadas (botones, cards, modales, tablas), mantener layout específico
- `caja.css` — eliminar ~100 líneas duplicadas, mantener layout caja-header, main-grid, tabs-nav específico
- `inventario.css` — eliminar ~150 líneas duplicadas, mantener stats, toolbar, compra-cards específico
- `empleados.css` — eliminar ~80 líneas duplicadas, mantener header, tabs, form-grid específico
- `perfil.css` — eliminar ~80 líneas duplicadas, mantener profile-card, avatar, keyinfo específico
- `login.css` — simplificar manteniendo login-specific layout
- `estilos.css` — integrar loading states y DNI lookup en componentes.css, mantener responsive helpers
- `pagos_personal.html` y `pagos_personal_detalle.html` — dependen de `panel.css` + `caja.css`, se benefician automáticamente

**Templates (ningún cambio obligatorio — es refactor CSS):**
- `base.html` — agregar carga de `componentes.css` después de `variables.css`, Font Awesome CDN unificado
- Los 11 templates heredan los nuevos estilos sin modificación de HTML
- Opcional: agregar clases modernas a elementos existentes si es necesario para el nuevo sistema

**Rendimiento:**
- Una sola carga de Font Awesome CDN elimina 6 cargas redundantes
- component.css reemplaza ~600 líneas duplicadas → menos CSS total
- Sin JS nuevo — solo CSS vanilla
