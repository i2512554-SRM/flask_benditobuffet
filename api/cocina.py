from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timezone

from bd import db
from models import (
    Usuario, Producto, Categoria, SolicitudInsumo, ActividadUsuario, crear_notificacion
)

cocina_bp = Blueprint('cocina', __name__, url_prefix='/api/cocina')

ROL_REQUERIDO = 3
STOCK_BAJO_DEFECTO = 10


def _ahora():
    return datetime.now(timezone.utc)


def _cocinero(fn):
    from functools import wraps

    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        uid = int(get_jwt_identity())
        u = Usuario.query.get(uid)
        if not u or u.id_rol != ROL_REQUERIDO or not u.estado:
            return jsonify({'success': False, 'error': 'Acceso restringido al personal de cocina'}), 403
        return fn(u, *args, **kwargs)

    return wrapper


def _umbral_stock():
    return request.args.get('min', STOCK_BAJO_DEFECTO, type=float) or STOCK_BAJO_DEFECTO


def _estado_stock(stock, umbral):
    stock = float(stock or 0)
    if stock <= 0:
        return 'Agotado'
    if stock < umbral:
        return 'Stock bajo'
    return 'Disponible'


def _serializar_producto(p, umbral=None):
    umbral = umbral or _umbral_stock()
    return {
        'id_producto': p.id_producto,
        'nombre': p.nombre,
        'categoria': p.categoria or None,
        'stock': float(p.stock or 0),
        'unidad': p.unidad_medida or 'Un',
        'unidad_medida': p.unidad_medida or 'Un',
        'estado': _estado_stock(p.stock, umbral),
        'activo': p.estado,
    }


def _serializar_solicitud(s):
    return {
        'id_solicitud': s.id_solicitud,
        'id_producto': s.id_producto,
        'producto': s.producto,
        'cantidad': s.cantidad,
        'observacion': s.observacion,
        'estado': s.estado,
        'respuesta': s.respuesta,
        'fecha': s.fecha.strftime('%d/%m/%Y %H:%M') if s.fecha else None,
    }


@cocina_bp.route('/dashboard', methods=['GET'])
@_cocinero
def dashboard(cocinero):
    umbral = _umbral_stock()
    productos = Producto.query.all()
    total_insumos = len(productos)
    stock_bajo = [p for p in productos if 0 < float(p.stock or 0) < umbral]
    agotados = [p for p in productos if float(p.stock or 0) <= 0]
    disponibles = [p for p in productos if float(p.stock or 0) >= umbral]
    pendientes = SolicitudInsumo.query.filter_by(
        id_usuario=cocinero.id_usuario, estado='Pendiente'
    ).order_by(SolicitudInsumo.fecha.desc()).all()

    return jsonify({
        'success': True,
        'data': {
            'usuario': {
                'nombres': cocinero.nombres,
                'apellido': cocinero.apellido,
                'rol': cocinero.rol.nombre if cocinero.rol else 'Cocinero',
            },
            'fecha': _ahora().strftime('%A, %d de %B del %Y'),
            'resumen': {
                'total_insumos': total_insumos,
                'disponibles': len(disponibles),
                'stock_bajo': len(stock_bajo),
                'agotados': len(agotados),
                'solicitudes_pendientes': len(pendientes),
            },
            'pendientes': [_serializar_solicitud(s) for s in pendientes],
        }
    })


@cocina_bp.route('/inventario', methods=['GET'])
@_cocinero
def inventario(cocinero):
    q = request.args.get('q', '').strip()
    umbral = _umbral_stock()
    query = Producto.query.outerjoin(Categoria, Producto.id_categoria == Categoria.id_categoria)
    if q:
        like = f'%{q.lower()}%'
        query = query.filter(db.or_(
            db.func.lower(Producto.nombre).like(like),
            db.func.lower(Categoria.nombre).like(like),
        ))
    productos = query.order_by(Producto.nombre.asc()).all()
    data = [_serializar_producto(p, umbral) for p in productos if p.estado]
    return jsonify({'success': True, 'data': data})


@cocina_bp.route('/alertas', methods=['GET'])
@_cocinero
def alertas(cocinero):
    umbral = _umbral_stock()
    productos = Producto.query.order_by(Producto.stock.asc()).all()
    data = [_serializar_producto(p, umbral) for p in productos if p.estado and float(p.stock or 0) < umbral]
    return jsonify({'success': True, 'data': data})


@cocina_bp.route('/solicitudes', methods=['GET'])
@_cocinero
def listar_solicitudes(cocinero):
    estado = request.args.get('estado', '').strip()
    q = SolicitudInsumo.query.filter_by(id_usuario=cocinero.id_usuario)
    if estado:
        q = q.filter(SolicitudInsumo.estado == estado)
    solicitudes = q.order_by(SolicitudInsumo.fecha.desc()).all()
    return jsonify({'success': True, 'data': [_serializar_solicitud(s) for s in solicitudes]})


@cocina_bp.route('/solicitudes', methods=['POST'])
@_cocinero
def crear_solicitud(cocinero):
    data = request.get_json(silent=True) or {}
    id_producto = data.get('id_producto')
    producto = Producto.query.get(id_producto) if id_producto else None
    if not producto:
        return jsonify({'success': False, 'error': 'Selecciona un producto o insumo válido'}), 400

    try:
        cantidad = float(data.get('cantidad') or 0)
        if cantidad <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'La cantidad debe ser mayor que cero'}), 400

    observacion = (data.get('observacion') or '').strip()
    solicitud = SolicitudInsumo(
        id_usuario=cocinero.id_usuario,
        id_producto=producto.id_producto,
        cantidad=cantidad,
        observacion=observacion or None,
        estado='Pendiente',
        fecha=_ahora()
    )
    db.session.add(solicitud)
    db.session.add(ActividadUsuario(
        id_usuario=cocinero.id_usuario,
        accion=f'Solicitó {cantidad:g} de {producto.nombre} para la cocina',
        fecha=_ahora()
    ))
    db.session.commit()

    return jsonify({'success': True, 'data': _serializar_solicitud(solicitud)}), 201