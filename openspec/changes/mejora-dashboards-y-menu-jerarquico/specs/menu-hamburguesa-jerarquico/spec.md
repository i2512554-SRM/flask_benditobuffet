## Purpose

Define el comportamiento del menú hamburguesa jerárquico por rol, que agrupa las opciones de navegación en categorías desplegables con flecha, abriéndose y cerrándose manualmente.

## ADDED Requirements

### Requirement: Apertura y cierre manual del menú hamburguesa
El menú hamburguesa (☰) SHALL abrir y cerrar el panel de navegación manualmente; el estado del menú no SHALL cambiar automáticamente por navegación.

#### Scenario: Abrir el menú desde el botón hamburguesa
- **WHEN** el usuario autenticado pulsado el botón ☰ en la esquina superior izquierda
- **THEN** el panel de navegación se despliega y permanece abierto hasta que el usuario lo cierre

#### Scenario: Cerrar el menú
- **WHEN** el usuario pulsa el fondo oscuro, pulsa el botón de cierre, o selecciona una opción
- **THEN** el panel de navegación se cierra

### Requirement: Categorías desplegables con flecha
El menú SHALL organizar las opciones en categorías; cada categoría cerrada muestra "▸" antes del nombre y cada categoría abierta muestra "▾". Las subcategorías SHALL aparecer únicamente cuando su categoría esté abierta.

#### Scenario: Categoría cerrada oculta subcategorías
- **WHEN** una categoría (p. ej. "Personal") está cerrada
- **THEN** se muestra "▸ Personal" sin subcategorías visibles

#### Scenario: Abrir una categoría
- **WHEN** el usuario pulsa una categoría cerrada (p. ej. "Personal")
- **THEN** la flecha cambia a "▾" y se muestran sus subcategorías (p. ej. Empleados, Pagos, Turnos, Adelantos, Solicitudes)

### Requirement: Visibilidad según rol
El menú SHALL mostrar únicamente las categorías y funciones que el rol autenticado tenga permitidas; no SHALL mostrar opciones de otros roles.

#### Scenario: Menú de administrador
- **WHEN** un usuario con rol Administrador abre el menú
- **THEN** ve el Panel Principal y las categorías Caja, Personal, Inventario e Inversión, Seguridad e IA Predictiva con sus subcategorías administrativas

#### Scenario: Menú de cajera
- **WHEN** una usuaria con rol Cajera abre el menú
- **THEN** ve su panel y el Control de Caja, y NO ve categorías administrativas (Personal, Inventario, Seguridad, IA)

#### Scenario: Menú de cocinero
- **WHEN** un usuario con rol Cocinero abre el menú
- **THEN** ve su panel, Insumos, Productos, Stock, Solicitudes y sus funciones de trabajador (Mi Información, Mis Turnos, Mis Pagos, Notificaciones)

#### Scenario: Menú de trabajador
- **WHEN** un usuario con rol Trabajador abre el menú
- **THEN** ve únicamente su panel y sus secciones personales (Mi Información, Mis Turnos, Mis Pagos, Notificaciones)