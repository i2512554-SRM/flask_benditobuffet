## Purpose

Define el rediseño del Panel del Administrador: notificaciones como tarjetas con prioridad/tipo/fecha y actividad reciente operacional (no logins).

## ADDED Requirements

### Requirement: Notificaciones enriquecidas
El bloque de alertas del panel Admin SHALL renderizar tarjetas pequeñas con icono (por tipo/sector), pill de prioridad (Alta/Media/Baja con colores) y fecha legible.

#### Scenario: Sección produce alerta
- **WHEN** el panel carga `/admin/alertas-resumen`
- **THEN** cada alerta se muestra con icono, prioridad calculada y fecha (o fallback heurístico por sección → Alerta de estrella/stock)

### Requirement: Actividad reciente operacional
`GET /api/admin/actividad-reciente?limit=N` SHALL agregar eventos de negocios reales (pagos, cierres de caja, solicitudes, inversiones) ordenados desc por fecha, excluyendo actividad de logins.

#### Scenario: Panel consulta feed de negocio
- **WHEN** el admin abre su panel
- **THEN** la columna "Actividad Reciente" muestra ítems `{ tipo, titulo, descripcion, fecha }` de la operación real de los últimos días (p.ej. "Cierre de caja S/. 1,250.00 — 02/09", "Nueva solicitud de adelanto — Marisol C.").