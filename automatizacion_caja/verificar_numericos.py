"""Lista tipos de importes y cantidades reales sin leer valores comerciales."""
from sqlalchemy import text
from app import app
from bd import db


COLUMNAS = {
    'usuario_perfiles': ('salario',),
    'pagos_empleados': ('monto',),
    'pagos_personal': ('monto',),
    'adelantos': ('monto',),
    'transacciones_caja': ('monto',),
    'cierres_caja': ('monto_inicial', 'total_ventas', 'total_gastos', 'neto'),
    'productos': ('precio', 'stock'),
    'inversiones': ('monto',),
    'compras_inventario': ('total_compra',),
    'detalle_compras_inventario': ('cantidad', 'precio_unitario', 'subtotal'),
    'inventario_movimientos': ('cantidad', 'stock_anterior', 'stock_posterior'),
    'solicitudes_insumos': ('cantidad',),
}


def verificar():
    condiciones = ' OR '.join(
        f"(table_name='{tabla}' AND column_name IN ({','.join(repr(c) for c in columnas)}))"
        for tabla, columnas in COLUMNAS.items()
    )
    return db.session.execute(text(f"""
        SELECT table_name, column_name, data_type, numeric_precision, numeric_scale
        FROM information_schema.columns
        WHERE table_schema='public' AND ({condiciones})
        ORDER BY table_name, ordinal_position
    """)).mappings().all()


def contar_incompatibles():
    return db.session.scalar(text("""
        SELECT sum(n) FROM (
            SELECT count(*) n FROM usuario_perfiles WHERE salario IS NOT NULL AND
                CASE WHEN salario::text IN ('NaN','Infinity','-Infinity') THEN true
                     ELSE abs(salario) >= 10000000000 OR salario <> round(salario, 2) END
            UNION ALL SELECT count(*) FROM pagos_empleados WHERE
                CASE WHEN monto::text IN ('NaN','Infinity','-Infinity') THEN true
                     ELSE abs(monto) >= 10000000000 OR monto <> round(monto, 2) END
            UNION ALL SELECT count(*) FROM cierres_caja WHERE
                CASE WHEN monto_inicial::text IN ('NaN','Infinity','-Infinity') THEN true
                     ELSE abs(monto_inicial::numeric) >= 10000000000 OR monto_inicial::numeric <> round(monto_inicial::numeric, 2) END
            UNION ALL SELECT count(*) FROM solicitudes_insumos WHERE
                CASE WHEN cantidad::text IN ('NaN','Infinity','-Infinity') THEN true
                     ELSE abs(cantidad::numeric) >= 1000000000 OR cantidad::numeric <> round(cantidad::numeric, 3) END
            UNION ALL SELECT count(*) FROM inventario_movimientos WHERE
                (stock_anterior IS NOT NULL AND (abs(stock_anterior) >= 1000000000 OR stock_anterior <> round(stock_anterior, 3))) OR
                (stock_posterior IS NOT NULL AND (abs(stock_posterior) >= 1000000000 OR stock_posterior <> round(stock_posterior, 3)))
        ) datos
    """))


if __name__ == '__main__':
    with app.app_context():
        for fila in verificar():
            precision = '' if fila['numeric_precision'] is None else f"({fila['numeric_precision']},{fila['numeric_scale']})"
            print(f"{fila['table_name']}.{fila['column_name']}={fila['data_type']}{precision}")
        print('incompatibles=' + str(contar_incompatibles()))
