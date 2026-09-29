-- Metas editables de los indicadores (fase 2).
-- Cada fila reemplaza los límites sugeridos de un KPI; sin filas, el sistema usa los sugeridos.
-- Ejecutar en el editor SQL de Supabase como dueño de las tablas, antes de reiniciar Flask.

BEGIN;
SET LOCAL search_path = public;

CREATE TABLE IF NOT EXISTS public.metas_indicadores (
    codigo VARCHAR(10) PRIMARY KEY,
    limite_atencion NUMERIC(10, 2) NOT NULL,
    limite_revisar NUMERIC(10, 2) NOT NULL,
    id_usuario BIGINT REFERENCES public.usuarios (id_usuario) ON DELETE SET NULL,
    actualizado_en TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT ck_metas_indicadores_codigo CHECK (codigo ~ '^KPI-[0-9]{2}$'),
    CONSTRAINT ck_metas_indicadores_limites CHECK (limite_atencion <> limite_revisar)
);

COMMENT ON TABLE public.metas_indicadores IS
    'Límites ajustados por el administrador para el semáforo de cada indicador (KPI).';

ALTER TABLE public.metas_indicadores ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON TABLE public.metas_indicadores FROM anon, authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.metas_indicadores TO buffet_backend;
DROP POLICY IF EXISTS buffet_backend_acceso ON public.metas_indicadores;
CREATE POLICY buffet_backend_acceso ON public.metas_indicadores
    FOR ALL TO buffet_backend USING (true) WITH CHECK (true);

COMMIT;

-- Verificación (debe devolver: t, f, t):
-- SELECT c.relrowsecurity,
--        has_table_privilege('anon', c.oid, 'SELECT'),
--        has_table_privilege('buffet_backend', c.oid, 'INSERT')
-- FROM pg_class c WHERE c.oid = 'public.metas_indicadores'::regclass;
