from datetime import date
from bisect import bisect_left
from decimal import Decimal, InvalidOperation
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import text
from models import db, TransaccionCaja, CierreCaja
from schemas.caja import transacciones_schema, cierre_schema, transaccion_schema
from api.fechas import ahora, limites_dia, periodo_financiero, utc, LIMA
from api.idempotencia import normalizar_clave
from api.roles import ROLES_CAJA, requiere_roles

caja_bp = Blueprint('caja', __name__)
METODOS = ('Efectivo', 'Tarjeta', 'Yape', 'Plin', 'Transferencia', 'Otros')


def _json_objeto(permitir_vacio=False):
    data = request.get_json(silent=True)
    if data is None and permitir_vacio:
        return {}
    return data if isinstance(data, dict) else None


def _monto(valor, positivo=False):
    try:
        monto = Decimal(str(valor))
        minimo = Decimal('.01') if positivo else Decimal('0')
        if (
            not monto.is_finite()
            or monto < minimo
            or monto > Decimal('9999999999.99')
            or monto.quantize(Decimal('.01')) != monto
        ):
            raise ValueError()
        return monto
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError()

_caja = requiere_roles(*ROLES_CAJA, mensaje='Acceso restringido a caja')

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

def _prefijos_movimientos(movimientos):
    fechas, ventas, gastos = [], [Decimal(0)], [Decimal(0)]
    for movimiento in movimientos:
        fechas.append(utc(movimiento.fecha))
        monto = Decimal(str(movimiento.monto))
        ventas.append(ventas[-1] + (monto if movimiento.tipo == 'Venta' else Decimal(0)))
        gastos.append(gastos[-1] + (monto if movimiento.tipo == 'Gasto' else Decimal(0)))
    return fechas, ventas, gastos

def _totales_intervalo(prefijos, inicio, fin):
    fechas, ventas, gastos = prefijos
    izquierda, derecha = bisect_left(fechas, utc(inicio)), bisect_left(fechas, utc(fin))
    total_ventas = ventas[derecha] - ventas[izquierda]
    total_gastos = gastos[derecha] - gastos[izquierda]
    return {
        'ventas': float(total_ventas.quantize(Decimal('.01'))),
        'gastos': float(total_gastos.quantize(Decimal('.01'))),
        'neto': float((total_ventas - total_gastos).quantize(Decimal('.01'))),
    }

def _historial(inicio=None, fin_periodo=None):
    query = CierreCaja.query
    if inicio is not None:
        query = query.filter(CierreCaja.fecha >= inicio, CierreCaja.fecha < fin_periodo)
    query = query.order_by(CierreCaja.fecha.desc(), CierreCaja.id_cierre.desc())
    cierres = query.all() if inicio is not None else query.limit(200).all()
    if not cierres:
        return []
    corte = ahora()
    resultado, intervalos = [], []
    siguiente = CierreCaja.query.filter(CierreCaja.fecha > cierres[0].fecha).order_by(CierreCaja.fecha).first()
    siguiente_apertura = utc(siguiente.fecha) if siguiente else None
    for c in cierres:
        item = cierre_schema.dump(c)
        fin = utc(c.fecha_cierre) if c.fecha_cierre else corte
        if fin_periodo is not None and fin > utc(fin_periodo):
            fin = utc(fin_periodo)
        if siguiente_apertura and fin > siguiente_apertura:
            fin = siguiente_apertura
            item['requiere_revision'] = True
            if c.estado == 'abierta':
                item['estado'] = 'pendiente de revisión'
        intervalos.append((c, item, utc(c.fecha), fin))
        siguiente_apertura = utc(c.fecha)

    limite_inferior = min(intervalo[2] for intervalo in intervalos)
    limite_superior = max(intervalo[3] for intervalo in intervalos)
    movimientos = _movimientos(limite_inferior, limite_superior).order_by(TransaccionCaja.fecha).all()
    prefijos = _prefijos_movimientos(movimientos)
    for c, item, apertura, fin in intervalos:
        totales = _totales_intervalo(prefijos, apertura, fin)
        # Conservar importes históricos guardados: mostrar el cálculo por apertura sin reescribirlos.
        item['total_ventas_registrado'] = float(c.total_ventas or 0)
        item.update(total_ventas=totales['ventas'], total_gastos=totales['gastos'], neto=totales['neto'])
        item['saldo_final'] = round(float(c.monto_inicial or 0) + totales['neto'], 2)
        resultado.append(item)
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
    data = _json_objeto(permitir_vacio=True)
    if data is None:
        return jsonify(success=False, error='El cuerpo debe ser un objeto JSON.'), 400
    try:
        monto = _monto(data.get('monto_inicial') or 0)
    except (ValueError, TypeError):
        return jsonify(success=False, error='El monto inicial admite hasta dos decimales.'), 400
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
    data = _json_objeto(permitir_vacio=True)
    if data is None:
        return jsonify(success=False, error='El cuerpo debe ser un objeto JSON.'), 400
    contado = None
    if data.get('efectivo_contado') is not None:
        try:
            contado = _monto(data['efectivo_contado'])
        except (ValueError, TypeError):
            return jsonify(success=False, error='El efectivo contado admite hasta dos decimales.'), 400
    fin = ahora()
    totales = _totales(_movimientos(cierre.fecha, fin).all())
    cierre.total_ventas, cierre.total_gastos = totales['ventas'], totales['gastos']
    cierre.efectivo_contado = contado
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
    data = _json_objeto()
    if data is None:
        return jsonify(success=False, error='El cuerpo debe ser un objeto JSON.'), 400
    if data.get('tipo') not in ('Venta', 'Gasto') or data.get('metodo_pago') not in METODOS:
        return jsonify(success=False, error='Selecciona el tipo y el método de pago.'), 400
    try:
        monto = _monto(data.get('monto'), positivo=True)
    except (ValueError, TypeError):
        return jsonify(success=False, error='Ingresa un monto positivo con hasta dos decimales.'), 400
    categoria = data.get('categoria') or ''
    descripcion = data.get('descripcion') or ''
    if (
        not isinstance(categoria, str)
        or len(categoria.strip()) > 150
        or not isinstance(descripcion, str)
    ):
        return jsonify(success=False, error='La categoría o la descripción no es válida.'), 400
    categoria = categoria.strip()
    descripcion = descripcion.strip()
    try:
        clave = normalizar_clave(data)
    except ValueError as error:
        return jsonify(success=False, error=str(error)), 400
    uid = int(get_jwt_identity())
    if clave:
        existente = TransaccionCaja.query.filter_by(clave_operacion=clave).first()
        if existente:
            coincide = (
                existente.id_usuario == uid and existente.tipo == data['tipo']
                and Decimal(str(existente.monto)).quantize(Decimal('.01')) == monto
                and existente.metodo_pago == data['metodo_pago']
                and (existente.descripcion or '') == descripcion
            )
            if not coincide:
                return jsonify(success=False, error='El identificador ya pertenece a otra operación.'), 409
            return jsonify(success=True, repetida=True, data=transaccion_schema.dump(existente))
    if not _abierta():
        return jsonify(success=False, error='Abre la caja antes de registrar movimientos.'), 409
    t = TransaccionCaja(id_usuario=int(get_jwt_identity()), tipo=data['tipo'], monto=monto,
        metodo_pago=data['metodo_pago'], categoria=categoria,
        descripcion=descripcion, clave_operacion=clave, fecha=ahora())
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
        datos = _datos_reporte(request.args.get('periodo', 'mes'), request.args.get('fecha'))
    except ValueError:
        return jsonify(success=False, error='Fecha o periodo no válido'), 400
    return jsonify(success=True, data=datos)

def _datos_reporte(periodo='mes', fecha_texto=None):
    inicio, fin, movimientos, puntos, totales = _calcular_reporte(periodo, fecha_texto)
    return {
        'ventas_mes': totales['ventas'], 'egresos_mes': totales['gastos'], 'neto_mes': totales['neto'],
        'inicio': inicio.isoformat(), 'fin': fin.isoformat(), 'puntos': puntos,
        'transacciones': transacciones_schema.dump(reversed(movimientos)),
        'cierres': _historial(inicio, fin),
    }

def puntos_reporte(periodo='mes', fecha_texto=None):
    return _calcular_reporte(periodo, fecha_texto)[3]

def _calcular_reporte(periodo, fecha_texto):
    fecha = date.fromisoformat(fecha_texto or ahora().astimezone(LIMA).date().isoformat())
    inicio, fin, buckets = periodo_financiero(periodo, fecha)
    movimientos = _movimientos(inicio, fin).order_by(TransaccionCaja.fecha, TransaccionCaja.id_transaccion).all()
    prefijos = _prefijos_movimientos(movimientos)
    puntos = []
    for etiqueta, a, b in buckets:
        total = _totales_intervalo(prefijos, a, b)
        puntos.append({'etiqueta': etiqueta, 'ingresos': total['ventas'], 'egresos': total['gastos'], 'ganancia': total['neto']})
    return inicio, fin, movimientos, puntos, _totales_intervalo(prefijos, inicio, fin)
