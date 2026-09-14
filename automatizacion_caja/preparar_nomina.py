"""Genera SQL revisable para PostgreSQL; no conecta ni aplica cambios.

Uso: python -m automatizacion_caja.preparar_nomina
Revisar/aplicar en la base de pruebas y registrar con el flujo de migraciones
del entorno antes de desplegar la funcionalidad semanal.
"""
from sqlalchemy.schema import CreateTable, CreateIndex
from sqlalchemy.dialects import postgresql
from models import SueldoSemanal, DescuentoSemanal, SesionUsuario, AtencionInsumo


def sql_nomina():
    dialecto = postgresql.dialect()
    sentencias = ['BEGIN;', 'SET LOCAL search_path = public;']
    for modelo in (SueldoSemanal, DescuentoSemanal, SesionUsuario, AtencionInsumo):
        tabla = modelo.__table__
        sentencias.append(str(CreateTable(tabla, if_not_exists=True).compile(dialect=dialecto)) + ';')
        for indice in sorted(tabla.indexes, key=lambda i: i.name):
            sentencias.append(str(CreateIndex(indice, if_not_exists=True).compile(dialect=dialecto)) + ';')
        sentencias.append(f'ALTER TABLE public.{tabla.name} ENABLE ROW LEVEL SECURITY;')
        # La aplicación usa su backend Flask; no se da acceso directo al cliente.
        sentencias.append(f'REVOKE ALL ON TABLE public.{tabla.name} FROM PUBLIC;')
        sentencias.append(f'''DO $$ BEGIN
    IF EXISTS (SELECT FROM pg_roles WHERE rolname = 'anon') THEN
        REVOKE ALL ON TABLE public.{tabla.name} FROM anon;
    END IF;
    IF EXISTS (SELECT FROM pg_roles WHERE rolname = 'authenticated') THEN
        REVOKE ALL ON TABLE public.{tabla.name} FROM authenticated;
    END IF;
END $$;''')
    sentencias.extend([
        'ALTER TABLE public.pagos_empleados ADD COLUMN IF NOT EXISTS tipo VARCHAR(100);',
        'ALTER TABLE public.pagos_empleados ADD COLUMN IF NOT EXISTS semana DATE;',
        'ALTER TABLE public.pagos_empleados ADD COLUMN IF NOT EXISTS id_pago_personal BIGINT REFERENCES public.pagos_personal(id_pago);',
        'CREATE UNIQUE INDEX IF NOT EXISTS ux_pago_empleado_personal ON public.pagos_empleados(id_pago_personal);',
        'ALTER TABLE public.descuentos_semanales ADD COLUMN IF NOT EXISTS clave_operacion VARCHAR(36);',
        'CREATE UNIQUE INDEX IF NOT EXISTS ux_descuento_operacion ON public.descuentos_semanales(clave_operacion);',
        # Solo vincular registros antiguos cuando la correspondencia es uno a uno.
        '''WITH candidatos AS (
    SELECT pe.id_pago, min(pp.id_pago) AS id_personal
    FROM public.pagos_empleados pe JOIN public.pagos_personal pp
      ON pe.id_usuario = pp.id_usuario AND pe.monto = pp.monto AND pe.estado = pp.estado
      AND pp.fecha = (pe.fecha_pago AT TIME ZONE 'America/Lima')::date
      AND coalesce(pe.descripcion, '') = coalesce(pp.descripcion, '')
    WHERE pe.id_pago_personal IS NULL
    GROUP BY pe.id_pago HAVING count(*) = 1
), unicos AS (
    SELECT c.* FROM candidatos c
    WHERE (SELECT count(*) FROM candidatos x WHERE x.id_personal = c.id_personal) = 1
      AND NOT EXISTS (SELECT 1 FROM public.pagos_empleados p WHERE p.id_pago_personal = c.id_personal)
)
UPDATE public.pagos_empleados pe
SET id_pago_personal = u.id_personal,
    tipo = CASE WHEN pp.tipo IN ('Salario semanal', 'Bono', 'Horas extra', 'Otros') THEN pp.tipo ELSE pe.tipo END,
    semana = coalesce(pe.semana, date_trunc('week', pe.fecha_pago AT TIME ZONE 'America/Lima')::date)
FROM unicos u, public.pagos_personal pp
WHERE pe.id_pago = u.id_pago AND pp.id_pago = u.id_personal;''',
        '''INSERT INTO public.atenciones_insumos (id_compra, id_solicitud)
SELECT c.id_compra, s.id_solicitud FROM public.compras_inventario c
JOIN public.solicitudes_insumos s ON s.respuesta = 'Stock repuesto con la compra ' || c.codigo
WHERE s.estado = 'Atendida' AND c.estado = 'Completada'
ON CONFLICT (id_compra, id_solicitud) DO NOTHING;''',
        'COMMIT;'])
    return '\n'.join(sentencias)


if __name__ == '__main__':
    print(sql_nomina())
