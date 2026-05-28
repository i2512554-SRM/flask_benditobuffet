## Context

Auditoría completa del sistema reveló:

| Métrica | Resultado |
|---------|-----------|
| Total tablas | 11 en 5 módulos |
| Tablas con card-conversion | 3 (caja ×2, pagos ×1) |
| Tablas sin data-label | 3 módulos (empleados, inventario, perfil) |
| Tablas sin overflow wrapper | 1 (empleados) |
| Inputs con iOS zoom risk | 2 módulos (empleados, caja) |
| Breakpoint más pequeño | 540px (login.css) — falta ≤380px |
| Touch targets ≥44px | Ninguno implementado |
| Profesional score | ~65/100 |

El módulo **caja** es la referencia de cómo debería funcionar todo. El módulo **empleados** es el más crítico.

## Goals / Non-Goals

**Goals:**
- 11/11 tablas con card-conversion y `data-label`
- 0 gaps de `min-width` que causen overflow
- 100% de inputs con `font-size ≥ 16px` (iOS fix)
- Touch targets ≥44px en mobile
- Breakpoint ≤380px funcional
- Stats grid adaptable

**Non-Goals:**
- No rediseño desktop
- No cambios de backend ni modelos
- No nuevas librerías
- No hamburger menu (alcance separado)
- No cambios en modales/overlays (ya responsive)

## Decisions

### 1. CSS de card-conversion UNIFICADO en estilos.css

**Decisión:** Una sola regla CSS en `estilos.css` dentro de `@media (max-width: 640px)` que convierta TODA tabla con `td[data-label]` a cards. Esto elimina la duplicación actual (caja.css tiene su propia versión, panel.css tiene otra).

```css
@media (max-width: 640px) {
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
    thead { display: none; }
    tbody tr {
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

Las reglas existentes en `caja.css` y `panel.css` se dejan intactas (no causan daño), pero el nuevo CSS unificado en `estilos.css` las complementa al cargarse primero.

**Alternativa:** Mantener la duplicación módulo por módulo. Se descarta porque es frágil (si se cambia el diseño de las cards, hay que cambiarlo en N lugares).

### 2. data-label como estándar único

**Decisión:** Todas las celdas `<td>` usan `data-label="Nombre Columna"`. En inventario, se reemplazan los atributos actuales `data-nombre`, `data-categoria`, `data-fecha`.

**Formato:** Mismo texto del `<th>` correspondiente, en español, con capitalización normal (e.g., `data-label="Precio Unitario"`).

### 3. Eliminar min-width, no modificarlos

**Decisión:** Eliminar las propiedades `min-width` problemáticas. El `overflow-x: auto` del wrapper maneja cualquier exceso. La tabla ocupa 100% del wrapper por defecto.

**Archivos y líneas:**
- `panel.css:267` — `.table-card { min-width: 840px }` → eliminar
- `panel.css:275` — `table { min-width: 720px }` → eliminar
- `caja.css:197` — `table { min-width: 760px }` → eliminar
- `inventario.css:220` — `table { min-width: 720px }` → eliminar
- `perfil.css:272` — `table { min-width: 520px }` → eliminar

### 4. iOS zoom: 16px fijo en inputs

**Decisión:** Cambiar `font-size: 14px` a `font-size: 16px` en las reglas de input/select/textarea de `empleados.css:88` y `caja.css:157`. iOS Safari no hace auto-zoom cuando el font-size es ≥16px.

### 5. Touch targets con min-height

**Decisión:** En `estilos.css` dentro de `@media (max-width: 640px)`, agregar `button, .btn-*, a.btn-* { min-height: 44px; }`. Esto aplica a todos los botones sin excepción.

Para los botones pequeños de acción en tabla de empleados (`.btn-edit`, `.btn-delete`, etc.), se agrega `padding-block: 12px` en el mismo breakpoint.

### 6. Breakpoint xs único a 380px

**Decisión:** Un solo breakpoint `@media (max-width: 380px)` en `estilos.css` que reduce padding de cards a 8px y escala títulos.

### 7. Stats grid 1 columna en ≤400px

**Decisión:** En `inventario.css`, agregar `@media (max-width: 400px)` con `grid-template-columns: 1fr`. Similar para perfil.

## Riesgos / Trade-offs

| Riesgo | Mitigación |
|--------|-----------|
| CSS unificado de card-conversion podría conflictuar con reglas existentes en caja.css/panel.css | Se prueba que las reglas existentes son compatibles; al estar en `estilos.css` (cargado primero), las reglas específicas de módulo tienen mayor prioridad y no se rompen |
| Eliminar min-width podría dejar tablas sin scroll en viewports intermedios | Se verifica que todos los wrappers tienen `overflow-x: auto`; empleados necesitará wrapper nuevo (está en tasks) |
| iOS zoom fix a 16px podría agrandar inputs en desktop | 16px es el estándar profesional y no afecta negativamente en desktop; de hecho mejora legibilidad |
| Touch targets de 44px podrían solaparse en la tabla de empleados (3 botones por fila) | Los botones se apilan verticalmente dentro de la card; 44px de altura es adecuado |
