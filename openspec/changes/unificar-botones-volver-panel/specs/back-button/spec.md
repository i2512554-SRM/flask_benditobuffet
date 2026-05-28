## ADDED Requirements

### Requirement: Botón de retroceso unificado (btn-back)
The system SHALL provide a reusable `.btn-back` component for navigating from submodules back to the main panel or parent page.

#### Scenario: Back button renders as icon button
- **WHEN** a `.btn-back` element is rendered without text content
- **THEN** it SHALL display as a fixed-size 42×42px square with a centered `fa-arrow-left` icon

#### Scenario: Back button with text renders as inline icon + text
- **WHEN** a `.btn-back` element contains text (e.g., "Volver al inicio")
- **THEN** it SHALL display the icon followed by the text, with consistent padding matching other `.btn-back` buttons

#### Scenario: Back button navigates on click
- **WHEN** user clicks a `.btn-back` element
- **THEN** the browser SHALL navigate to the URL specified in the `href` attribute (or `location.href` for button elements)

#### Scenario: Hover state
- **WHEN** user hovers over a `.btn-back` element
- **THEN** the button SHALL shift 3px to the left (`translateX(-3px)`) and change background to the module's primary color with white icon/text

#### Scenario: Dark mode consistency
- **WHEN** the page is in dark mode
- **THEN** the `.btn-back` button SHALL use the dark mode CSS variables for background, border, and text colors, maintaining the same size and shape

#### Scenario: Responsive behavior
- **WHEN** the viewport is 640px or narrower
- **THEN** the `.btn-back` button SHALL maintain its 42×42px size and not become full-width or distorted

#### Scenario: Position in header
- **WHEN** a `.btn-back` is placed inside a module header
- **THEN** it SHALL be positioned before the `<h1>` as a standalone element (not inside the `<h1>`), with a consistent bottom margin

#### Scenario: Accessibility
- **WHEN** a `.btn-back` contains only an icon
- **THEN** it SHALL have an `aria-label` or `title` attribute describing the destination (e.g., "Volver al panel")

### Requirement: Coexistencia con módulos existentes
The `.btn-back` component SHALL integrate with each module's existing CSS variables for theming without duplicating size/layout rules.

#### Scenario: Module-specific hover color
- **WHEN** a module defines a custom hover color (e.g., inventario defines `--inventario-primary`)
- **THEN** the `.btn-back:hover` in that module SHALL use that module's primary color as background

#### Scenario: No card displacement
- **WHEN** the `.btn-back` is added or replaced in a template
- **THEN** the layout of cards and content below the header SHALL remain unchanged (no shifts, gaps, or overlaps compared to the current layout)
