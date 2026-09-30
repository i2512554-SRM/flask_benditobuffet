BEGIN;
SET LOCAL search_path = public;

ALTER TABLE public.transacciones_caja
    ADD COLUMN IF NOT EXISTS clave_operacion VARCHAR(36);
ALTER TABLE public.inventario_movimientos
    ADD COLUMN IF NOT EXISTS clave_operacion VARCHAR(36);
ALTER TABLE public.compras_inventario
    ADD COLUMN IF NOT EXISTS clave_operacion VARCHAR(36);
ALTER TABLE public.pagos_empleados
    ADD COLUMN IF NOT EXISTS clave_operacion VARCHAR(36);

CREATE UNIQUE INDEX IF NOT EXISTS ux_transacciones_caja_operacion
    ON public.transacciones_caja (clave_operacion)
    WHERE clave_operacion IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS ux_inventario_movimientos_operacion
    ON public.inventario_movimientos (clave_operacion)
    WHERE clave_operacion IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS ux_compras_inventario_operacion
    ON public.compras_inventario (clave_operacion)
    WHERE clave_operacion IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS ux_pagos_empleados_operacion
    ON public.pagos_empleados (clave_operacion)
    WHERE clave_operacion IS NOT NULL;

COMMIT;
