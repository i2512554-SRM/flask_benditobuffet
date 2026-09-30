# Correcciones del sistema — septiembre de 2026

## Caja y reportes

- Administrador y cajero pueden consultar el mismo reporte de caja por día, semana, mes o año, avanzar y retroceder periodos y revisar los movimientos que componen cada total.
- Los totales provienen de transacciones, no de sumar cierres diarios que podían repetir ventas. Los periodos usan la hora de Lima e incluyen completo el último día.
- Los cierres nuevos consideran solo su apertura. Las aperturas antiguas superpuestas se señalan para revisión; sus registros originales no se reescriben.
- Registrar un movimiento requiere caja abierta, monto positivo y método de pago. Los botones se bloquean mientras se envía la operación; se rechazan solicitudes idénticas simultáneas en el cliente. Las escrituras de caja e inventario se serializan por transacción en PostgreSQL.
- El balance mostrado es ventas menos egresos registrados en caja. No es una utilidad contable que incluya automáticamente toda compra o pago del personal.

## Personal y perfiles

- Crear empleados requiere administrador y contraseña inicial. DNI de 8 números, teléfono de 9 números y nombres sin cifras se validan en cliente y servidor. Las opciones de turno son Tarde y Noche; los registros antiguos no se migran automáticamente.
- Los tipos de pago se seleccionan, con opción Otros. Los campos monetarios nuevos están vacíos y muestran un ejemplo que desaparece al enfocarlos.
- El historial general incluye pagos pendientes y adelantos. Mis pagos muestra las tablas y estados. Solicitar adelanto abre un formulario y actualiza el historial al enviarlo; no se ofrece al administrador.
- El historial semanal consulta de lunes a domingo. Saldo = sueldo fijo semanal − abonos de salario − adelantos entregados − descuentos vigentes por platos, faltas u otros. Bonos, horas extra y pagos pendientes no reducen el sueldo base. Los adelantos se descuentan en la semana de entrega; los pagos tienen una semana asignada. Actualizar consulta sin generar pagos.
- Cada sueldo tiene fecha de vigencia: un cambio posterior no cambia las semanas anteriores. Los descuentos pueden anularse, dejando registro de la acción. Un saldo negativo se muestra expresamente; no se oculta ni se traslada automáticamente a otra semana. Sin tarifa configurada se informa que falta configurar el sueldo.
- El perfil envía correctamente la foto como formulario multipart y muestra una vista previa. El cambio de contraseña se realiza mediante contraseña actual, nueva y confirmación.
- Volver utiliza la página anterior dentro de la aplicación, con una ruta de respaldo cuando no existe historial interno.

## Inventario y seguridad

- Se unifica la compra de productos bajo Inversiones (compras). Cada compra aumenta stock y registra su costo; proveedor opcional. Entrada sin compra sirve para una reposición o ajuste sin registrar una nueva inversión.
- La unidad se elige manualmente: Kg, Un o Lt. No se convierten automáticamente las cantidades históricas de arroz, azúcar u otros productos: elegir Kg corrige la etiqueta, no convierte cantidades ni precios.
- Cocina puede crear/editar productos, consultar reportes y registrar entradas/salidas. Las inversiones y anulaciones permanecen a cargo del administrador. Se conservan solicitudes de insumos.
- Los reportes incluyen existencias y movimientos; se elimina la duplicación de tarjetas de compras/inversiones. Los registros anteriores de inversión permanecen consultables.
- Seguridad deja de duplicar Empleados e Historial de actividad. La actividad reciente del panel dirige al módulo correspondiente. Se reducen consultas repetidas al cargar empleados y accesos.

## Retención de accesos recomendada

La herramienta conserva 90 días de accesos, valida el periodo y procesa lotes de hasta 1000 registros. Por defecto solo informa cuántos eliminaría: `python -m automatizacion_caja.limpiar_logs`. Para aplicar se exige respaldo: `python -m automatizacion_caja.limpiar_logs --aplicar --respaldo logs/respaldos-accesos`. El archivo se escribe y sincroniza antes de eliminar cada lote. Incluye accesos, duplicados antiguos de inicio de sesión, consultas DNI y sesiones caducadas desde hace más de 90 días. Conserva la actividad de pagos y operaciones.

Se incluye `automatizacion_caja/programar_limpieza.ps1`: instala una tarea diaria a las 03:00 en Windows; por defecto solo revisa, con `-Aplicar` respalda y elimina. Debe ejecutarse en el servidor con la configuración de base de datos correcta. Requiere sesión iniciada y recupera ejecuciones pendientes. No se ha instalado una tarea ni eliminado registros reales desde esta sesión. Los respaldos contienen datos de acceso: mantener la carpeta privada y definir cuándo archivarlos o eliminarlos.

## Activación del sueldo semanal

La actualización requiere las tablas `sueldos_semanales`, `descuentos_semanales`, `sesiones_usuario` y `atenciones_insumos`, además de columnas de concepto, semana y vínculo en pagos. `python -m automatizacion_caja.preparar_nomina` genera el SQL desde los modelos, sin conectarse a una base ni aplicar cambios. Primero revisarlo y aplicarlo en PostgreSQL de pruebas, registrar la migración con el flujo del entorno y después aplicarla antes de desplegar el código. El SQL habilita RLS y retira acceso directo a clientes; Flask debe conectarse con el rol de backend autorizado (propietario de estas tablas o con BYPASSRLS). No se agrega acceso de nómina mediante la API pública de Supabase.

Los sueldos mensuales anteriores no se convierten: el administrador ingresa el monto semanal acordado. La migración solo vincula pagos antiguos con correspondencia inequívoca. Los pagos sin concepto deben clasificarse en el historial antes de mostrar un saldo liquidable. Cambiar la tarifa de una semana ya existente modifica deliberadamente esa vigencia y deja constancia en actividad.

Se retiró del código una contraseña de base de datos incrustada. Debe rotarse en el proveedor y actualizarse la configuración del servidor: el secreto anterior permanece en el historial Git. Esta sesión no lo rotó. Ahora se requieren DB_USER, DB_PASSWORD y DB_HOST. Las consultas DNI requieren DNI_API_TOKEN y acceso de administrador. Después del despliegue todos deberán iniciar sesión otra vez; cerrar sesión revoca también la renovación y cambiar contraseña invalida las sesiones anteriores.

El historial permite completar o cancelar pagos pendientes sin duplicarlos. Se protegen el último administrador activo, las decisiones finales de adelantos y los descuentos frente a reintentos con la misma clave. Se corrigieron stock fraccionario, filtros combinados, reposición anulada y reportes con más de 200 cierres. Las cantidades se normalizan a tres decimales; las columnas históricas de stock conservan su tipo actual.

## Verificación

Pruebas aisladas: `python -m unittest discover -s tests -v`. Utilizan SQLite en memoria y no conectan con Supabase. Cubren permisos, validación de empleados, cierre/reapertura, aperturas históricas superpuestas, límite mensual en Lima, adelantos pendientes, cancelación de aprobados, compras sin proveedor, stock, pago semanal y foto multipart.

Interfaz: `npm run build` desde `frontend`. Para revisión manual con datos ficticios: `python -m tests.preview`, abrir `http://127.0.0.1:5056`. Usuarios locales `user1` (administrador), `user2` (cajero), `user3` (cocina), `user4` (trabajador); contraseña exclusivamente de prueba: `demo-local-2026`. El servidor solo escucha en localhost y usa memoria; no debe desplegarse.

La vista local incluye movimientos y cierres ficticios desde el 1 de abril de 2025 hasta ayer: ventas por efectivo, Yape y tarjeta, gastos variables, mayor venta los fines de semana y temporadas altas. Los lunes no tienen movimientos. Permite comparar días, semanas, meses y años en Reportes de caja. Los datos se recrean al reiniciar; el cargador rechaza bases persistentes y no inserta nada en Supabase.

No se han ejecutado migraciones ni operaciones sobre los datos reales. Los bloqueos de concurrencia de PostgreSQL requieren validación en un entorno de pruebas PostgreSQL antes de producción; SQLite verifica la lógica de los flujos, no el comportamiento de esos bloqueos.

Resultado local al 14 de septiembre: 32 pruebas aprobadas, una prueba PostgreSQL omitida, compilación de la interfaz correcta y generador SQL ejecutado sin conexión. Las nuevas regresiones cubren los trece hallazgos de la revisión, además de DNI, contraseñas, retención y ausencia de tablas. La revisión visual previa cubrió reportes, pagos/adelantos, empleados, perfil y sueldo semanal; los nuevos cambios se verificaron mediante pruebas de API y compilación. La prueba opcional de PostgreSQL requiere `TEST_POSTGRES_URL`; no se ejecutó por falta de un entorno PostgreSQL de pruebas configurado.

Se sustituyó PrimeVue 5.0.1 por PrimeVue 4.5.5 y el tema por `@primeuix/themes` 2.0.3, versiones oficiales MIT fijadas con archivo de dependencias actualizado. La compilación y revisión visual funcionan sin el aviso de licencia. No se oculta ni modifica ningún mecanismo de comprobación. Referencia: https://github.com/primefaces/primevue (mantenimiento de las versiones MIT).
