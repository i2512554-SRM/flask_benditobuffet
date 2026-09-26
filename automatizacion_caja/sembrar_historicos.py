"""Sembrador idempotente de datos históricos de demostración para gráficos y KPIs.

Usa la BD de producción con las variables DB_USER/DB_PASSWORD/DB_HOST del entorno.
Sin argumentos: solo planifica (no toca la BD). Con --aplicar: inserta los datos.
Los registros se marcan con '[demo histórico]' y no se duplican en re-ejecuciones.
"""
import calendar
import os
import random
import sys
from datetime import date, datetime, time, timedelta, timezone

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from dotenv import load_dotenv

load_dotenv(os.path.join(_PROJECT_ROOT, ".env"))

from flask import Flask

from bd import db, init_db
from models import (Categoria, InventarioMovimiento, PagoPersonal, Producto,
                    TransaccionCaja, CierreCaja, Usuario)
from api.fechas import LIMA

MARCA = '[demo histórico]'
DESDE = date(2025, 4, 1)
MONTO_INICIAL = 100


def _app():
    app = Flask(__name__)
    init_db(app)
    return app


def _local(y, m, d, h, mi):
    return datetime.combine(date(y, m, d), time(h, mi), LIMA).astimezone(timezone.utc)


def _plan():
    n_dias = (3, 8, 12, 17, 22, 26)
    dias_gastos = (5, 19)
    hoy = datetime.now(LIMA).date()
    mes = date(DESDE.year, DESDE.month, 1)
    indice = 0
    total_meses = 0
    while mes <= hoy:
        total_meses += 1
        mes = (mes.replace(day=28) + timedelta(days=4)).replace(day=1)
    return total_meses, n_dias, dias_gastos


def _seleccionar_contexto():
    admin = Usuario.query.filter_by(id_rol=1, estado=True).order_by(Usuario.id_usuario).first()
    if admin is None:
        raise RuntimeError('No hay un usuario administrador para asignar los movimientos.')
    empleado = Usuario.query.filter_by(id_rol=4, estado=True).order_by(Usuario.id_usuario).first() or admin
    categoria = Categoria.query.filter(Categoria.nombre.ilike('%insumo%')).first() or Categoria.query.first()
    if categoria is None:
        categoria = Categoria(nombre='Insumos', fecha_creacion=datetime.now(timezone.utc))
        db.session.add(categoria)
        db.session.flush()
    ahora = datetime.now(timezone.utc)
    producto_demo = Producto.query.filter(Producto.nombre.like('%(demo)')).first()
    productos = []
    if producto_demo is None:
        for nombre, precio, costo, stock in (('Arroz extra (demo)', 5.0, 4.2, 40.0),
                                             ('Pollo entero (demo)', 16.0, 13.0, 25.0)):
            p = Producto(nombre=nombre, precio=precio, costo=costo, stock=stock,
                         unidad_medida='Kg', descripcion=MARCA, estado=True,
                         id_categoria=categoria.id_categoria, fecha_registro=ahora, fecha_edicion=ahora)
            db.session.add(p)
            productos.append(p)
        db.session.flush()
    else:
        productos = Producto.query.filter(Producto.nombre.like('%(demo)')).all()
    return admin, empleado, productos


def _ya_sembrado():
    return TransaccionCaja.query.filter(TransaccionCaja.descripcion.like(MARCA + '%')).first() is not None


def sembrar():
    total_meses, n_dias, dias_gastos = _plan()
    if _ya_sembrado():
        print(f'Ya existen datos con marca {MARCA!r}. Nada que insertar.')
        return 0
    admin, empleado, productos = _seleccionar_contexto()

    rng = random.Random(2025)
    contadores = {'transacciones': 0, 'cierres': 0, 'pagos': 0, 'movimientos': 0}
    hoy = datetime.now(LIMA).date()
    mes = date(DESDE.year, DESDE.month, 1)
    indice = 0

    while mes <= hoy:
        y, m = mes.year, mes.month
        ultimo = calendar.monthrange(y, m)[1]
        base_ventas = 1300 + indice * 90
        total_v = 0.0
        total_g = 0.0

        for i, d in enumerate(n_dias):
            monto = round(base_ventas / len(n_dias) * rng.uniform(0.85, 1.15), 2)
            total_v += monto
            db.session.add(TransaccionCaja(
                id_usuario=admin.id_usuario, tipo='Venta', monto=monto,
                metodo_pago=rng.choice(['Efectivo', 'Yape', 'Tarjeta']),
                descripcion=MARCA, fecha=_local(y, m, d, 9 + (i % 3) * 4, 15)))
        for d in dias_gastos:
            monto = round(rng.uniform(60, 200), 2)
            total_g += monto
            db.session.add(TransaccionCaja(
                id_usuario=admin.id_usuario, tipo='Gasto', monto=monto,
                metodo_pago='Efectivo', descripcion=MARCA, fecha=_local(y, m, d, 18, 30)))

        db.session.add(CierreCaja(
            id_usuario=admin.id_usuario, monto_inicial=MONTO_INICIAL,
            total_ventas=round(total_v, 2), total_gastos=round(total_g, 2),
            observaciones=MARCA, estado='cerrada',
            fecha=_local(y, m, 1, 8, 0), fecha_cierre=_local(y, m, ultimo, 18, 30)))

        if indice >= total_meses - 12:
            db.session.add(PagoPersonal(
                id_usuario=empleado.id_usuario, monto=round(320 + rng.uniform(0, 220), 2),
                fecha=date(y, m, ultimo), tipo='Salario semanal', estado='Completado',
                descripcion=MARCA))
            contadores['pagos'] += 1

        if indice >= total_meses - 4:
            for k in range(3):
                producto = productos[indice % len(productos)]
                cantidad = round(rng.uniform(0.5, 3.0), 2)
                motivo = 'Merma por caducidad' if k == 2 else 'Preparación de platos'
                db.session.add(InventarioMovimiento(
                    id_producto=producto.id_producto, id_usuario=empleado.id_usuario,
                    tipo='Salida', cantidad=-cantidad, motivo=motivo,
                    observacion=MARCA, fecha=_local(y, m, n_dias[k], 11, 45)))
            contadores['movimientos'] += 3

        contadores['transacciones'] += len(n_dias) + len(dias_gastos)
        contadores['cierres'] += 1

        indice += 1
        mes = (mes.replace(day=28) + timedelta(days=4)).replace(day=1)

    db.session.commit()
    print('Datos históricos insertados:')
    for clave in ('transacciones', 'cierres', 'pagos', 'movimientos'):
        print(f'  - {clave}: {contadores[clave]}')
    return indice


def main():
    aplicar = '--aplicar' in sys.argv
    if _plan()[0] <= 0:
        print('No hay meses a sembrar.')
        return
    if aplicar:
        with _app().app_context():
            total = sembrar()
            if total:
                print(f'Listo. {total} meses cubiertos desde {DESDE.isoformat()}.')
    else:
        total = _plan()[0]
        print(f'Modo lectura: se insertarían aprox. {total} meses desde {DESDE.isoformat()} '
              f'(transacciones, 1 cierre/mes, pagos de los ultimos 12 meses, salidas de los ultimos 4).')
        print('Ejecuta con --aplicar para insertar.')


if __name__ == '__main__':
    main()