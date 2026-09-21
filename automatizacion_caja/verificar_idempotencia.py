"""Comprueba, sin modificar datos, si la migración de idempotencia está aplicada."""
from sqlalchemy import text
from app import app
from bd import db


def verificar():
    esperadas = {
        'transacciones_caja', 'inventario_movimientos', 'compras_inventario', 'pagos_empleados'
    }
    filas = db.session.execute(text("""
        SELECT table_name
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND column_name = 'clave_operacion'
          AND table_name IN ('transacciones_caja', 'inventario_movimientos', 'compras_inventario', 'pagos_empleados')
    """)).scalars().all()
    presentes = set(filas)
    nombres = {f'ux_{tabla}_operacion' for tabla in esperadas}
    indices = set(db.session.execute(text("""
        SELECT indice.relname FROM pg_index i
        JOIN pg_class indice ON indice.oid=i.indexrelid
        WHERE indice.relname IN ('ux_transacciones_caja_operacion',
            'ux_inventario_movimientos_operacion', 'ux_compras_inventario_operacion',
            'ux_pagos_empleados_operacion')
          AND i.indisunique AND i.indisvalid
    """)).scalars())
    return {'completa': presentes == esperadas and indices == nombres,
            'faltantes': sorted(esperadas - presentes),
            'indices_faltantes': sorted(nombres - indices)}


if __name__ == '__main__':
    with app.app_context():
        resultado = verificar()
        print('completa=' + str(resultado['completa']).lower())
        print('faltantes=' + ','.join(resultado['faltantes']))
        print('indices_faltantes=' + ','.join(resultado['indices_faltantes']))
