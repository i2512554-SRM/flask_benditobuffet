## Context

La ruta `pagos_personal_detalle` (app.py:291) recibe `id_usuario` y obtiene `empleado = Usuario.query.get_or_404(id_usuario)`, pasando el objeto `empleado` completo al template (app.py:300). El template actualmente ignora este dato para el título, usando "Pagos Personal" genérico.

## Goals / Non-Goals

**Goals:**
- Mostrar "Historial de [nombres] [apellido]" dinámicamente según el empleado consultado
- Actualizar el subtítulo para reflejar el contexto

**Non-Goals:**
- No modificar rutas, lógica de negocio, CSS, ni otros templates
- No cambiar el resto del contenido de la página

## Decisions

1. **Usar `empleado.nombres` y `empleado.apellido`**: El objeto `empleado` ya está disponible en el contexto del template (pasado como `empleado=empleado` en la línea 300 de app.py). Los campos `nombres` y `apellido` son los mismos usados en `pagos_personal.html` y otras vistas.
2. **Subtítulo descriptivo**: Se cambia el subtítulo genérico por "Historial de pagos, adelantos y movimientos" — más escueto y directamente relacionado con el contenido.

## Riesgos / Trade-offs

- **Riesgo mínimo**: Solo se cambian expresiones Jinja estáticas por dinámicas usando una variable ya disponible. Sin cambios en backend.
