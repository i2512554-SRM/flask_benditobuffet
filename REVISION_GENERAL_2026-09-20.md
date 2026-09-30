# Revisión general del sistema — 20 de septiembre de 2026

## Alcance y resultados

Revisión de código, pruebas aisladas de API y recorridos en navegador con usuarios ficticios. Las únicas consultas realizadas sobre la base real fueron lecturas: conexión como buffet_backend y acceso correcto a usuarios, sesiones, caja, pagos y productos. No se registraron operaciones comerciales reales ni se cambiaron permisos durante esta revisión.

- 33 pruebas de la suite: 32 aprobadas y una omitida porque falta TEST_POSTGRES_URL.
- Recorrido adicional de 39 rutas GET con cuatro roles: 156 solicitudes; 63 respuestas 200, 91 respuestas 403 y dos 404 por recursos de la muestra. Cero errores 500 o excepciones. Esto verifica disponibilidad, no la exactitud de cada resultado ni una matriz exhaustiva de permisos.
- Compilación de frontend correcta el 20/09.
- Navegador: administrador (revisión del 18/09), cocina, trabajador y cajero (20/09). Se comprobó carga de módulos, acceso a reportes, cambio de abril a mayo de 2025, entrada de stock que abre el diálogo, solicitud ficticia de adelanto y aparición en historial, regreso con Volver, cierre de sesión, rechazo de acceso de cocina a personal, apertura de caja con S/100 e ingreso ficticio de S/50.
- Diagnósticos adicionales reproducibles en `python -m tests.revision_general`: detectan los dos fallos de backend descritos abajo. Es una herramienta diagnóstica, no una suite que garantice que esos defectos estén corregidos.

## Fallos confirmados, por prioridad

### Alta: una cuenta desactivada conserva acciones con una sesión anterior

Se desactivó un usuario ficticio tras emitir su sesión y se solicitó cancelar su adelanto pendiente: respuesta 200. `api/sesiones.py` comprueba revocación, caducidad y contraseña, pero no estado del usuario/rol; `cancelar_adelanto` en `api/perfil.py` solo exige JWT y propiedad del adelanto. Unificar la comprobación de cuenta/rol activo en todas las acciones protegidas y agregar regresión de sesión emitida antes de desactivar al usuario.

### Media: un bono válido se rechaza como pago duplicado

Registrar salario de S/25 y después un bono de S/25 para el mismo empleado y día devuelve 200 y 400. `_duplicado_pago` en `api/personal.py` compara usuario, día, monto y estado, pero omite concepto y semana. Distinguir una repetición de la misma operación de dos pagos legítimos; usar identificador único de operación y concepto/semana correctos.

### Media: tarjetas distintas tienen el mismo destino

- Cocina: Ver Insumos, Productos y stock, tarjeta Insumos y tarjeta Productos conducen a `/inventario/operaciones?vista=productos` sin distinguir acciones.
- Trabajador: Mis pagos y Mis adelantos llegan a `/trabajador/pagos`; la segunda no abre el formulario ni selecciona la sección de adelantos. Mis solicitudes conduce a notificaciones.
- Cajero: Ir al Control de Caja aparece dos veces en la misma pantalla.
- Administrador: Registrar Pago lleva al listado de pagos; exige pulsar un segundo botón para abrir el formulario.

Recomendación: un acceso por función en cada grupo. Las acciones con verbo Registrar/Solicitar deben abrir su formulario; los accesos a listas deben usar nombres de listas. No eliminar automáticamente accesos repetidos entre menú global y contenido: pueden ser útiles, a diferencia de dos tarjetas vecinas que prometen funciones distintas.

### Media: fechas y horas inconsistentes

Cocina muestra días/meses en inglés dentro de una frase española. `api/cocina.py` y `api/trabajador.py` usan strftime dependiente del idioma del servidor. En la demostración SQLite se observaron movimientos de 19:00 Lima como 00:00 del día siguiente: SQLite pierde la zona al serializar, y el navegador recibe una fecha sin offset. Esto se confirmó en la demostración, no se ha demostrado el mismo defecto en PostgreSQL real. Emitir ISO con zona desde el servidor y formatear de manera uniforme con es-PE/America/Lima; probar límites de día/mes en ambos motores.

### Baja: funciones y accesibilidad poco claras

¿Olvidaste tu contraseña? es texto sin acción. Ofrecer un flujo real o indicar que se contacte al administrador. En inventario hay botones de icono sin nombre accesible. Añadir etiquetas descriptivas y revisar uso con teclado y en móvil. El botón Volver funcionó en el recorrido probado; su respaldo fijo a /panel en módulos compartidos merece una prueba separada por rol al abrir una URL directamente.

## Recomendaciones de backend

1. Resolver primero la cuenta desactivada y el falso duplicado de pagos.
2. Extender el identificador de operación usado en descuentos a pagos, ingresos/egresos e inventario. Deshabilitar un botón no protege de reintentos después de una desconexión.
3. Optimizar `_historial`: actualmente carga movimientos desde el cierre más antiguo hasta hoy y vuelve a recorrerlos para cada cierre, incluso para consultar meses históricos. Acotar el intervalo necesario, agregar en SQL o recorrer datos ordenados una sola vez; medir antes/después.
4. Separar la lógica financiera de las rutas: rendimiento invoca `reportes.__wrapped__()`. Usar un servicio compartido con parámetros explícitos y pruebas propias.
5. Añadir integración con PostgreSQL y pruebas de solicitudes simultáneas. La suite SQLite no valida RLS, bloqueos de PostgreSQL ni diferencias del esquema real.

## Recomendaciones de base de datos

1. Confirmar rotación de la antigua contraseña administrativa: la cuenta limitada no invalida esa credencial. No se verificó la rotación en esta revisión.
2. Registrar migraciones versionadas que incluyan tablas, restricciones, índices y permisos del backend. Comprobar compatibilidad antes de iniciar la aplicación para evitar repetir el fallo de actualización pendiente.
3. Alinear modelos y tipos reales: importes exactos con Numeric/Decimal y precisión definida para cantidades. La auditoría anterior encontró columnas reales decimales frente a modelos Float; no convertir toda la base a ciegas. [Tipos numéricos de PostgreSQL](https://www.postgresql.org/docs/current/datatype-numeric.html).
4. Revisar manualmente el pago histórico sin concepto; no adivinar si fue salario o bono.
5. Probar restauración en un entorno separado y respaldar también fotos de perfil y configuración protegida. Los respaldos de Supabase no incluyen archivos de Storage ni contraseñas de roles personalizados; las fotos locales también necesitan copia aparte. [Respaldos de Supabase](https://supabase.com/docs/guides/platform/backups).

## Límites y siguiente paso

No se certificó cada botón, móvil, recuperación de contraseña, restauración, concurrencia real ni funcionamiento bajo carga. La demostración multihilo en SQLite presentó errores de conexión/sesión; se continuó en una instancia serial en el puerto 5057. Esto es una limitación del entorno de demostración que debe corregirse, no prueba de un fallo equivalente en producción.

Se recomienda corregir primero los dos fallos de backend, luego navegación y fechas, y finalmente completar integración PostgreSQL y restauración. Esta entrega contiene diagnóstico y recomendaciones; no aplica esas correcciones ni crea commits.
