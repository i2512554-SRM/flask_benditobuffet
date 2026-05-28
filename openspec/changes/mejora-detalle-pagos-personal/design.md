## Context

`pagos_personal_detalle.html` es la vista que muestra el detalle de pagos y adelantos de un empleado. Actualmente:
- El botón de volver usa clase `btn-back` (sin estilos), texto `#sebas`, y enlace a `panel`
- Las tres tablas (pagos registrados, pagos personal, adelantos) se muestran todas a la vez apiladas verticalmente
- Hay dos `header-actions` vacíos
- En `pagos_personal.html`, el botón "Ver" en la tabla de empleados no es descriptivo

## Goals / Non-Goals

**Goals:**
- Botón de volver con estilo `btn-outline`, texto "Volver", enlace correcto a `pagos_personal`
- Navegación por pestañas/botones para alternar entre las 3 tablas
- Una sola tabla visible a la vez

**Non-Goals:**
- No modificar rutas, lógica de negocio, ni modelos
- No cambiar la vista `pagos_personal.html` excepto el texto del botón
- No agregar nuevas dependencias externas

## Decisions

1. **Patrón view-toggle existente**: Se reutiliza la misma estructura de `.view-toggle` + `.btn-secondary` + clase `hidden` + JS que ya funciona en `pagos_personal.html`, garantizando consistencia visual y de comportamiento.
2. **btn-outline para volver**: Se usa la clase `btn-outline` (botón del sistema con borde y fondo transparente) en lugar de crear una nueva clase, manteniendo el icono `fa-arrow-left` y agregando el texto "Volver".
3. **ID por tabla + hidden**: Cada `.table-card` recibe un ID único (`pagosRegistradosCard`, `pagosPersonalCard`, `adelantosCard`) y la clase `hidden` por defecto. El JS las alterna al hacer clic en los botones.
4. **Primera tabla visible por defecto**: Al cargar la página, la primera tabla (Pagos Registrados) se muestra sin `hidden`.

## Riesgos / Trade-offs

- **Riesgo**: Si en el futuro se agregan más tipos de tablas, habrá que agregar más botones y JS. → Mitigación: El patrón es escalable y fácil de extender.
- **Trade-off**: Se agrega JS inline en el template en lugar de un archivo separado, pero esto es consistente con el resto del proyecto.
