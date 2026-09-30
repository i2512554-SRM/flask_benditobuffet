# Dashboard de KPIs — Informe final (25 de septiembre de 2026)

Implementación del **panel de indicadores del administrador (8 KPIs)** en el módulo
`/panel/indicadores` de "Bendito Buffet", construido en cinco fases y verificado contra
la base de datos real (Supabase) y una suite aislada.

Fases: ① consultas SQL documentadas → ② API backend con variación/tendencia/serie →
③ dashboard Vue con gráficos → ④ tests de los campos nuevos y rango personalizado →
⑤ informe final.

---

## 1. Endpoint (backend)

**`GET /api/indicadores`** · solo rol admin (`id_rol == 1`, `_permitido` en `api/indicadores.py`).

| Parámetro   | Valores | Descripción |
|---|---|---|
| `periodo`   | `dia` · `semana` · `mes` · `anio` | Periodo financiero (defecto `mes`) |
| `fecha`     | `YYYY-MM-DD` | Fecha de referencia (por defecto hoy en Lima) |
| `inicio`    | `YYYY-MM-DD` | Rango personalizado — inicio |
| `fin`       | `YYYY-MM-DD` | Rango personalizado — fin (exclusivo), máx. 400 días |

- Respuesta `meta`: `periodo`, `fecha`, `inicio`, `fin`, `prev_inicio`, `prev_fin` (periodo
  anterior equivalente), `corte`.
- Comparación vs periodo anterior: `variacion`, `tendencia` (`sube`/`baja`/`estable`/
  `sin_base`/`sin_datos`) y `comparacion` (valores del periodo previo).
- `serie`: evolución dentro del periodo (diaria para rango cortos, mensual para rangos > 60 días).
- Sin tocar `api/fechas.py`: el rango personalizado se resuelve internamente con `limites_dia`.
- Errores `400`: fecha/periodo inválidos, rango con extremos cruzados, rango incompleto
  (solo `inicio` o solo `fin`), rango > 400 días, ISO mal formada.

## 2. Los 8 KPI (fórmulas implementadas)

| KPI | Nombre | Unidad | Fórmula | Estimado |
|---|---|---|---|---|
| KPI-01 | Margen operativo de caja | % | `(cobros−egresos)/cobros×100` | No |
| KPI-02 | Variación de ventas | % | `(V−V₋₁)/V₋₁×100` | No |
| KPI-03 | Cobertura de inventario | días | `stock_actual / (consumo 30d / días)` | Sí |
| KPI-04 | Tasa de merma | % | `costo mermas / costo salidas×100` | Sí |
| KPI-05 | Costo laboral sobre ventas | % | `Σ sueldos prorrateados / ventas×100` | Sí |
| KPI-06 | Margen bruto estimado | % | `(V−costo vendido)/V×100` | Sí |
| KPI-07 | Diferencia de cierre de caja | % | promedio por cierre `(contado−esperado)/esperado×100` | No |
| KPI-08 | Capital inmovilizado | % | `inmovilizado sin movimiento / valor total×100` | Sí |

Decisiones de diseño:

- **KPI-07 es diferencia relativa en %** (negativo = faltante, positivo = sobrante). Los valores
  absolutos se conservan en `detalle` (`sobrante_total`, `faltante_total`, `diferencia_global`) y
  por cierre en `serie` (`diferencia_abs`).
- Caja solo distingue `Venta`/`Gasto`; el cálculo de cobros = ventas, egresos = gastos.
- La merma se clasifica por palabras clave del motivo (`merma|deterioro|vencid|dañ|desperdicio|
  faltante|caduc|avaria|robo`), excluyendo reversas de compras (`id_compra` nulo).
- Los KPIs 03, 04, 05, 06 y 08 se marcan `estimado=True` con `nota` explicativa porque dependen de
  datos parciales (costo actual, salidas, etc.). En el panel se muestran con el badge **Estimado**.
- Denominador 0 o datos faltantes → `valor: null` y mensaje "Sin datos".
- Referencia para la validación en SQL: [`automatizacion_caja/kpis.sql`](automatizacion_caja/kpis.sql).

## 3. Dashboard Vue (`frontend/src/views/panel/IndicadoresView.vue`)

- **Barra de periodo**: Hoy · Semana actual · Mes actual · Mes anterior (fecha derivada, oculta el
  selector) · Año actual · Rango personalizado (inputs Desde/Hasta).
- **8 tarjetas KPI**: valor formateado, badge "Estimado" cuando aplica, **tendencia** con flecha y
  color (verde/rojo según si subir es bueno o malo para ese KPI), **variación vs periodo anterior**
  y alerta/nota.
- **Gráficos por KPI** (Chart.js 4 + vue-chartjs, con los componentes existentes):
  - KPI-01 → `LineChartFinanciero` (Ingresos/Egresos/Balance por bucket).
  - KPI-02 → barras de ventas (S/).
  - KPI-03 → barras horizontales (top-10 cobertura en días).
  - KPI-04, 05, 06 → barras de evolución (%).
  - KPI-07 → barras de diferencia de efectivo (S/) por cierre.
  - KPI-08 → dona de inmovilizado por categoría (S/).
- Estados vacíos ("Sin datos para mostrar en este periodo") y mensajes de error.

Correcciones aplicadas en la revisión de la vista:

1. **Bug "Mes anterior"**: calculaba el penúltimo mes; se corrigió usando `new Date(año, mes, 0)`.
2. **Bug fecha UTC**: `hoyISO()` usaba `toISOString()` (adelantaba el día en Lima); ahora usa
   `fechaLocal` de `utils/format.js`.
3. **Unidad de variación**: `%` solo para KPI-02 (variación relativa); los demás muestran
   **pp** (puntos porcentuales).

## 4. Verificación

- **Suite aislada (SQLite, sin tocar Supabase)**: `+ python -m unittest discover -s tests -t .` →
  **57 pruebas OK, 1 omitida** (requiere `TEST_POSTGRES_URL`).
  - Nuevas: campos `variacion/tendencia/comparacion/serie` presentes; KPI-01 margen 50 % vs 100 %
    anterior → `baja`; KPI-02 +100 % → `sube`; KPI-07 serie por cierre; rango personalizado
    (límites, buckets diarios) y rangos inválidos → `400`.
- **Contra la BD real (Supabase)**: `GET /api/indicadores` responde `200` con periodo `rango` y
  buckets correctos; KPI-01 margen 89.30 %, KPI-02 +12.44 %, KPI-04 merma 9.49 %, KPI-06 margen
  bruto 97.50 %, KPI-08 inmovilizado 36.03 %, KPI-03 cobertura Arroz 0.25 d / Pollo 16.08 d,
  KPI-07 sin cierres con conteo en el periodo.
- **Frontend**: `npm run build` (Vite) compila correctamente.

## 5. Pendientes y notas

- **Requiere reiniciar Flask** para que el backend con rango personalizado quede activo en vivo.
- La vista en el navegador debe validarse visualmente tras el reinicio.
- Pendientes heredados del proyecto (ajenos a este trabajo): confirmación del bug #4 y descripciones
  de los bugs #6 y #10.
- El log "Falta aplicar la actualización de esquema del sistema" es un aviso pre-existente del test
  `test_revision.py:308`, no un error de esta funcionalidad.