-- Bloquea el acceso público (API de Supabase) a 4 tablas creadas fuera del sistema.
-- Ninguna es usada por la app: el usuario buffet_backend no tiene permiso de lectura sobre ellas.
-- Activar RLS sin políticas deniega todo a anon y authenticated; postgres y service_role no se ven afectados.
-- No borra datos. Ejecutar en el editor SQL de Supabase como dueño de las tablas.

BEGIN;
SET LOCAL search_path = public;

ALTER TABLE public.conceptos_pago ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.metodos_pago ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sesiones_caja ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.transaccion_pagos ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE public.conceptos_pago, public.metodos_pago, public.sesiones_caja, public.transaccion_pagos
    FROM anon, authenticated;

COMMIT;

-- Verificación (debe devolver 0 filas):
-- SELECT c.relname FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
-- WHERE n.nspname = 'public' AND c.relkind IN ('r', 'p')
--   AND (NOT c.relrowsecurity OR has_table_privilege('anon', c.oid, 'SELECT'));
