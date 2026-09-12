from api.validaciones import numero
from sqlalchemy import text
import uuid
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date, timedelta
from functools import wraps
from bd import db
from models import (
    Producto, Inversion, Categoria, Proveedor, ActividadUsuario, Usuario,
    CompraInventario, DetalleCompraInventario, InventarioMovimiento,
    SolicitudInsumo, crear_notificacion
)
from schemas.inventario import (
    producto_schema, productos_schema, inversion_schema, inversiones_schema,
    compra_inventario_schema, compras_inventario_schema,
    inventario_movimientos_schema
)

inventario_bp = Blueprint('inventario', __name__)

UNIDADES_VALIDAS = {'Kg', 'Un', 'Lt'}


def _ahora():
    return datetime.utcnow()


def _requiere_roles(*roles):
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            uid = int(get_jwt_identity())
            u = Usuario.query.get(uid)
            if not u or not u.estado or u.id_rol not in roles:
                return jsonify({'success': False, 'error': 'Acceso restringido a inventario'}), 403
            if request.method in ('POST', 'PUT', 'DELETE'):
                if db.engine.dialect.name == 'postgresql':
                    db.session.execute(text('SELECT pg_advisory_xact_lock(72451002)'))
                data = request.get_json(silent=True) or {}
                try:
                    for campo in ('stock', 'precio', 'monto', 'cantidad'):
                        if campo in data and data[campo] is not None:
                            numero(data[campo], .000001 if campo in ('monto', 'cantidad') else 0)
                    for linea in data.get('detalle') or []:
                        numero(linea.get('cantidad'), .000001)
                        numero(linea.get('precio_unitario'), 0)
                except (ValueError, TypeError, AttributeError):
                    return jsonify(success=False, error='Revisa cantidades y precios: deben ser números válidos, sin negativos.'), 400
            return fn(*args, **kwargs)
        return wrapper
    return decorator


_solo_admin = _requiere_roles(1)
_inventario_stock = _requiere_roles(1, 3)


def _uniq_nombre(nombre, excluir=None):
    """Busca un producto con el mismo nombre ignorando mayúsculas y espacios."""
    if not nombre:
        return None
    q = Producto.query.filter(
        db.func.lower(db.func.trim(Producto.nombre)) == nombre.strip().lower()
    )
    if excluir:
        q = q.filter(Producto.id_producto != excluir)
    return q.first()


def _categoria_por_defecto():
    cat = Categoria.query.filter(db.func.lower(Categoria.nombre) == 'ingredientes').first()
    if not cat:
        cat = Categoria.query.first()
    if not cat:
        cat = Categoria(nombre='Ingredientes', fecha_creacion=_ahora())
        db.session.add(cat)
        db.session.flush()
    return cat


def _registrar_movimiento(id_producto, id_usuario, tipo, cantidad, stock_anterior,
                          stock_posterior, motivo, observacion=None, id_compra=None):
    db.session.add(InventarioMovimiento(
        id_producto=id_producto,
        id_usuario=id_usuario,
        tipo=tipo,
        cantidad=cantidad,
        stock_anterior=stock_anterior,
        stock_posterior=stock_posterior,
        motivo=motivo or observacion,
        id_compra=id_compra,
        observacion=observacion or motivo,
        fecha=_ahora()
    ))


@inventario_bp.route('/resumen', methods=['GET'])
@_inventario_stock
def get_resumen():
    total_inventario = db.session.query(
        db.func.coalesce(db.func.sum(Producto.precio * Producto.stock), 0)
    ).scalar() or 0
    equipamiento = db.session.query(
        db.func.coalesce(db.func.sum(Producto.precio * Producto.stock), 0)
    ).join(Categoria, Producto.id_categoria == Categoria.id_categoria).filter(
        db.func.lower(Categoria.nombre).like('%equipamiento%')
    ).scalar() or 0

    hoy = date.today()
    inicio_mes = datetime(hoy.year, hoy.month, 1)
    fin_mes = datetime(hoy.year, hoy.month, hoy.day) + timedelta(days=1)
    inversiones_mes = db.session.query(
        db.func.coalesce(db.func.sum(Inversion.monto), 0)
    ).filter(Inversion.fecha >= inicio_mes, Inversion.fecha < fin_mes).scalar() or 0
    compras_mes = db.session.query(db.func.coalesce(db.func.sum(CompraInventario.total_compra), 0)).filter(
        CompraInventario.fecha >= inicio_mes, CompraInventario.fecha < fin_mes,
        CompraInventario.estado == 'Completada').scalar() or 0
    inversiones_mes += compras_mes
    productos_mes = Producto.query.filter(
        Producto.fecha_registro >= inicio_mes, Producto.fecha_registro < fin_mes
    ).count()

    return jsonify({
        'success': True,
        'data': {
            'valor_total': float(total_inventario),
            'inversiones_mes': float(inversiones_mes),
            'articulos_registrados': Producto.query.count(),
            'productos_mes': productos_mes,
            'equipamiento_valor': float(equipamiento),
        }
    })


@inventario_bp.route('/inversiones/<int:id>', methods=['GET'])
@_solo_admin
def get_inversion(id):
    inversion = Inversion.query.get_or_404(id)
    return jsonify({'success': True, 'data': inversion_schema.dump(inversion)})


@inventario_bp.route('/inversiones/<int:id>', methods=['DELETE'])
@_solo_admin
def eliminar_inversion(id):
    inversion = Inversion.query.get_or_404(id)
    admin_id = int(get_jwt_identity())
    db.session.delete(inversion)
    db.session.add(ActividadUsuario(id_usuario=admin_id, accion='Eliminó compra/inversión de inventario', fecha=_ahora()))
    db.session.commit()
    return jsonify({'success': True, 'message': 'Compra/inversión eliminada'})


@inventario_bp.route('/productos', methods=['GET'])
@_inventario_stock
def get_productos():
    query = Producto.query.options(db.joinedload(Producto.categoria_rel))
    q = request.args.get('q', '').strip()
    cat = request.args.get('cat', '').strip()
    activos = request.args.get('activos', '').strip() == '1'
    if cat:
        query = query.join(Categoria, Producto.id_categoria == Categoria.id_categoria).filter(db.func.lower(Categoria.nombre) == cat.lower())
    if activos:
        query = query.filter(Producto.estado == True)
    if q:
        like = f"%{q.lower()}%"
        query = query.outerjoin(Categoria, Producto.id_categoria == Categoria.id_categoria).filter(db.or_(
            db.func.lower(Producto.nombre).like(like),
            db.func.lower(Categoria.nombre).like(like),
        ))
    productos = query.order_by(Producto.nombre.asc()).all()
    return jsonify({'success': True, 'data': productos_schema.dump(productos)})


@inventario_bp.route('/productos/<int:id>', methods=['GET'])
@_inventario_stock
def get_producto(id):
    producto = Producto.query.get_or_404(id)
    return jsonify({'success': True, 'data': producto_schema.dump(producto)})


@inventario_bp.route('/productos', methods=['POST'])
@_inventario_stock
def crear_producto():
    data = request.get_json()
    nombre = (data.get('nombre') or '').strip()
    if not nombre:
        return jsonify({'success': False, 'error': 'El nombre del producto es obligatorio'}), 400

    unidad = (data.get('unidad_medida') or data.get('unidad') or 'Un').strip()
    if unidad not in UNIDADES_VALIDAS:
        return jsonify({'success': False, 'error': f'Unidad de medida no válida. Usa: {", ".join(sorted(UNIDADES_VALIDAS))}'}), 400

    duplicado = _uniq_nombre(nombre)
    if duplicado:
        return jsonify({
            'success': False,
            'error': "El producto ya existe en el sistema. Si deseas aumentar su cantidad, utiliza la opción 'Agregar stock'.",
            'existe': True,
            'id_producto': duplicado.id_producto
        }), 409

    try:
        stock_inicial = float(data.get('stock', 0) or 0)
    except (TypeError, ValueError):
        stock_inicial = 0
    if stock_inicial < 0:
        return jsonify({'success': False, 'error': 'El stock inicial no puede ser negativo'}), 400

    id_categoria = data.get('id_categoria')
    if not id_categoria:
        id_categoria = _categoria_por_defecto().id_categoria

    producto = Producto(
        nombre=nombre,
        precio=float(data.get('precio', 0) or 0),
        stock=stock_inicial,
        unidad_medida=unidad,
        descripcion=(data.get('descripcion') or '').strip() or None,
        estado=bool(data.get('estado', True)),
        id_categoria=id_categoria,
        fecha_registro=_ahora(),
        fecha_edicion=_ahora()
    )
    db.session.add(producto)
    db.session.flush()
    if stock_inicial > 0:
        _registrar_movimiento(
            producto.id_producto, int(get_jwt_identity()), 'Entrada', stock_inicial,
            0, stock_inicial, 'Stock inicial al crear producto'
        )
    db.session.commit()
    return jsonify({'success': True, 'data': producto_schema.dump(producto)}), 201


@inventario_bp.route('/productos/<int:id>', methods=['PUT'])
@_inventario_stock
def actualizar_producto(id):
    producto = Producto.query.get_or_404(id)
    data = request.get_json()

    nombre = (data.get('nombre') if data.get('nombre') is not None else producto.nombre).strip()
    if not nombre:
        return jsonify({'success': False, 'error': 'El nombre del producto es obligatorio'}), 400
    duplicado = _uniq_nombre(nombre, excluir=producto.id_producto)
    if duplicado:
        return jsonify({
            'success': False,
            'error': "El producto ya existe en el sistema. Si deseas aumentar su cantidad, utiliza la opción 'Agregar stock'.",
            'existe': True,
            'id_producto': duplicado.id_producto
        }), 409

    unidad = (data.get('unidad_medida') if data.get('unidad_medida') is not None else producto.unidad_medida).strip()
    if unidad not in UNIDADES_VALIDAS:
        return jsonify({'success': False, 'error': f'Unidad de medida no válida. Usa: {", ".join(sorted(UNIDADES_VALIDAS))}'}), 400

    producto.nombre = nombre
    producto.unidad_medida = unidad
    if 'descripcion' in data:
        producto.descripcion = (data.get('descripcion') or '').strip() or None
    if 'estado' in data:
        producto.estado = bool(data['estado'])
    if 'precio' in data:
        producto.precio = float(data.get('precio') or 0)
    if data.get('id_categoria'):
        producto.id_categoria = data['id_categoria']
    # El stock NO se modifica por edición: solo entrada/salida
    producto.fecha_edicion = _ahora()

    db.session.commit()
    return jsonify({'success': True, 'data': producto_schema.dump(producto)})


@inventario_bp.route('/productos/<int:id>', methods=['DELETE'])
@_solo_admin
def eliminar_producto(id):
    producto = Producto.query.get_or_404(id)
    tiene_movimientos = InventarioMovimiento.query.filter_by(id_producto=producto.id_producto).first() is not None
    if tiene_movimientos:
        producto.estado = False
        producto.fecha_edicion = _ahora()
        db.session.commit()
        return jsonify({'success': True, 'message': 'Producto desactivado (conserva su historial)', 'data': producto_schema.dump(producto)})
    db.session.delete(producto)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Producto eliminado'})


@inventario_bp.route('/productos/<int:id>/stock/entrada', methods=['POST'])
@_inventario_stock
def entrada_stock(id):
    producto = Producto.query.get_or_404(id)
    if not producto.estado:
        return jsonify({'success': False, 'error': 'El producto está inactivo y no puede recibir stock'}), 400
    data = request.get_json() or {}
    try:
        cantidad = float(data.get('cantidad', 0))
    except (TypeError, ValueError):
        cantidad = 0
    if cantidad <= 0:
        return jsonify({'success': False, 'error': 'La cantidad a agregar debe ser mayor a cero'}), 400

    anterior = float(producto.stock or 0)
    posterior = anterior + cantidad
    motivo = (data.get('motivo') or '').strip() or 'Ingreso de stock'
    producto.stock = posterior
    producto.fecha_edicion = _ahora()
    _registrar_movimiento(
        producto.id_producto, int(get_jwt_identity()), 'Entrada', cantidad,
        anterior, posterior, motivo,
        observacion=(data.get('observacion') or '').strip() or None
    )
    db.session.commit()
    return jsonify({'success': True, 'message': 'Stock agregado correctamente', 'data': producto_schema.dump(producto)})


@inventario_bp.route('/productos/<int:id>/stock/salida', methods=['POST'])
@_inventario_stock
def salida_stock(id):
    producto = Producto.query.get_or_404(id)
    if not producto.estado:
        return jsonify({'success': False, 'error': 'El producto está inactivo y no puede registrar salidas'}), 400
    data = request.get_json() or {}
    try:
        cantidad = float(data.get('cantidad', 0))
    except (TypeError, ValueError):
        cantidad = 0
    if cantidad <= 0:
        return jsonify({'success': False, 'error': 'La cantidad a retirar debe ser mayor a cero'}), 400

    anterior = float(producto.stock or 0)
    if cantidad > anterior:
        return jsonify({'success': False, 'error': 'No hay suficiente stock disponible.'}), 400

    motivo = (data.get('motivo') or '').strip()
    if not motivo:
        return jsonify({'success': False, 'error': 'El motivo de la salida es obligatorio'}), 400

    posterior = anterior - cantidad
    producto.stock = posterior
    producto.fecha_edicion = _ahora()
    _registrar_movimiento(
        producto.id_producto, int(get_jwt_identity()), 'Salida', -cantidad,
        anterior, posterior, motivo,
        observacion=(data.get('observacion') or '').strip() or None
    )
    db.session.commit()
    return jsonify({'success': True, 'message': 'Salida registrada correctamente', 'data': producto_schema.dump(producto)})


@inventario_bp.route('/productos/<int:id>/stock', methods=['PUT'])
@_solo_admin
def actualizar_stock(id):
    producto = Producto.query.get_or_404(id)
    data = request.get_json()
    nuevo = float(data['stock'])
    anterior = float(producto.stock or 0)
    diferencia = nuevo - anterior
    producto.stock = nuevo
    producto.fecha_edicion = _ahora()
    if diferencia:
        _registrar_movimiento(
            producto.id_producto, int(get_jwt_identity()), 'Ajuste', diferencia,
            anterior, max(0, nuevo), 'Ajuste manual de stock'
        )
    db.session.commit()
    return jsonify({'success': True, 'data': producto_schema.dump(producto)})


@inventario_bp.route('/movimientos', methods=['GET'])
@_inventario_stock
def get_movimientos():
    query = InventarioMovimiento.query
    prod = request.args.get('producto', '').strip()
    tipo = request.args.get('tipo', '').strip()
    if prod:
        like = f"%{prod.lower()}%"
        query = query.join(Producto, InventarioMovimiento.id_producto == Producto.id_producto).filter(db.func.lower(Producto.nombre).like(like))
    if tipo:
        query = query.filter(db.func.lower(InventarioMovimiento.tipo) == tipo.lower())
    movimientos = query.order_by(InventarioMovimiento.fecha.desc()).limit(500).all()
    return jsonify({'success': True, 'data': inventario_movimientos_schema.dump(movimientos)})


@inventario_bp.route('/compras', methods=['GET'])
@_solo_admin
def get_compras():
    compras = CompraInventario.query.order_by(CompraInventario.fecha.desc()).all()
    return jsonify({'success': True, 'data': compras_inventario_schema.dump(compras)})


@inventario_bp.route('/compras/<int:id>', methods=['GET'])
@_solo_admin
def get_compra(id):
    compra = CompraInventario.query.get_or_404(id)
    return jsonify({'success': True, 'data': compra_inventario_schema.dump(compra)})


@inventario_bp.route('/compras', methods=['POST'])
@_solo_admin
def crear_compra():
    data = request.get_json()
    detalle = data.get('detalle') or []
    if not detalle:
        return jsonify({'success': False, 'error': 'Agrega al menos un producto a la compra'}), 400
    id_proveedor = data.get('id_proveedor')
    if id_proveedor and not db.session.get(Proveedor, id_proveedor):
        return jsonify({'success': False, 'error': 'Selecciona un proveedor válido para la compra'}), 400

    usuario_id = int(get_jwt_identity())
    n_hoy = CompraInventario.query.filter(
        db.func.date(CompraInventario.fecha) == date.today()
    ).count() + 1
    codigo = f"COMPRA-{date.today().strftime('%Y%m%d')}-{uuid.uuid4().hex[:10]}"

    compra = CompraInventario(
        codigo=codigo,
        id_proveedor=id_proveedor,
        id_usuario=usuario_id,
        total_compra=0,
        notas=data.get('notas', ''),
        estado='Completada',
        fecha=_ahora()
    )
    db.session.add(compra)
    db.session.flush()

    total = 0
    for linea in detalle:
        id_producto = linea.get('id_producto')
        producto = Producto.query.get(id_producto)
        if not producto:
            db.session.rollback()
            return jsonify({'success': False, 'error': 'Producto no encontrado para la compra'}), 400
        cantidad = float(linea.get('cantidad') or 0)
        precio = float(linea.get('precio_unitario') or 0)
        subtotal = cantidad * precio
        total += subtotal
        det = DetalleCompraInventario(
            id_compra=compra.id_compra,
            id_producto=producto.id_producto,
            cantidad=cantidad,
            precio_unitario=precio,
        )
        db.session.add(det)
        anterior = float(producto.stock or 0)
        posterior = anterior + cantidad
        producto.stock = posterior
        producto.fecha_edicion = _ahora()

        pendientes = SolicitudInsumo.query.filter_by(
            id_producto=producto.id_producto, estado='Pendiente'
        ).all()
        disponible = cantidad
        for s in sorted(pendientes, key=lambda item: item.fecha):
            if s.cantidad > disponible:
                continue
            disponible -= s.cantidad
            s.estado = 'Atendida'
            s.respuesta = f'Stock repuesto con la compra {codigo}'
            crear_notificacion(
                s.id_usuario,
                'Solicitud de insumo atendida',
                f'{producto.nombre}: tu solicitud fue atendida con la compra {codigo}.'
            )

        _registrar_movimiento(
            producto.id_producto, usuario_id, 'Entrada', cantidad,
            anterior, posterior, f'Ingreso por compra {codigo}',
            id_compra=compra.id_compra
        )

    compra.total_compra = total
    db.session.add(ActividadUsuario(
        id_usuario=usuario_id,
        accion=f'Registró compra de inventario {codigo}',
        fecha=_ahora()
    ))
    db.session.commit()
    return jsonify({'success': True, 'data': compra_inventario_schema.dump(compra)}), 201


@inventario_bp.route('/compras/<int:id>', methods=['DELETE'])
@_solo_admin
def eliminar_compra(id):
    compra = CompraInventario.query.get_or_404(id)
    if compra.estado != 'Completada':
        return jsonify({'success': False, 'error': 'La compra ya fue anulada'}), 400

    usuario_id = int(get_jwt_identity())
    for det in compra.detalle:
        producto = Producto.query.get(det.id_producto)
        if producto:
            anterior = float(producto.stock or 0)
            if anterior < det.cantidad:
                db.session.rollback()
                return jsonify(success=False, error='No se puede anular: parte del stock ya fue utilizado.'), 409
            posterior = anterior - det.cantidad
            producto.stock = posterior
            producto.fecha_edicion = _ahora()
            _registrar_movimiento(
                det.id_producto, usuario_id, 'Salida', -det.cantidad,
                anterior, posterior, f'Anulación de compra {compra.codigo} (reversa de stock)',
                id_compra=compra.id_compra
            )
        else:
            _registrar_movimiento(
                det.id_producto, usuario_id, 'Salida', -det.cantidad,
                0, 0, f'Anulación de compra {compra.codigo} (reversa de stock)',
                id_compra=compra.id_compra
            )

    compra.estado = 'Anulada'
    db.session.add(ActividadUsuario(
        id_usuario=usuario_id,
        accion=f'Anuló compra de inventario {compra.codigo}',
        fecha=_ahora()
    ))
    db.session.commit()
    return jsonify({'success': True, 'message': 'Compra anulada y stock revertido'})


@inventario_bp.route('/inversiones', methods=['GET'])
@_solo_admin
def get_inversiones():
    inversiones = Inversion.query.order_by(Inversion.fecha.desc()).all()
    return jsonify({'success': True, 'data': inversiones_schema.dump(inversiones)})


@inventario_bp.route('/inversiones', methods=['POST'])
@_solo_admin
def crear_inversion():
    data = request.get_json()
    inversion = Inversion(
        descripcion=data['descripcion'],
        monto=data['monto'],
        fecha=_ahora(),
        id_proveedor=data.get('id_proveedor'),
        notas=data.get('notas', '')
    )
    db.session.add(inversion)
    db.session.commit()
    return jsonify({'success': True, 'data': inversion_schema.dump(inversion)})


@inventario_bp.route('/categorias', methods=['GET'])
@_inventario_stock
def get_categorias():
    categorias = Categoria.query.all()
    return jsonify({'success': True, 'data': [{'id_categoria': c.id_categoria, 'nombre': c.nombre} for c in categorias]})


@inventario_bp.route('/categorias', methods=['POST'])
@_solo_admin
def crear_categoria():
    data = request.get_json()
    categoria = Categoria(nombre=data['nombre'], fecha_creacion=datetime.now())
    db.session.add(categoria)
    db.session.commit()
    return jsonify({'success': True, 'data': {'id_categoria': categoria.id_categoria, 'nombre': categoria.nombre}})


@inventario_bp.route('/proveedores', methods=['GET'])
@_solo_admin
def get_proveedores():
    proveedores = Proveedor.query.all()
    return jsonify({'success': True, 'data': [{'id_proveedor': p.id_proveedor, 'nombre': p.nombre} for p in proveedores]})


@inventario_bp.route('/proveedores', methods=['POST'])
@_solo_admin
def crear_proveedor():
    data = request.get_json()
    proveedor = Proveedor(
        nombre=data['nombre'],
        ruc=data.get('ruc') or None,
        telefono=data.get('telefono') or None,
        correo=data.get('correo') or None,
        direccion=data.get('direccion') or None,
        estado=True,
        fecha_creacion=_ahora()
    )
    db.session.add(proveedor)
    db.session.commit()
    return jsonify({'success': True, 'data': {'id_proveedor': proveedor.id_proveedor, 'nombre': proveedor.nombre}})