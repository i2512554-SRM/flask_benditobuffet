BEGIN;
SET LOCAL search_path = public;

ALTER TABLE public.cierres_caja
    ADD COLUMN IF NOT EXISTS efectivo_contado NUMERIC(12, 2);

COMMENT ON COLUMN public.cierres_caja.efectivo_contado IS
    'Efectivo físico contado al cerrar la caja (KPI-07). NULL si no se registró.';

COMMIT;