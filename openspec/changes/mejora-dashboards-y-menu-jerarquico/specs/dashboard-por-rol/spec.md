## Purpose

Define la estructura y el contenido de los dashboards personalizados por rol, que presentan bienvenida con nombre y rol, fecha, resumen, acciones rápidas, notificaciones y actividad relevante según los permisos del usuario.

## ADDED Requirements

### Requirement: Dashboard de bienvenida por rol
Todo dashboard autenticado SHALL saludar al usuario con su nombre y mostrar su rol, la fecha actual y un título contextual de su panel. El destino inicial de cada rol SHALL ser su propio dashboard.

#### Scenario: Bienvenida de administrador
- **WHEN** un Administrador inicia sesión
- **THEN** es dirigido a su panel y ve "¡Hola, [Nombre]!", su rol y la fecha actual

#### Scenario: Bienvenida de cajera
- **WHEN** una Cajera inicia sesión
- **THEN** es dirigida a su Panel de Caja (no al Control de Caja) y ve "¡Hola, [Nombre]!" y "Bienvenida a tu panel de Caja"

#### Scenario: Bienvenida de cocinero
- **WHEN** un Cocinero inicia sesión
- **THEN** es dirigido a su panel de cocina y ve su bienvenida personalizada con nombre, rol y fecha

#### Scenario: Bienvenida de trabajador
- **WHEN** un Trabajador inicia sesión
- **THEN** es dirigido a su panel y ve su bienvenida personalizada con nombre, rol y fecha

### Requirement: Contenido de cada dashboard según rol
Cada dashboard SHALL presentar resumen, acciones rápidas, notificaciones y actividad relevante acorde a los permisos del rol, siguiendo el orden visual bienvenida → resumen → gráfico/información relevante → acciones rápidas → notificaciones y actividad; no se generarán zonas vacías grandes.

#### Scenario: Resumen del administrador
- **WHEN** un Administrador ve su panel
- **THEN** el panel muestra resumen financiero (ventas, egresos, ganancia neta), rendimiento financiero, notificaciones (solicitudes, stock bajo, agotados, pagos pendientes, alertas), acciones rápidas (Caja, Inventario, Personal, Registrar Pago, Revisar Solicitudes) y actividad reciente del sistema

#### Scenario: Resumen de la cajera
- **WHEN** una Cajera ve su panel
- **THEN** el panel muestra tarjetas de estado de caja, monto inicial, ingresos del día, egresos del día y saldo actual, además de acciones rápidas y movimientos recientes

#### Scenario: Resumen del cocinero
- **WHEN** un Cocinero ve su panel
- **THEN** el panel muestra resumen de inventario, productos con stock bajo, productos agotados, solicitudes pendientes, notificaciones y acciones rápidas de su área (Insumos, Productos, Stock, Solicitudes)

#### Scenario: Resumen del trabajador
- **WHEN** un Trabajador ve su panel
- **THEN** el panel muestra únicamente su próximo turno, su último pago, el estado de sus solicitudes, sus adelantos permitidos y sus notificaciones

### Requirement: Privacidad de la información del trabajador
El dashboard del trabajador SHALL mostrar solo información propia (turnos, pagos, adelantos y solicitudes del usuario autenticado), sin datos de otros trabajadores.

#### Scenario: Consulta de información propia
- **WHEN** un Trabajador autenticado consulta su panel
- **THEN** todas las secciones muestran datos filtrados a su usuario y no existen vínculos ni datos de otros trabajadores

### Requirement: Acciones rápidas de cajera en el panel
El Panel de Cajera SHALL ofrecer las acciones "Abrir Caja", "Registrar Ingreso", "Registrar Egreso" y "Control de Caja". Las tres primeras SHALL abrir el modal correspondiente dentro del panel sin navegar al Control de Caja; solo "Control de Caja" SHALL navegar a la pantalla completa del módulo.

#### Scenario: Abrir caja sin navegación
- **WHEN** la Cajera pulsa "Abrir Caja" en su panel
- **THEN** se abre el modal de apertura para ingresar el monto inicial y permanece en el panel

#### Scenario: Registrar ingreso sin navegación
- **WHEN** la Cajera pulsa "Registrar Ingreso" en su panel
- **THEN** se abre el modal de ingreso dentro del panel sin cambiar de vista

#### Scenario: Registrar egreso sin navegación
- **WHEN** la Cajera pulsa "Registrar Egreso" en su panel
- **THEN** se abre el modal de egreso dentro del panel sin cambiar de vista

#### Scenario: Ir al Control de Caja
- **WHEN** la Cajera pulsa "Control de Caja"
- **THEN** el sistema navega al módulo completo de Gestión de Caja

### Requirement: Actividad reciente del administrador
El panel de Administrador SHALL mostrar los últimos movimientos importantes del sistema (p. ej. ingreso registrado, egreso registrado, pago realizado, producto actualizado, solicitud creada) a partir de los registros existentes.

#### Scenario: Visualización de actividad reciente
- **WHEN** un Administrador ve su panel y existen movimientos registrados
- **THEN** el panel lista los últimos movimientos con tipo y fecha sin duplicar historiales