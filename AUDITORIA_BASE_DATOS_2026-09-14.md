# Auditoría de base de datos — 14 de septiembre de 2026

## Correcciones aplicadas después de la revisión

Con autorización del usuario se ejecutó `python -m automatizacion_caja.proteger_bd --aplicar` en una transacción confirmada. Las 25 tablas tienen ahora RLS habilitado y carecen de permisos SELECT/INSERT/UPDATE/DELETE/TRUNCATE para anon/authenticated; también se revocaron permisos PUBLIC. Se comprobó acceso de lectura del backend en todas. Se adaptaron chk_pago_tipo y chk_metodo_pago conservando los valores históricos, se añadió validación de monto positivo y finito a pagos_empleados y se crearon los cinco índices recomendados. No se alteraron importes, contraseñas ni usuarios. El resto del documento conserva los hallazgos originales como evidencia histórica.

Actualización posterior: el usuario confirmó que solo este sistema utiliza la base. Se creó `buffet_backend` con LOGIN y sin SUPERUSER, CREATEDB, CREATEROLE, REPLICATION ni BYPASSRLS. Tiene permisos de lectura/escritura sobre las 25 tablas, uso de sus secuencias y políticas RLS exclusivas para el backend; no tiene CREATE en public ni TRUNCATE. Se verificaron lecturas y una inserción de sesión revertida. `.env` utiliza ahora una nueva credencial generada, sin mostrarla ni guardarla en Git. Los permisos por empleado continúan siendo responsabilidad de Flask: esta cuenta representa al servidor, no a cada usuario final.

Pendientes: rotación de la contraseña administrativa anterior desde el panel de Supabase, clasificación del pago histórico (requiere conocer su concepto), alineación completa de tipos/modelos y validación de backups/PITR, red y exposición de API en el proveedor. Cambiar la credencial de la aplicación no invalida la contraseña administrativa anterior. No se ha realizado una restauración de respaldo ni se declara completada esa comprobación. Las futuras migraciones deben ejecutarse con una cuenta administrativa y conceder explícitamente al backend acceso a cualquier nueva tabla/secuencia.

Revisión de la base configurada mediante transacciones de solo lectura. No se modificaron datos, usuarios, contraseñas ni permisos. Resultados agregados: no se extrajeron valores personales. Herramienta reproducible: `python -m automatizacion_caja.auditar_bd`. No equivale a una certificación de seguridad ni a una prueba de penetración.

## Prioridad alta

1. **Tres tablas sin protección RLS y con permisos de lectura/escritura para anon y authenticated:** `pagos_empleados`, `notificaciones`, `solicitudes_insumos`. La exposición por Internet depende de que la Data API publique estas tablas; no se comprobó ese ajuste ni se intentó acceder a datos por HTTP. Es una configuración insegura confirmada, no evidencia de una filtración. Recomendación: habilitar RLS y retirar permisos directos de clientes, conservando el acceso del backend Flask.
2. **21 tablas mantienen permisos amplios para roles de clientes.** Se confirmó además TRUNCATE para anon en esas 21 tablas. RLS no protege TRUNCATE; esto no implica que la Data API ofrezca una ruta para ejecutarlo. Las otras 18 tienen RLS sin políticas, que bloquea las operaciones ordinarias por esos roles, pero conviene retirar los permisos innecesarios. Las cuatro tablas nuevas ya tienen RLS y lectura/escritura revocadas para anon/authenticated.
3. **Restricciones incompatibles con la interfaz.** `pagos_personal.chk_pago_tipo` solo acepta Pago y Adelanto; el servidor envía Salario semanal, Bono, Horas extra u Otros. `transacciones_caja.chk_metodo_pago` solo acepta Efectivo, Tarjeta y Transferencia; rechaza Yape, Plin y Otros. Los valores están confirmados en el catálogo: no se insertaron operaciones reales para provocar errores. Actualizar estas restricciones conservando los valores históricos. La actualización anterior de tablas/columnas quedó incompleta respecto de estas reglas.
4. **La aplicación se conecta como postgres con BYPASSRLS.** Un fallo del backend o una credencial comprometida tiene alcance amplio. Crear un rol exclusivo con los permisos mínimos necesarios, diseñar su acceso a las tablas con RLS y probarlo antes de sustituir la conexión; cambiar el rol sin preparar permisos bloquearía el sistema.
5. **Secreto anterior en el historial Git.** En la revisión de código anterior se retiró una contraseña incrustada. No se ha verificado su rotación en el proveedor. Debe rotarse y actualizarse en el servidor; retirarla del archivo actual no invalida copias históricas.

## Integridad y coherencia

- 25 tablas de la aplicación presentes; no faltan las columnas esperadas por los modelos. Esto no significa igualdad completa de tipos, restricciones y valores por defecto.
- Todas tienen clave primaria; no se encontraron relaciones declaradas ausentes, registros huérfanos en las claves foráneas examinadas, restricciones sin validar ni índices inválidos.
- Cero grupos duplicados de usuario, correo o número de documento, comparados tras quitar espacios extremos e ignorar mayúsculas.
- 11 usuarios; todas las claves tienen formato bcrypt y hay dos administradores activos. No se evaluó la fortaleza de las contraseñas originales ni se intentó descifrarlas.
- Un pago histórico sin concepto clasificado y sin vínculo a pagos_personal. Debe revisarse manualmente; no inferir que corresponde a sueldo ni duplicarlo para resolverlo.
- Cero montos no positivos/no finitos en pagos_empleados y transacciones_caja, cero stock negativo/no finito y cero movimientos de caja sin método.
- Existe una caja con estado abierta; no es por sí sola un error. No hay cierres con fecha de cierre anterior a apertura.
- pagos_empleados no tiene CHECK de monto/estado/concepto. Añadir restricciones coherentes con el servidor después de revisar valores heredados.
- La mayoría de importes/stock reales usa tipos decimales, aunque los modelos Python declaran varios Float. `cierres_caja.monto_inicial` y `solicitudes_insumos.cantidad` sí son aproximados. Alinear modelos y esquema y definir precisión monetaria y de cantidades antes de migrar.

## Rendimiento y operación

- Cinco claves foráneas sin índice inicial adecuado: inversiones.id_proveedor, descuentos_semanales.registrado_por, sueldos_semanales.registrado_por, atenciones_insumos.id_solicitud, inventario_movimientos.id_compra. Añadir índices según uso; con este volumen no se demostró que sean la causa de la lentitud.
- Base de aproximadamente 12 MB. 235 intentos de acceso, ninguno mayor de 90 días, y 204 registros de actividad. No hay evidencia de saturación por estos conteos.
- PostgreSQL 17.6 observado; no se evaluó disponibilidad de actualización del proveedor.
- TLS activo entre el cliente Python y el pool, confirmado con la conexión cliente. pg_stat_ssl muestra false en el backend observado: puede corresponder al tramo interno pool–PostgreSQL. No permite concluir que las credenciales viajan sin cifrar desde la aplicación. Verificar configuración interna con el proveedor. El código exige sslmode=require; evaluar verificación de certificado y nombre con la configuración admitida por el proveedor.
- No se verificaron restauraciones de backups, PITR, reglas de red, MFA del panel, ajustes de exposición Data API ni rotación del secreto. Tampoco se ejecutaron los Advisors oficiales porque no hay CLI/MCP configurado; se revisaron catálogos directamente.

## Orden recomendado

1. Corregir RLS y permisos innecesarios, verificando que Flask mantenga acceso.
2. Adaptar las dos restricciones incompatibles y probar pagos y métodos de caja en PostgreSQL de pruebas.
3. Rotar el secreto anterior y preparar el rol restringido del backend.
4. Revisar el pago histórico; alinear tipos y completar restricciones e índices.
5. Comprobar restauración de respaldo y revisar configuración de red y Data API en el panel del proveedor.

Referencias: [RLS y permisos de Supabase](https://supabase.com/docs/guides/database/postgres/row-level-security), [Advisors y comprobaciones de integridad/rendimiento](https://supabase.com/docs/guides/observability/advisors).
