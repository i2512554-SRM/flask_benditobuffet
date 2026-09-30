"""Histórico ficticio para la vista local; no permite usar una base persistente."""
from datetime import date, datetime, time, timedelta, timezone
from random import Random

from api.fechas import LIMA, ahora
from models import db, CierreCaja, TransaccionCaja


def cargar_historico():
    if db.engine.url.drivername != 'sqlite' or db.engine.url.database not in (None, '', ':memory:'):
        raise RuntimeError('Los datos de demostración solo se cargan en SQLite en memoria.')
    marca = 'DEMO histórico de gráficos'
    if TransaccionCaja.query.filter_by(descripcion=marca).first():
        return 0
    rng = Random(20250401)
    dia = date(2025, 4, 1)
    ultimo = ahora().astimezone(LIMA).date() - timedelta(days=1)
    cantidad = 0
    while dia <= ultimo:
        # Lunes sin atención: permite comprobar días sin movimientos.
        if dia.weekday() != 0:
            def instante(hora):
                return datetime.combine(dia, time(hora), LIMA).astimezone(timezone.utc)

            tendencia = ((dia.year - 2025) * 12 + dia.month - 4) * 12
            temporada = 100 if dia.month in (7, 12) else 0
            fin_semana = 130 if dia.weekday() >= 5 else 0
            ventas = 420 + tendencia + temporada + fin_semana + rng.randrange(-90, 130)
            efectivo = round(ventas * .5, 2)
            yape = round(ventas * .3, 2)
            gastos = round(ventas * rng.uniform(.25, .48), 2)
            for hora, monto, metodo in [(12, efectivo, 'Efectivo'), (14, yape, 'Yape'),
                                         (19, round(ventas - efectivo - yape, 2), 'Tarjeta')]:
                db.session.add(TransaccionCaja(id_usuario=2, tipo='Venta', monto=monto,
                    fecha=instante(hora), metodo_pago=metodo, descripcion=marca))
            db.session.add(TransaccionCaja(id_usuario=2, tipo='Gasto', monto=gastos,
                fecha=instante(16), metodo_pago='Efectivo', descripcion=marca))
            db.session.add(CierreCaja(id_usuario=2, monto_inicial=100,
                total_ventas=ventas, total_gastos=gastos, fecha=instante(9),
                fecha_cierre=instante(22), estado='cerrada', observaciones=marca))
            cantidad += 4
        dia += timedelta(days=1)
    db.session.commit()
    return cantidad
