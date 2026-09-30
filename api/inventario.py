from api.validaciones import numero, cantidad_decimal
from api.idempotencia import normalizar_clave
from api.roles import ADMIN, ROLES_INVENTARIO
from api.cocina import _estado_stock, STOCK_BAJO_DEFECTO
from api.fechas import ahora, iso_utc, limites_dia, LIMA
from models import AtencionInsumo
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
import uuid
import re
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
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
    return ahora()


def _serializar_datetime(schema, objeto, *campos):
    data = schema.dump(objeto)
    for campo in campos:
        data[campo] = iso_utc(getattr(objeto, campo, None))
    return data


def _serializar_datetime_lista(schema, objetos, *campos):
    data = schema.dump(objetos)
    for item, objeto in zip(data, objetos):
        for campo in campos:
            item[campo] = iso_utc(getattr(objeto, campo, None))
    return data


def _serializar_producto(producto):
    return _serializar_datetime(
        producto_schema, producto, 'fecha_registro', 'fecha_edicion'
    )


def _json_objeto():
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else None


def _texto(data, campo, maximo=None, obligatorio=False):
    valor = data.get(campo)
    if valor is None:
        if obligatorio:
            raise ValueError()
        return None
    if not isinstance(valor, str):
        raise ValueError()
    valor = valor.strip()
    if (obligatorio and not valor) or (maximo is not None and len(valor) > maximo):
        raise ValueError()
    return valor or None


def _decimal_campo(valor, escala, maximo, permitir_nulo=False):
    if valor in (None, '') and permitir_nulo:
        return None
    try:
        numero_decimal = Decimal(str(valor))
        unidad = Decimal(1).scaleb(-escala)
        if (
            not numero_decimal.is_finite()
            or numero_decimal < 0
            or numero_decimal > Decimal(maximo)
            or numero_decimal.quantize(unidad) != numero_decimal
        ):
            raise ValueError()
        return numero_decimal
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError()


def _requiere_roles(*roles):
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            uid = int(get_jwt_identity())
            u = db.session.get(Usuario, uid)
            if not u or not u.estado or u.id_rol not in roles:
                return jsonify({'success': False, 'error': 'Acceso restringido a inventario'}), 403
            if request.method in ('POST', 'PUT', 'DELETE'):
                if db.engine.dialect.name == 'postgresql':
                    db.session.execute(text('SELECT pg_advisory_xact_lock(72451002)'))
                recibido = request.get_json(silent=True)
                data = recibido if isinstance(recibido, dict) else {}
                try:
                    for campo in ('stock', 'precio', 'monto', 'cantidad', 'costo'):
                        if campo in data and data[campo] is not None:
                            numero(data[campo], .000001 if campo in ('monto', 'cantidad') else 0)
                            if campo in ('stock', 'cantidad'):
                                cantidad_decimal(data[campo])
                    for linea in data.get('detalle') or []:
                        numero(linea.get('cantidad'), .000001)
                        cantidad_decimal(linea.get('cantidad'))
                        numero(linea.get('precio_unitario'), 0)
                except (ValueError, TypeError, AttributeError):
                    return jsonify(success=False, error='Revisa cantidades y precios: deben ser números válidos, sin negativos.'), 400
            return fn(*args, **kwargs)
        return wrapper
    return decorator


_solo_admin = _requiere_roles(ADMIN)
_inventario_stock = _requiere_roles(*ROLES_INVENTARIO)


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
                          stock_posterior, motivo, observacion=None, id_compra=None,
                          clave_operacion=None):
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
        clave_operacion=clave_operacion,
        fecha=_ahora()
    ))


def _costo_promedio(costo_actual, stock_actual, cantidad, precio):
    if costo_actual is None or stock_actual <= 0:
        return Decimal(str(precio)).quantize(Decimal('.001'), rounding=ROUND_HALF_UP)
    total = stock_actual * Decimal(str(costo_actual)) + cantidad * Decimal(str(precio))
    return (total / (stock_actual + cantidad)).quantize(Decimal('.001'), rounding=ROUND_HALF_UP)


def _costo_sin_compra(costo_actual, stock_actual, cantidad, precio):
    restante = stock_actual - cantidad
    if costo_actual is None or restante <= 0:
        return costo_actual
    valor = stock_actual * Decimal(str(costo_actual)) - cantidad * Decimal(str(precio))
    if valor <= 0:
        return costo_actual
    return (valor / restante).quantize(Decimal('.001'), rounding=ROUND_HALF_UP)


def _clave_o_error(data):
    try:
        return normalizar_clave(data), None
    except ValueError as error:
        return None, (jsonify({'success': False, 'error': str(error)}), 400)


def _movimiento_repetido(clave, producto, uid, tipo, cantidad, motivo):
    if not clave:
        return None
    existente = InventarioMovimiento.query.filter_by(clave_operacion=clave).first()
    if not existente:
        return None
    esperada = cantidad if tipo == 'Entrada' else -cantidad
    coincide = (
        existente.id_producto == producto.id_producto and existente.id_usuario == uid
        and existente.tipo == tipo and cantidad_decimal(existente.cantidad, existente=True) == esperada
        and (existente.motivo or '') == motivo
    )
    if not coincide:
        return jsonify({'success': False, 'error': 'El identificador ya pertenece a otra operación.'}), 409
    return jsonify({'success': True, 'repetida': True,
        'message': 'La operación ya estaba registrada', 'data': _serializar_producto(producto)})


@inventario_bp.route('/resumen', methods=['GET'])
@_inventario_stock
def get_resumen():
    total_inventario = db.session.query(
        db.func.coalesce(db.func.sum(Producto.costo * Producto.stock), 0)
    ).filter(Producto.estado.is_(True), Producto.costo.isnot(None)).scalar() or 0
    equipamiento = db.session.query(
        db.func.coalesce(db.func.sum(Producto.costo * Producto.stock), 0)
    ).join(Categoria, Producto.id_categoria == Categoria.id_categoria).filter(
        Producto.estado.is_(True), Producto.costo.isnot(None),
        db.func.lower(Categoria.nombre).like('%equipamiento%')
    ).scalar() or 0

    hoy = ahora().astimezone(LIMA).date()
    inicio_mes = limites_dia(hoy.replace(day=1))[0]
    fin_mes = limites_dia(hoy)[1]
    vigentes = Inversion.query.filter(Inversion.estado != 'Anulada')
    inversiones_mes = db.session.query(
        db.func.coalesce(db.func.sum(Inversion.monto), 0)
    ).filter(Inversion.estado != 'Anulada', Inversion.fecha >= inicio_mes, Inversion.fecha < fin_mes).scalar() or 0
    compras_mes = db.session.query(db.func.coalesce(db.func.sum(CompraInventario.total_compra), 0)).filter(
        CompraInventario.fecha >= inicio_mes, CompraInventario.fecha < fin_mes,
        CompraInventario.estado == 'Completada').scalar() or 0
    inversiones_mes += compras_mes
    inversiones_mes_cantidad = vigentes.filter(
        Inversion.fecha >= inicio_mes, Inversion.fecha < fin_mes
    ).count()
    compras_mes_cantidad = CompraInventario.query.filter(
        CompraInventario.fecha >= inicio_mes, CompraInventario.fecha < fin_mes,
        CompraInventario.estado == 'Completada').count()
    productos_mes = Producto.query.filter(
        Producto.fecha_registro >= inicio_mes, Producto.fecha_registro < fin_mes
    ).count()

    ultima = vigentes.order_by(Inversion.fecha.desc(), Inversion.id_inversion.desc()).first()
    ultima_inversion = {
        'id_inversion': ultima.id_inversion,
        'descripcion': ultima.descripcion,
        'monto': float(ultima.monto),
        'fecha': iso_utc(ultima.fecha),
    } if ultima else None

    estados = {'Disponible': 'disponibles', 'Stock bajo': 'stock_bajo', 'Agotado': 'agotados'}
    stock_estados = {'disponibles': 0, 'stock_bajo': 0, 'agotados': 0}
    productos_activos = Producto.query.filter(Producto.estado.is_(True)).all()
    for producto in productos_activos:
        stock_estados[estados[_estado_stock(producto.stock, STOCK_BAJO_DEFECTO)]] += 1

    return jsonify({
        'success': True,
        'data': {
            'valor_total': float(total_inventario),
            'productos_sin_costo': Producto.query.filter(
                Producto.estado.is_(True), Producto.costo.is_(None)
            ).count(),
            'inversiones_mes': float(inversiones_mes),
            'articulos_registrados': len(productos_activos),
            'productos_mes': productos_mes,
            'equipamiento_valor': float(equipamiento),
            'inversiones_mes_cantidad': inversiones_mes_cantidad + compras_mes_cantidad,
            'ultima_inversion': ultima_inversion,
            'stock_estados': stock_estados,
        }
    })


@inventario_bp.route('/valor-stock', methods=['GET'])
@_inventario_stock
def valor_stock():
    con_costo = Producto.query.filter(Producto.estado.is_(True), Producto.costo.isnot(None)).count()
    sin_costo = Producto.query.filter(Producto.estado.is_(True), Producto.costo.is_(None)).count()
    filas = db.session.query(
        Categoria.nombre,
        db.func.coalesce(db.func.sum(Producto.stock * Producto.costo), 0)

    ).join(Categoria, Producto.id_categoria == Categoria.id_categoria).filter(
        Producto.estado.is_(True), Producto.costo.isnot(None)
    ).group_by(Categoria.nombre).order_by(
        db.func.sum(Producto.stock * Producto.costo).desc()
    ).all()
    return jsonify({
        'success': True,
        'data': {
            'total_productos': con_costo + sin_costo,
            'con_costo': con_costo,
            'sin_costo': sin_costo,
            'categorias': [{'categoria': nombre, 'valor_stock': float(valor)} for nombre, valor in filas]
        }
    })


@inventario_bp.route('/inversiones/<int:id>', methods=['GET'])
@_solo_admin
def get_inversion(id):
    inversion = db.session.get(Inversion, id) or abort(404)
    return jsonify({'success': True, 'data': _serializar_datetime(
        inversion_schema, inversion, 'fecha', 'fecha_anulacion'
    )})


@inventario_bp.route('/inversiones/<int:id>', methods=['DELETE'])
@_solo_admin
def anular_inversion(id):
    inversion = Inversion.query.filter_by(id_inversion=id).with_for_update().first() or abort(404)
    if inversion.estado == 'Anulada':
        return jsonify({'success': False, 'error': 'La inversión ya fue anulada'}), 409
    inversion.estado = 'Anulada'
    inversion.fecha_anulacion = _ahora()
    db.session.add(ActividadUsuario(id_usuario=int(get_jwt_identity()),
        accion=f'Anuló la inversión #{inversion.id_inversion}: {inversion.descripcion}'[:255], fecha=_ahora()))
    db.session.commit()
    return jsonify({'success': True, 'message': 'Inversión anulada; se conserva en el historial',
                    'data': _serializar_datetime(inversion_schema, inversion, 'fecha', 'fecha_anulacion')})


@inventario_bp.route('/productos', methods=['GET'])
@_inventario_stock
def get_productos():
    query = Producto.query.options(db.joinedload(Producto.categoria_rel)).outerjoin(Categoria, Producto.id_categoria == Categoria.id_categoria)
    q = request.args.get('q', '').strip()
    cat = request.args.get('cat', '').strip()
    activos = request.args.get('activos', '').strip() == '1'
    if cat:
        query = query.filter(db.func.lower(Categoria.nombre) == cat.lower())
    if activos:
        query = query.filter(Producto.estado == True)
    if q:
        like = f"%{q.lower()}%"
        query = query.filter(db.or_(
            db.func.lower(Producto.nombre).like(like),
            db.func.lower(Categoria.nombre).like(like),
        ))
    productos = query.order_by(Producto.nombre.asc()).all()
    return jsonify({'success': True, 'data': _serializar_datetime_lista(
        productos_schema, productos, 'fecha_registro', 'fecha_edicion'
    )})


@inventario_bp.route('/productos/<int:id>', methods=['GET'])
@_inventario_stock
def get_producto(id):
    producto = db.session.get(Producto, id) or abort(404)
    return jsonify({'success': True, 'data': _serializar_producto(producto)})


@inventario_bp.route('/productos', methods=['POST'])
@_inventario_stock
def crear_producto():
    data = _json_objeto()
    if data is None:
        return jsonify({'success': False, 'error': 'Envía un objeto JSON válido'}), 400
    try:
        nombre = _texto(data, 'nombre', 200, obligatorio=True)
        unidad_valor = data.get('unidad_medida', data.get('unidad', 'Un'))
        if not isinstance(unidad_valor, str):
            raise ValueError()
        unidad = unidad_valor.strip()
        stock_inicial = cantidad_decimal(data.get('stock', 0))
        precio = _decimal_campo(data.get('precio', 0), 2, '9999999999.99')
        costo = _decimal_campo(data.get('costo'), 3, '999999999.999', permitir_nulo=True)
        descripcion = _texto(data, 'descripcion', 255)
        estado = data.get('estado', True)
        if unidad not in UNIDADES_VALIDAS or not isinstance(estado, bool):
            raise ValueError()
    except ValueError:
        return jsonify({'success': False, 'error': 'Revisa nombre, unidad, stock, precio, costo y estado del producto'}), 400

    duplicado = _uniq_nombre(nombre)
    if duplicado:
        return jsonify({
            'success': False,
            'error': "El producto ya existe en el sistema. Si deseas aumentar su cantidad, utiliza la opción 'Agregar stock'.",
            'existe': True,
            'id_producto': duplicado.id_producto
        }), 409

    id_categoria = data.get('id_categoria')
    if id_categoria in (None, ''):
        id_categoria = _categoria_por_defecto().id_categoria
    else:
        try:
            id_categoria = int(id_categoria)
        except (TypeError, ValueError):
            return jsonify({'success': False, 'error': 'Selecciona una categoría válida'}), 400
        if not db.session.get(Categoria, id_categoria):
            return jsonify({'success': False, 'error': 'Selecciona una categoría válida'}), 400

    producto = Producto(
        nombre=nombre,
        precio=precio,
        costo=costo,
        stock=stock_inicial,
        unidad_medida=unidad,
        descripcion=descripcion,
        estado=estado,
        id_categoria=id_categoria,
        fecha_registro=_ahora(),
        fecha_edicion=_ahora()
    )
    try:
        db.session.add(producto)
        db.session.flush()
        if stock_inicial > 0:
            _registrar_movimiento(
                producto.id_producto, int(get_jwt_identity()), 'Entrada', stock_inicial,
                0, stock_inicial, 'Stock inicial al crear producto'
            )
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'No se pudo registrar el producto con los datos indicados'}), 409
    return jsonify({'success': True, 'data': _serializar_producto(producto)}), 201


@inventario_bp.route('/productos/<int:id>', methods=['PUT'])
@_inventario_stock
def actualizar_producto(id):
    producto = db.session.get(Producto, id) or abort(404)
    data = _json_objeto()
    if data is None:
        return jsonify({'success': False, 'error': 'Envía un objeto JSON válido'}), 400
    try:
        nombre = _texto({'nombre': data.get('nombre', producto.nombre)}, 'nombre', 200, obligatorio=True)
        unidad_valor = data.get('unidad_medida', producto.unidad_medida)
        if not isinstance(unidad_valor, str):
            raise ValueError()
        unidad = unidad_valor.strip()
        if unidad not in UNIDADES_VALIDAS:
            raise ValueError()
        descripcion = _texto(data, 'descripcion', 255) if 'descripcion' in data else producto.descripcion
        precio = _decimal_campo(data['precio'], 2, '9999999999.99') if 'precio' in data else producto.precio
        costo = _decimal_campo(data['costo'], 3, '999999999.999', permitir_nulo=True) if 'costo' in data else producto.costo
        estado = data.get('estado', producto.estado)
        if not isinstance(estado, bool):
            raise ValueError()
    except ValueError:
        return jsonify({'success': False, 'error': 'Revisa nombre, unidad, precio, costo y estado del producto'}), 400

    duplicado = _uniq_nombre(nombre, excluir=producto.id_producto)
    if duplicado:
        return jsonify({
            'success': False,
            'error': "El producto ya existe en el sistema. Si deseas aumentar su cantidad, utiliza la opción 'Agregar stock'.",
            'existe': True,
            'id_producto': duplicado.id_producto
        }), 409

    producto.nombre = nombre
    producto.unidad_medida = unidad
    producto.descripcion = descripcion
    producto.estado = estado
    producto.precio = precio
    producto.costo = costo
    if data.get('id_categoria') not in (None, ''):
        try:
            id_categoria = int(data['id_categoria'])
        except (TypeError, ValueError):
            return jsonify({'success': False, 'error': 'Selecciona una categoría válida'}), 400
        if not db.session.get(Categoria, id_categoria):
            return jsonify({'success': False, 'error': 'Selecciona una categoría válida'}), 400
        producto.id_categoria = id_categoria
    producto.fecha_edicion = _ahora()

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'No se pudo actualizar el producto con los datos indicados'}), 409
    return jsonify({'success': True, 'data': _serializar_producto(producto)})


@inventario_bp.route('/productos/<int:id>', methods=['DELETE'])
@_solo_admin
def eliminar_producto(id):
    producto = db.session.get(Producto, id) or abort(404)
    tiene_historial = any(
        modelo.query.filter_by(id_producto=producto.id_producto).first() is not None
        for modelo in (InventarioMovimiento, SolicitudInsumo, DetalleCompraInventario)
    )
    if not tiene_historial:
        try:
            db.session.delete(producto)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Producto eliminado'})
        except IntegrityError:
            db.session.rollback()
            producto = db.session.get(Producto, id) or abort(404)
    producto.estado = False
    producto.fecha_edicion = _ahora()
    db.session.commit()
    return jsonify({'success': True, 'message': 'Producto desactivado (conserva su historial)', 'data': _serializar_producto(producto)})


@inventario_bp.route('/productos/<int:id>/stock/entrada', methods=['POST'])
@_inventario_stock
def entrada_stock(id):
    producto = db.session.get(Producto, id) or abort(404)
    if not producto.estado:
        return jsonify({'success': False, 'error': 'El producto está inactivo y no puede recibir stock'}), 400
    data = _json_objeto()
    if data is None:
        return jsonify({'success': False, 'error': 'Envía un objeto JSON válido'}), 400
    try:
        cantidad = cantidad_decimal(data.get('cantidad', 0))
    except (TypeError, ValueError):
        cantidad = 0
    if cantidad <= 0:
        return jsonify({'success': False, 'error': 'La cantidad a agregar debe ser mayor a cero'}), 400

    try:
        motivo = _texto(data, 'motivo', 255) or 'Ingreso de stock'
        observacion = _texto(data, 'observacion', 255)
    except ValueError:
        return jsonify({'success': False, 'error': 'El motivo y la observación admiten hasta 255 caracteres'}), 400
    clave, error = _clave_o_error(data)
    if error:
        return error
    uid = int(get_jwt_identity())
    repetida = _movimiento_repetido(clave, producto, uid, 'Entrada', cantidad, motivo)
    if repetida:
        return repetida
    anterior = cantidad_decimal(producto.stock or 0, existente=True)
    posterior = anterior + cantidad
    producto.stock = posterior
    producto.fecha_edicion = _ahora()
    _registrar_movimiento(
        producto.id_producto, uid, 'Entrada', cantidad,
        anterior, posterior, motivo,
        observacion=observacion,
        clave_operacion=clave
    )
    db.session.commit()
    return jsonify({'success': True, 'message': 'Stock agregado correctamente', 'data': _serializar_producto(producto)})


@inventario_bp.route('/productos/<int:id>/stock/salida', methods=['POST'])
@_inventario_stock
def salida_stock(id):
    producto = db.session.get(Producto, id) or abort(404)
    if not producto.estado:
        return jsonify({'success': False, 'error': 'El producto está inactivo y no puede registrar salidas'}), 400
    data = _json_objeto()
    if data is None:
        return jsonify({'success': False, 'error': 'Envía un objeto JSON válido'}), 400
    try:
        cantidad = cantidad_decimal(data.get('cantidad', 0))
    except (TypeError, ValueError):
        cantidad = 0
    if cantidad <= 0:
        return jsonify({'success': False, 'error': 'La cantidad a retirar debe ser mayor a cero'}), 400

    try:
        motivo = _texto(data, 'motivo', 255, obligatorio=True)
        observacion = _texto(data, 'observacion', 255)
    except ValueError:
        return jsonify({'success': False, 'error': 'El motivo de la salida es obligatorio y admite hasta 255 caracteres'}), 400

    clave, error = _clave_o_error(data)
    if error:
        return error
    uid = int(get_jwt_identity())
    repetida = _movimiento_repetido(clave, producto, uid, 'Salida', cantidad, motivo)
    if repetida:
        return repetida
    anterior = cantidad_decimal(producto.stock or 0, existente=True)
    if cantidad > anterior:
        return jsonify({'success': False, 'error': 'No hay suficiente stock disponible.'}), 400
    posterior = anterior - cantidad
    producto.stock = posterior
    producto.fecha_edicion = _ahora()
    _registrar_movimiento(
        producto.id_producto, uid, 'Salida', -cantidad,
        anterior, posterior, motivo,
        observacion=observacion,
        clave_operacion=clave
    )
    db.session.commit()
    return jsonify({'success': True, 'message': 'Salida registrada correctamente', 'data': _serializar_producto(producto)})


@inventario_bp.route('/productos/<int:id>/stock', methods=['PUT'])
@_solo_admin
def actualizar_stock(id):
    producto = db.session.get(Producto, id) or abort(404)
    data = _json_objeto()
    if data is None:
        return jsonify({'success': False, 'error': 'Envía un objeto JSON válido'}), 400
    try:
        nuevo = cantidad_decimal(data.get('stock'))
    except (TypeError, ValueError):
        return jsonify({'success': False, 'error': 'El stock debe ser un número no negativo con hasta tres decimales'}), 400
    anterior = cantidad_decimal(producto.stock or 0, existente=True)
    diferencia = nuevo - anterior
    producto.stock = nuevo
    producto.fecha_edicion = _ahora()
    if diferencia:
        _registrar_movimiento(
            producto.id_producto, int(get_jwt_identity()), 'Ajuste', diferencia,
            anterior, nuevo, 'Ajuste manual de stock'
        )
    db.session.commit()
    return jsonify({'success': True, 'data': _serializar_producto(producto)})


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
    return jsonify({'success': True, 'data': _serializar_datetime_lista(
        inventario_movimientos_schema, movimientos, 'fecha'
    )})


@inventario_bp.route('/compras', methods=['GET'])
@_solo_admin
def get_compras():
    compras = CompraInventario.query.order_by(CompraInventario.fecha.desc()).all()
    return jsonify({'success': True, 'data': _serializar_datetime_lista(
        compras_inventario_schema, compras, 'fecha'
    )})


@inventario_bp.route('/compras/<int:id>', methods=['GET'])
@_solo_admin
def get_compra(id):
    compra = db.session.get(CompraInventario, id) or abort(404)
    return jsonify({'success': True, 'data': _serializar_datetime(
        compra_inventario_schema, compra, 'fecha'
    )})


@inventario_bp.route('/compras', methods=['POST'])
@_solo_admin
def crear_compra():
    data = _json_objeto()
    if data is None:
        return jsonify({'success': False, 'error': 'Envía un objeto JSON válido'}), 400
    clave, error = _clave_o_error(data)
    if error:
        return error
    if not isinstance(data.get('notas') or '', str):
        return jsonify({'success': False, 'error': 'Las notas de la compra no son válidas'}), 400
    detalle = data.get('detalle') or []
    if not isinstance(detalle, list) or not detalle:
        return jsonify({'success': False, 'error': 'Agrega al menos un producto a la compra'}), 400
    try:
        id_proveedor = int(data['id_proveedor']) if data.get('id_proveedor') else None
    except (TypeError, ValueError):
        return jsonify({'success': False, 'error': 'Selecciona un proveedor válido para la compra'}), 400
    if id_proveedor and not db.session.get(Proveedor, id_proveedor):
        return jsonify({'success': False, 'error': 'Selecciona un proveedor válido para la compra'}), 400

    usuario_id = int(get_jwt_identity())
    lineas_normalizadas = []
    cantidades_por_producto = {}
    try:
        for linea in detalle:
            cantidad = cantidad_decimal(linea.get('cantidad'))
            precio = numero(linea.get('precio_unitario'), 0)
            if cantidad <= 0 or precio >= 10000000000 or round(precio, 2) != precio:
                raise ValueError()
            id_producto = int(linea.get('id_producto'))
            lineas_normalizadas.append((id_producto, cantidad, Decimal(str(precio))))
            cantidades_por_producto[id_producto] = cantidades_por_producto.get(id_producto, Decimal('0')) + cantidad
    except (ValueError, TypeError, AttributeError):
        return jsonify({'success': False, 'error': 'Cada producto requiere cantidad positiva y precio con hasta dos decimales.'}), 400
    if clave:
        existente = CompraInventario.query.filter_by(clave_operacion=clave).first()
        if existente:
            guardadas = sorted((d.id_producto, cantidad_decimal(d.cantidad, existente=True), Decimal(str(d.precio_unitario)))
                               for d in existente.detalle)
            coincide = (existente.id_usuario == usuario_id and existente.id_proveedor == id_proveedor
                        and (existente.notas or '') == (data.get('notas') or '')
                        and guardadas == sorted(lineas_normalizadas) and existente.estado == 'Completada')
            if not coincide:
                return jsonify({'success': False, 'error': 'El identificador ya pertenece a otra operación.'}), 409
            return jsonify({'success': True, 'repetida': True,
                'data': _serializar_datetime(compra_inventario_schema, existente, 'fecha')})
    codigo = f"COMPRA-{ahora().astimezone(LIMA).strftime('%Y%m%d')}-{uuid.uuid4().hex[:10]}"

    compra = CompraInventario(
        codigo=codigo,
        id_proveedor=id_proveedor,
        id_usuario=usuario_id,
        total_compra=0,
        notas=data.get('notas', ''),
        estado='Completada',
        clave_operacion=clave,
        fecha=_ahora()
    )
    db.session.add(compra)
    db.session.flush()

    total = Decimal('0.00')
    productos_compra = {}
    for id_producto, cantidad, precio in lineas_normalizadas:
        producto = db.session.get(Producto, id_producto)
        if not producto:
            db.session.rollback()
            return jsonify({'success': False, 'error': 'Producto no encontrado para la compra'}), 400
        productos_compra[id_producto] = producto
        subtotal = (cantidad * precio).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        total += subtotal
        det = DetalleCompraInventario(
            id_compra=compra.id_compra,
            id_producto=producto.id_producto,
            cantidad=cantidad,
            precio_unitario=precio,
        )
        db.session.add(det)
        anterior = cantidad_decimal(producto.stock or 0, existente=True)
        producto.costo = _costo_promedio(producto.costo, anterior, cantidad, precio)
        posterior = anterior + cantidad
        producto.stock = posterior
        producto.fecha_edicion = _ahora()

        _registrar_movimiento(
            producto.id_producto, usuario_id, 'Entrada', cantidad,
            anterior, posterior, f'Ingreso por compra {codigo}',
            id_compra=compra.id_compra
        )

    for id_producto, disponible in cantidades_por_producto.items():
        producto = productos_compra[id_producto]
        pendientes = SolicitudInsumo.query.filter_by(
            id_producto=id_producto, estado='Pendiente'
        ).all()
        for s in sorted(pendientes, key=lambda item: item.fecha):
            requerida = cantidad_decimal(s.cantidad, existente=True)
            if requerida > disponible:
                continue
            disponible -= requerida
            s.estado = 'Atendida'
            db.session.add(AtencionInsumo(id_compra=compra.id_compra, id_solicitud=s.id_solicitud))
            s.respuesta = f'Stock repuesto con la compra {codigo}'
            crear_notificacion(
                s.id_usuario,
                'Solicitud de insumo atendida',
                f'{producto.nombre}: tu solicitud fue atendida con la compra {codigo}.'
            )

    compra.total_compra = total
    db.session.add(ActividadUsuario(
        id_usuario=usuario_id,
        accion=f'Registró compra de inventario {codigo}',
        fecha=_ahora()
    ))
    db.session.commit()
    return jsonify({'success': True, 'data': _serializar_datetime(
        compra_inventario_schema, compra, 'fecha'
    )}), 201


@inventario_bp.route('/compras/<int:id>', methods=['DELETE'])
@_solo_admin
def eliminar_compra(id):
    compra = db.session.get(CompraInventario, id) or abort(404)
    if compra.estado != 'Completada':
        return jsonify({'success': False, 'error': 'La compra ya fue anulada'}), 400

    usuario_id = int(get_jwt_identity())
    for det in compra.detalle:
        producto = db.session.get(Producto, det.id_producto)
        if producto:
            anterior = cantidad_decimal(producto.stock or 0, existente=True)
            cantidad = cantidad_decimal(det.cantidad, existente=True)
            if anterior < cantidad:
                db.session.rollback()
                return jsonify(success=False, error='No se puede anular: parte del stock ya fue utilizado.'), 409
            posterior = anterior - cantidad
            producto.costo = _costo_sin_compra(producto.costo, anterior, cantidad, det.precio_unitario)
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

    for atencion in AtencionInsumo.query.filter_by(id_compra=id).all():
        solicitud = db.session.get(SolicitudInsumo, atencion.id_solicitud)
        if solicitud and solicitud.estado == 'Atendida':
            solicitud.estado = 'Pendiente'
            solicitud.respuesta = f'Pendiente nuevamente: se anuló la compra {compra.codigo}'
            crear_notificacion(solicitud.id_usuario, 'Solicitud de insumo pendiente', solicitud.respuesta)
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
    return jsonify({'success': True, 'data': _serializar_datetime_lista(
        inversiones_schema, inversiones, 'fecha', 'fecha_anulacion'
    )})


@inventario_bp.route('/inversiones', methods=['POST'])
@_solo_admin
def crear_inversion():
    data = _json_objeto()
    if data is None:
        return jsonify({'success': False, 'error': 'Envía un objeto JSON válido'}), 400
    try:
        descripcion = _texto(data, 'descripcion', 255, obligatorio=True)
        notas = _texto(data, 'notas') or ''
        monto = Decimal(str(data.get('monto')))
        if not monto.is_finite() or monto <= 0 or monto >= Decimal('10000000000') or monto.quantize(Decimal('.01')) != monto:
            raise ValueError()
        id_proveedor = int(data['id_proveedor']) if data.get('id_proveedor') not in (None, '') else None
    except (InvalidOperation, TypeError, ValueError):
        return jsonify({'success': False, 'error': 'Indica descripción, monto positivo con hasta dos decimales y proveedor válido'}), 400
    if id_proveedor is not None:
        proveedor = db.session.get(Proveedor, id_proveedor)
        if not proveedor or not proveedor.estado:
            return jsonify({'success': False, 'error': 'Selecciona un proveedor válido'}), 400
    inversion = Inversion(
        descripcion=descripcion,
        monto=monto,
        fecha=_ahora(),
        id_proveedor=id_proveedor,
        notas=notas
    )
    try:
        db.session.add(inversion)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'No se pudo registrar la inversión con los datos indicados'}), 409
    return jsonify({'success': True, 'data': _serializar_datetime(
        inversion_schema, inversion, 'fecha'
    )})


@inventario_bp.route('/categorias', methods=['GET'])
@_inventario_stock
def get_categorias():
    categorias = Categoria.query.all()
    return jsonify({'success': True, 'data': [{'id_categoria': c.id_categoria, 'nombre': c.nombre} for c in categorias]})


@inventario_bp.route('/categorias', methods=['POST'])
@_solo_admin
def crear_categoria():
    data = _json_objeto()
    if data is None:
        return jsonify({'success': False, 'error': 'Envía un objeto JSON válido'}), 400
    try:
        nombre = _texto(data, 'nombre', 100, obligatorio=True)
    except ValueError:
        return jsonify({'success': False, 'error': 'El nombre de la categoría es obligatorio y admite hasta 100 caracteres'}), 400
    if Categoria.query.filter(db.func.lower(Categoria.nombre) == nombre.lower()).first():
        return jsonify({'success': False, 'error': 'La categoría ya existe'}), 409
    categoria = Categoria(nombre=nombre, fecha_creacion=_ahora())
    try:
        db.session.add(categoria)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'La categoría ya existe'}), 409
    return jsonify({'success': True, 'data': {'id_categoria': categoria.id_categoria, 'nombre': categoria.nombre}})


@inventario_bp.route('/proveedores', methods=['GET'])
@_solo_admin
def get_proveedores():
    proveedores = Proveedor.query.all()
    return jsonify({'success': True, 'data': [{
        'id_proveedor': p.id_proveedor,
        'nombre': p.nombre,
        'ruc': p.ruc,
        'telefono': p.telefono,
        'correo': p.correo,
        'direccion': p.direccion,
        'estado': p.estado,
    } for p in proveedores]})


@inventario_bp.route('/proveedores', methods=['POST'])
@_solo_admin
def crear_proveedor():
    data = _json_objeto()
    if data is None:
        return jsonify({'success': False, 'error': 'Envía un objeto JSON válido'}), 400
    try:
        nombre = _texto(data, 'nombre', 150, obligatorio=True)
        ruc = _texto(data, 'ruc', 20)
        telefono = _texto(data, 'telefono', 20)
        correo = _texto(data, 'correo', 150)
        direccion = _texto(data, 'direccion', 255)
    except ValueError:
        return jsonify({'success': False, 'error': 'Revisa los campos y longitudes del proveedor'}), 400
    if correo and not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', correo):
        return jsonify({'success': False, 'error': 'El correo del proveedor no es válido'}), 400
    proveedor = Proveedor(
        nombre=nombre,
        ruc=ruc,
        telefono=telefono,
        correo=correo.lower() if correo else None,
        direccion=direccion,
        estado=True,
        fecha_creacion=_ahora()
    )
    try:
        db.session.add(proveedor)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'No se pudo registrar el proveedor con los datos indicados'}), 409
    return jsonify({'success': True, 'data': {
        'id_proveedor': proveedor.id_proveedor,
        'nombre': proveedor.nombre,
        'ruc': proveedor.ruc,
        'telefono': proveedor.telefono,
        'correo': proveedor.correo,
        'direccion': proveedor.direccion,
        'estado': proveedor.estado,
    }})
