from flask import Blueprint, request, jsonify
from datetime import datetime, timezone

from bd import db
from api.validaciones import cantidad_decimal
from api.fechas import iso_utc
from api.roles import COCINA, requiere_roles
from schemas.cocina import producto_cocina_schema, solicitud_schema, solicitudes_schema
from models import (
    Producto, Categoria, SolicitudInsumo, ActividadUsuario
)

cocina_bp = Blueprint('cocina', __name__, url_prefix='/api/cocina')

STOCK_BAJO_DEFECTO = 10


def _json_objeto():
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else None


def _ahora():
    return datetime.now(timezone.utc)


_cocinero = requiere_roles(COCINA, mensaje='Acceso restringido al personal de cocina', pasar_usuario=True)


def _umbral_stock():
    return request.args.get('min', STOCK_BAJO_DEFECTO, type=float) or STOCK_BAJO_DEFECTO


def _estado_stock(stock, umbral):
    stock = float(stock or 0)
    if stock <= 0:
        return 'Agotado'
    if stock < umbral:
        return 'Stock bajo'
    return 'Disponible'


def _serializar_producto(p, umbral):
    return {**producto_cocina_schema.dump(p), 'estado': _estado_stock(p.stock, umbral)}


@cocina_bp.route('/dashboard', methods=['GET'])
@_cocinero
def dashboard(cocinero):
    umbral = _umbral_stock()
    productos = Producto.query.filter(Producto.estado.is_(True)).all()
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
            'fecha': iso_utc(_ahora()),
            'resumen': {
                'total_insumos': total_insumos,
                'disponibles': len(disponibles),
                'stock_bajo': len(stock_bajo),
                'agotados': len(agotados),
                'solicitudes_pendientes': len(pendientes),
            },
            'pendientes': solicitudes_schema.dump(pendientes),
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
    return jsonify({'success': True, 'data': solicitudes_schema.dump(solicitudes)})


@cocina_bp.route('/solicitudes', methods=['POST'])
@_cocinero
def crear_solicitud(cocinero):
    data = _json_objeto()
    if data is None:
        return jsonify(success=False, error='El cuerpo debe ser un objeto JSON.'), 400
    try:
        if isinstance(data.get('id_producto'), bool):
            raise ValueError()
        id_producto = int(data.get('id_producto'))
    except (TypeError, ValueError):
        id_producto = None
    producto = db.session.get(Producto, id_producto) if id_producto else None
    if not producto or not producto.estado:
        return jsonify({'success': False, 'error': 'Selecciona un producto o insumo válido'}), 400

    try:
        cantidad = float(cantidad_decimal(data.get('cantidad') or 0, .001))
        if cantidad <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'La cantidad debe ser mayor que cero'}), 400

    observacion_recibida = data.get('observacion') or ''
    if not isinstance(observacion_recibida, str) or len(observacion_recibida.strip()) > 255:
        return jsonify(success=False, error='La observación admite hasta 255 caracteres.'), 400
    observacion = observacion_recibida.strip()
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

    return jsonify({'success': True, 'data': solicitud_schema.dump(solicitud)}), 201
