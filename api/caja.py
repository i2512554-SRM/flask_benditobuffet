from datetime import date, datetime
from decimal import Decimal
from functools import wraps
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import text
from models import db, TransaccionCaja, CierreCaja, Usuario
from schemas.caja import transacciones_schema, cierre_schema, transaccion_schema
from api.fechas import ahora, limites_dia, periodo_financiero, utc, LIMA
from api.validaciones import numero

caja_bp = Blueprint('caja', __name__)
METODOS = ('Efectivo', 'Tarjeta', 'Yape', 'Plin', 'Transferencia', 'Otros')

def _caja(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        u = db.session.get(Usuario, int(get_jwt_identity()))
        if not u or u.id_rol not in (1, 2) or not u.estado:
            return jsonify(success=False, error='Acceso restringido a caja'), 403
        return fn(*args, **kwargs)
    return wrapper

def _bloquear_caja():
    # Bloqueo compartido entre procesos; se libera al terminar la transacción.
    if db.engine.dialect.name == 'postgresql':
        db.session.execute(text('SELECT pg_advisory_xact_lock(72451001)'))

def _abierta():
    ultima = CierreCaja.query.order_by(CierreCaja.fecha.desc(), CierreCaja.id_cierre.desc()).first()
    return ultima if ultima and ultima.estado == 'abierta' else None

def _movimientos(inicio, fin):
    return TransaccionCaja.query.filter(TransaccionCaja.fecha >= inicio, TransaccionCaja.fecha < fin)

def _totales(movimientos):
    ventas = sum((Decimal(str(t.monto)) for t in movimientos if t.tipo == 'Venta'), Decimal(0))
    gastos = sum((Decimal(str(t.monto)) for t in movimientos if t.tipo == 'Gasto'), Decimal(0))
    return {'ventas': float(ventas.quantize(Decimal('.01'))), 'gastos': float(gastos.quantize(Decimal('.01'))),
            'neto': float((ventas - gastos).quantize(Decimal('.01')))}

def _historial():
    cierres = CierreCaja.query.order_by(CierreCaja.fecha.desc()).limit(200).all()
    if not cierres:
        return []
    movimientos = _movimientos(min(c.fecha for c in cierres), ahora()).all()
    resultado = []
    siguiente_apertura = None
    for c in cierres:
        item = cierre_schema.dump(c)
        fin = utc(c.fecha_cierre) if c.fecha_cierre else ahora()
        if siguiente_apertura and fin > siguiente_apertura:
            fin = siguiente_apertura
            item['requiere_revision'] = True
            if c.estado == 'abierta':
                item['estado'] = 'pendiente de revisión'
        totales = _totales([t for t in movimientos if utc(c.fecha) <= utc(t.fecha) < fin])
        # Conservar importes históricos guardados: mostrar el cálculo por apertura sin reescribirlos.
        item['total_ventas_registrado'] = c.total_ventas
        item.update(total_ventas=totales['ventas'], total_gastos=totales['gastos'], neto=totales['neto'])
        item['saldo_final'] = round(float(c.monto_inicial or 0) + totales['neto'], 2)
        resultado.append(item)
        siguiente_apertura = utc(c.fecha)
    return resultado

@caja_bp.route('/actual')
@_caja
def get_caja_actual():
    inicio, fin = limites_dia()
    totales = _totales(_movimientos(inicio, fin).all())
    cierre = _abierta()
    movimientos = _movimientos(utc(cierre.fecha) if cierre else inicio, ahora()).order_by(TransaccionCaja.fecha.desc()).all()
    sesion = _totales(movimientos)
    return jsonify(success=True, data={
        'abierta': cierre is not None, 'cierre': cierre_schema.dump(cierre) if cierre else None,
        'ventas_dia': totales['ventas'], 'gastos_dia': totales['gastos'], 'neto_dia': totales['neto'],
        'ventas_apertura': sesion['ventas'], 'gastos_apertura': sesion['gastos'],
        'saldo_actual': round(float(cierre.monto_inicial or 0) + sesion['neto'], 2) if cierre else totales['neto'],
        'transacciones': transacciones_schema.dump(movimientos)})

@caja_bp.route('/abrir', methods=['POST'])
@_caja
def abrir_caja():
    _bloquear_caja()
    if _abierta():
        return jsonify(success=False, error='Ya existe una caja abierta. Ciérrala antes de abrir otra.'), 409
    try:
        monto = numero((request.get_json(silent=True) or {}).get('monto_inicial') or 0)
    except (ValueError, TypeError):
        return jsonify(success=False, error='Monto inicial no válido'), 400
    cierre = CierreCaja(id_usuario=int(get_jwt_identity()), monto_inicial=monto, total_ventas=0,
                        total_gastos=0, estado='abierta', fecha=ahora())
    db.session.add(cierre)
    db.session.commit()
    return jsonify(success=True, data=cierre_schema.dump(cierre))

@caja_bp.route('/cerrar', methods=['POST'])
@_caja
def cerrar_caja():
    _bloquear_caja()
    cierre = _abierta()
    if not cierre:
        return jsonify(success=False, error='No hay caja abierta'), 409
    fin = ahora()
    totales = _totales(_movimientos(cierre.fecha, fin).all())
    cierre.total_ventas, cierre.total_gastos = totales['ventas'], totales['gastos']
    cierre.estado, cierre.fecha_cierre = 'cerrada', fin
    db.session.commit()
    return jsonify(success=True, data=cierre_schema.dump(cierre))

@caja_bp.route('/transacciones')
@_caja
def get_transacciones():
    inicio, fin = limites_dia()
    cierre = _abierta()
    movimientos = _movimientos(cierre.fecha if cierre else inicio, fin).order_by(TransaccionCaja.fecha.desc()).all()
    if request.args.get('historico', type=int) == 1:
        limite = max(1, min(request.args.get('limit', 50, type=int), 500))
        return jsonify(success=True, data={'transacciones': transacciones_schema.dump(movimientos),
            'historico': _historial(), 'ultimos_movimientos': transacciones_schema.dump(
                TransaccionCaja.query.order_by(TransaccionCaja.fecha.desc()).limit(limite).all())})
    return jsonify(success=True, data=transacciones_schema.dump(movimientos))

@caja_bp.route('/transacciones', methods=['POST'])
@_caja
def crear_transaccion():
    _bloquear_caja()
    if not _abierta():
        return jsonify(success=False, error='Abre la caja antes de registrar movimientos.'), 409
    data = request.get_json(silent=True) or {}
    if data.get('tipo') not in ('Venta', 'Gasto') or data.get('metodo_pago') not in METODOS:
        return jsonify(success=False, error='Selecciona el tipo y el método de pago.'), 400
    try:
        monto = numero(data.get('monto'), .01)
        if round(monto, 2) != monto:
            raise ValueError()
    except (ValueError, TypeError):
        return jsonify(success=False, error='Ingresa un monto positivo con hasta dos decimales.'), 400
    t = TransaccionCaja(id_usuario=int(get_jwt_identity()), tipo=data['tipo'], monto=monto,
        metodo_pago=data['metodo_pago'], categoria=data.get('categoria', ''),
        descripcion=data.get('descripcion', ''), fecha=ahora())
    db.session.add(t)
    db.session.commit()
    return jsonify(success=True, data=transaccion_schema.dump(t))

@caja_bp.route('/historial')
@_caja
def get_historial():
    return jsonify(success=True, data=_historial())

@caja_bp.route('/reportes')
@_caja
def reportes():
    try:
        fecha = date.fromisoformat(request.args.get('fecha') or ahora().astimezone(LIMA).date().isoformat())
        inicio, fin, buckets = periodo_financiero(request.args.get('periodo', 'mes'), fecha)
    except ValueError:
        return jsonify(success=False, error='Fecha o periodo no válido'), 400
    movimientos = _movimientos(inicio, fin).order_by(TransaccionCaja.fecha.desc()).all()
    puntos = []
    for etiqueta, a, b in buckets:
        total = _totales([t for t in movimientos if a <= utc(t.fecha) < b])
        puntos.append({'etiqueta': etiqueta, 'ingresos': total['ventas'], 'egresos': total['gastos'], 'ganancia': total['neto']})
    totales = _totales(movimientos)
    return jsonify(success=True, data={
        'ventas_mes': totales['ventas'], 'egresos_mes': totales['gastos'], 'neto_mes': totales['neto'],
        'inicio': inicio.isoformat(), 'fin': fin.isoformat(), 'puntos': puntos,
        'transacciones': transacciones_schema.dump(movimientos),
        'cierres': [c for c in _historial() if inicio <= utc(datetime.fromisoformat(c['fecha'])) < fin]})
