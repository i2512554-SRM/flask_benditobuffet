BEGIN;
SET LOCAL search_path = public;

ALTER TABLE public.inversiones
    ADD COLUMN IF NOT EXISTS estado VARCHAR(20) NOT NULL DEFAULT 'Registrada',
    ADD COLUMN IF NOT EXISTS fecha_anulacion TIMESTAMPTZ;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_inversion_estado') THEN
        ALTER TABLE public.inversiones
            ADD CONSTRAINT chk_inversion_estado CHECK (estado IN ('Registrada', 'Anulada'));
    END IF;
END $$;

COMMENT ON COLUMN public.inversiones.estado IS
    'Registrada o Anulada. Las inversiones no se borran: se anulan para conservar el historial.';

COMMIT;
