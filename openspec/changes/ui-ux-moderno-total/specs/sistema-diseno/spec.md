## ADDED Requirements

### Requirement: Paleta de color unificada con 4 escalas
El sistema SHALL usar una paleta de 4 escalas cromáticas definidas en `variables.css`: primary (naranja), secondary (verde petróleo), neutral (gris oscuro a claro), semantic (verde éxito, rojo error, amarillo warning). Cada escala SHALL tener 5-7 variantes de intensidad.

#### Scenario: Esquema de colores primarios
- **DADO** la paleta de colores
- **CUANDO** se inspecciona `--primary-500`
- **ENTONCES** SHALL ser `#ff6b00` (naranja primario)
- **Y** `--primary-600` SHALL ser `#e06000`
- **Y** `--primary-100` SHALL ser `#fff0e6` (fondo suave)

#### Scenario: Esquema de colores secundarios
- **DADO** la paleta de colores
- **CUANDO** se inspecciona `--secondary-500`
- **ENTONCES** SHALL ser `#0a2e2f` (verde petróleo)
- **Y** `--secondary-100` SHALL ser `#e6f0f0`

#### Scenario: Escala neutral
- **DADO** la paleta de colores
- **CUANDO** se inspecciona `--neutral-50`
- **ENTONCES** SHALL ser `#f8f9fa`
- **Y** `--neutral-900` SHALL ser `#0f172a`

### Requirement: Sistema de spacing basado en 4px
El sistema SHALL usar una escala de espaciado basada en múltiplos de 4px: `--space-1: 4px`, `--space-2: 8px`, `--space-3: 12px`, `--space-4: 16px`, `--space-5: 20px`, `--space-6: 24px`, `--space-8: 32px`, `--space-10: 40px`, `--space-12: 48px`, `--space-16: 64px`.

#### Scenario: Uso de spacing tokens
- **CUANDO** un componente necesita padding
- **ENTONCES** SHALL usar `var(--space-4)` en lugar de `16px`
- **Y** SHALL evitar valores hardcodeados

### Requirement: Tipografía unificada con solo Inter
El sistema SHALL usar únicamente la fuente `Inter` de Google Fonts. Se SHALL eliminar Lexend de `login.css`, `panel.css`, `empleados.css`.

#### Scenario: Body text
- **DADO** la tipografía del sistema
- **CUANDO** se inspecciona `body`
- **ENTONCES** `font-family` SHALL ser `'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`
- **Y** `font-size` SHALL ser `16px` en desktop

#### Scenario: Jerarquía tipográfica
- **DADO** la jerarquía tipográfica
- **CUANDO** se usa `--text-xs` (12px), `--text-sm` (14px), `--text-base` (16px), `--text-lg` (18px), `--text-xl` (20px), `--text-2xl` (24px), `--text-3xl` (30px), `--text-4xl` (36px)
- **ENTONCES** SHALL estar definidos como variables en `:root`

### Requirement: Elevation con 3 niveles
El sistema SHALL tener 3 niveles de sombra: `--shadow-sm` (baja, para cards), `--shadow-md` (media, para modales), `--shadow-lg` (alta, para dropdowns/toasts). Cada una SHALL tener variante dark.

#### Scenario: Shadow tokens
- **DADO** los tokens de elevation
- **CUANDO** se usa `--shadow-sm`
- **ENTONCES** SHALL ser `0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04)` en modo claro
- **Y** en dark mode SHALL ser más intensa

### Requirement: Border-radius unificado
El sistema SHALL usar tokens de border-radius: `--radius-sm: 6px`, `--radius-md: 10px`, `--radius-lg: 14px`, `--radius-xl: 18px`, `--radius-2xl: 24px`, `--radius-full: 9999px`.

#### Scenario: Uso de radius tokens
- **CUANDO** un input, botón o card necesita border-radius
- **ENTONCES** SHALL usar los tokens de radius (ej: `border-radius: var(--radius-md)`)
- **Y** NO SHALL tener valores hardcodeados
