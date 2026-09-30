"""Genera datos de ejemplo coherentes (6 meses de un buffet) para demostraciones e indicadores.

Solo para bases de demostración: se niega a correr si la base parece tener uso real.
Sin argumentos: muestra el plan sin escribir nada.
Aplicar: --aplicar --confirmo-datos-de-ejemplo
Reemplazar los datos de ejemplo anteriores: agregar --reemplazar
Todo lo generado lleva la marca '[demo histórico]'.
"""
import os
import random
import sys
from datetime import date, datetime, time, timedelta, timezone

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from dotenv import load_dotenv

load_dotenv(os.path.join(_PROJECT_ROOT, '.env'))

from sqlalchemy import or_

from bd import db
from models import (Categoria, CierreCaja, InventarioMovimiento, PagoEmpleado, PagoPersonal, Producto,
                    SueldoSemanal, TransaccionCaja, Usuario)
from api.fechas import LIMA
from api.roles import ADMIN, CAJERA, COCINA, TRABAJADOR

MARCA = '[demo histórico]'
DIAS_HISTORIA = 182
SEMANAS_DE_PAGOS = 8
MAX_TRANSACCIONES_REALES = 50
REGISTRO_SUELDOS_DEMO = datetime(2000, 1, 1, tzinfo=timezone.utc)
MONTO_INICIAL = 200
SUELDO_POR_ROL = {CAJERA: 350, COCINA: 450, TRABAJADOR: 300}
VENTA_BASE_POR_DIA = {1: 1700, 2: 1700, 3: 1750, 4: 2200, 5: 2900, 6: 3100}
METODOS_VENTA = (('Efectivo', 40), ('Yape', 30), ('Tarjeta', 20), ('Plin', 10))
INSUMOS = (
    ('Pollo entero (demo)', 'Kg', 13.0, 21.6, 65.0, True, False),
    ('Arroz extra (demo)', 'Kg', 4.2, 14.4, 180.0, False, True),
    ('Papa amarilla (demo)', 'Kg', 2.5, 10.8, 160.0, True, False),
    ('Cebolla roja (demo)', 'Kg', 2.8, 5.4, 80.0, True, False),
    ('Tomate (demo)', 'Kg', 4.2, 5.4, 25.0, True, False),
    ('Aceite vegetal (demo)', 'Lt', 9.8, 2.7, 55.0, False, False),
    ('Fideos tallarín (demo)', 'Kg', 3.6, 3.6, 70.0, False, False),
    ('Carne de res (demo)', 'Kg', 18.0, 7.2, 100.0, True, False),
    ('Sal (demo)', 'Kg', 1.2, 0.5, 20.0, False, False),
)


def _instante(dia, hora, minuto=0):
    return datetime.combine(dia, time(hora, minuto), LIMA).astimezone(timezone.utc)


def _dia_lima(valor):
    valor = valor if valor.tzinfo else valor.replace(tzinfo=timezone.utc)
    return valor.astimezone(LIMA).date()


def _con_marca(texto):
    return f'{texto} {MARCA}'


def _es_demo(columna):
    return columna.like(f'%{MARCA}%')


def _sueldos_demo():
    return SueldoSemanal.query.filter(or_(
        SueldoSemanal.fecha == REGISTRO_SUELDOS_DEMO,
        (SueldoSemanal.desde == date(2024, 12, 30)) & (SueldoSemanal.monto == 300),
    ))


def diagnostico():
    reales = TransaccionCaja.query.filter(or_(TransaccionCaja.descripcion.is_(None), ~_es_demo(TransaccionCaja.descripcion))).all()
    cierres_reales = CierreCaja.query.filter(or_(CierreCaja.observaciones.is_(None), ~_es_demo(CierreCaja.observaciones))).all()
    dias_ocupados = {_dia_lima(t.fecha) for t in reales} | {_dia_lima(c.fecha) for c in cierres_reales}
    return {
        'transacciones_reales': len(reales),
        'dias_ocupados': dias_ocupados,
        'demo_existente': TransaccionCaja.query.filter(_es_demo(TransaccionCaja.descripcion)).count(),
    }


def borrar_demo():
    borrados = {}
    borrados['pagos_empleados'] = PagoEmpleado.query.filter(_es_demo(PagoEmpleado.descripcion)).delete(synchronize_session=False)
    borrados['pagos_personal'] = PagoPersonal.query.filter(_es_demo(PagoPersonal.descripcion)).delete(synchronize_session=False)
    borrados['transacciones'] = TransaccionCaja.query.filter(_es_demo(TransaccionCaja.descripcion)).delete(synchronize_session=False)
    borrados['cierres'] = CierreCaja.query.filter(_es_demo(CierreCaja.observaciones)).delete(synchronize_session=False)
    borrados['movimientos'] = InventarioMovimiento.query.filter(or_(
        _es_demo(InventarioMovimiento.observacion), _es_demo(InventarioMovimiento.motivo))).delete(synchronize_session=False)
    borrados['sueldos'] = _sueldos_demo().delete(synchronize_session=False)
    db.session.flush()
    return borrados


def _repartir(total, partes, rng):
    pesos = [rng.uniform(0.6, 1.4) for _ in range(partes)]
    suma = sum(pesos)
    montos = [max(15.0, round(total * p / suma * 2) / 2) for p in pesos]
    return montos


def _productos_demo(ahora):
    categoria = (Categoria.query.filter(Categoria.nombre.ilike('%ingrediente%')).first()
                 or Categoria.query.filter(Categoria.nombre.ilike('%insumo%')).first()
                 or Categoria.query.first())
    if categoria is None:
        categoria = Categoria(nombre='Ingredientes', fecha_creacion=ahora)
        db.session.add(categoria)
        db.session.flush()
    productos = []
    for nombre, unidad, costo, _, stock, _, _ in INSUMOS:
        producto = Producto.query.filter_by(nombre=nombre).first()
        if producto is None:
            producto = Producto(nombre=nombre, precio=0, id_categoria=categoria.id_categoria,
                                fecha_registro=ahora - timedelta(days=DIAS_HISTORIA + 7))
            db.session.add(producto)
        producto.unidad_medida = unidad
        producto.costo = costo
        producto.stock = stock
        producto.estado = True
        producto.descripcion = MARCA
        producto.fecha_edicion = ahora
        productos.append(producto)
    db.session.flush()
    return productos


def sembrar(hoy, semilla=2026):
    rng = random.Random(semilla)
    ahora = datetime.now(timezone.utc)
    info = diagnostico()
    admin = Usuario.query.filter_by(id_rol=ADMIN, estado=True).order_by(Usuario.id_usuario).first()
    if admin is None:
        raise RuntimeError('No hay un administrador activo para registrar los datos.')
    empleados = Usuario.query.filter(Usuario.estado.is_(True), Usuario.id_rol != ADMIN).order_by(Usuario.id_usuario).all()
    cajeras = [e for e in empleados if e.id_rol == CAJERA] or [admin]
    cocina = [e for e in empleados if e.id_rol == COCINA] or [admin]
    productos = _productos_demo(ahora)

    inicio = hoy - timedelta(days=DIAS_HISTORIA)
    lunes_inicio = inicio - timedelta(days=inicio.weekday())
    filas = []
    contador = {'dias': 0, 'transacciones': 0, 'cierres': 0, 'movimientos': 0, 'pagos': 0, 'sueldos': 0}

    for empleado in empleados:
        filas.append(SueldoSemanal(id_usuario=empleado.id_usuario, desde=lunes_inicio,
                                   monto=SUELDO_POR_ROL.get(empleado.id_rol, 300),
                                   registrado_por=admin.id_usuario, fecha=REGISTRO_SUELDOS_DEMO))
        contador['sueldos'] += 1

    dia = inicio
    semana = 0
    while dia < hoy:
        if dia.weekday() == 0:
            semana += 1
        if dia.weekday() == 0 or dia in info['dias_ocupados']:
            dia += timedelta(days=1)
            continue
        cajera = cajeras[dia.toordinal() % len(cajeras)]
        total_dia = VENTA_BASE_POR_DIA[dia.weekday()] * (1 + 0.004 * semana) * rng.uniform(0.88, 1.12)
        ventas = _repartir(total_dia, max(8, round(total_dia / 180)), rng)
        efectivo = float(MONTO_INICIAL)
        total_ventas = total_gastos = 0.0
        for indice, monto in enumerate(sorted(ventas)):
            metodo = rng.choices([m for m, _ in METODOS_VENTA], [p for _, p in METODOS_VENTA])[0]
            filas.append(TransaccionCaja(id_usuario=cajera.id_usuario, tipo='Venta', monto=monto, metodo_pago=metodo,
                                         categoria='Buffet', descripcion=_con_marca('Consumo en salón'),
                                         fecha=_instante(dia, 12 + (indice * 10) // len(ventas), rng.randint(0, 59))))
            total_ventas += monto
            efectivo += monto if metodo == 'Efectivo' else 0
        gastos = [('Compras menores de mercado', round(rng.uniform(80, 220), 2), 'Efectivo', 'Insumos')]
        if dia.day % 4 == 0:
            gastos.append(('Balón de gas', round(rng.uniform(60, 90), 2), 'Efectivo', 'Servicios'))
        if dia.weekday() == 1:
            gastos.append(('Pago a proveedor de carnes', round(rng.uniform(1200, 1600), 2), 'Transferencia', 'Proveedores'))
        if dia.weekday() == 4:
            gastos.append(('Pago a proveedor de verduras', round(rng.uniform(500, 700), 2), 'Transferencia', 'Proveedores'))
        if dia.day == 5:
            gastos.append(('Luz y agua', round(rng.uniform(450, 650), 2), 'Transferencia', 'Servicios'))
            gastos.append(('Alquiler del local', 3500.0, 'Transferencia', 'Alquiler'))
        for concepto, monto, metodo, categoria in gastos:
            filas.append(TransaccionCaja(id_usuario=cajera.id_usuario, tipo='Gasto', monto=monto, metodo_pago=metodo,
                                         categoria=categoria, descripcion=_con_marca(concepto),
                                         fecha=_instante(dia, 21, rng.randint(0, 50))))
            total_gastos += monto
            efectivo -= monto if metodo == 'Efectivo' else 0
        sorteo = rng.random()
        diferencia = 0.0 if sorteo < 0.8 else round(rng.uniform(-3, 3), 2) if sorteo < 0.92 else -round(rng.uniform(5, 20), 2)
        filas.append(CierreCaja(id_usuario=cajera.id_usuario, monto_inicial=MONTO_INICIAL,
                                total_ventas=round(total_ventas, 2), total_gastos=round(total_gastos, 2),
                                efectivo_contado=round(efectivo + diferencia, 2), observaciones=MARCA, estado='cerrada',
                                fecha=_instante(dia, 11, 30), fecha_cierre=_instante(dia, 22, 40)))
        contador['transacciones'] += len(ventas) + len(gastos)
        contador['cierres'] += 1

        responsable = cocina[dia.toordinal() % len(cocina)]
        dias_para_hoy = (hoy - dia).days
        for producto, (_, _, _, consumo, _, perecible, sin_movimiento) in zip(productos, INSUMOS):
            if sin_movimiento and dias_para_hoy <= 45:
                continue
            cantidad = round(consumo * rng.uniform(0.85, 1.15), 3)
            filas.append(InventarioMovimiento(id_producto=producto.id_producto, id_usuario=responsable.id_usuario,
                                              tipo='Salida', cantidad=-cantidad, motivo='Preparación del buffet',
                                              observacion=MARCA, fecha=_instante(dia, 10, rng.randint(0, 59))))
            contador['movimientos'] += 1
            if perecible and dia.weekday() == 6 and rng.random() < 0.7:
                merma = round(consumo * rng.uniform(0.15, 0.35), 3)
                filas.append(InventarioMovimiento(id_producto=producto.id_producto, id_usuario=responsable.id_usuario,
                                                  tipo='Salida', cantidad=-merma,
                                                  motivo=rng.choice(['Merma por vencimiento', 'Producto dañado']),
                                                  observacion=MARCA, fecha=_instante(dia, 22, 0)))
                contador['movimientos'] += 1
            if dia.weekday() == 1 and not sin_movimiento:
                filas.append(InventarioMovimiento(id_producto=producto.id_producto, id_usuario=admin.id_usuario,
                                                  tipo='Entrada', cantidad=round(consumo * 6, 3),
                                                  motivo='Reposición semanal', observacion=MARCA,
                                                  fecha=_instante(dia, 9, 0)))
                contador['movimientos'] += 1
        contador['dias'] += 1
        dia += timedelta(days=1)

    lunes_actual = hoy - timedelta(days=hoy.weekday())
    pagos = []
    for semanas_atras in range(1, SEMANAS_DE_PAGOS + 1):
        lunes = lunes_actual - timedelta(weeks=semanas_atras)
        for empleado in empleados:
            monto = SUELDO_POR_ROL.get(empleado.id_rol, 300)
            pagos.append((empleado, lunes, monto, PagoPersonal(
                id_usuario=empleado.id_usuario, monto=monto, fecha=lunes + timedelta(days=6), tipo='Salario semanal',
                estado='Pagado', descripcion=_con_marca('Salario semanal:'))))
    db.session.add_all([espejo for *_, espejo in pagos])
    db.session.flush()
    for empleado, lunes, monto, espejo in pagos:
        filas.append(PagoEmpleado(id_usuario=empleado.id_usuario, monto=monto, estado='Pagado', tipo='Salario semanal',
                                  fecha_pago=datetime.combine(lunes + timedelta(days=6), time(0, 0), LIMA).astimezone(timezone.utc),
                                  semana=lunes, id_pago_personal=espejo.id_pago, descripcion=_con_marca('Salario semanal:')))
        contador['pagos'] += 1

    db.session.add_all(filas)
    db.session.flush()
    return contador


def main():
    from flask import Flask
    from bd import init_db

    aplicar = '--aplicar' in sys.argv
    confirmado = '--confirmo-datos-de-ejemplo' in sys.argv
    reemplazar = '--reemplazar' in sys.argv
    app = Flask(__name__)
    init_db(app)
    with app.app_context():
        info = diagnostico()
        hoy = datetime.now(LIMA).date()
        print(f'Transacciones sin marca de ejemplo: {info["transacciones_reales"]} | con marca: {info["demo_existente"]}')
        print(f'Días reservados para datos manuales (no se generan datos ahí): {len(info["dias_ocupados"])}')
        if info['transacciones_reales'] > MAX_TRANSACCIONES_REALES:
            sys.exit(f'La base tiene más de {MAX_TRANSACCIONES_REALES} transacciones reales: '
                     'este script es solo para bases de demostración. No se hizo ningún cambio.')
        if not (aplicar and confirmado):
            print(f'Modo plan: se generarían {DIAS_HISTORIA} días de historia hasta {hoy - timedelta(days=1)}.')
            print('Para aplicar: --aplicar --confirmo-datos-de-ejemplo [--reemplazar]')
            return
        if info['demo_existente'] and not reemplazar:
            sys.exit('Ya existen datos de ejemplo. Agrega --reemplazar para regenerarlos. No se hizo ningún cambio.')
        try:
            if reemplazar:
                print('Borrados:', borrar_demo())
            resultado = sembrar(hoy)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        print('Generados:', resultado)


if __name__ == '__main__':
    main()
