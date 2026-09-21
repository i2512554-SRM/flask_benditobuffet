"""Genera o aplica la migración PostgreSQL para evitar movimientos duplicados.

Sin ``--aplicar`` no conecta ni modifica la base. La aplicación requiere una
cuenta administrativa de migraciones; el usuario normal del backend no debe poder
alterar tablas.

Uso: python -m automatizacion_caja.preparar_idempotencia [--aplicar]
"""
import argparse
from pathlib import Path


def sql_idempotencia():
    ruta = Path(__file__).resolve().parent / 'migraciones' / '2026_09_21_01_idempotencia.sql'
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
                # El SQL impreso incluye BEGIN/COMMIT para el editor; aquí la
                # confirmación se hace solo después de verificar el esquema.
                sentencias = sql_idempotencia().removeprefix('BEGIN;\n').removesuffix('\nCOMMIT;')
                cursor.execute(sentencias, prepare=False)
                while cursor.nextset():
                    pass
                cursor.execute("""
                    SELECT count(*) FROM information_schema.columns
                    WHERE table_schema='public' AND column_name='clave_operacion'
                      AND table_name IN ('transacciones_caja','inventario_movimientos','compras_inventario','pagos_empleados')
                """)
                if cursor.fetchone()[0] != 4:
                    raise RuntimeError('La verificación de columnas no fue satisfactoria')
                cursor.execute("""
                    SELECT count(*) FROM pg_index i
                    JOIN pg_class indice ON indice.oid = i.indexrelid
                    WHERE indice.relname IN (
                        'ux_transacciones_caja_operacion', 'ux_inventario_movimientos_operacion',
                        'ux_compras_inventario_operacion', 'ux_pagos_empleados_operacion'
                    ) AND i.indisunique AND i.indisvalid
                """)
                if cursor.fetchone()[0] != 4:
                    raise RuntimeError('La verificación de índices únicos no fue satisfactoria')
            raw.commit()
            print('Migración aplicada y verificada.')
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
    argumentos = parser.parse_args()
    if argumentos.aplicar:
        aplicar()
    else:
        print(sql_idempotencia())
