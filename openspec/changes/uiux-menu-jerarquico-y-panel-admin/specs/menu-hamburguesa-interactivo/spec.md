## Purpose

Define la interacción completa del menú hamburguesa jerárquico por rol: apertura manual, flechas, indización, estado activo, transiciones y navegación por ítem.

## ADDED Requirements

### Requirement: Apertura manual del menú
El drawer NO SHALL abrirse automáticamente al navegar o al montar; solo SHALL abrirse/cerrarse mediante el botón hamburguesa (o cierre: fondo oscuro/interacción de ítem).

#### Scenario: Abrir manualmente
- **WHEN** el usuario pulsa el botón ☰
- **THEN** el drawer se abre; no se reabre solo en navegaciones posteriores

### Requirement: Jerarquía visual con flecha e indización
- **WHEN** una categoría está cerrada → flecha `▸`; abierta → `▾` (rotación animada 90°)
- **THEN** los sub-ítems se muestran con indentación creciente (12px/nivel) y transición escalonada (~30ms)
- **AND** solo se muestran sub-ítems de categorías abiertas

### Requirement: Estado activo con indicador vertical
Le ítem de la ruta actual SHALL mostrarse con fondo teñido de primario, texto primario y barra vertical izquierda de 3px.

### Requirement: Métricas como chips en ítems de menú
Los ítems con métrica SHALL mostrar un chip compacto a la derecha (formato `es-PE`), coloreado por estado y jamás bloqueando la navegación si el fetch falla.

#### Scenario: Caja con datos vivos
- **WHEN** la caja está abierta y el usuario abre el menú
- **THEN** "Control de Caja" muestra `S/. <ventas día>` y el panel muestra el monto contable correspondiente