## Context

La vista `inventario_compra_detalle.html` tiene dos botones en el header: "Volver al Inventario" (clase `btn-secondary`, color blanco) y "Cerrar Sesión" (clase `btn-outline`). El color blanco no coincide con la paleta del sistema (naranja `#ff7b00`). El botón de cerrar sesión es redundante porque el sistema ya provee esa funcionalidad en el header principal.

## Goals / Non-Goals

**Goals:**
- Cambiar el botón "Volver al Inventario" a color naranja consistente con `btn-primary`
- Eliminar el botón "Cerrar Sesión"
- Mantener la misma estructura y layout del header

**Non-Goals:**
- No modificar estilos CSS globales ni de otros templates
- No cambiar rutas ni lógica de negocio
- No alterar otros botones del sistema

## Decisions

1. **Usar `btn-primary` en lugar de modificar `btn-secondary`**: La clase `btn-primary` ya existe con el gradiente naranja (`--btn-gradient-start` → `--btn-gradient-end`) y es la forma más directa de aplicar el color del sistema sin crear CSS nuevo ni afectar otros usos de `btn-secondary` en el módulo inventario.
2. **Eliminar el botón "Cerrar Sesión"**: Se remueve el `<a>` completo del template, manteniendo el `header-actions` con un solo botón.

## Riesgos / Trade-offs

- **Riesgo**: `btn-primary` está diseñado para acciones principales (guardar, crear), no para navegación secundaria. → Mitigación: El color naranja es deseado explícitamente por el usuario y `btn-primary` es la única clase naranja preexistente. El gradiente se ve apropiado como botón de acción.
- **Trade-off**: Si en el futuro se quiere estandarizar botones de "volver" en naranja, convendría crear una clase compartida. Por ahora un cambio mínimo es preferible.
