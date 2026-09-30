"""Genera la migración para alinear importes y cantidades con los modelos.

Sin ``--aplicar`` solo imprime SQL. La aplicación requiere una cuenta de
migraciones con permiso ALTER; la cuenta normal del backend debe ser rechazada.
"""
import argparse
from pathlib import Path


def sql_precision():
    ruta = Path(__file__).resolve().parent / 'migraciones' / '2026_09_21_02_precision_numerica.sql'
    return ruta.read_text(encoding='utf-8').strip()


def aplicar():
    from app import app
    from bd import db
    with app.app_context():
        raw = db.engine.raw_connection()
        try:
            with raw.cursor() as cursor:
                cursor.execute("SET LOCAL lock_timeout='10s'")
                cursor.execute("SET LOCAL statement_timeout='60s'")
                sentencias = sql_precision().removeprefix('BEGIN;\n').removesuffix('\nCOMMIT;')
                cursor.execute(sentencias, prepare=False)
                while cursor.nextset():
                    pass
                cursor.execute("""
                    SELECT count(*) FROM information_schema.columns
                    WHERE table_schema='public' AND
                      (table_name,column_name) IN (
                        ('usuario_perfiles','salario'), ('pagos_empleados','monto'),
                        ('cierres_caja','monto_inicial'), ('solicitudes_insumos','cantidad'),
                        ('inventario_movimientos','stock_anterior'),
                        ('inventario_movimientos','stock_posterior'))
                      AND data_type='numeric' AND numeric_precision=12
                      AND numeric_scale=CASE WHEN column_name IN ('cantidad','stock_anterior','stock_posterior') THEN 3 ELSE 2 END
                """)
                if cursor.fetchone()[0] != 6:
                    raise RuntimeError('La verificación de precisión no fue satisfactoria')
            raw.commit()
            print('Precisión numérica aplicada y verificada.')
        except Exception as error:
            raw.rollback()
            codigo = getattr(error, 'sqlstate', None) or getattr(getattr(error, 'orig', None), 'sqlstate', None)
            print('Migración revertida: ' + type(error).__name__ + (f' ({codigo})' if codigo else ''))
            raise SystemExit(1)
        finally:
            raw.close()
            db.engine.dispose()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--aplicar', action='store_true')
    args = parser.parse_args()
    aplicar() if args.aplicar else print(sql_precision())
