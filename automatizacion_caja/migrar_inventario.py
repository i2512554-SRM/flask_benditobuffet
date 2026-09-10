#!/usr/bin/env python3
"""
Migra el esquema de inventario para el cambio "mejorar-modulo-productos-inventario":
  1. Agrega columnas a `productos`: unidad_medida, descripcion, estado.
  2. Agrega columnas a `inventario_movimientos`: stock_anterior, stock_posterior, motivo.
  3. Relena stock_anterior/stock_posterior de movimientos existentes (acumulado por producto).
  4. Deduplica productos con el mismo nombre (ignorando mayusculas/minusculas) reasignando
     referencias y sumando stock. Idempotente y seguro (ADD COLUMN IF NOT EXISTS).
  5. Relaja el check `chk_movimiento_cantidad` de `cantidad > 0` a `cantidad <> 0` para
     permitir salidas/ajustes con cantidad negativa (historial con signo).

Uso: python automatizacion_caja/migrar_inventario.py
"""

import os
import sys

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from dotenv import load_dotenv

load_dotenv(os.path.join(_PROJECT_ROOT, ".env"))

from sqlalchemy import text

from bd import db
import app as app_module  # noqa: F401  (inicializa app/BD)


def columnas_total(nombres, esquema, tabla):
    rows = db.session.execute(text(
        f"SELECT column_name FROM information_schema.columns WHERE table_schema = :e AND table_name = :t"
    ), {"e": esquema, "t": tabla}).fetchall()
    return set(r[0] for r in rows)


def agregar_columnas():
    print("== 1. Columnas nuevas ==")
    for tabla, col, tipo, nulll in [
        ("productos", "unidad_medida", "VARCHAR(10)", False),
        ("productos", "descripcion", "VARCHAR(255)", True),
        ("productos", "estado", "BOOLEAN", False),
        ("inventario_movimientos", "stock_anterior", "NUMERIC", True),
        ("inventario_movimientos", "stock_posterior", "NUMERIC", True),
        ("inventario_movimientos", "motivo", "VARCHAR(255)", True),
    ]:
        existing = db.session.execute(text(
            "SELECT column_name FROM information_schema.columns WHERE table_name = :t"
        ), {"t": tabla}).fetchall()
        nombres = {r[0] for r in existing}
        if col in nombres:
            print(f"  - {tabla}.{col} ya existe")
            continue
        null_clause = "NOT NULL" if not nulll else ""
        default = ""
        if tabla == "productos" and col in ("unidad_medida", "estado"):
            default = " DEFAULT 'Un'" if col == "unidad_medida" else " DEFAULT TRUE"
        db.session.execute(text(f"ALTER TABLE {tabla} ADD COLUMN {col} {tipo} {null_clause}{default}"))
        print(f"  + {tabla}.{col} agregada")
    db.session.commit()


def relenar_stocks():
    print("== 2. Relenado de stock_anterior / stock_posterior ==")
    movs = db.session.execute(text(
        "SELECT id_movimiento, id_producto, tipo, cantidad FROM inventario_movimientos ORDER BY id_producto, fecha, id_movimiento"
    )).fetchall()
    acumulado = {}
    cambios = 0
    for m_id, p_id, tipo, cant in movs:
        cant = float(cant)
        anterior = acumulado.get(p_id, 0.0)
        posterior = anterior + (cant if str(tipo).strip().lower() == "entrada" else -cant)
        db.session.execute(text(
            "UPDATE inventario_movimientos SET stock_anterior = :a, stock_posterior = :p WHERE id_movimiento = :m"
        ), {"a": anterior, "p": posterior, "m": m_id})
        acumulado[p_id] = posterior
        cambios += 1
    for p_id, total in acumulado.items():
        db.session.execute(text(
            "UPDATE productos SET stock = :s WHERE id_producto = :p AND stock IS DISTINCT FROM :s"
        ), {"s": total, "p": p_id})
    db.session.commit()
    print(f"  - {cambios} movimientos relenados")


def relajar_check_cantidad():
    print("== 3. Check de cantidad con signo ==")
    existe = db.session.execute(text(
        "SELECT 1 FROM pg_constraint WHERE conname = 'chk_movimiento_cantidad'"
    )).scalar()
    if not existe:
        print("  - Sin restricciones previas")
    else:
        db.session.execute(text("ALTER TABLE inventario_movimientos DROP CONSTRAINT chk_movimiento_cantidad"))
        print("  - chk_movimiento_cantidad (cantidad > 0) eliminada")
    db.session.execute(text(
        "ALTER TABLE inventario_movimientos ADD CONSTRAINT chk_movimiento_cantidad CHECK (cantidad <> 0)"
    ))
    db.session.commit()
    print("  + chk_movimiento_cantidad recreada como cantidad <> 0 (cambios negativos)")



def deduplicar():
    print("== 3. Deduplicacion de productos (case-insensitive) ==")
    dups = db.session.execute(text(
        "SELECT lower(trim(nombre)) AS key, count(*) AS n FROM productos GROUP BY lower(trim(nombre)) HAVING count(*) > 1"
    )).fetchall()
    if not dups:
        print("  - Sin duplicados")
        return
    for key, _ in dups:
        filas = db.session.execute(text(
            "SELECT id_producto, nombre, stock FROM productos WHERE lower(trim(nombre)) = :k ORDER BY id_producto"
        ), {"k": key}).fetchall()
        maestro_id, maestro_nombre, _ = filas[0]
        for dup_id, dup_nombre, dup_stock in filas[1:]:
            db.session.execute(text(
                "UPDATE inventario_movimientos SET id_producto = :m WHERE id_producto = :d"
            ), {"m": maestro_id, "d": dup_id})
            db.session.execute(text(
                "UPDATE detalle_compras_inventario SET id_producto = :m WHERE id_producto = :d"
            ), {"m": maestro_id, "d": dup_id})
            db.session.execute(text(
                "UPDATE solicitudes_insumos SET id_producto = :m WHERE id_producto = :d"
            ), {"m": maestro_id, "d": dup_id})
            db.session.execute(text(
                "UPDATE productos SET stock = stock + :s, fecha_edicion = now() WHERE id_producto = :m"
            ), {"s": float(dup_stock or 0), "m": maestro_id})
            db.session.execute(text("DELETE FROM productos WHERE id_producto = :d"), {"d": dup_id})
            print(f"  - '{dup_nombre}' (id {dup_id}) fusionado en '{maestro_nombre}' (id {maestro_id})")
    db.session.commit()


def verificar():
    print("== 4. Verificacion ==")
    for t in ["productos", "inventario_movimientos"]:
        filas = db.session.execute(text(
            "SELECT column_name FROM information_schema.columns WHERE table_name = :t"
        ), {"t": t}).fetchall()
        print(f"  {t}: {', '.join(sorted(r[0] for r in filas))}")
    n_dups = db.session.execute(text(
        "SELECT count(*) FROM (SELECT lower(trim(nombre)) k FROM productos GROUP BY lower(trim(nombre)) HAVING count(*) > 1) x"
    )).scalar()
    n_null = db.session.execute(text(
        "SELECT count(*) FROM inventario_movimientos WHERE stock_anterior IS NULL OR stock_posterior IS NULL"
    )).scalar()
    n_prod = db.session.execute(text("SELECT count(*) FROM productos")).scalar()
    n_mov = db.session.execute(text("SELECT count(*) FROM inventario_movimientos")).scalar()
    print(f"  duplicados: {n_dups} | movimientos con stock NULL: {n_null} | productos: {n_prod} | movimientos: {n_mov}")


if __name__ == "__main__":
    with app_module.app.app_context():
        agregar_columnas()
        relajar_check_cantidad()
        deduplicar()
        relenar_stocks()
        verificar()
    print("Migracion completada.")