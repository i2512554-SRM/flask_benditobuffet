from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Producto, Inversion, Categoria, Proveedor
from schemas.inventario import producto_schema, productos_schema, inversion_schema, inversiones_schema

inventario_bp = Blueprint('inventario', __name__)

@inventario_bp.route('/productos', methods=['GET'])
@jwt_required()
def get_productos():
    productos = Producto.query.all()
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
    categoria = Categoria(nombre=data['nombre'])
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