# Correcciones por fases — 21 de septiembre de 2026

## Resultado verificado en entorno aislado

1. Sesiones y pagos: una cuenta desactivada pierde acceso con su sesión anterior; un bono y un salario del mismo importe se registran por separado; la semana salarial se calcula en hora de Lima.
2. Navegación: los accesos rápidos de cajero, cocina, trabajador y administración abren la acción o el listado indicado; la solicitud de adelanto abre su formulario y aparece en su historial.
3. Fechas y reportes: API con zona horaria explícita, interfaz en español y hora de Lima. Los movimientos se suman una vez por periodo y el reporte muestra detalle paginado junto al gráfico.
4. Rendimiento: el historial de cierres evita recorrer repetidamente todos los movimientos; el gráfico consulta solo los puntos necesarios.
5. Operaciones repetidas: ingreso, egreso, stock, compra y pago llevan una clave única por intento; el servidor evita repetir el movimiento al recibir la misma clave. Los botones de stock y compra se desactivan mientras se guarda. Las líneas de compra se redondean por subtotal antes de sumar el total.
6. Precisión: importes y cantidades usan `Decimal`/`Numeric` en modelos y cálculos internos; las respuestas JSON siguen enviando números compatibles con la interfaz.
7. Pagos: los filtros rechazan meses y años inválidos con una respuesta clara; el próximo pago se calcula según el día de Lima incluso alrededor de medianoche UTC.

La suite más reciente ejecutó 46 pruebas: 45 aprobadas y una omitida porque no hay una base separada en `TEST_POSTGRES_URL`. La compilación de Vue concluyó correctamente. El navegador local mostró el reporte mensual con gráfico, 69 movimientos y navegación por páginas. También se comprobó que un doble clic de ingreso registró un solo movimiento. La verificación de bloqueos de caja, inventario y personal en PostgreSQL respondió correctamente con la cuenta limitada; no sustituye una prueba de concurrencia con dos conexiones activas y escritura en una base desechable.

## Migraciones aplicadas a la base real

El 21 de septiembre se identificó la base activa del proyecto correcto y se verificó que coincide con la configuración de esta aplicación. Antes de modificarla, se creó un respaldo lógico local del esquema `public` con `pg_dump` 17.11. El archivo quedó fuera de Git, con acceso restringido al propietario, SYSTEM y administradores; su SHA-256 es `77e2726cdfc3227644d2a646b3f930a7221a5acf32282aafcfbd71ef17dc9958`. `pg_restore` pudo leer y descomprimir sus 25 tablas y sus entradas de datos. Los recuentos de siete tablas clave coincidieron con la base. Este respaldo **no** incluye Supabase Auth, Storage ni roles, y todavía no se ha probado una restauración completa. El plan gratuito no ofrece los respaldos administrados de Supabase.

Se aplicaron, en este orden y en transacciones independientes, los archivos versionados:

- [`2026_09_21_01_idempotencia.sql`](automatizacion_caja/migraciones/2026_09_21_01_idempotencia.sql): cuatro columnas `clave_operacion` e índices únicos parciales.
- [`2026_09_21_02_precision_numerica.sql`](automatizacion_caja/migraciones/2026_09_21_02_precision_numerica.sql): control previo de incompatibilidades y seis conversiones a `NUMERIC`.

El editor SQL informó éxito en ambos casos. Después, con la cuenta limitada `buffet_backend`, `verificar_idempotencia` confirmó las cuatro columnas y los cuatro índices únicos válidos; `verificar_numericos` confirmó los seis tipos y cero valores incompatibles. Los recuentos de las siete tablas siguieron iguales: usuarios 11, pagos 1, transacciones 6, movimientos de inventario 5, compras 0, cierres 5 y solicitudes 0. La cuenta de la aplicación conserva sus permisos limitados. El respaldo se puede repetir mediante [`respaldar_publico.py`](automatizacion_caja/respaldar_publico.py), usando los binarios PostgreSQL 17 y un directorio privado fuera del repositorio.

Estas verificaciones prueban el esquema y los recuentos, pero no demuestran que el despliegue remoto esté ejecutando la nueva versión de la aplicación. Los scripts `preparar_idempotencia.py` y `preparar_precision_numerica.py` usan exactamente los SQL enlazados para otros entornos.

## Trabajo todavía por validar

La demostración corre con datos ficticios aislados. Queda probar concurrencia real, restauración y carga en una base PostgreSQL de pruebas; la suite actual no certifica esos escenarios ni el despliegue de la base real. El diagnóstico inicial se conserva en [`REVISION_GENERAL_2026-09-20.md`](REVISION_GENERAL_2026-09-20.md); los defectos allí descritos son el estado anterior a estas correcciones.
