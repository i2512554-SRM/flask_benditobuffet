-- =====================================================================
-- CONSULTAS SQL DE LOS 8 KPI — Bendito Buffet
-- Base real: PostgreSQL (Supabase). Zona horaria del negocio: America/Lima.
--
-- CONVENCIÓN DE PARÁMETROS DE VENTANA (obligatorios):
--   :inicio, :fin          ventana del periodo actual  (UTC, [inicio, fin))
--   :prev_inicio, :prev_fin  ventana del periodo anterior comparable (UTC)
--   :corte                 fecha de corte para KPIs de estado actual (UTC)
--   :ventana_dias          días de ventana de consumo/inmovilizado (30)
--
-- Todo movimiento registrado en transacciones_caja es CONFIRMADO por
-- defecto (no existe campo estado/confirmación).
--
-- Mapeos acordados con la estructura real:
--   'Venta'  -> INGRESO / cobro operativo CONFIRMADO
--   'Gasto'  -> EGRESO  / egreso operativo CONFIRMADO
--   Salida de inventario con motivo de merma (texto)  -> motivo_grupo = 'Merma'
--   Salida de preparación/venta                        -> motivo_grupo = 'Consumo'
--   Costo: no existe snapshot por movimiento; se usa productos.costo actual.
--
-- DENOMINADOR EN CERO / SIN DATOS: todo valor se devuelve como NULL
-- (backend/frontend muestran "Sin datos"), nunca Infinity ni NaN.
-- =====================================================================


-- =====================================================================
-- UTILIDADES (CTE compartidas)
-- =====================================================================

-- Clasifica cada salida de inventario en un grupo operativo.
-- id_compra IS NULL descarta las reversas de compras (entradas anuladas).
-- No existen transferencias internas ni correcciones administrativas en la
-- estructura actual: todas las salidas restantes son consumo/venta/merma.
CREATE OR REPLACE VIEW vw_kpi_salidas AS
SELECT
    m.id_movimiento,
    m.id_producto,
    m.cantidad,
    m.fecha,
    p.costo,
    CASE WHEN lower(m.motivo) ~ 'merma|deterioro|vencid|caduc|desperdicio|robo|faltante|avaria|daño'
         THEN 'Merma'
         ELSE 'Consumo'
    END AS motivo_grupo
FROM public.inventario_movimientos m
JOIN public.productos p ON p.id_producto = m.id_producto
WHERE m.tipo = 'Salida'
  AND m.id_compra IS NULL;

-- Días operativos de una ventana en hora de Lima (distintos días con salidas).
SELECT COUNT(DISTINCT (fecha AT TIME ZONE 'America/Lima')::date) AS dias_operativos
FROM public.inventario_movimientos
WHERE tipo = 'Salida' AND id_compra IS NULL
  AND fecha >= :inicio AND fecha < :fin;


-- =====================================================================
-- KPI-01 · Margen operativo de caja sobre cobros
-- Formula: ((Σ cobros - Σ egresos) / Σ cobros) × 100
-- Filtros: ventana [inicio, fin); tipo Venta=cobro, Gasto=egreso
-- CODIFICACION: Venta (+) ; Gasto (-). NULL si no hay cobros.
-- =====================================================================
WITH actual AS (
    SELECT
        COALESCE(SUM(CASE WHEN tipo = 'Venta' THEN monto ELSE 0 END), 0) AS cobros,
        COALESCE(SUM(CASE WHEN tipo = 'Gasto' THEN monto ELSE 0 END), 0)  AS egresos
    FROM public.transacciones_caja
    WHERE fecha >= :inicio AND fecha < :fin
),
previa AS (
    SELECT
        COALESCE(SUM(CASE WHEN tipo = 'Venta' THEN monto ELSE 0 END), 0) AS cobros,
        COALESCE(SUM(CASE WHEN tipo = 'Gasto' THEN monto ELSE 0 END), 0)  AS egresos
    FROM public.transacciones_caja
    WHERE fecha >= :prev_inicio AND fecha < :prev_fin
)
SELECT
    a.cobros,
    a.egresos,
    a.cobros - a.egresos                           AS neto,
    CASE WHEN a.cobros > 0
         THEN round((a.cobros - a.egresos) * 100.0 / a.cobros, 2)
         ELSE NULL                                 -- denominador 0 -> "Sin datos"
    END                                            AS margen_pct,
    p.cobros                                       AS cobros_anterior,
    p.egresos                                      AS egresos_anterior,
    CASE WHEN a.cobros > 0 AND p.cobros > 0 AND p.cobros <> a.cobros
         THEN round((a.cobros - p.cobros) * 100.0 / p.cobros, 2)
         ELSE NULL
    END                                            AS variacion_pct
FROM actual a CROSS JOIN previa p;


-- =====================================================================
-- KPI-02 · Variación porcentual de ventas netas
-- Formula: ((Ventas_P - Ventas_P-1) / Ventas_P-1) × 100
-- Ventas netas = SUM(monto) de transacciones Venta (no existen devoluciones).
-- NULL si el periodo anterior vale 0 -> "Sin datos".
-- =====================================================================
WITH actual AS (
    SELECT COALESCE(SUM(monto), 0) AS ventas
    FROM public.transacciones_caja
    WHERE tipo = 'Venta' AND fecha >= :inicio AND fecha < :fin
),
previa AS (
    SELECT COALESCE(SUM(monto), 0) AS ventas
    FROM public.transacciones_caja
    WHERE tipo = 'Venta' AND fecha >= :prev_inicio AND fecha < :prev_fin
)
SELECT
    a.ventas AS ventas_actuales,
    p.ventas AS ventas_anterior,
    CASE WHEN p.ventas > 0
         THEN round((a.ventas - p.ventas) * 100.0 / p.ventas, 2)
         ELSE NULL
    END      AS variacion_pct
FROM actual a CROSS JOIN previa p;


-- =====================================================================
-- KPI-03 · Días estimados de cobertura de inventario
-- Formula: stock utilizable / consumo diario promedio
-- Consumo diario promedio = SUM(cantidad_base) de salidas por consumo/venta
--   (motivo_grupo='Consumo') dividido entre días operativos de la ventana.
-- Stock utilizable = stock actual (no existen reservado/no apto).
-- Aviso de cobertura baja: cobertura <= 7 días.
-- =====================================================================
WITH consumo AS (
    SELECT
        s.id_producto,
        SUM(ABS(s.cantidad))                                  AS total_consumo,
        COUNT(DISTINCT (s.fecha AT TIME ZONE 'America/Lima')::date) AS dias_operativos
    FROM vw_kpi_salidas s
    WHERE s.motivo_grupo = 'Consumo'
      AND s.fecha >= :inicio AND s.fecha < :corte
    GROUP BY s.id_producto
)
SELECT
    p.id_producto,
    p.nombre,
    p.unidad_medida,
    p.stock,
    c.total_consumo,
    c.dias_operativos,
    GREATEST(c.total_consumo / NULLIF(c.dias_operativos, 0), 0) AS consumo_diario,
    CASE WHEN c.total_consumo > 0 AND c.dias_operativos > 0
         THEN round(p.stock / (c.total_consumo / c.dias_operativos), 2)
         ELSE NULL                                              -- sin consumo -> sin cobertura
    END                                                         AS cobertura_dias
FROM public.productos p
LEFT JOIN consumo c ON c.id_producto = p.id_producto
WHERE p.estado = true AND p.fecha_registro < :corte
ORDER BY cobertura_dias ASC NULLS LAST
LIMIT :top_n;   -- top-N productos con menor cobertura (gráfico / detalle)


-- =====================================================================
-- KPI-04 · Tasa de merma valorizada
-- Formula: (costo merma / costo total salidas operativas) × 100
-- Numerador  = SUM(ABS(cantidad) × costo) con motivo_grupo='Merma'
-- Denominador= SUM(ABS(cantidad) × costo) de consumo/venta + merma
--              (todas las salidas operativas; excluye reversas id_compra).
-- NULL si no hay salidas o si hay salidas sin costo conocido.
-- =====================================================================
WITH salidas AS (
    SELECT motivo_grupo, ABS(cantidad) AS cantidad_base, costo, fecha
    FROM vw_kpi_salidas
    WHERE fecha >= :inicio AND fecha < :fin
)
SELECT
    motivo_grupo,
    SUM(cantidad_base * costo) AS monto
FROM salidas
GROUP BY motivo_grupo;  -- filas: Consumo / Merma (composición del KPI)

-- Valor final del KPI-04 (agregado):
WITH costeo AS (
    SELECT
        COALESCE(SUM(CASE WHEN motivo_grupo = 'Merma' THEN ABS(s.cantidad) ELSE 0 END * s.costo), 0) AS costo_merma,
        COALESCE(SUM(ABS(s.cantidad) * s.costo), 0)                                                 AS costo_salidas,
        COUNT(*) FILTER (WHERE s.costo IS NULL)                                                     AS salidas_sin_costo
    FROM vw_kpi_salidas s
    WHERE s.fecha >= :inicio AND s.fecha < :fin
)
SELECT
    costo_merma,
    costo_salidas,
    CASE WHEN costo_salidas > 0 AND salidas_sin_costo = 0
         THEN round(costo_merma * 100.0 / costo_salidas, 2)
         ELSE NULL
    END AS merma_pct
FROM costeo;


-- =====================================================================
-- KPI-05 · Ratio de costo laboral sobre ventas netas
-- Formula: (costo laboral imputable al periodo / ventas netas) × 100
-- Costo laboral = Σ por empleado, por semana salarial (lunes a domingo):
--   tarifa = sueldo semanal vigente al inicio de la semana (desde <= semana)
--   costo  = max(tarifa - descuentos de esa semana, 0) × proporción del
--            periodo que cae en esa semana.
-- Los adelantos NO son costo laboral (no se suman).
-- NULL si no hay ventas, no hay sueldos vigentes o hay empleados activos
-- sin sueldo configurado.
-- =====================================================================
WITH empleados AS (
    SELECT id_usuario
    FROM public.usuarios
    WHERE estado = true AND id_rol <> 1
),
semanas AS (
    -- Lunes de cada semana con solape en [inicio, fin), convertidos a UTC.
    SELECT
        s.semana :: date AS semana,
        y.semana_inicio + '7 days'::interval AS semana_fin
    FROM generate_series(
        date_trunc('week', (:inicio AT TIME ZONE 'America/Lima')::date),
        date_trunc('week', (:fin   AT TIME ZONE 'America/Lima')::date),
        interval '7 days'
    ) AS s(semana)
    ... -- (implementación del prorrateo por día en FASE 2; referencia aquí)
)
-- Referencia de agregados por semana (sin el prorrateo por día):
SELECT
    s.id_usuario,
    sw.desde                    AS sueldo_vigente_desde,
    s.monto,
    COALESCE(d.descuento, 0)    AS descuento_semanal
FROM public.sueldos_semanales s
JOIN (SELECT id_usuario, MAX(desde) AS desde
      FROM public.sueldos_semanales
      WHERE desde < (:fin AT TIME ZONE 'America/Lima')::date
      GROUP BY id_usuario) sw ON sw.id_usuario = s.id_usuario AND sw.desde = s.desde
LEFT JOIN (
    SELECT id_usuario, semana, SUM(monto) AS descuento
    FROM public.descuentos_semanales
    WHERE anulado = false
      AND semana >= (:inicio AT TIME ZONE 'America/Lima')::date
      AND semana <= (:fin   AT TIME ZONE 'America/Lima')::date
    GROUP BY id_usuario, semana
) d ON d.id_usuario = s.id_usuario AND d.semana = sw.desde;

-- Ventas netas del periodo (mismo filtro que KPI-02):
SELECT COALESCE(SUM(monto), 0) AS ventas_netas
FROM public.transacciones_caja
WHERE tipo = 'Venta' AND fecha >= :inicio AND fecha < :fin;


-- =====================================================================
-- KPI-06 · Margen bruto estimado sobre ventas netas
-- Formula: ((ventas netas - costo de productos vendidos) / ventas netas) × 100
-- Costo vendido estimado = Σ(ABS(cantidad) × costo) de salidas por
-- consumo/venta (motivo_grupo='Consumo') en el periodo.
-- NULL si ventas = 0 o hay salidas consideradas sin costo.
-- =====================================================================
WITH ventas AS (
    SELECT COALESCE(SUM(monto), 0) AS ventas
    FROM public.transacciones_caja
    WHERE tipo = 'Venta' AND fecha >= :inicio AND fecha < :fin
),
costeo AS (
    SELECT
        COALESCE(SUM(ABS(s.cantidad) * s.costo), 0) AS costo_vendido,
        COUNT(*) FILTER (WHERE s.costo IS NULL)     AS salidas_sin_costo,
        COUNT(*)                                    AS salidas_consideradas
    FROM vw_kpi_salidas s
    WHERE s.motivo_grupo = 'Consumo'
      AND s.fecha >= :inicio AND s.fecha < :fin
)
SELECT
    v.ventas,
    c.costo_vendido,
    c.salidas_consideradas,
    c.salidas_sin_costo,
    CASE WHEN v.ventas > 0 AND c.salidas_sin_costo = 0
         THEN round((v.ventas - c.costo_vendido) * 100.0 / v.ventas, 2)
         ELSE NULL
    END AS margen_bruto_pct
FROM ventas v CROSS JOIN costeo c;


-- =====================================================================
-- KPI-07 · Diferencia relativa de cierre de caja
-- Formula: ((efectivo contado - saldo esperado) / saldo esperado) × 100
-- Saldo esperado = monto_inicial + Σ entradas en efectivo − Σ salidas en
--   efectivo dentro de la sesión (apertura → fecha_cierre, acotada por la
--   siguiente apertura y por el fin del periodo).
-- Contado = cierre.efectivo_contado (nuevo, migrado).
-- Si saldo esperado = 0 → la diferencia relativa es NULL (se reporta la
--   diferencia absoluta). Negativo = faltante; positivo = sobrante.
-- =====================================================================
SELECT
    c.id_cierre,
    c.fecha                                                      AS apertura,
    c.fecha_cierre,
    c.monto_inicial,
    c.efectivo_contado,
    LEAST(COALESCE(c.fecha_cierre, now()),
          COALESCE(LEAD(c.fecha) OVER (ORDER BY c.fecha), c.fecha_cierre),
          :fin)                                                  AS fin_sesion,
    (SELECT COALESCE(SUM(CASE WHEN t.tipo = 'Venta' THEN t.monto
                              WHEN t.tipo = 'Gasto' THEN -t.monto
                              ELSE 0 END), 0)
     FROM public.transacciones_caja t
     WHERE t.metodo_pago = 'Efectivo'
       AND t.fecha >= c.fecha
       AND t.fecha < LEAST(COALESCE(c.fecha_cierre, now()),
                           COALESCE(LEAD(c.fecha) OVER (ORDER BY c.fecha), c.fecha_cierre),
                           :fin)
    )                                                           AS flujo_efectivo
FROM public.cierres_caja c
WHERE c.estado = 'cerrada'
  AND COALESCE(c.fecha_cierre, c.fecha) >= :inicio
  AND COALESCE(c.fecha_cierre, c.fecha) < :fin
ORDER BY c.fecha;

-- Valor agregado del KPI-07 (promedio simple de la diferencia relativa por
-- cierre con conteo; NULL si no hay cierres con efetivo_contado):
WITH sesiones AS (
    SELECT
        c.id_cierre, c.fecha, c.fecha_cierre, c.monto_inicial, c.efectivo_contado,
        LEAST(COALESCE(c.fecha_cierre, now()),
              COALESCE(LEAD(c.fecha) OVER (ORDER BY c.fecha), c.fecha_cierre),
              :fin) AS fin_sesion
    FROM public.cierres_caja c
    WHERE c.estado = 'cerrada'
      AND COALESCE(c.fecha_cierre, c.fecha) >= :inicio
      AND COALESCE(c.fecha_cierre, c.fecha) < :fin
),
ventas_efectivo AS (
    SELECT t.id_usuario, t.monto, t.tipo, t.fecha
    FROM public.transacciones_caja t
    WHERE t.metodo_pago = 'Efectivo'
)
SELECT
    COUNT(*) FILTER (WHERE s.efectivo_contado IS NOT NULL)                AS cierres_con_conteo,
    COUNT(*) FILTER (WHERE s.efectivo_contado IS NULL)                AS cierres_sin_conteo,
    COALESCE(ROUND(SUM(s.efectivo_contado - (s.monto_inicial + e.flujo))::numeric, 2), 0) AS diferencia_total,
    ROUND(AVG(
        CASE WHEN (s.monto_inicial + e.flujo) <> 0
             THEN (s.efectivo_contado - (s.monto_inicial + e.flujo))
                  * 100.0 / (s.monto_inicial + e.flujo)
             ELSE NULL
        END
    ), 2)                                                             AS diferencia_relativa_pct
FROM sesiones s
LEFT JOIN LATERAL (
    SELECT COALESCE(SUM(CASE WHEN t.tipo = 'Venta' THEN t.monto
                             WHEN t.tipo = 'Gasto' THEN -t.monto
                             ELSE 0 END), 0) AS flujo
    FROM ventas_efectivo t
    WHERE t.fecha >= s.fecha AND t.fecha < s.fin_sesion
) e ON true
WHERE s.efectivo_contado IS NOT NULL;


-- =====================================================================
-- KPI-08 · Índice de capital inmovilizado en inventario
-- Formula: (valor stock sin movimiento / valor total inventario utilizable) × 100
-- Sin movimiento = sin salidas por consumo/venta en la ventana (30 días).
-- Valor = stock utilizable × costo actual (productos activos con stock > 0).
-- NULL si el valor total es 0 o hay productos activos con stock sin costo.
-- =====================================================================
WITH en_movimiento AS (
    SELECT DISTINCT s.id_producto
    FROM vw_kpi_salidas s
    WHERE s.motivo_grupo = 'Consumo'
      AND s.fecha >= :corte - (:ventana_dias::int * interval '1 day')
      AND s.fecha < :corte
),
productos AS (
    SELECT
        p.id_producto, p.nombre, p.stock, p.costo, p.estado,
        em.id_producto IS NOT NULL AS tiene_movimiento
    FROM public.productos p
    LEFT JOIN en_movimiento em ON em.id_producto = p.id_producto
    WHERE p.estado = true AND p.stock > 0 AND p.fecha_registro < :corte
)
SELECT
    COUNT(*)                                                            AS productos_con_stock,
    COUNT(*) FILTER (WHERE NOT tiene_movimiento)                        AS productos_sin_movimiento,
    COUNT(*) FILTER (WHERE costo IS NULL)                               AS productos_sin_costo,
    COALESCE(ROUND(SUM(p.stock * p.costo)::numeric, 2), 0)              AS valor_total,
    COALESCE(ROUND(SUM(CASE WHEN NOT p.tiene_movimiento
                            THEN p.stock * p.costo ELSE 0 END)::numeric, 2), 0) AS valor_inmovilizado,
    CASE WHEN SUM(p.stock * p.costo) > 0 AND COUNT(*) FILTER (WHERE p.costo IS NULL) = 0
         THEN ROUND(SUM(CASE WHEN NOT p.tiene_movimiento
                             THEN p.stock * p.costo ELSE 0 END)
                    * 100.0 / SUM(p.stock * p.costo), 2)
         ELSE NULL
    END                                                                 AS inmovilizado_pct
FROM productos p;


-- =====================================================================
-- SERIES AUXILIARES PARA GRÁFICOS
-- =====================================================================

-- KPI-01/02/06 · Tendencia por bucket (ingresos/egresos/neto) dentro del
-- periodo. Bucket = día para mes, semana para año (reutiliza el criterio
-- de api/fechas.py -> periodo_financiero).
SELECT
    CASE WHEN :granularidad = 'semana'
         THEN to_char(date_trunc('week', fecha AT TIME ZONE 'America/Lima'), 'YYYY-IW')
         ELSE to_char((fecha AT TIME ZONE 'America/Lima')::date, 'YYYY-MM-DD')
    END                                                       AS etiqueta,
    COALESCE(SUM(CASE WHEN tipo = 'Venta' THEN monto ELSE 0 END), 0) AS ingresos,
    COALESCE(SUM(CASE WHEN tipo = 'Gasto'  THEN monto ELSE 0 END), 0) AS egresos,
    COALESCE(SUM(CASE WHEN tipo = 'Venta' THEN monto ELSE -monto END), 0) AS neto
FROM public.transacciones_caja
WHERE fecha >= :inicio AND fecha < :fin
GROUP BY 1
ORDER BY 1;

-- KPI-04 · Evolución de la tasa de merma por periodo (misma ventana/agregado):
WITH por_bucket AS (
    SELECT
        to_char(date_trunc('month', s.fecha AT TIME ZONE 'America/Lima'), 'YYYY-MM') AS periodo,
        COALESCE(SUM(CASE WHEN s.motivo_grupo = 'Merma' THEN ABS(s.cantidad) * s.costo ELSE 0 END), 0) AS costo_merma,
        COALESCE(SUM(ABS(s.cantidad) * s.costo), 0) AS costo_salidas
    FROM vw_kpi_salidas s
    WHERE s.fecha >= :inicio AND s.fecha < :fin
    GROUP BY 1
)
SELECT periodo, costo_merma, costo_salidas,
       CASE WHEN costo_salidas > 0 THEN round(costo_merma * 100.0 / costo_salidas, 2)
            ELSE NULL END AS merma_pct
FROM por_bucket ORDER BY 1;

-- KPI-07 · Evolución por sesión de caja (efectivo esperado vs contado):
SELECT
    c.id_cierre,
    c.fecha                                                  AS apertura,
    c.fecha_cierre,
    c.monto_inicial,
    c.efectivo_contado,
    (monto_inicial + e.flujo)                                AS esperado,
    c.efectivo_contado - (monto_inicial + e.flujo)           AS diferencia_abs,
    CASE WHEN (monto_inicial + e.flujo) <> 0
         THEN round((c.efectivo_contado - (monto_inicial + e.flujo))
                    * 100.0 / (monto_inicial + e.flujo), 2)
         ELSE NULL
    END                                                      AS diferencia_pct
FROM public.cierres_caja c
LEFT JOIN LATERAL (
    SELECT COALESCE(SUM(CASE WHEN t.tipo = 'Venta' THEN t.monto
                             WHEN t.tipo = 'Gasto' THEN -t.monto
                             ELSE 0 END), 0) AS flujo
    FROM public.transacciones_caja t
    WHERE t.metodo_pago = 'Efectivo'
      AND t.fecha >= c.fecha
      AND t.fecha < LEAST(COALESCE(c.fecha_cierre, now()),
                          COALESCE(LEAD(c.fecha) OVER (ORDER BY c.fecha), c.fecha_cierre),
                          :fin)
) e ON true
WHERE c.estado = 'cerrada'
  AND COALESCE(c.fecha_cierre, c.fecha) >= :inicio
  AND COALESCE(c.fecha_cierre, c.fecha) < :fin
ORDER BY c.fecha;

-- KPI-08 · Desglose por categoría (valor total vs inmovilizado):
SELECT
    c.nombre                    AS categoria,
    COUNT(*)                    AS productos,
    COALESCE(ROUND(SUM(p.stock * p.costo)::numeric, 2), 0)                     AS valor,
    COALESCE(ROUND(SUM(CASE WHEN NOT em.tiene THEN p.stock * p.costo
                            ELSE 0 END)::numeric, 2), 0)                       AS valor_inmovilizado
FROM public.productos p
JOIN public.categorias c ON c.id_categoria = p.id_categoria
LEFT JOIN LATERAL (
    SELECT true AS tiene FROM vw_kpi_salidas s
    WHERE s.id_producto = p.id_producto AND s.motivo_grupo = 'Consumo'
      AND s.fecha >= :corte - (:ventana_dias::int * interval '1 day') AND s.fecha < :corte
    LIMIT 1
) em ON true
WHERE p.estado = true AND p.stock > 0 AND p.fecha_registro < :corte
GROUP BY 1 ORDER BY valor DESC;