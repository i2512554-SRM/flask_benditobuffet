## Context

Actualmente existen **9 templates** con botones de "volver al panel", cada uno implementado con clases distintas:

| Template | Clase actual | Tamaño | Posición |
|----------|-------------|--------|----------|
| caja.html | `.btn-outline` + inline `font-size:16px` | Variable (padding 14px 20px) | Dentro de `<h1>` |
| inventario.html | `.btn-outline` + inline `font-size:16px` | Variable | Dentro de `<h1>` |
| perfil.html | `.back-profile` | **42×42 fijo** | Standalone, antes del `<h1>` |
| empleados.html | *(sin clase)* | Heredado | Dentro de `<h1>` |
| empleados_form.html | *(sin clase)* | Heredado | Dentro de `<h1>` |
| pagos_personal.html | `.btn-outline` (texto) | Variable | Standalone, antes del `<h1>` |
| pagos_personal_detalle.html | `.btn-outline` + inline `font-size:16px` | Variable | Dentro de `<h1>` |
| login.html | `.volver` | Inline, sin forma de botón | Standalone, antes del card |
| inventario_compra_detalle.html | `.btn-secondary` (texto) | Variable | En `header-actions` (derecha) |

El diseño unificado debe:
- Usar un tamaño fijo consistente (42×42px, el más pulido del proyecto)
- Posicionar el botón fuera del `<h1>` como elemento standalone
- Mantener la variación de color por módulo mediante CSS variables
- No afectar el layout de las cards

## Goals / Non-Goals

**Goals:**
- Una sola clase CSS `.btn-back` para todos los botones de retroceso
- Tamaño y forma consistentes en todos los módulos
- Posición predecible: primero en el header, fuera del `<h1>`
- Hover unificado: `translateX(-3px)` + color primario del módulo
- Soporte para modo claro y oscuro
- Eliminación de código muerto (`.link-back`, `.volver`, `.back-profile`)
- Compatibilidad con icon-only y variante con texto

**Non-Goals:**
- No se cambian botones de cierre de modales/overlays (`.close-modal`, `.close-overlay`, Cancelar)
- No se cambia la lógica de navegación ni rutas
- No se rediseña el header completo de cada módulo
- No se afecta el funcionamiento del theme toggle

## Decisions

### 1. Clase base en `variables.css`

**Decisión:** Definir `.btn-back` en `variables.css` para que esté disponible globalmente sin depender de un CSS de módulo específico.

**Alternativa considerada:** Definirla en `estilos.css` o en `panel.css`. Se descarta `estilos.css` porque es para estilos genéricos, y `panel.css` no lo cargan todos los módulos.

**Estructura propuesta:**

```css
.btn-back {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    width: 42px;
    height: 42px;
    border-radius: 12px;
    background: var(--bg-card);
    color: var(--text-main);
    text-decoration: none;
    border: 1px solid var(--border-color);
    transition: all 0.3s ease;
    cursor: pointer;
    flex-shrink: 0;
}
.btn-back:hover {
    transform: translateX(-3px);
    background: var(--btn-primary);
    color: white;
    border-color: var(--btn-primary);
}
/* Variante con texto: permite que el botón se expanda */
.btn-back:not(:empty):not(:has(.fa-arrow-left:only-child)) {
    width: auto;
    padding: 0 18px;
}
```

### 2. Tamaño fijo de 42×42px

**Decisión:** El tamaño `42×42px` es el que ya usa `perfil.css` (el más refinado del proyecto) y es compacto pero cliqueable.

**Alternativa considerada:** 40×40, 44×44, 48×48. 42 ofrece buen balance entre los estándares de accesibilidad (al menos 44px recomendado por WCAG, pero 42px está cerca) y el diseño compacto actual.

### 3. Posición: antes del `<h1>` como elemento standalone

**Decisión:** En cada template, el `.btn-back` se coloca como primer elemento dentro del contenedor del header, fuera del `<h1>`, con `margin-bottom: 14px` (consistente con perfil actual).

```html
<header class="...-header">
    <div>
        <a href="{{ url_for('panel') }}" class="btn-back" aria-label="Volver al panel">
            <i class="fa-solid fa-arrow-left"></i>
        </a>
        <h1>Título del Módulo</h1>
        <p>Subtítulo</p>
    </div>
    ...
</header>
```

### 4. Inline `font-size: 16px` se elimina

**Decisión:** El tamaño del icono se define en la clase base (no inline), usando un tamaño fijo de ~16px (equivalente a `1rem`) para consistencia.

### 5. Variante con texto

**Decisión:** Cuando el botón necesita texto (login, pagos), se usa la misma clase `.btn-back` con texto adentro. El CSS detecta contenido extra y se expande automáticamente:

```html
<a href="/" class="btn-back" aria-label="Volver al inicio">
    <i class="fa-solid fa-arrow-left"></i> Volver al inicio
</a>
```

### 6. Módulos con hover específico

**Decisión:** Cada módulo que quiera un color de hover distinto puede sobrescribir:

```css
/* ejemplo: inventario.css */
.inventario-header .btn-back:hover {
    background: var(--inventario-primary);
    border-color: var(--inventario-primary);
}
```

No se fuerza — cada módulo decide si sobrescribe. Por defecto usa `var(--btn-primary)`.

## Riesgos / Trade-offs

| Riesgo | Mitigación |
|--------|-----------|
| El botón icon-only sin texto puede no ser intuitivo para algunos usuarios | Se añade `aria-label` descriptivo y `title` como fallback |
| Cambiar la posición de dentro del `<h1>` a standalone puede alterar el layout vertical del header y desplazar las cards | Verificar cada template con el nuevo markup; el `margin-bottom: 14px` está calibrado con el diseño actual de perfil que ya funciona |
| `flex-shrink: 0` es necesario para evitar que el botón se comprima en layouts flexibles, pero podría causar overflow si no se usa correctamente | Solo se aplica al `.btn-back` directamente, ningún contenedor hereda la propiedad |
| La variante con texto no debe tener `width: 42px` fijo | Se usa `:not(:empty):not(:has(.fa-arrow-left:only-child))` o, como alternativa más portable, se usa la clase `.btn-back-text` para esos casos |
