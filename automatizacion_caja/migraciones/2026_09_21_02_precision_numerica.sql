BEGIN;
SET LOCAL search_path = public;

DO $$
DECLARE incompatibles BIGINT;
BEGIN
    SELECT sum(n) INTO incompatibles FROM (
        SELECT count(*) n FROM usuario_perfiles WHERE salario IS NOT NULL AND
            CASE WHEN salario::text IN ('NaN','Infinity','-Infinity') THEN true
                 ELSE abs(salario) >= 10000000000 OR salario <> round(salario, 2) END
        UNION ALL SELECT count(*) FROM pagos_empleados WHERE
            CASE WHEN monto::text IN ('NaN','Infinity','-Infinity') THEN true
                 ELSE abs(monto) >= 10000000000 OR monto <> round(monto, 2) END
        UNION ALL SELECT count(*) FROM cierres_caja WHERE
            CASE WHEN monto_inicial::text IN ('NaN','Infinity','-Infinity') THEN true
                 ELSE abs(monto_inicial::numeric) >= 10000000000 OR monto_inicial::numeric <> round(monto_inicial::numeric, 2) END
        UNION ALL SELECT count(*) FROM solicitudes_insumos WHERE
            CASE WHEN cantidad::text IN ('NaN','Infinity','-Infinity') THEN true
                 ELSE abs(cantidad::numeric) >= 1000000000 OR cantidad::numeric <> round(cantidad::numeric, 3) END
        UNION ALL SELECT count(*) FROM inventario_movimientos WHERE
            (stock_anterior IS NOT NULL AND (abs(stock_anterior) >= 1000000000 OR stock_anterior <> round(stock_anterior, 3))) OR
            (stock_posterior IS NOT NULL AND (abs(stock_posterior) >= 1000000000 OR stock_posterior <> round(stock_posterior, 3)))
    ) datos;
    IF incompatibles > 0 THEN
        RAISE EXCEPTION 'Hay % valores que requieren revisión manual antes de convertir tipos', incompatibles;
    END IF;
END $$;

ALTER TABLE public.usuario_perfiles ALTER COLUMN salario TYPE NUMERIC(12,2) USING salario::numeric(12,2);
ALTER TABLE public.pagos_empleados ALTER COLUMN monto TYPE NUMERIC(12,2) USING monto::numeric(12,2);
ALTER TABLE public.cierres_caja ALTER COLUMN monto_inicial TYPE NUMERIC(12,2) USING monto_inicial::numeric(12,2);
ALTER TABLE public.solicitudes_insumos ALTER COLUMN cantidad TYPE NUMERIC(12,3) USING cantidad::numeric(12,3);
ALTER TABLE public.inventario_movimientos ALTER COLUMN stock_anterior TYPE NUMERIC(12,3) USING stock_anterior::numeric(12,3);
ALTER TABLE public.inventario_movimientos ALTER COLUMN stock_posterior TYPE NUMERIC(12,3) USING stock_posterior::numeric(12,3);

COMMIT;
