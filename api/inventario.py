from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date, time, timedelta
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


def _inventario(fn):
    from functools import wraps

    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        uid = int(get_jwt_identity())
        u = Usuario.query.get(uid)
        if not u or u.id_rol != 1 or not u.estado:
            return jsonify({'success': False, 'error': 'Acceso restringido a administración de inventario'}), 403
        return fn(*args, **kwargs)

    return wrapper

@inventario_bp.route('/resumen', methods=['GET'])
@_inventario
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
@_inventario
def get_inversion(id):
    inversion = Inversion.query.get_or_404(id)
    return jsonify({'success': True, 'data': inversion_schema.dump(inversion)})

@inventario_bp.route('/inversiones/<int:id>', methods=['DELETE'])
@_inventario
def eliminar_inversion(id):
    inversion = Inversion.query.get_or_404(id)
    admin_id = int(get_jwt_identity())
    db.session.delete(inversion)
    db.session.add(ActividadUsuario(id_usuario=admin_id, accion='Eliminó compra/inversión de inventario', fecha=datetime.now()))
    db.session.commit()
    return jsonify({'success': True, 'message': 'Compra/inversión eliminada'})

@inventario_bp.route('/productos', methods=['GET'])
@_inventario
def get_productos():
    query = Producto.query
    q = request.args.get('q', '').strip()
    cat = request.args.get('cat', '').strip()
    if cat:
        query = query.join(Categoria, Producto.id_categoria == Categoria.id_categoria).filter(db.func.lower(Categoria.nombre) == cat.lower())
    if q:
        like = f"%{q.lower()}%"
        query = query.outerjoin(Categoria, Producto.id_categoria == Categoria.id_categoria).filter(db.or_(
            db.func.lower(Producto.nombre).like(like),
            db.func.lower(Categoria.nombre).like(like),
        ))
    productos = query.order_by(Producto.fecha_registro.desc()).all()
    return jsonify({'success': True, 'data': productos_schema.dump(productos)})

@inventario_bp.route('/productos/<int:id>', methods=['GET'])
@_inventario
def get_producto(id):
    producto = Producto.query.get_or_404(id)
    return jsonify({'success': True, 'data': producto_schema.dump(producto)})

@inventario_bp.route('/productos', methods=['POST'])
@_inventario
def crear_producto():
    data = request.get_json()
    from datetime import datetime
    stock_inicial = float(data.get('stock', 0))
    producto = Producto(
        nombre=data['nombre'],
        precio=data['precio'],
        stock=stock_inicial,
        id_categoria=data['id_categoria'],
        fecha_registro=datetime.utcnow(),
        fecha_edicion=datetime.utcnow()
    )
    db.session.add(producto)
    db.session.flush()
    if stock_inicial > 0:
        db.session.add(InventarioMovimiento(
            id_producto=producto.id_producto,
            id_usuario=int(get_jwt_identity()),
            tipo='Entrada',
            cantidad=stock_inicial,
            observacion='Stock inicial al crear producto',
            fecha=datetime.utcnow()
        ))
    db.session.commit()
    return jsonify({'success': True, 'data': producto_schema.dump(producto)})

@inventario_bp.route('/productos/<int:id>', methods=['PUT'])
@_inventario
def actualizar_producto(id):
    producto = Producto.query.get_or_404(id)
    data = request.get_json()
    from datetime import datetime
    
    producto.nombre = data.get('nombre', producto.nombre)
    producto.precio = data.get('precio', producto.precio)
    producto.stock = data.get('stock', producto.stock)
    producto.id_categoria = data.get('id_categoria', producto.id_categoria)
    producto.fecha_edicion = datetime.utcnow()
    
    db.session.commit()
    return jsonify({'success': True, 'data': producto_schema.dump(producto)})

@inventario_bp.route('/productos/<int:id>', methods=['DELETE'])
@_inventario
def eliminar_producto(id):
    producto = Producto.query.get_or_404(id)
    db.session.delete(producto)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Producto eliminado'})

@inventario_bp.route('/productos/<int:id>/stock', methods=['PUT'])
@_inventario
def actualizar_stock(id):
    producto = Producto.query.get_or_404(id)
    data = request.get_json()
    nuevo = float(data['stock'])
    diferencia = nuevo - producto.stock
    usuario_id = int(get_jwt_identity())
    producto.stock = nuevo
    if diferencia:
        db.session.add(InventarioMovimiento(
            id_producto=producto.id_producto,
            id_usuario=usuario_id,
            tipo='Ajuste',
            cantidad=abs(diferencia),
            observacion='Ajuste manual de stock',
            fecha=datetime.utcnow()
        ))
    db.session.commit()
    return jsonify({'success': True, 'data': producto_schema.dump(producto)})

@inventario_bp.route('/movimientos', methods=['GET'])
@_inventario
def get_movimientos():
    query = InventarioMovimiento.query
    prod = request.args.get('producto', '').strip()
    tipo = request.args.get('tipo', '').strip()
    if prod:
        like = f"%{prod.lower()}%"
        query = query.join(Producto, InventarioMovimiento.id_producto == Producto.id_producto).filter(db.func.lower(Producto.nombre).like(like))
    if tipo:
        query = query.filter(db.func.lower(InventarioMovimiento.tipo) == tipo.lower())
    movimientos = query.order_by(InventarioMovimiento.fecha.desc()).limit(200).all()
    return jsonify({'success': True, 'data': inventario_movimientos_schema.dump(movimientos)})

@inventario_bp.route('/compras', methods=['GET'])
@_inventario
def get_compras():
    compras = CompraInventario.query.order_by(CompraInventario.fecha.desc()).all()
    return jsonify({'success': True, 'data': compras_inventario_schema.dump(compras)})

@inventario_bp.route('/compras/<int:id>', methods=['GET'])
@_inventario
def get_compra(id):
    compra = CompraInventario.query.get_or_404(id)
    return jsonify({'success': True, 'data': compra_inventario_schema.dump(compra)})

@inventario_bp.route('/compras', methods=['POST'])
@_inventario
def crear_compra():
    data = request.get_json()
    detalle = data.get('detalle') or []
    if not detalle:
        return jsonify({'success': False, 'error': 'Agrega al menos un producto a la compra'}), 400

    usuario_id = int(get_jwt_identity())
    n_hoy = CompraInventario.query.filter(
        db.func.date(CompraInventario.fecha) == date.today()
    ).count() + 1
    codigo = f"COMPRA-{date.today().strftime('%Y%m%d')}-{n_hoy:03d}"

    compra = CompraInventario(
        codigo=codigo,
        id_proveedor=data.get('id_proveedor'),
        id_usuario=usuario_id,
        total_compra=0,
        notas=data.get('notas', ''),
        estado='Completada',
        fecha=datetime.utcnow()
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
        producto.stock = (producto.stock or 0) + cantidad
        producto.fecha_edicion = datetime.utcnow()

        pendientes = SolicitudInsumo.query.filter_by(
            id_producto=producto.id_producto, estado='Pendiente'
        ).all()
        for s in pendientes:
            s.estado = 'Atendida'
            s.respuesta = f'Stock repuesto con la compra {codigo}'
            crear_notificacion(
                s.id_usuario,
                'Solicitud de insumo atendida',
                f'{producto.nombre}: tu solicitud fue atendida con la compra {codigo}.'
            )

        db.session.add(InventarioMovimiento(
            id_producto=producto.id_producto,
            id_usuario=usuario_id,
            tipo='Entrada',
            cantidad=cantidad,
            id_compra=compra.id_compra,
            observacion=f'Ingreso por compra {codigo}',
            fecha=datetime.utcnow()
        ))

    compra.total_compra = total
    db.session.add(ActividadUsuario(
        id_usuario=usuario_id,
        accion=f'Registró compra de inventario {codigo}',
        fecha=datetime.utcnow()
    ))
    db.session.commit()
    return jsonify({'success': True, 'data': compra_inventario_schema.dump(compra)}), 201

@inventario_bp.route('/compras/<int:id>', methods=['DELETE'])
@_inventario
def eliminar_compra(id):
    compra = CompraInventario.query.get_or_404(id)
    if compra.estado != 'Completada':
        return jsonify({'success': False, 'error': 'La compra ya fue anulada'}), 400

    usuario_id = int(get_jwt_identity())
    for det in compra.detalle:
        producto = Producto.query.get(det.id_producto)
        if producto:
            producto.stock = max(0, (producto.stock or 0) - det.cantidad)
            producto.fecha_edicion = datetime.utcnow()
        db.session.add(InventarioMovimiento(
            id_producto=det.id_producto,
            id_usuario=usuario_id,
            tipo='Salida',
            cantidad=det.cantidad,
            observacion=f'Anulación de compra {compra.codigo} (reversa de stock)',
            fecha=datetime.utcnow()
        ))

    compra.estado = 'Anulada'
    compra.fecha = datetime.utcnow()
    db.session.add(ActividadUsuario(
        id_usuario=usuario_id,
        accion=f'Anuló compra de inventario {compra.codigo}',
        fecha=datetime.utcnow()
    ))
    db.session.commit()
    return jsonify({'success': True, 'message': 'Compra anulada y stock revertido'})

@inventario_bp.route('/inversiones', methods=['GET'])
@_inventario
def get_inversiones():
    inversiones = Inversion.query.order_by(Inversion.fecha.desc()).all()
    return jsonify({'success': True, 'data': inversiones_schema.dump(inversiones)})

@inventario_bp.route('/inversiones', methods=['POST'])
@_inventario
def crear_inversion():
    data = request.get_json()
    from datetime import datetime
    inversion = Inversion(
        descripcion=data['descripcion'],
        monto=data['monto'],
        fecha=datetime.utcnow(),
        id_proveedor=data.get('id_proveedor'),
        notas=data.get('notas', '')
    )
    db.session.add(inversion)
    db.session.commit()
    return jsonify({'success': True, 'data': inversion_schema.dump(inversion)})

@inventario_bp.route('/categorias', methods=['GET'])
@_inventario
def get_categorias():
    categorias = Categoria.query.all()
    return jsonify({'success': True, 'data': [{'id_categoria': c.id_categoria, 'nombre': c.nombre} for c in categorias]})

@inventario_bp.route('/categorias', methods=['POST'])
@_inventario
def crear_categoria():
    data = request.get_json()
    from datetime import datetime
    categoria = Categoria(nombre=data['nombre'], fecha_creacion=datetime.now())
    db.session.add(categoria)
    db.session.commit()
    return jsonify({'success': True, 'data': {'id_categoria': categoria.id_categoria, 'nombre': categoria.nombre}})

@inventario_bp.route('/proveedores', methods=['GET'])
@_inventario
def get_proveedores():
    proveedores = Proveedor.query.all()
    return jsonify({'success': True, 'data': [{'id_proveedor': p.id_proveedor, 'nombre': p.nombre} for p in proveedores]})

@inventario_bp.route('/proveedores', methods=['POST'])
@_inventario
def crear_proveedor():
    data = request.get_json()
    from datetime import datetime
    proveedor = Proveedor(
        nombre=data['nombre'],
        ruc=data.get('ruc') or None,
        telefono=data.get('telefono') or None,
        correo=data.get('correo') or None,
        direccion=data.get('direccion') or None,
        estado=True,
        fecha_creacion=datetime.utcnow()
    )
    db.session.add(proveedor)
    db.session.commit()
    return jsonify({'success': True, 'data': {'id_proveedor': proveedor.id_proveedor, 'nombre': proveedor.nombre}})