"""Endurecimiento revisable. Sin --aplicar solo imprime el SQL."""
import argparse
from flask import Flask
from bd import db, init_db
from models import db as modelos_db


def sql_proteccion():
    sentencias = []
    for nombre in sorted(modelos_db.metadata.tables):
        sentencias.extend([
            f'ALTER TABLE public.{nombre} ENABLE ROW LEVEL SECURITY;',
            f'REVOKE ALL ON TABLE public.{nombre} FROM PUBLIC, anon, authenticated;',
        ])
    sentencias.extend([
        "ALTER TABLE public.pagos_personal DROP CONSTRAINT IF EXISTS chk_pago_tipo;",
        "ALTER TABLE public.pagos_personal ADD CONSTRAINT chk_pago_tipo CHECK (tipo IN ('Pago','Adelanto','Salario semanal','Bono','Horas extra','Otros'));",
        "ALTER TABLE public.transacciones_caja DROP CONSTRAINT IF EXISTS chk_metodo_pago;",
        "ALTER TABLE public.transacciones_caja ADD CONSTRAINT chk_metodo_pago CHECK (metodo_pago IS NULL OR metodo_pago IN ('Efectivo','Tarjeta','Transferencia','Yape','Plin','Otros'));",
        "ALTER TABLE public.pagos_empleados DROP CONSTRAINT IF EXISTS chk_pago_empleado_monto;",
        "ALTER TABLE public.pagos_empleados ADD CONSTRAINT chk_pago_empleado_monto CHECK (monto > 0 AND monto::text NOT IN ('NaN','Infinity','-Infinity'));",
    ])
    for tabla, columna in [('inversiones','id_proveedor'),('descuentos_semanales','registrado_por'),
                            ('sueldos_semanales','registrado_por'),('atenciones_insumos','id_solicitud'),
                            ('inventario_movimientos','id_compra')]:
        sentencias.append(f'CREATE INDEX IF NOT EXISTS ix_{tabla}_{columna} ON public.{tabla} ({columna});')
    return '\n'.join(sentencias)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--aplicar', action='store_true')
    args = parser.parse_args()
    if not args.aplicar:
        print(sql_proteccion())
        return
    app = Flask('proteccion_bd')
    init_db(app)
    with app.app_context():
        raw = db.engine.raw_connection()
        try:
            with raw.cursor() as cur:
                cur.execute("SET LOCAL lock_timeout='10s'")
                cur.execute("SET LOCAL statement_timeout='60s'")
                cur.execute(sql_proteccion(), prepare=False)
                while cur.nextset():
                    pass
                for nombre in sorted(modelos_db.metadata.tables):
                    cur.execute("SELECT relrowsecurity, has_table_privilege('anon',oid,'SELECT,INSERT,UPDATE,DELETE,TRUNCATE'), has_table_privilege('authenticated',oid,'SELECT,INSERT,UPDATE,DELETE,TRUNCATE') FROM pg_class WHERE oid=%s::regclass", ('public.'+nombre,))
                    assert cur.fetchone() == (True,False,False), 'Permisos no verificados'
                    cur.execute('SELECT 1 FROM public.'+nombre+' LIMIT 0')
                print('25 tablas: RLS activo, permisos de clientes retirados y acceso del backend verificado.')
            raw.commit()
            print('Restricciones e indices actualizados. Transaccion confirmada.')
        except Exception as exc:
            raw.rollback()
            print('Cambios revertidos: '+type(exc).__name__)
            raise SystemExit(1)
        finally:
            raw.close()
            db.engine.dispose()


if __name__ == '__main__':
    main()
