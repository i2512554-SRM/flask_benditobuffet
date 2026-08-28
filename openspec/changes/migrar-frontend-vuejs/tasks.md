## 1. Setup Base del Frontend

- [x] 1.1 Crear proyecto Vue.js con Vite en carpeta frontend/ - verificar que npm run dev funciona
- [x] 1.2 Instalar dependencias: vue-router, pinia, primevue, primeicons, axios - verificar package.json actualizado
- [x] 1.3 Configurar PrimeVue con tema Lara - verificar que componentes PrimeVue cargan correctamente
- [x] 1.4 Configurar Vue Router con rutas base - verificar navegacion entre vistas dummy
- [x] 1.5 Configurar Pinia store de autenticacion - verificar store funciona con datos mock
- [x] 1.6 Crear layout base (AppHeader, AppSidebar, AppFooter) - verificar layout se muestra en todas las vistas

## 2. Backend API Flask

- [x] 2.1 Instalar flask-cors, flask-jwt-extended, flask-marshmallow - verificar imports funcionan
- [x] 2.2 Configurar CORS en app.py para permitir requests desde localhost:5173 - verificar con curl
- [x] 2.3 Crear estructura de carpetas api/ y schemas/ - verificar que modulos se importan correctamente
- [x] 2.4 Implementar endpoints de autenticacion (login, logout, refresh) - verificar con Postman/curl
- [x] 2.5 Implementar serializacion JSON con marshmallow schemas - verificar que datos se retornan como JSON
- [x] 2.6 Configurar manejo de errores centralizado - verificar que errores retornan JSON consistente

## 3. Modulo de Autenticacion

- [x] 3.1 Crear LoginView.vue con formulario PrimeVue - verificar que formulario se muestra correctamente
- [x] 3.2 Implementar llamada a API de login con axios - verificar que token se recibe y almacena
- [x] 3.3 Implementar store de auth con Pinia (login, logout, refreshToken) - verificar persistencia en localStorage
- [x] 3.4 Configurar axios interceptor para JWT automatico - verificar que requests incluyen token
- [x] 3.5 Implementar ProtectedRoute component - verificar que rutas no autenticadas redirigen a login
- [x] 3.6 Implementar logout y limpieza de sesion - verificar que token se elimina correctamente

## 4. Modulo Panel Admin

- [x] 4.1 Crear PanelAdminView.vue con PrimeVue cards - verificar que stats se muestran correctamente
- [x] 4.2 Implementar endpoint /api/admin/panel-stats - verificar que retorna ventas, egresos, neto
- [x] 4.3 Crear componente StatsCard reutilizable - verificar que muestra datos con formato correcto
- [x] 4.4 Implementar ModuleCard para navegacion - verificar que redirige a modulos correctamente
- [x] 4.5 Crear componente ActionsButtons - verificar que botones funcionan

## 5. Modulo de Caja
- [x] 5.1 Crear CajaView.vue con PrimeVue DataTable - verificar que tabla muestra transacciones

- [x] 5.2 Implementar endpoints de caja (abrir, cerrar, transacciones) - verificar CRUD completo
- [x] 5.3 Crear formulario de apertura de caja - verificar que abre caja correctamente
- [x] 5.4 Crear formulario de registro de transacciones - verificar que registra ingreso/egreso
- [x] 5.5 Implementar cierre de caja con resumen - verificar que calcula totales correctamente
- [x] 5.6 Crear vista de historial con filtros por fecha - verificar que muestra datos filtrados

## 6. Modulo de Personal
- [x] 6.1 Crear PersonalView.vue con navegacion a submodulos - verificar que muestra menu de opciones

- [x] 6.2 Implementar endpoints CRUD de empleados - verificar crear, leer, actualizar, eliminar
- [x] 6.3 Crear EmpleadosView.vue con DataTable - verificar que lista empleados con paginacion
- [x] 6.4 Crear EmpleadoFormView.vue con formulario PrimeVue - verificar que formulario valida y envia datos
- [x] 6.5 Implementar endpoints de pagos - verificar registro y consulta de pagos
- [x] 6.6 Crear PagosView.vue con historial de pagos - verificar que muestra historial por empleado
- [x] 6.7 Implementar endpoints de turnos - verificar asignacion y consulta
- [x] 6.8 Crear TurnosView.vue con calendario - verificar que muestra turnos por fecha
- [x] 6.9 Implementar endpoints de adelantos - verificar registro y consulta de pendientes
- [x] 6.10 Crear AdelantosView.vue - verificar que muestra adelantos pendientes
- [x] 6.11 Implementar endpoints de salarios con calculo automatico - verificar calculo mensual
- [x] 6.12 Crear SalariosView.vue con calculo detallado - verificar que muestra desglose por empleado

## 7. Modulo de Inventario

- [x] 7.1 Implementar endpoints CRUD de productos - verificar crear, leer, actualizar, eliminar
- [x] 7.2 Crear InventarioView.vue con PrimeVue DataTable - verificar que lista productos con stock
- [x] 7.3 Implementar endpoint de actualizacion de stock - verificar que ajusta stock correctamente
- [x] 7.4 Crear formulario de productos con categorias - verificar que formulario valida datos
- [x] 7.5 Implementar endpoints de compras - verificar registro con detalle de proveedor
- [x] 7.6 Crear InversionDetalleView.vue con historial de compras - verificar que muestra historial
- [x] 7.7 Implementar endpoints de categorias y proveedores - verificar CRUD basico
- [x] 7.8 Crear formularios de categorias y proveedores - verificar que funcionan

## 8. Tema Oscuro y UX

- [x] 8.1 Implementar toggle de tema oscuro en AppHeader - verificar que cambia tema PrimeVue
- [x] 8.2 Configurar persistencia de tema en localStorage - verificar que tema se mantiene al recargar
- [x] 8.3 Implementar loading states con PrimeVue ProgressSpinner - verificar que muestra spinner en llamadas API
- [x] 8.4 Implementar Toast notifications para exitos y errores - verificar que muestra feedback al usuario
- [x] 8.5 Implementar ConfirmDialog para acciones destructivas - verificar que pide confirmacion antes de eliminar

## 9. Integracion y Limpieza

- [x] 9.1 Probar flujo completo: login -> panel -> modulo -> operacion - verificar que todo funciona
- [x] 9.2 Verificar que todos los modulos migrados funcionan igual que version Jinja2 - comparar comportamiento
- [x] 9.3 Eliminar templates Jinja2 de carpeta templates/ - verificar que frontend Vue funciona independiente
- [x] 9.4 Eliminar archivos JS legacy de static/js/ - verificar que no hay dependencias rotas
- [x] 9.5 Eliminar rutas render_template de app.py - verificar que solo quedan endpoints API
- [x] 9.6 Optimizar bundle con vite build - verificar que tamano es razonable
- [x] 9.7 Crear script de build y deploy - verificar que npm run build genera dist/ correcto
