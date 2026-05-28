## ADDED Requirements

### Requirement: Micro-interacciones en todos los elementos interactivos
Todo elemento interactivo (botón, enlace, input, tab, toggle) SHALL tener una transición suave de 200ms en propiedades como `background`, `color`, `border-color`, `box-shadow`, `transform`. Los botones SHALL elevarse 1px en hover con shadow incrementado.

#### Scenario: Botón hover
- **DADO** un `.btn` o `.btn-primary`
- **CUANDO** el usuario hace hover
- **ENTONCES** `transform: translateY(-1px)` Y `box-shadow: var(--shadow-md)` SHALL aplicarse
- **Y** la transición SHALL durar 200ms

#### Scenario: Focus visible
- **DADO** un input o botón
- **CUANDO** recibe foco por teclado (Tab)
- **ENTONCES** SHALL tener `outline: 2px solid var(--primary-500)` con `outline-offset: 2px`
- **Y** SHALL usar `:focus-visible` no `:focus` para evitar outline en clicks

### Requirement: Glassmorphism en headers y cards principales
Los headers de módulo SHALL tener efecto glass en modo oscuro: fondo semitransparente con blur. Las cards principales (`.card-elevated`) SHALL tener glass en dark mode.

#### Scenario: Header glass en dark mode
- **DADO** un `<header>` o `.caja-header` en dark mode
- **CUANDO** se renderiza
- **ENTONCES** SHALL tener `background: rgba(15, 23, 42, 0.7)` y `backdrop-filter: blur(16px)`
- **Y** `border-bottom: 1px solid var(--border-color)`

### Requirement: Tipografía fluida con clamp()
Los títulos principales SHALL usar `clamp()` para escalar fluidamente entre viewports. `h1` SHALL ser `clamp(1.5rem, 2.5vw, 2.5rem)`, `h2` SHALL ser `clamp(1.2rem, 2vw, 1.8rem)`.

#### Scenario: Título fluido
- **DADO** un `<h1>` en la página
- **CUANDO** se cambia el viewport de 320px a 1920px
- **ENTONCES** el font-size SHALL escalar fluidamente entre 1.5rem y 2.5rem

### Requirement: Sombras con gradiente sutil
Las cards principales SHALL tener un borde con gradiente sutil en la parte superior (efecto de luz ambiental) en modo claro.

#### Scenario: Card glow
- **DADO** una `.card-elevated`
- **CUANDO** se renderiza en modo claro
- **ENTONCES** SHALL tener `box-shadow: 0 1px 0 var(--primary-100) inset, var(--shadow-md)`

### Requirement: Estados vacíos con diseño atractivo
Las tablas sin datos o estados vacíos SHALL tener un diseño visualmente atractivo: icono grande + mensaje + opcional CTA, no solo texto gris.

#### Scenario: Empty state
- **DADO** una tabla sin datos
- **CUANDO** se muestra el mensaje "No hay artículos registrados"
- **ENTONCES** SHALL estar dentro de un `td[colspan] > .empty-state` con icono decorativo y padding generoso

### Requirement: Scrollbar custom global
El scrollbar SHALL ser custom en toda la aplicación, definido en `variables.css` o `componentes.css`, NO duplicado en cada módulo.

#### Scenario: Scrollbar unificado
- **DADO** la aplicación
- **CUANDO** hay contenido con scroll
- **ENTONCES** el scrollbar SHALL usar `var(--scrollbar-track)` y `var(--scrollbar-thumb)`
- **Y** SHALL tener `border-radius: var(--radius-full)` con `width: 8px`

### Requirement: Dark mode sin valores hardcodeados
NINGÚN archivo CSS SHALL contener valores de color hardcodeados. TODOS los colores SHALL obtenerse de `var(--*)` tokens definidos en `variables.css`.

#### Scenario: Overlay dark mode
- **DADO** un `.modal` o `.overlay`
- **CUANDO** se renderiza en dark mode
- **ENTONCES** SU background SHALL usar `var(--overlay-bg)` (NO `rgba(0,0,0,0.55)` hardcodeado)
