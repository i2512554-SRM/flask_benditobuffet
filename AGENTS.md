# AGENTS.md

Guía de convenciones del proyecto **Bendito Buffet** (Flask + Vue 3 + PrimeVue).

## Entorno y comandos

- **Backend**: Python (venv en `.venv`). Punto de entrada `app.py`.
  - Ejecutar: `.venv\Scripts\python.exe app.py` (Windows).
  - Cambios en `api/**` o `schemas/**` requieren **reiniciar Flask** para aplicarse.
  - **1 endpoint (`api/*.py`) ↔ 1 archivo (`schemas/*.py`)**. Al crear un endpoint, crear su esquema correspondiente. Excepción: `api/personal.py` usa `schemas/usuario.py`.
    - Todo objeto de modelo que sale en una respuesta se serializa con un esquema. Las filas calculadas (totales, resúmenes, KPIs agregados) pueden armarse en el endpoint.
    - Los esquemas no consultan la base; si un campo requiere una consulta, el endpoint lo agrega después del `dump`.
  - Migraciones: SQL en `automatizacion_caja/migraciones/AAAA_MM_DD_NN_nombre.sql`. El usuario de la app (`buffet_backend`) no es dueño de las tablas: las migraciones se ejecutan en el editor SQL de Supabase **antes** de reiniciar Flask con el código que las usa.
- **Frontend**: en `frontend/` (Vite). Comando de verificación:
  - `npm run build` (desde `frontend/`). Debe pasar tras cualquier cambio.
- **Git**: solo hacer commits cuando el usuario lo pida explícitamente.

## Estructura del frontend (`frontend/src/`)

- `views/<modulo>/`: vistas organizadas por módulo.
  - convención de nombres: un archivo por vista `NombrePascal+View.vue`.
  - módulos: `auth/`, `panel/`, `cajera/`, `caja/`, `personal/`, `inventario/`, `seguridad/`, `cocina/`, `trabajador/`. `PerfilView.vue` e `IAPredictivaView.vue` permanecen en la raíz de `views/`.
- **No existe alias `@`** en `vite.config.js`: todos los imports son **relativos** con `../...`.
  - Al mover una vista un nivel más profundo, los imports `../x` cambian a `../../x` (incluye `@import` de CSS y `url(../`).
- **`router/links.js` es la fuente única de URLs** del frontend. No escribir rutas literales (`'/caja/resumen'`, etc.) en vistas/componentes: importar `{ links }` de `../router/links` (y `homeForRole(rol)` para el home por rol). El router usa `links` como única definición de paths.
- Componentes de dominio compartidos viven en `components/<modulo>/` (ej. `components/caja/CajaTransaccionDialog.vue`), usados desde varias vistas; no duplicar diálogos.
  - Componentes UI genéricos en `components/ui/`, layout en `components/layout/`, gráficos en `components/charts/`.
- Fechas/horas: el backend emite ISO UTC (`+00:00`). Para mostrar, convertir con `new Date()` + `.toLocaleString('es-PE', { timeZone: 'America/Lima' })`. `utils/format.js` expone helpers (`soloFecha`, `soloHora`, `formatFecha`).

## Backend

- Caja solo tiene tipos `Venta` y `Gasto` (no existe tipo "Ingreso"): en el frontend se muestra `Venta → Ingreso` y `Gasto → Egreso`.
- En `schemas/caja.py`, campos `responsable` y `turno` se resuelven vía `fields.Method` usando `db.session.get(Usuario, id)`.
- Roles: usar las constantes y decoradores de `api/roles.py` (`ADMIN`, `CAJERA`, `COCINA`, `TRABAJADOR`, `requiere_roles`, `admin_required`); en el frontend, `config/roles.js`. No escribir IDs de rol literales.
- Respuestas de error: siempre `{"success": false, "error": "..."}`; `message` solo para respuestas exitosas.
- Series por intervalos (reportes, indicadores): una sola consulta y sumas acumuladas (`_prefijos_movimientos` / `_totales_intervalo` en `api/caja.py`), nunca una consulta por punto.

## Convenciones de código

- No agregar comentarios al código salvo que se pidan.
- Mantener el idioma de la interfaz y de los mensajes en español.