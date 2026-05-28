## Context

La auditoría responsive reveló que el proyecto tiene ~65% de soporte mobile. Las áreas críticas son:

| Módulo | Puntaje | Problema principal |
|--------|---------|-------------------|
| Caja | Bueno | Gap 640-760px en min-width de tabla |
| Inventario | Moderado | Sin card-conversion, stats apretadas |
| Perfil | Moderado | Sin card-conversion, min-width 520px |
| Empleados | **Malo** | Sin card-conversion, sin overflow wrapper, 7 columnas |
| Pagos | Bueno | Ya tiene data-label y card-conversion |
| Login | Adecuado | Sin touch-target mínimo |

## Goals / Non-Goals

**Goals:**
- Toda tabla → cards en viewport ≤640px con `data-label`
- Cerrar todos los gaps de `min-width` que causan overflow
- Breakpoint xs ≤380px con padding/font-size reducidos
- Touch targets mínimos de 44px en mobile
- Overflow wrapper en tabla de empleados
- Stats grid responsive en 1-2 columnas según viewport

**Non-Goals:**
- No se rediseña el layout desktop
- No se cambia la estructura de datos ni backend
- No se agregan librerías externas
- No se tocan los modales ni overlays (ya responsive)
- No se cambia el sistema de temas (dark mode)

## Decisions

### 1. CSS de card-conversion unificado en estilos.css

**Decisión:** Las reglas de conversión tabla→cards se centralizan en `estilos.css` con un selector genérico que aplica a cualquier `td[data-label]`. Esto evita duplicar el mismo CSS en cada módulo.

**Estructura propuesta (en estilos.css, dentro de @media ≤640px):**
```css
/* Card conversion universal para cualquier tabla con data-label */
table td[data-label]::before {
    content: attr(data-label);
    font-weight: 600;
    display: block;
    margin-bottom: 4px;
    color: var(--text-muted);
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
@media (max-width: 640px) {
    thead { display: none; }
    tr {
        display: flex;
        flex-direction: column;
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        background: var(--bg-card);
    }
    td {
        display: flex;
        flex-direction: column;
        border: none;
        padding: 6px 0;
    }
}
```

### 2. data-label en lugar de data-personalizados

**Decisión:** Usar `data-label="Nombre de columna"` estándar en todas las tablas (reemplazando `data-nombre`, `data-categoria`, `data-fecha` en inventario). Esto permite que el CSS unificado funcione sin excepciones.

**Alternativa considerada:** Mantener `data-nombre` etc. y mapearlos en cada CSS de módulo. Se descarta porque añade complejidad innecesaria.

### 3. Eliminar min-width en lugar de cambiarlos

**Decisión:** Simplemente eliminar las propiedades `min-width` problemáticas. El layout natural con `overflow-x: auto` en el wrapper ya maneja el scroll horizontal cuando la tabla es más ancha que el viewport.

**Alternativa considerada:** Cambiar a `min-width: 100%` o valores relativos. No es necesario — la tabla ocupa el 100% del wrapper por defecto.

### 4. Breakpoint xs a 380px (no 375 ni 360)

**Decisión:** Usar `380px` como breakpoint para pantallas muy pequeñas. Cubre iPhone SE (375px) y Galaxy S24 (360px) sin fragmentar en múltiples breakpoints.

### 5. Touch targets con padding adicional

**Decisión:** En viewport ≤640px, añadir `padding-block: 12px` a todos los botones (o `min-height: 44px`). Esto es menos invasivo que cambiar todas las alturas fijas.

## Riesgos / Trade-offs

| Riesgo | Mitigación |
|--------|-----------|
| El CSS unificado de card-conversion podría romper tablas sin `data-label` | El selector `td[data-label]` garantiza que solo afecta a celdas con el atributo |
| Eliminar min-widths podría hacer que tablas se vean comprimidas en viewports intermedios | Ya existe overflow-x: auto en los wrappers; el scroll está disponible si es necesario |
| Touch targets de 44px podrían hacer botones muy grandes en ciertos contextos (tabla de empleados) | Se aplica solo en ≤640px, y botones de acción ya tienen padding pequeño ajustable |
| El breakpoint 380px añade un octavo breakpoint al proyecto | Es necesario para cubrir dispositivos reales; se consolida en `estilos.css` en lugar de esparcirlo |
