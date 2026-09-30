# Revisión de flujos — 13 de septiembre de 2026

Actualización del 14 de septiembre: este documento conserva la evidencia de la revisión original. Los trece defectos descritos debajo ya tienen correcciones y pruebas de regresión en `tests/test_revision.py`. Resultado: 32 pruebas aprobadas y una omitida por requerir PostgreSQL. La interfaz compila y el generador SQL funciona; siguen pendientes la aplicación y validación del esquema en PostgreSQL de pruebas, el despliegue y la rotación de la contraseña retirada del código. Consultar `CAMBIOS_Y_VERIFICACION.md` para las condiciones de activación. Las ubicaciones de líneas siguientes corresponden al código anterior.

Revisión del código en `codex/correcciones-paneles-y-sueldos`, después del commit `f8d1396`. Se revisaron rutas y permisos de administrador, caja, personal, inventario, cocina, trabajador, perfil y autenticación, junto con los formularios que las consumen. Se ejecutaron 14 reproducciones aisladas con SQLite en memoria: 13 muestran defectos o riesgos funcionales y una confirma el requisito de activación de nómina. No se consultaron ni modificaron datos reales. No se aplicaron correcciones al código del sistema durante esta revisión.

## Hallazgos de prioridad alta

### 1. Los bonos reducen el sueldo pendiente

- Ubicación: `api/personal.py:434` y `api/personal.py:457`.
- Reproducción: configurar sueldo de S/ 350 y registrar un pago de S/ 50 con tipo Bono. La respuesta devuelve sueldo 350, pagos 50 y saldo 300.
- Impacto: un bono pagado se trata como abono al sueldo fijo; el saldo de sueldo debería conservarse en 350 si el bono es adicional. Afecta igualmente otros conceptos extraordinarios.
- Corrección: guardar el concepto de pago de forma estructurada y distinguir abonos al sueldo de pagos adicionales. No inferirlo únicamente del texto de descripción.

### 2. Adelantos cancelados o ya resueltos pueden volver a gestionarse

- Ubicación: `api/admin.py:195–212`.
- Reproducción: cancelar una solicitud como trabajador, aprobarla como administrador y luego rechazarla. Las tres operaciones devuelven 200.
- Impacto: un adelanto que ya se entregó puede desaparecer de las deducciones al cambiarlo a Rechazado. Dos administradores también pueden sobrescribir decisiones.
- Corrección: transiciones de estado verificadas en servidor, control de concurrencia y procedimiento explícito de reversión para importes ya entregados.

### 3. El adelanto se descuenta en la semana de solicitud, no de entrega

- Ubicación: `api/personal.py:438–439`, `api/admin.py:212`.
- Reproducción: solicitud de S/ 30 del domingo 6 de septiembre, aprobada posteriormente. El historial asigna 30 a la semana terminada el día 6 y 0 a la siguiente.
- Impacto: modifica un periodo anterior y deja sin descontar el adelanto en el periodo de entrega. Hoy Aprobado se interpreta como dinero entregado, sin una fecha de desembolso independiente.
- Corrección: separar solicitud, aprobación y entrega; usar la semana de liquidación o fecha de entrega acordada. Aplicar la misma regla a pagos efectuados en una fecha distinta de la semana que remuneran.

### 4. El último administrador puede desactivar su propia cuenta

- Ubicación: `api/personal.py:149–152`; revisar también cambio de rol en `actualizar_empleado`.
- Reproducción: con un único administrador activo, eliminar lógicamente su propia cuenta devuelve 200 y quedan cero administradores activos.
- Impacto: se pierde la capacidad de administrar el sistema desde la interfaz.
- Corrección: impedir desactivar o degradar al último administrador activo, con verificación transaccional.

### 5. Cerrar sesión no invalida la renovación de sesión

- Ubicación: `api/auth.py:150–166`.
- Reproducción: después de llamar a logout, el token de renovación anterior sigue obteniendo un token nuevo: respuesta 200.
- Impacto: borrar la sesión del navegador no revoca una copia del token. El cambio de contraseña tampoco incorpora revocación en servidor.
- Corrección: sesiones revocables o versión de credenciales/sesión comprobada en acceso y renovación, revocada al cerrar sesión o cambiar contraseña.

### 6. Cantidades fraccionarias bloquean salidas válidas de inventario

- Ubicación: `api/inventario.py:327–341` y campos Float del inventario.
- Reproducción: partir de 0.3 Kg y retirar 0.1 Kg. Se guarda 0.19999999999999998. Retirar los 0.2 Kg restantes devuelve 400 por falta de stock.
- Impacto: impide consumir el saldo real de productos medidos en Kg o litros.
- Corrección: precisión decimal acordada y consistente en almacenamiento, sumas y comparación de cantidades. Definir precisión por unidad y validar cantidades enteras para productos por unidad si corresponde.

## Otros defectos reproducidos

| Flujo | Resultado observado | Ubicación | Corrección propuesta |
| --- | --- | --- | --- |
| Buscar producto dentro de una categoría | `cat=Ingredientes&q=arroz` provoca OperationalError al combinar las dos uniones de Categoría. | `api/inventario.py:163–170` | Usar una única unión para ambos filtros. |
| Anular compra que atendió una solicitud | Tras comprar 5 y anular, el stock vuelve a 0 pero la solicitud sigue Atendida. | `api/inventario.py:461`, `api/inventario.py:485–521` | Relacionar atención con compra y cantidad; revertir o revisar la atención al anular. |
| Consultar cierres antiguos | Con 201 cierres, el primer cierre existe pero su reporte diario devuelve cero cierres. | `api/caja.py:44`, función `reportes` | Filtrar por periodo antes de limitar y paginar con total; conservar el contexto necesario de aperturas vecinas. |
| Reintentar el mismo descuento | Dos envíos iguales devuelven 200 y guardan dos descuentos. | `api/personal.py:497–514` | Clave de idempotencia persistida por operación; bloquear botones no cubre reintentos o varias pestañas. |
| Editar DNI duplicado | Cambiar el DNI de un empleado por el de otro genera IntegrityError sin manejar. | `api/personal.py:107–144` | Verificar duplicados y manejar el conflicto con rollback y mensaje claro. |
| Pagar un registro pendiente | Registrar después el mismo pago como Pagado deja un registro Pagado y otro Pendiente; no existe ruta PUT/PATCH de pago para completar el original. | `api/personal.py:309–364`, `frontend/src/views/PagosView.vue` | Incorporar transición Pendiente → Pagado/Cancelado sobre un único pago y sincronizar los registros relacionados. |
| Solicitud de cocina con cantidad no finita | Cantidad `"Infinity"` devuelve 201 y almacena infinito. | `api/cocina.py:155–160` | Usar validación de número finito, límites y precisión; validar también producto activo. |

## Observaciones adicionales confirmadas por lectura de código

- **Credencial en el código:** `bd.py:14` contiene un valor predeterminado no vacío para DB_PASSWORD. No se reprodujo aquí su contenido ni se probó su validez. Eliminar el secreto del código y rotarlo si sigue vigente; retirarlo del último archivo no lo elimina del historial de Git.
- **Consulta DNI sin autenticación:** `app.py:114–134` expone la consulta sin comprobar sesión ni rol. Si DNI_API_TOKEN está configurado, una persona sin iniciar sesión puede consumir esa integración y consultar datos. Restringirla a administradores y limitar su uso. No se llamó al proveedor externo en esta revisión.
- **No se puede quitar el último turno:** `frontend/src/views/TurnosView.vue:116` abandona la función si la selección queda vacía. Permitir guardar vacío cuando se desasignan turnos.
- **La limpieza no controla todo el crecimiento de accesos:** el login agrega un evento a `actividad_usuario` (`api/auth.py:129`), pero la limpieza conserva toda esa tabla. La retención de `intentos_login` no elimina estos duplicados. Separar eventos de acceso de los eventos de negocio o aplicar una política específica que preserve pagos y operaciones.
- **Cambio de contraseña inconsistente:** `api/perfil.py:229–236` no aplica el mínimo de ocho caracteres que sí exige crear empleados. Una contraseña muy larga termina en error genérico en lugar de validación. Unificar la política en ambos flujos.
- **Información de sueldo inconsistente:** el perfil sigue mostrando el salario mensual de `UsuarioPerfil`, mientras el historial nuevo usa `SueldoSemanal`. Debe mostrar la tarifa semanal vigente o identificar claramente el dato anterior.

## Requisito de activación, no un incidente demostrado en producción

El historial de sueldos consulta incondicionalmente las tablas nuevas (`api/personal.py:442–444`). Al retirar la tabla de sueldos únicamente de la base ficticia, la consulta genera OperationalError. Es indispensable aplicar y verificar la preparación de nómina antes de desplegar el código. Ya era un paso pendiente de la entrega anterior; no se inspeccionó el esquema real.

## Límites de la revisión

- Las reproducciones usan SQLite en memoria; no certifican bloqueos ni concurrencia reales de PostgreSQL.
- Se revisó el flujo de interfaz en código; esta pasada no es una prueba visual completa en todos los dispositivos.
- Las quince pruebas funcionales de la entrega anterior no cubrían estos casos de estados, conceptos de pago, fracciones y periodos históricos. Deben ampliarse al corregirlos.
- Conviene atender primero saldos/adelantos, protección del administrador, sesiones y cantidades fraccionarias; después búsquedas, estados pendientes y detalles de historial.
