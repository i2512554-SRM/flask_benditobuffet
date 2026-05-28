## Context

`pagos_personal_detalle.html` tiene un header con dos áreas: la izquierda contiene un botón "Volver" + título, y la derecha contiene "Cerrar Sesión" + botón de tema. El botón "Cerrar Sesión" es redundante, y tener "Volver" en la izquierda mezclado con el título compite visualmente con la jerarquía del encabezado.

## Goals / Non-Goals

**Goals:**
- Mover el botón "Volver" a la esquina superior derecha (`header-buttons`)
- Eliminar "Cerrar Sesión" del `header-buttons`
- Mantener el botón de alternar modo noche

**Non-Goals:**
- No modificar estilos CSS, rutas, ni lógica de negocio
- No afectar otros templates

## Decisions

1. **Mover el `<a>` de Volver tal cual**: Se traslada el mismo elemento con clase `btn-outline`, icono y texto "Volver" desde el `<div>` izquierdo al `header-buttons`, reemplazando el `<a>` de logout.
2. **Eliminar el div vacío**: Al quitar el botón "Volver" de la izquierda, el `<div>` del header izquierdo queda solo con el título y subtítulo, más limpio.

## Riesgos / Trade-offs

- **Riesgo mínimo**: Solo se mueve un elemento HTML y se elimina otro. No hay cambios de lógica ni estilos.
