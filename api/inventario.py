from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date, time, timedelta
from models import db, Producto, Inversion, Categoria, Proveedor, ActividadUsuario
from schemas.inventario import producto_schema, productos_schema, inversion_schema, inversiones_schema

inventario_bp = Blueprint('inventario', __name__)

@inventario_bp.route('/resumen', methods=['GET'])
@jwt_required()
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
@jwt_required()
def get_inversion(id):
    inversion = Inversion.query.get_or_404(id)
    return jsonify({'success': True, 'data': inversion_schema.dump(inversion)})

@inventario_bp.route('/inversiones/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar_inversion(id):
    inversion = Inversion.query.get_or_404(id)
    admin_id = int(get_jwt_identity())
    db.session.delete(inversion)
    db.session.add(ActividadUsuario(id_usuario=admin_id, accion='Eliminó compra/inversión de inventario', fecha=datetime.now()))
    db.session.commit()
    return jsonify({'success': True, 'message': 'Compra/inversión eliminada'})

@inventario_bp.route('/productos', methods=['GET'])
@jwt_required()
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
@jwt_required()
def get_producto(id):
    producto = Producto.query.get_or_404(id)
    return jsonify({'success': True, 'data': producto_schema.dump(producto)})

@inventario_bp.route('/productos', methods=['POST'])
@jwt_required()
def crear_producto():
    data = request.get_json()
    from datetime import datetime
    producto = Producto(
        nombre=data['nombre'],
        precio=data['precio'],
        stock=data.get('stock', 0),
        id_categoria=data['id_categoria'],
        fecha_registro=datetime.utcnow(),
        fecha_edicion=datetime.utcnow()
    )
    db.session.add(producto)
    db.session.commit()
    return jsonify({'success': True, 'data': producto_schema.dump(producto)})

@inventario_bp.route('/productos/<int:id>', methods=['PUT'])
@jwt_required()
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
@jwt_required()
def eliminar_producto(id):
    producto = Producto.query.get_or_404(id)
    db.session.delete(producto)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Producto eliminado'})

@inventario_bp.route('/productos/<int:id>/stock', methods=['PUT'])
@jwt_required()
def actualizar_stock(id):
    producto = Producto.query.get_or_404(id)
    data = request.get_json()
    producto.stock = data['stock']
    db.session.commit()
    return jsonify({'success': True, 'data': producto_schema.dump(producto)})

@inventario_bp.route('/inversiones', methods=['GET'])
@jwt_required()
def get_inversiones():
    inversiones = Inversion.query.order_by(Inversion.fecha.desc()).all()
    return jsonify({'success': True, 'data': inversiones_schema.dump(inversiones)})

@inventario_bp.route('/inversiones', methods=['POST'])
@jwt_required()
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
@jwt_required()
def get_categorias():
    categorias = Categoria.query.all()
    return jsonify({'success': True, 'data': [{'id_categoria': c.id_categoria, 'nombre': c.nombre} for c in categorias]})

@inventario_bp.route('/categorias', methods=['POST'])
@jwt_required()
def crear_categoria():
    data = request.get_json()
    from datetime import datetime
    categoria = Categoria(nombre=data['nombre'], fecha_creacion=datetime.now())
    db.session.add(categoria)
    db.session.commit()
    return jsonify({'success': True, 'data': {'id_categoria': categoria.id_categoria, 'nombre': categoria.nombre}})

@inventario_bp.route('/proveedores', methods=['GET'])
@jwt_required()
def get_proveedores():
    proveedores = Proveedor.query.all()
    return jsonify({'success': True, 'data': [{'id_proveedor': p.id_proveedor, 'nombre': p.nombre} for p in proveedores]})

@inventario_bp.route('/proveedores', methods=['POST'])
@jwt_required()
def crear_proveedor():
    data = request.get_json()
    from datetime import datetime
    proveedor = Proveedor(
        nombre=data['nombre'],
        ruc=data.get('ruc', ''),
        telefono=data.get('telefono', ''),
        correo=data.get('correo', ''),
        direccion=data.get('direccion', ''),
        estado=True,
        fecha_creacion=datetime.utcnow()
    )
    db.session.add(proveedor)
    db.session.commit()
    return jsonify({'success': True, 'data': {'id_proveedor': proveedor.id_proveedor, 'nombre': proveedor.nombre}})