## ADDED Requirements

### Requirement: Biblioteca de componentes en `componentes.css`
SHALL existir un archivo `static/css/componentes.css` que contenga TODAS las definiciones de componentes compartidos, eliminando la duplicación en los CSS modulares. `base.html` SHALL cargarlo después de `variables.css`. Cada CSS modular SHALL eliminar sus definiciones de botones, cards, modales, tabs, tablas y formularios que estén duplicadas.

#### Scenario: Carga de componentes.css
- **DADO** `base.html`
- **CUANDO** se carga cualquier página
- **ENTONCES** `componentes.css` SHALL cargarse automáticamente después de `variables.css`
- **Y** antes de cualquier CSS modular

### Requirement: Botones unificados con 3 variantes
El sistema SHALL tener 3 variantes de botón: `.btn` (base, compartido), `.btn-primary` (naranja con gradiente sutil), `.btn-secondary` (borde con fondo transparente/hover), `.btn-outline` (solo borde). Todos los botones SHALL usar `var(--radius-md)` y `var(--space-3)` vertical padding.

#### Scenario: Botón primario
- **DADO** un `.btn-primary`
- **CUANDO** se renderiza
- **ENTONCES** SHALL tener `background: linear-gradient(135deg, var(--primary-500), var(--primary-600))`
- **Y** `color: white`
- **Y** al hover SHALL tener `transform: translateY(-1px)` con `box-shadow` incrementado

#### Scenario: Botón secundario
- **DADO** un `.btn-secondary`
- **CUANDO** se renderiza
- **ENTONCES** SHALL tener `background: var(--bg-secondary)`, `border: 1px solid var(--border-color)`
- **Y** al hover SHALL cambiar a `background: var(--bg-card)` y `border-color: var(--primary-500)`

### Requirement: Cards unificadas con 3 variantes
El sistema SHALL tener `.card` (base), `.card-elevated` (con shadow-md), `.card-glass` (con backdrop-filter blur para dark mode).

#### Scenario: Card base
- **DADO** un `.card`
- **CUANDO** se renderiza
- **ENTONCES** SHALL tener `border-radius: var(--radius-xl)`, `background: var(--bg-card)`, `border: 1px solid var(--border-color)`, `padding: var(--space-6)`

#### Scenario: Card glass (dark mode)
- **DADO** un `.card-glass` en dark mode
- **CUANDO** se renderiza
- **ENTONCES** SHALL tener `background: rgba(15, 23, 42, 0.6)` y `backdrop-filter: blur(12px)`

### Requirement: Modales unificados
El sistema SHALL tener patrón único: `.modal` (overlay fixed), `.modal-content` (card centrada), `.modal-actions` (flex-end). Todos los modales SHALL usar `--overlay-bg`, no valores hardcodeados.

#### Scenario: Modal unificado
- **DADO** un `.modal`
- **CUANDO** se renderiza
- **ENTONCES** SHALL usar `position: fixed; inset: 0; background: var(--overlay-bg)`
- **Y** `.modal-content` SHALL tener `width: min(520px, 100%)`, `border-radius: var(--radius-2xl)`

### Requirement: Tabs unificados con estilo pill
El sistema SHALL tener `.tabs-nav` con `.tab-button` en estilo pill (border-radius: var(--radius-full)), `.tab-button.active` con fondo primary. Todos los módulos SHALL usar este mismo patrón.

#### Scenario: Tab pill active
- **DADO** un `.tab-button.active`
- **CUANDO** se renderiza
- **ENTONCES** SHALL tener `background: var(--btn-primary)`, `color: white`, `border-color: transparent`

### Requirement: Tablas con patrón responsive unificado
El sistema SHALL tener un único patrón de tabla en `componentes.css` para la conversión a cards en viewport ≤640px, eliminando las 4 copias existentes en panel.css, caja.css, inventario.css y estilos.css.

#### Scenario: Tabla responsive unificada
- **DADO** una tabla en viewport ≤640px
- **CUANDO** tiene `<td data-label="...">`
- **ENTONCES** SHALL convertirse a cards con el patrón de `componentes.css`
- **Y** los módulos NO SHALL tener su propia regla `table { display: block }` duplicada

### Requirement: Formularios unificados
El sistema SHALL tener `.form-group`, `.form-label`, `.form-input`, `.form-select`, `.form-textarea` como componentes compartidos en `componentes.css`.

#### Scenario: Input unificado
- **DADO** un `.form-input`
- **CUANDO** se renderiza
- **ENTONCES** SHALL tener `padding: var(--space-3) var(--space-4)`, `border-radius: var(--radius-md)`, `border: 1px solid var(--border-color)`, `font-size: 16px`
- **Y** al focus SHALL tener `border-color: var(--primary-500)` con `box-shadow: 0 0 0 3px var(--primary-100)`

### Requirement: Badges unificados
El sistema SHALL tener `.badge` (base) con variantes `.badge-success`, `.badge-warning`, `.badge-danger`, `.badge-info`.

#### Scenario: Badge success
- **DADO** un `.badge-success`
- **CUANDO** se renderiza
- **ENTONCES** SHALL tener `background: rgba(22, 163, 74, 0.12)`, `color: var(--success-600)`, `border-radius: var(--radius-full)`
