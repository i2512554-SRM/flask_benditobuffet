## Purpose

Define el apartado "Rendimiento financiero" con un gráfico de líneas actualizable por periodo (Día/Semana/Mes/Año), alimentado por los movimientos y cierres existentes en la base de datos, con indicadores de Ingresos, Egresos y Ganancia seleccionables.

## ADDED Requirements

### Requirement: Apartado de rendimiento financiero
El Administrador y la Cajera SHALL disponer de un apartado "Rendimiento financiero" con un gráfico de líneas que represente la evolución de los datos. La data SHALL provenir de las transacciones y cierres existentes en la base de datos, sin crear un historial duplicado.

#### Scenario: Gráfico en el panel del administrador
- **WHEN** un Administrador consulta su panel
- **THEN** ve el apartado "Rendimiento financiero" con información financiera general

#### Scenario: Gráfico en el panel de la cajera
- **WHEN** una Cajera consulta su panel
- **THEN** ve el apartado "Rendimiento financiero" con información de su gestión de caja y los movimientos que puede consultar

### Requirement: Filtros por periodo
El gráfico SHALL ofrecer los filtros Día, Semana, Mes y Año; al seleccionar uno, el gráfico SHALL actualizarse con la agregación del periodo correspondiente y las etiquetas del eje de escala apropiadas.

#### Scenario: Cambio de filtro de periodo
- **WHEN** el usuario selecciona el filtro "Mes" en el apartado de rendimiento
- **THEN** el gráfico se recalcula y muestra la evolución mensual del periodo correspondiente

#### Scenario: Selección por omisión
- **WHEN** el usuario abre el panel por primera vez
- **THEN** el apartado de rendimiento muestra el periodo por omisión (Semana) por defecto y el gráfico carga sus datos automáticamente

### Requirement: Selección de indicadores
El apartado de rendimiento SHALL permitir seleccionar opcionalmente los indicadores Ingresos, Egresos y Ganancia para mostrarlos u ocultarlos en el gráfico de forma independiente.

#### Scenario: Oculta un indicador
- **WHEN** el usuario desmarca el indicador "Egresos"
- **THEN** la línea de egresos desaparece del gráfico y las líneas restantes permanecen en escala

#### Scenario: Restaura el indicador
- **WHEN** el usuario vuelve a marcar el indicador "Egresos"
- **THEN** la línea de egresos reaparece en el gráfico

### Requirement: Datos de agregación existentes
El backend SHALL exponer un endpoint que agregue por periodo los movimientos (Venta/Gasto) y/o cierres existentes, devolviendo los puntos de Ingresos, Egresos y Ganancia por cada punto del periodo, sin persistir datos nuevos para el gráfico.

#### Scenario: Respuesta del endpoint de rendimiento
- **WHEN** el frontend solicita los datos de rendimiento para un periodo válido
- **THEN** el endpoint responde exitosamente con los puntos del periodo y sus valores de ingresos, egresos y ganancia