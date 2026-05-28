## Context

El módulo de Pagos al Personal tiene tres elementos clave que muestran datos agregados:
1. **Cards de estadísticas** (Total Pagado, Total Adelantos, Neto, Empleados Activos, Próximo Pago)
2. **Tabla de empleados** (resumen por empleado con pagado/adelantos/neto)
3. **Tabla de historial** (pagos registrados)

Actualmente, al registrar un pago o adelanto, el servidor procesa y redirige con `redirect(url_for('pagos_personal'))`, causando una recarga completa. No hay forma de actualizar solo una parte de la página.

## Goals / Non-Goals

**Goals:**
- Registrar pagos y adelantos sin recargar la página (fetch + JSON)
- Actualizar las 3 cards principales (Total Pagado, Total Adelantos, Neto) con los nuevos valores
- Actualizar la tabla de empleados si está visible
- Actualizar la tabla de historial si está visible
- Mantener compatibilidad con navegadores sin JS (POST tradicional como fallback)
- No perder ninguna validación existente

**Non-Goals:**
- No cambiar la UI del overlay de registro (solo el mecanismo de envío)
- No afectar otras páginas del sistema
- No agregar librerías externas (usar fetch nativo)

## Decisions

```
┌──────────────────────────────────────────────────────────────┐
│                    FLUJO ACTUAL                              │
│                                                              │
│  Form POST ──→ Servidor procesa ──→ redirect ──→ Recarga    │
│                                                              │
│                    FLUJO NUEVO                                │
│                                                              │
│  Form fetch ──→ Servidor procesa                              │
│                     │                                         │
│                     ├─ ¿AJAX? ──Sí──→ JSON {stats, empleados,│
│                     │                    historial, msg}       │
│                     │                     │                   │
│                     │              JS actualiza el DOM        │
│                     │                                         │
│                     └─ No ──→ redirect tradicional            │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## Decisions

1. **Detección AJAX por header**: Usar `request.headers.get('X-Requested-With') == 'XMLHttpRequest'` para diferenciar peticiones fetch de POST tradicionales. Es el estándar y no requiere cambios en el frontend más allá del header.

2. **Respuesta JSON con datos completos**: El JSON devuelve `{ success, message, stats: {...}, empleados: [...], historial: [...] }`. Así el frontend solo tiene que mapear los datos al DOM, sin hacer peticiones adicionales.

3. **IDs en elementos del DOM**: Se agregan IDs a los `<h2>` de cada card de estadística y a los `<tbody>` de las tablas para facilitar la actualización con JS:
   - `#totalPagadoValue`, `#totalAdelantosValue`, `#netoMesValue`
   - `#empleadosTableBody`, `#historialTableBody`

4. **Recálculo en servidor**: Se crea una función `_get_resumen_pagos_data(inicio, fin)` que ejecuta las mismas consultas que `pagos_personal()`, para que el JSON tenga datos frescos inmediatamente después del registro.

5. **Mantener POST tradicional como fallback**: Si el fetch falla o JS está deshabilitado, el formulario sigue funcionando con POST normal gracias al atributo `method="post"` y `action`.

## Riesgos / Trade-offs

- **Riesgo**: La respuesta JSON puede ser grande si hay muchos empleados. → Mitigación: El sistema es de gestión interna, no tendrá cientos de empleados. La respuesta completa es aceptable.
- **Riesgo**: Error de red durante el fetch → Mitigación: El formulario conserva su comportamiento POST tradicional como fallback mediante `catch` en la promesa.
- **Trade-off**: Se modifica el template y el backend simultáneamente. → Mitigación: Cambios localizados y con fallback, cualquier error no rompe el flujo existente.
