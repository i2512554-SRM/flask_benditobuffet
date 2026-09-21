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

## Aplicación pendiente en la base real

La cuenta `buffet_backend` no tiene permiso `ALTER TABLE` (PostgreSQL 42501). El intento controlado de migración se revirtió; **la base real no fue modificada**. La verificación de solo lectura encontró cuatro columnas `clave_operacion` y sus índices todavía ausentes. Hay además seis columnas con precisión distinta al modelo; el control previo encontró cero valores incompatibles con su conversión.

Antes de desplegar esta versión sobre la base real, respaldar la base y aplicar, en ese orden, mediante una cuenta administradora de migraciones:

- [`2026_09_21_01_idempotencia.sql`](automatizacion_caja/migraciones/2026_09_21_01_idempotencia.sql): cuatro claves de operación e índices únicos parciales.
- [`2026_09_21_02_precision_numerica.sql`](automatizacion_caja/migraciones/2026_09_21_02_precision_numerica.sql): control de valores y seis conversiones a `NUMERIC`.

Son transacciones independientes. La segunda puede bloquear tablas mientras convierte columnas, por lo que conviene una ventana de mantenimiento. Tras aplicarlas, ejecutar `python -m automatizacion_caja.verificar_idempotencia` y `python -m automatizacion_caja.verificar_numericos`; solo entonces iniciar la nueva versión de la aplicación. La cuenta limitada debe conservarse sin privilegios de migración. Los scripts `preparar_idempotencia.py` y `preparar_precision_numerica.py` usan exactamente los SQL enlazados y pueden aplicarlos con `--aplicar` cuando se configure temporalmente una conexión administrativa segura.

## Trabajo todavía por validar

La demostración corre con datos ficticios aislados. Queda probar concurrencia real, restauración y carga en una base PostgreSQL de pruebas; la suite actual no certifica esos escenarios ni el despliegue de la base real. El diagnóstico inicial se conserva en [`REVISION_GENERAL_2026-09-20.md`](REVISION_GENERAL_2026-09-20.md); los defectos allí descritos son el estado anterior a estas correcciones.
