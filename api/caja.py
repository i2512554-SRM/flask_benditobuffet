from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, TransaccionCaja, CierreCaja, Usuario
from schemas.caja import transaccion_schema, transacciones_schema, cierre_schema, cierres_schema

caja_bp = Blueprint('caja', __name__)

ROLES_PERMITIDOS = (1, 2)


def _caja(fn):
    from functools import wraps

    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        uid = int(get_jwt_identity())
        u = Usuario.query.get(uid)
        if not u or u.id_rol not in ROLES_PERMITIDOS or not u.estado:
            return jsonify({'success': False, 'error': 'Acceso restringido a caja'}), 403
        return fn(*args, **kwargs)

    return wrapper

@caja_bp.route('/actual', methods=['GET'])
@_caja
def get_caja_actual():
    from datetime import datetime, timedelta
    hoy = datetime.utcnow().date()
    inicio = datetime.combine(hoy, datetime.min.time())
    fin = datetime.combine(hoy + timedelta(days=1), datetime.min.time())

    ventas = db.session.query(db.func.coalesce(db.func.sum(TransaccionCaja.monto), 0))
    ventas = ventas.filter(TransaccionCaja.tipo == 'Venta', TransaccionCaja.fecha >= inicio, TransaccionCaja.fecha < fin).scalar()

    gastos = db.session.query(db.func.coalesce(db.func.sum(TransaccionCaja.monto), 0))
    gastos = gastos.filter(TransaccionCaja.tipo == 'Gasto', TransaccionCaja.fecha >= inicio, TransaccionCaja.fecha < fin).scalar()

    transacciones = TransaccionCaja.query.filter(
        TransaccionCaja.fecha >= inicio,
        TransaccionCaja.fecha < fin
    ).order_by(TransaccionCaja.fecha.desc()).all()

    cierre = CierreCaja.query.filter(
        CierreCaja.fecha >= inicio, CierreCaja.fecha < fin, CierreCaja.estado == 'abierta'
    ).first()

    return jsonify({
        'success': True,
        'data': {
            'abierta': cierre is not None,
            'cierre': cierre_schema.dump(cierre) if cierre else None,
            'ventas_dia': float(ventas),
            'gastos_dia': float(gastos),
            'neto_dia': float(ventas) - float(gastos),
            'transacciones': transacciones_schema.dump(transacciones)
        }
    })

@caja_bp.route('/abrir', methods=['POST'])
@_caja
def abrir_caja():
    from datetime import datetime, timedelta
    data = request.get_json(silent=True) or {}
    hoy = datetime.utcnow().date()
    inicio = datetime.combine(hoy, datetime.min.time())
    fin = datetime.combine(hoy + timedelta(days=1), datetime.min.time())

    cierre_hoy = CierreCaja.query.filter(
        CierreCaja.fecha >= inicio, CierreCaja.fecha < fin, CierreCaja.estado == 'abierta'
    ).first()
    if cierre_hoy:
        return jsonify({'success': False, 'message': 'Ya hay una caja abierta hoy'}), 400

    monto_inicial = 0
    if 'monto_inicial' in data and data['monto_inicial'] not in (None, ''):
        try:
            monto_inicial = float(str(data['monto_inicial']).replace(',', '.'))
        except (ValueError, TypeError):
            return jsonify({'success': False, 'error': 'El monto inicial debe ser un número'}), 400
        if monto_inicial < 0:
            return jsonify({'success': False, 'error': 'El monto inicial no puede ser negativo'}), 400

    cierre = CierreCaja(
        id_usuario=get_jwt_identity(),
        monto_inicial=monto_inicial,
        total_ventas=0,
        total_gastos=0,
        estado='abierta',
        fecha=datetime.utcnow()
    )
    db.session.add(cierre)
    db.session.commit()
    return jsonify({'success': True, 'data': cierre_schema.dump(cierre)})

@caja_bp.route('/cerrar', methods=['POST'])
@_caja
def cerrar_caja():
    from datetime import datetime, timedelta
    hoy = datetime.utcnow().date()
    inicio = datetime.combine(hoy, datetime.min.time())
    fin = datetime.combine(hoy + timedelta(days=1), datetime.min.time())

    cierre = CierreCaja.query.filter(
        CierreCaja.fecha >= inicio, CierreCaja.fecha < fin, CierreCaja.estado == 'abierta'
    ).first()
    if not cierre:
        return jsonify({'success': False, 'message': 'No hay caja abierta hoy'}), 400
    
    cierre.total_ventas = db.session.query(db.func.coalesce(db.func.sum(TransaccionCaja.monto), 0)).filter(
        TransaccionCaja.tipo == 'Venta', TransaccionCaja.fecha >= inicio, TransaccionCaja.fecha < fin
    ).scalar() or 0
    cierre.total_gastos = db.session.query(db.func.coalesce(db.func.sum(TransaccionCaja.monto), 0)).filter(
        TransaccionCaja.tipo == 'Gasto', TransaccionCaja.fecha >= inicio, TransaccionCaja.fecha < fin
    ).scalar() or 0
    cierre.estado = 'cerrada'
    cierre.fecha_cierre = datetime.utcnow()
    db.session.commit()
    return jsonify({'success': True, 'data': cierre_schema.dump(cierre)})

@caja_bp.route('/transacciones', methods=['GET'])
@_caja
def get_transacciones():
    from datetime import datetime, timedelta
    hoy = datetime.utcnow().date()
    inicio = datetime.combine(hoy, datetime.min.time())
    fin = datetime.combine(hoy + timedelta(days=1), datetime.min.time())

    historico = request.args.get('historico', type=int) == 1
    transacciones = TransaccionCaja.query.filter(
        TransaccionCaja.fecha >= inicio,
        TransaccionCaja.fecha < fin
    ).order_by(TransaccionCaja.fecha.desc()).all()

    if historico:
        limite = request.args.get('limit', 50, type=int)
        cierres = CierreCaja.query.order_by(CierreCaja.fecha.desc()).all()
        historicos = TransaccionCaja.query.order_by(TransaccionCaja.fecha.desc()).limit(min(limite, 500)).all()
        return jsonify({'success': True, 'data': {
            'transacciones': transacciones_schema.dump(transacciones),
            'historico': cierres_schema.dump(cierres),
            'ultimos_movimientos': transacciones_schema.dump(historicos),
        }})

    return jsonify({'success': True, 'data': transacciones_schema.dump(transacciones)})

@caja_bp.route('/transacciones', methods=['POST'])
@_caja
def crear_transaccion():
    from datetime import datetime
    data = request.get_json(silent=True) or {}

    tipo = (data.get('tipo') or '').strip()
    if tipo not in ('Venta', 'Gasto'):
        return jsonify({'success': False, 'error': 'El tipo debe ser Venta o Gasto'}), 400

    try:
        monto = float(str(data.get('monto', '')).replace(',', '.'))
        if monto <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'El monto debe ser un número mayor que cero'}), 400

    transaccion = TransaccionCaja(
        id_usuario=get_jwt_identity(),
        tipo=tipo,
        monto=monto,
        metodo_pago=data.get('metodo_pago', 'Efectivo'),
        categoria=data.get('categoria', ''),
        descripcion=data.get('descripcion', ''),
        fecha=datetime.utcnow()
    )
    db.session.add(transaccion)
    db.session.commit()
    return jsonify({'success': True, 'data': transaccion_schema.dump(transaccion)})

@caja_bp.route('/historial', methods=['GET'])
@_caja
def get_historial():
    cierres = CierreCaja.query.order_by(CierreCaja.fecha.desc()).all()
    return jsonify({'success': True, 'data': cierres_schema.dump(cierres)})
