## Context

La vista `pagos_personal.html` muestra una tabla a la vez (empleados o historial) dentro de la sección `.tables`. El CSS compartido en `panel.css` define `.tables` con `grid-template-columns: 1.5fr 1fr` en pantallas >=900px, diseñado para mostrar dos tarjetas lado a lado. Como `pagos_personal.html` solo muestra una tarjeta (la otra está oculta con `display: none`), la tarjeta visible queda alojada en la primera columna del grid, descentrada. Además, los botones `.view-toggle` están alineados a la izquierda.

## Goals / Non-Goals

**Goals:**
- La tabla de empleados e historial deben aparecer centradas horizontalmente con igual distancia a izquierda y derecha
- Los botones de alternar vista ("Empleados" / "Historial") deben estar centrados
- No afectar la vista `pagos_personal_detalle.html` que sí usa correctamente el grid de dos columnas

**Non-Goals:**
- No modificar rutas, lógica de negocio, ni JS
- No cambiar el comportamiento de mostrar/ocultar tablas

## Decisions

1. **Usar clase modificadora `tables--single` en lugar de alterar el grid global**: La regla existente `grid-template-columns: 1.5fr 1fr` en el media query >=900px es correcta para `pagos_personal_detalle.html` que muestra dos tablas simultáneas. Usar una clase BEM modifier (`tables--single`) permite override específico sin romper otras vistas.
2. **Centrar `.view-toggle` con `justify-content: center`**: Simplemente se agrega esta propiedad al flex container existente, no afecta otros usos de `.view-toggle` porque solo existe en `pagos_personal.html`.

## Riesgos / Trade-offs

- **Riesgo**: Si en el futuro se agregan más vistas que usen `.tables` con una sola tabla, habrá que aplicar la misma clase manualmente. → Mitigación: Es un patrón explícito y fácil de replicar.
- **Trade-off**: Se modifica `panel.css` compartido, pero los cambios son mínimos y específicos (una clase `tables--single` y una propiedad en `.view-toggle`).
