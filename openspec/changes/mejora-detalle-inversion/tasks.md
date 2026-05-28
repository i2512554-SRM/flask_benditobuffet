## 1. Actualizar estilos en inventario.css

- [x] 1.1 Mejorar `.detalle-card`: agregar `max-width: 800px; margin: 1.5rem auto;`, aumentar padding a `2rem`, mejorar sombra
- [x] 1.2 Agregar `.detalle-badge` para el ID de inversión (píldora con fondo semitransparente)
- [x] 1.3 Cambiar `.detalle-grid` a 3 columnas `1fr 1fr 1fr` para metadatos con etiquetas
- [x] 1.4 Agregar `.detalle-field` (label + valor apilados) con label semitransparente y valor en negrita
- [x] 1.5 Agregar `.detalle-divider` para el separador entre metadatos y descripción
- [x] 1.6 Mejorar `.detalle-section` con mejor padding para descripción y notas
- [x] 1.7 Actualizar media query 700px para apilar metadatos en 1 columna y ajustar paddings

## 2. Reestructurar el template HTML

- [x] 2.1 En `inventario_compra_detalle.html`: cambiar estructura de `.detalle-card` con badge, grid de metadatos con etiquetas, separador, y descripción/notas mejoradas
- [x] 2.2 Verificar que todas las variables de inversión (inversion.id_inversion, monto, proveedor, fecha, descripcion, notas) se rendericen correctamente
