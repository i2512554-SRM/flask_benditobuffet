# Propuesta de KPIs técnicos — Sistema de Gestión "Bendito Buffet"

Informe realizado sobre el código real del proyecto (`flask_benditobuffet`): modelos
(`models.py`), APIs (`api/`), migraciones (`automatizacion_caja/`), interfaz
(`frontend/src/views/`) y auditoría de base de datos (`AUDITORIA_BASE_DATOS_2026-09-14.md`).
Fecha: 18 de septiembre de 2026.

---

## PARTE 1 — ANÁLISIS INICIAL DEL PROYECTO

### 1.1 ¿Qué problemas del restaurante pueden medirse mediante indicadores?

| Problema de negocio | Síntoma dado por el sistema |
|---|---|
| Falta de control del flujo de caja | Egresos (Gasto) que se acercan o superan a las ventas por apertura |
| Stock muerto o sobrestock | Productos que no salen en semanas y compras de pánico |
| Desabastecimiento inesperado | Productos en estado "Stock bajo"/"Agotado" sin aviso previo |
| Ventas sin tendencia conocida | Imposibilidad de anticipar cuándo reponer o ajustar personal |
| Planilla descontrolada | Adelantos, bonos y descuentos que escapan del salario semanal |
| Riesgo de accesos indebidos | Intentos de login fallidos repetidos |

### 1.2 ¿Qué información ya existe (o debería existir) en la base de datos?

**Existe hoy** (verificado en `models.py`, `AUDITORIA_BASE_DATOS_2026-09-14.md`):

- `transacciones_caja`: tipo (`Venta`/`Gasto`), `monto`, `metodo_pago`, `categoria`, `fecha`.
- `cierres_caja`: `monto_inicial`, `total_ventas`, `total_gastos`, `neto` (computado), `estado`, `fecha_cierre`.
- `productos`: `nombre`, `precio`, `stock`, `unidad_medida` (Kg/Un/Lt), `estado`, `id_categoria`.
- `inventario_movimientos`: `tipo` (Entrada/Salida/Ajuste), `cantidad` (con signo), `stock_anterior`,
  `stock_posterior`, `motivo`, `id_compra`, `fecha`.
- `compras_inventario` y `detalle_compras_inventario`: `total_compra`, `cantidad`, `precio_unitario`, `subtotal` (computado), proveedor.
- `usuarios`, `roles` (1 admin, 2 cajera, 3 cocinero, 4 trabajador), `documentos_identidad` (DNI).
- `pagos_empleados` y `pagos_personal`: `monto`, `fecha`, `tipo` (Salario semanal/Bono/Horas extra/Otros), `estado`.
- `sueldos_semanales`, `descuentos_semanales` (con `anulado`, `clave_operacion`).
- `adelantos`: `monto`, `estado` (Pendiente/Aprobado), `fecha`, `fecha_gestion`.
- `solicitudes_insumos` (Pendiente/Atendida) y `atenciones_insumos` (vínculo solicitud→compra).
- `intentos_login` (`resultado`: exito/fallido), `actividad_usuario`, `notificaciones`.

**Conclusión para los 5 KPIs seleccionados:** los datos disponibles **son suficientes**. Los 5
indicadores se calculan con información que el sistema ya produce (ver PARTE 4).

### 1.3 ¿Qué módulos generan datos para los KPIs?

| Módulo | Endpoints principales | Datos que produce |
|---|---|---|
| Caja | `/api/caja/transacciones`, `/abrir`, `/cerrar`, `/reportes` | Ventas, gastos, métodos de pago, cierres |
| Inventario | `/api/inventario/productos/*/stock/*`, `/movimientos`, `/compras`, `/resumen` | Entradas/salidas, stock con trazabilidad, compras |
| Cocina | `/api/cocina/dashboard`, `/solicitudes`, `/alertas` | Solicitudes de insumos, estados de stock |
| Personal | `/api/personal/pagos`, `/adelantos`, `/salarios`, `/pagos/empleado/*` | Pagos, adelantos, sueldos, descuentos |
| Seguridad | `api/auth.py`, `api/sesiones.py`, `intentos_login` | Intentos de acceso, actividad, sesiones |
| Trabajador | `/api/trabajador/dashboard`, `/turnos`, `/pagos` | Percepción del rol 2/3/4 |
| RENIEC (futuro) | `/api/dni/<dni>` (apisperu) | Validación de DNI en registro/contratación |

### 1.4 ¿Qué decisiones podría tomar el administrador con esos indicadores?

- Si los gastos se comen el flujo de caja (recortar, renegociar proveedores).
- Si las ventas crecen o caen (promocionar, abastecer, ajustar personal).
- Qué productos tienen stock muerto y cuáles se rotan bien (dónde poner/mover dinero).
- Cuándo y cuánto comprar de productos de compra diaria (cantidad de pedido).
- Si la planilla cabe dentro de la venta del periodo.

### 1.5 ¿Qué datos adicionales sería necesario almacenar?

Para los 5 KPIs seleccionados: **ninguno**. En la PARTE 4 se documentan dos campos opcionales de
mejora futura (costeo monetario y clasificación de mermas), no requeridos por estos indicadores.

---

## PARTE 2 — DOCUMENTO DE DEFINICIÓN DE KPIs (5 seleccionados)

### KPI-01 · Margen de flujo de caja

**En palabras simples:** imagina un día de trabajo en el restaurante: entran S/ 100 por los
platos que se venden, y de esa misma caja se pagan S/ 70 en gastos del día (insumos comprados,
vuelto, pagos pequeños, etc.). Al cerrar quedan S/ 30 en la caja: el margen es del 30 %. Si ese
número baja a 10 % o 5 %, significa que cada vez queda menos dinero de cada sol vendido, y conviene
revisar los gastos. Es la respuesta rápida a "¿estoy ganando o perdiendo dinero hoy?".

1. **Nombre:** Margen de flujo de caja (%).
2. **Fórmula:**
   ```
   ((Σ Ventas − Σ Gastos) / Σ Ventas) × 100
   ```
   donde `Ventas = SUM(monto) WHERE tipo = 'Venta'` y `Gastos = SUM(monto) WHERE tipo = 'Gasto'` en el periodo `[inicio, fin)`.
3. **Fuente de datos:**
   - Numerador: `SUM(transacciones_caja.monto)` para `tipo='Venta'` − `SUM(transacciones_caja.monto)` para `tipo='Gasto'`.
   - Denominador: `SUM(transacciones_caja.monto)` para `tipo='Venta'`.
   - Tabla: `transacciones_caja` · Campos: `tipo`, `monto`, `fecha`.
   - Módulo: **Caja** (`/api/caja/transacciones`, `/api/caja/reportes`).
4. **Interpretación:** Porcentaje del dinero ingresado por ventas que realmente queda en caja después de los egresos registrados. Señala cuánto de cada sol de venta sobrevive al gasto.
5. **Utilidad:** Decidir recorte/renegociación de gastos, abrir caja con monto inicial adecuado y detectar cierres "en rojo" (margen negativo) a tiempo.
6. **Frecuencia:** Diario; acumulado semanal y mensual.
7. **Meta o referencia:** Sin dato histórico suficiente para meta propia. Referencia orientativa de industria: 15 %–30 %. **Validar** contra 8–12 semanas de datos reales.

### KPI-02 · Variación porcentual de ventas vs periodo anterior

**En palabras simples:** es como medir la temperatura del negocio. Compara cuánto vendió el
restaurante esta semana (o este mes) contra la semana (o mes) anterior. Si la diferencia es
positiva, las ventas crecen; si es negativa, están bajando. Por ejemplo: si este mes se vendió
S/ 12,000 y el anterior S/ 10,000, la variación es +20 %. Con eso sabes si conviene abastecerse
más, hacer una promoción o ajustar el personal, en lugar de adivinar.

1. **Nombre:** Variación porcentual de ventas (% `Δ`).
2. **Fórmula:**
   ```
   ((V(t) − V(t−1)) / V(t−1)) × 100
   ```
   siendo `V(t)` = ventas del periodo actual y `V(t−1)` = ventas del periodo equivalente anterior.
3. **Fuente de datos:**
   - Numerador: `SUM(transacciones_caja.monto)` actual − anterior (ambas con `tipo='Venta'`).
   - Denominador: `SUM(transacciones_caja.monto)` del periodo anterior (`tipo='Venta'`).
   - Tabla: `transacciones_caja` · Campos: `tipo`, `monto`, `fecha`.
   - Módulo: **Caja / Rendimiento** (`/api/rendimiento`, `/api/caja/reportes`).
4. **Interpretación:** Crecimiento (positivo) o caída (negativo) de la venta frente al periodo equivalente anterior.
5. **Utilidad:** Decidir campañas/promociones, dimensionar personal y compras según la dirección de la tendencia.
6. **Frecuencia:** Semanal y mensual (comparación contra el periodo previo).
7. **Meta o referencia:** ≥ 0 % (crecimiento continuo). Calibrar umbral de alerta por estacionalidad con datos históricos.

### KPI-03 · Rotación por producto y cadencia de compra

**En palabras simples:** responde "¿qué tan rápido se consume cada producto?". Se mira producto por
producto: si tienes arroz y lo consumes 3 veces al mes según lo que guardas en promedio, rota
3 veces. Como algunos productos (verduras, carnes) se compran a diario y su número saldría enorme y
confuso, el sistema los agrupa en tres casos: (1) **compra diaria** → lo más útil es saber cuánto
comprar mañana; (2) **compra semanal** → cuándo reponer; y (3) **almacén/secos** → si un producto
lleva semanas sin salir, es "dinero parado" y el sistema lo avisa para promocionarlo o retirarlo.

1. **Nombre:** Rotación por producto y cadencia de compra (por producto, en su propia unidad Kg/Un/Lt).
2. **Fórmula:**
   ```
   Rotación del producto = Σ |salidas del producto en el periodo| / Stock promedio del producto
   ```
   - Salidas: `inventario_movimientos.cantidad` con `tipo='Salida'` (o `tipo='Ajuste'` con `cantidad < 0`).
   - Stock promedio: promedio de `inventario_movimientos.stock_posterior` (cierre diario) del producto en el periodo, o `(stock inicial + stock final) / 2` sobre `productos.stock`.
   - Como es por producto y en unidades propias, **no requiere costo unitario** y **no se mezclan unidades** entre productos.
   - **Cadencia de compra** (clasificación automática según días de cobertura, ver KPI-04):
     - **Alta (compra diaria)** · cobertura ≤ 1–2 días → no reportar el número de rotación (resulta muy alto y confuso); reportar **consumo diario** y **cantidad de pedido sugerida** = consumo diario × plazo del proveedor.
     - **Media (semanal)** · cobertura 3–7 días → **rotación semanal** + **punto de reorden**.
     - **Baja (almacén/secos)** · cobertura > 7 días → **rotación mensual** + **alerta de stock muerto** (sin salidas en 30/60/90 días).
3. **Fuente de datos:**
   - Numerador: `SUM(ABS(inventario_movimientos.cantidad))` filtrando `id_producto`, `tipo`/`cantidad`, `fecha`.
   - Denominador: `AVG(inventario_movimientos.stock_posterior)` (o `productos.stock` inicial/final) por `id_producto`.
   - Tablas: `inventario_movimientos` (campos `cantidad`, `tipo`, `stock_posterior`, `fecha`, `id_producto`), `productos` (campos `stock`, `unidad_medida`).
   - Módulo: **Inventario** (`/api/inventario/movimientos`, `/api/inventario/resumen`).
4. **Interpretación:** Cuántas veces se consume el producto en el periodo según su stock promedio. La lectura correcta depende de la cadencia: para productos de compra diaria (verduras, carnes) el número de rotación pierde sentido operativo y manda la cobertura (KPI-04); para producto de almacén, la rotación baja sí es una alerta de stock muerto.
5. **Utilidad:** Detectar "stock muerto" (productos sin salida en N días → promoción o retiro), dimensionar la cantidad de pedido de los productos de compra diaria y ajustar la frecuencia de compra de cada grupo.
6. **Frecuencia:** Cálculo diario por producto; reporte semanal de tendencia.
7. **Meta o referencia:** Por cadencia — almacén/secos: rotación mensual ≥ 1; alerta de "stock muerto": sin salidas en 30/60/90 días según el grupo; compra diaria: cobertura ≤ 2 días como normal operativa. Calibrar con histórico.

### KPI-04 · Días de cobertura de inventario (run-out)

**En palabras simples:** responde a la pregunta del día a día: "¿cuántos días me va a durar esto?".
Si tienes 20 kilos de arroz y la cocina usa 2 kilos por día, te alcanza para 10 días. Así sabes con
anticipación cuándo pedir al proveedor (por ejemplo, si él demora 3 días, hay que comprar cuando
queden unos 4 días de stock). Evita que la cocina se quede sin ingredientes el sábado sin aviso.

1. **Nombre:** Días de cobertura (run-out) por producto.
2. **Fórmula:**
   ```
   Días de cobertura = Stock actual del producto / Consumo diario promedio
   Consumo diario promedio = Σ |salidas| de los últimos 30 días / 30
   ```
3. **Fuente de datos:**
   - Numerador: `productos.stock`.
   - Denominador: `inventario_movimientos.cantidad` (tipo `Salida` o `Ajuste` negativo) de los últimos 30 días.
   - Tablas: `productos` (campo `stock`), `inventario_movimientos` (campos `tipo`, `cantidad`, `fecha`, `id_producto`).
   - Módulo: **Inventario / Cocina** (`/api/cocina/inventario`, `/api/cocina/alertas`).
4. **Interpretación:** Cuántos días puede operar la cocina con el stock actual al ritmo promedio de consumo. Predice el desabastecimiento ANTES de llegar a "Agotado".
5. **Utilidad:** Fechas y volúmenes de compra sugeridos; reduce compras de pánico y sobrestock. Es la base de la clasificación de cadencia del KPI-03.
6. **Frecuencia:** Diaria (en la práctica, tiempo real).
7. **Meta o referencia:** 3–7 días para perecederos; 14–30 días para secos/abarrotes (orientativo). Calibrar con el ciclo real de compras.

### KPI-05 · Ratio de costo laboral sobre ventas

**En palabras simples:** muestra qué parte de lo que vendes se va en pagar a tu personal. Por
ejemplo, si en una semana vendiste S/ 10,000 y pagaste S/ 3,500 en sueldos más S/ 500 en adelantos,
el 40 % de tu venta se fue en la planilla. En restaurantes, cuando ese porcentaje se acerca o pasa
del 35–40 %, la rentabilidad peligra: sirve para decidir si el negocio aguanta más personal, si
conviene ajustar turnos, o para notar que los adelantos están subiendo el costo en silencio.

1. **Nombre:** Ratio de costo laboral (%).
2. **Fórmula:**
   ```
   ((Σ Pagos pagados + Σ Adelantos aprobados) / Σ Ventas) × 100
   ```
3. **Fuente de datos:**
   - Numerador: `pagos_empleados.monto` (estado='Pagado') y `adelantos.monto` (estado='Aprobado', por `fecha_gestion`).
   - Denominador: `transacciones_caja.monto` (`tipo='Venta'`).
   - Tablas: `pagos_empleados` (campos `monto`, `estado`, `fecha_pago`), `adelantos` (`monto`, `estado`, `fecha_gestion`), `transacciones_caja` (`monto`, `tipo`, `fecha`).
   - Módulos: **Personal** (`/api/personal/pagos`) + **Caja**.
4. **Interpretación:** Porcentaje de la venta que se destina a la planilla (sueldos + adelantos entregados). Valores altos comprometen la rentabilidad.
5. **Utilidad:** Dimensionar turnos, decidir contrataciones/recortes y controlar que los adelantos no inflen el costo laboral del mes.
6. **Frecuencia:** Semanal y mensual.
7. **Meta o referencia:** 25 %–35 % es un rango habitual de costo de mano de obra en restaurantes (orientativo). Calibrar con la estructura real de personal.

---

## PARTE 3 — KPI, MÉTRICAS Y DATOS A UTILIZAR

| KPI | Métrica | Dato requerido | Tabla | Campo | Tipo de dato | Módulo | Periodicidad |
|---|---|---|---|---|---|---|---|
| KPI-01 Margen de flujo de caja | Suma de ventas | Monto por movimiento | transacciones_caja | monto / tipo / fecha | NUMERIC / VARCHAR(50) / TIMESTAMPTZ | Caja | Diaria |
| KPI-01 | Suma de gastos | Monto por movimiento | transacciones_caja | monto / tipo / fecha | Ídem | Caja | Diaria |
| KPI-02 Variación de ventas | Suma de ventas por periodo | Monto y fecha | transacciones_caja | monto / tipo / fecha | Ídem | Caja / Rendimiento | Semanal–Mensual |
| KPI-03 Rotación por producto | Salidas del producto | Cantidad por movimiento | inventario_movimientos | cantidad / tipo / fecha / id_producto | NUMERIC / VARCHAR(30) | Inventario | Diaria (reporte semanal) |
| KPI-03 | Stock promedio | Cierre diario de stock | inventario_movimientos | stock_posterior / id_producto | NUMERIC | Inventario | Diaria (reporte semanal) |
| KPI-03 | Unidad de medida | Unidad del producto | productos | unidad_medida | VARCHAR(10) | Inventario | — |
| KPI-04 Días de cobertura | Stock actual | Cantidad en stock | productos | stock | NUMERIC | Inventario / Cocina | Diaria |
| KPI-04 | Consumo diario promedio | Salidas de últimos 30 días | inventario_movimientos | cantidad / tipo / fecha | NUMERIC | Inventario / Cocina | Diaria |
| KPI-05 Costo laboral | Pagos y adelantos | Montos pagados y adelantos aprobados | pagos_empleados / adelantos | monto / estado / fecha | NUMERIC | Personal | Semanal–Mensual |
| KPI-05 | Ventas del periodo | Monto de ventas | transacciones_caja | monto / tipo / fecha | NUMERIC | Caja | Semanal–Mensual |

---

## PARTE 4 — MODIFICACIÓN DE LA BASE DE DATOS

**Conclusión: los 5 KPIs se calculan con los datos actuales. No se requiere modificar la base de datos.**

Antes se consideró `productos.costo_promedio` para una rotación valorizada en dinero; al reformular
el KPI-03 por producto y en unidades (Kg/Un/Lt), el costeo dejó de ser necesario y además no se
mezclan unidades entre productos.

### Campos opcionales de mejora futura (NO requeridos — solo si luego se quiere medir dinero o mermas)

| Tabla | Campo nuevo | Tipo de dato | Propósito | KPI futuro |
|---|---|---|---|---|
| `productos` | `costo_promedio` | `NUMERIC(12,2) NOT NULL DEFAULT 0` | Rotación global valorizada en soles y costeo de consumo | Rotación monetaria / mermas |
| `inventario_movimientos` | `tipo_salida` | `VARCHAR(30) NULL` (CHECK catálogo) | Clasificar mermas/pérdidas | Tasa de pérdidas y mermas |

---

## PARTE 5 — PROPUESTA TÉCNICA DE IMPLEMENTACIÓN EN EL SISTEMA

### Backend (Flask + PostgreSQL)

- Nuevo blueprint **`/api/kpis`** con dos endpoints agregados en SQL (mismo patrón de `api/caja.py`):
  - `GET /api/kpis/dashboard` → KPI de tiempo real: margen de caja (KPI-01), ticket/ventas del día, días de cobertura top-10 (KPI-04), grupos de cadencia con alertas de stock (KPI-03).
  - `GET /api/kpis/analisis?periodo=mes&fecha=YYYY-MM-DD` → KPI por periodo: margen acumulado (01), variación de ventas (02), rotación por producto y cadencia (03), costo laboral (05).
  - Filtros opcionales: `producto`, `categoria`, `empleado`, `umbral`.
- Consultas con `SUM`/`COUNT`/`AVG` sobre las fuentes de la PARTE 3, reutilizando `api/fechas.py`
  (`periodo_financiero`) para los buckets día/semana/mes/año.
- La clasificación de cadencia (KPI-03) se calcula en SQL a partir del `Días de cobertura` (KPI-04):
  `CASE WHEN cobertura <= 2 THEN 'Alta' WHEN cobertura <= 7 THEN 'Media' ELSE 'Baja' END`.

### Frontend (Vue 3 + PrimeVue)

| Dónde | KPIs | Gráfico sugerido | Filtros |
|---|---|---|---|
| **Dashboard admin** (`PanelAdminView` + tarjetas) | KPI-01, 02, 04, 03 | Tarjetas de número + Gauge + DataTable top-10 cobertura | Periodo día/semana/mes |
| **Caja → Reportes financieros** | KPI-01, KPI-02 | Línea (evolución ventas/margen) + media móvil 4 semanas | Fecha, periodo |
| **Inventario → Reportes** | KPI-03, KPI-04 | Tabs por cadencia (Alta/Media/Baja); barras de consumo; ranking de stock muerto | Producto, categoría, rango |
| **Personal → Reportes** (`PagosView`/`SalariosView`) | KPI-05 | Barras costo laboral vs ventas por mes | Mes, empleado |
| **IA Predictiva** (`IAPredictivaView`) | KPI-04 proyectado | Línea reales vs proyección; cantidad de pedido sugerida por producto | Periodo |

### Comportamiento de actualización

- **Tiempo real:** margen/balance de caja (KPI-01) y días de cobertura (KPI-04) al abrir las vistas
  (patrón de `get_caja_actual` y `cocina/dashboard`).
- **Por periodo:** variación (02), rotación/cadencia (03) y costo laboral (05) en `/api/kpis/analisis`.
- **Predicción:** la proyección de reabastecimiento y la cantidad de pedido sugerida (KPI-03/04) se
  activan desde la primera semana de movimientos; la tendencia de ventas (KPI-02) requiere acumular
  ≥ 8–12 semanas de `transacciones_caja` para ser significativa.

### Preguntas que podrá responder el administrador

- ¿Las ventas aumentan o disminuyen? → **KPI-01, KPI-02**
- ¿Cuánto de cada sol de venta queda en caja? → **KPI-01**
- ¿Qué productos tienen stock muerto y cuáles rotan bien? → **KPI-03**
- ¿Cuánto comprar de los productos de compra diaria y cuándo? → **KPI-03, KPI-04**
- ¿La planilla cabe dentro de la venta? → **KPI-05**