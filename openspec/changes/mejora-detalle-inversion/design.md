## Context

La vista `inventario_compra_detalle.html` actualmente muestra la información en un `.detalle-card` que ocupa el ancho completo sin centrar. Los estilos existentes en `inventario.css` son funcionales pero básicos. El resto del sistema usa tarjetas centradas con sombras suaves, padding generoso y bordes redondeados (20px) que esta vista no aprovecha completamente.

## Goals / Non-Goals

**Goals:**
- Centrar el `.detalle-card` horizontalmente con un max-width definido
- Mejorar la jerarquía visual: ID como badge/título, metadatos en grid, descripción con separación clara
- Reutilizar tokens CSS existentes (variables `--inventario-*`)
- Mantener 100% compatible con el responsive actual (breakpoints 980px, 700px, 400px)
- Solo modificar `inventario_compra_detalle.html` y `inventario.css`

**Non-Goals:**
- No cambiar rutas, lógica de negocio, modelos, ni otros templates
- No agregar nuevas dependencias externas
- No modificar el comportamiento del botón "Volver" o "Cerrar Sesión"

## Decisions

1. **Max-width en la card**: Se aplica `max-width: 800px; margin: 0 auto;` al `.detalle-card` para centrarlo. 800px es un ancho de lectura cómodo para una vista de detalle.
2. **Display grid para metadatos**: Los campos monto, proveedor y fecha se muestran en un grid de 3 columnas con igual peso (`1fr 1fr 1fr`) para desktop, apilándose en mobile vía media query. Cada campo usa el patrón label encima + valor, similar a tarjetas de estadísticas del sistema.
3. **Badge para el ID**: El número de inversión se muestra como un badge estilizado (`#123`) en lugar de texto plano de encabezado.
4. **Separador visual**: Un `hr` sutil entre los metadatos y la descripción/notas para diferenciar secciones.
5. **Sin nuevos archivos**: Todo el CSS adicional se agrega al bloque existente de "SECCIÓN DE DETALLE" en `inventario.css`.

## Riesgos / Trade-offs

- **Riesgo**: El max-width de 800px puede verse pequeño en pantallas ultra-wide. → Mitigación: El proyecto usa `max-width: 1500px` en `.main-container`, 800px es intencional para legibilidad de detalle, y el contenido se centra con margen automático.
- **Riesgo**: Si en el futuro se agregan más campos a la inversión, el grid de 3 columnas puede desbalancearse. → Mitigación: El grid usa `1fr` iguales, no tamaños fijos, por lo que se adapta naturalmente.
- **Trade-off**: Se modifica `inventario.css` que es compartido con otras vistas del módulo inventario. → Mitigación: Solo se modifican clases específicas de detalle (`.detalle-card`, `.detalle-grid`, `.detalle-meta`), sin tocar clases compartidas.
