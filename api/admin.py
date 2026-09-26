from api.fechas import utc, limites_dia, LIMA, ahora
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity
from datetime import date, timedelta
from bd import db
from api.roles import ADMIN, admin_required
from schemas.admin import (roles_schema, actividades_schema, adelantos_admin_schema, intentos_login_schema,
                           bloqueos_login_schema, actividad_reciente_schema)
from models import Rol, Usuario, TransaccionCaja, CierreCaja, Adelanto, ActividadUsuario, IntentoLogin, BloqueoLogin, Producto, SolicitudInsumo, PagoEmpleado, Inversion, crear_notificacion

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


def _json_objeto():
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else None


def _limite_consulta(predeterminado, maximo):
    valor = request.args.get('limit')
    if valor is None:
        return predeterminado
    try:
        limite = int(valor)
    except (TypeError, ValueError):
        return None
    return limite if 1 <= limite <= maximo else None

def _usuarios_por_id(ids):
    ids = {i for i in ids if i is not None}
    if not ids:
        return {}
    return {u.id_usuario: u for u in Usuario.query.filter(Usuario.id_usuario.in_(ids)).all()}

@admin_bp.route('/panel-stats', methods=['GET'])
@admin_required
def get_panel_stats():
    from api.fechas import ahora, LIMA, periodo_financiero
    from api.caja import _movimientos, _totales
    inicio, fin, _ = periodo_financiero('mes', ahora().astimezone(LIMA).date())
    total = _totales(_movimientos(inicio, fin).all())
    return jsonify(success=True, data={'ventas_mes': total['ventas'], 'egresos_mes': total['gastos'], 'neto_mes': total['neto']})


@admin_bp.route('/roles', methods=['GET'])
@admin_required
def listar_roles():
    roles = Rol.query.order_by(Rol.id_rol).all()
    totales = dict(db.session.query(Usuario.id_rol, db.func.count(Usuario.id_usuario)).group_by(Usuario.id_rol).all())
    data = [{**fila, 'total_usuarios': totales.get(r.id_rol, 0)} for fila, r in zip(roles_schema.dump(roles), roles)]
    return jsonify({'success': True, 'data': data})


@admin_bp.route('/actividad', methods=['GET'])
@admin_required
def listar_actividad():
    limite = _limite_consulta(100, 500)
    if limite is None:
        return jsonify({'success': False, 'error': 'El límite debe ser un entero entre 1 y 500'}), 400
    registros = ActividadUsuario.query.order_by(ActividadUsuario.fecha.desc()).limit(limite).all()
    usuarios = _usuarios_por_id(a.id_usuario for a in registros)
    data = []
    for fila, a in zip(actividades_schema.dump(registros), registros):
        emp = usuarios.get(a.id_usuario)
        fila.update(usuario=f"{emp.nombres} {emp.apellido}" if emp else 'Desconocido', correo=emp.correo if emp else '-')
        data.append(fila)
    return jsonify({'success': True, 'data': data})


@admin_bp.route('/alertas-resumen', methods=['GET'])
@admin_required
def alertas_resumen():
    umbral = 10
    activos = Producto.query.filter(Producto.estado.is_(True))
    stock_bajo = activos.filter(Producto.stock > 0, Producto.stock < umbral).count()
    agotados = activos.filter(db.or_(Producto.stock <= 0, Producto.stock.is_(None))).count()
    adelantos_pendientes = Adelanto.query.filter(Adelanto.estado == 'Pendiente').count()
    solicitudes_pendientes = SolicitudInsumo.query.filter(SolicitudInsumo.estado == 'Pendiente').count()
    pagos_pendientes = PagoEmpleado.query.filter(PagoEmpleado.estado == 'Pendiente').count()
    instante = ahora()
    bloqueos_activos = BloqueoLogin.query.filter(
        BloqueoLogin.bloqueado_hasta.isnot(None),
        BloqueoLogin.bloqueado_hasta > instante
    ).count()
    hoy = instante.astimezone(LIMA).date()
    inicio, fin = limites_dia(hoy)
    movimientos_hoy = TransaccionCaja.query.filter(
        TransaccionCaja.fecha >= inicio, TransaccionCaja.fecha < fin
    ).count()
    inicio_mes = limites_dia(date(hoy.year, hoy.month, 1))[0]
    siguiente_mes = date(hoy.year + 1, 1, 1) if hoy.month == 12 else date(hoy.year, hoy.month + 1, 1)
    fin_mes = limites_dia(siguiente_mes)[0]
    pagos_mes = PagoEmpleado.query.filter(
        PagoEmpleado.estado == 'Pagado',
        PagoEmpleado.fecha_pago >= inicio_mes,
        PagoEmpleado.fecha_pago < fin_mes
    ).count()
    empleados_activos = Usuario.query.filter(Usuario.estado == True, Usuario.id_rol != ADMIN).count()
    from api.caja import _abierta
    caja_pendiente_cierre = _abierta() is not None
    return jsonify({'success': True, 'data': {
        'stock_bajo': stock_bajo,
        'agotados': agotados,
        'adelantos_pendientes': adelantos_pendientes,
        'solicitudes_pendientes': solicitudes_pendientes,
        'pagos_pendientes': pagos_pendientes,
        'bloqueos_activos': bloqueos_activos,
        'movimientos_hoy': movimientos_hoy,
        'empleados_activos': empleados_activos,
        'pagos_mes': pagos_mes,
        'caja_pendiente_cierre': caja_pendiente_cierre,
    }})


@admin_bp.route('/actividad-reciente', methods=['GET'])
@admin_required
def actividad_reciente():
    limite = _limite_consulta(10, 50)
    if limite is None:
        return jsonify({'success': False, 'error': 'El límite debe ser un entero entre 1 y 50'}), 400
    items = []

    pagos = PagoEmpleado.query.options(db.joinedload(PagoEmpleado.usuario_empleado)).order_by(PagoEmpleado.fecha_pago.desc()).limit(limite).all()
    for p in pagos:
        emp = p.usuario_empleado
        nombre = f"{emp.nombres} {emp.apellido}".strip() if emp else 'Empleado'
        items.append({
            'tipo': 'pago',
            'titulo': f'Pago {"registrado" if p.estado == "Pagado" else p.estado.lower()}',
            'descripcion': f'S/ {p.monto:.2f} a {nombre}',
            'fecha': p.fecha_pago,
            'icono': 'money',
        })

    cierres = CierreCaja.query.filter(CierreCaja.estado == 'cerrada').order_by(CierreCaja.fecha_cierre.desc()).limit(limite).all()
    cajeras = _usuarios_por_id(c.id_usuario for c in cierres)
    for c in cierres:
        emp = cajeras.get(c.id_usuario)
        nombre = f"{emp.nombres} {emp.apellido}".strip() if emp else 'Cajera'
        items.append({
            'tipo': 'cierre_caja',
            'titulo': 'Cierre de caja',
            'descripcion': f'Ventas S/ {float(c.total_ventas or 0):.2f} · Saldo S/ {float(c.neto or 0):.2f} por {nombre}',
            'fecha': c.fecha_cierre or c.fecha,
            'icono': 'cash-register',
        })

    adelantos = Adelanto.query.options(db.joinedload(Adelanto.usuario_adelanto)).order_by(Adelanto.fecha.desc()).limit(limite).all()
    for a in adelantos:
        emp = a.usuario_adelanto
        nombre = f"{emp.nombres} {emp.apellido}".strip() if emp else 'Empleado'
        items.append({
            'tipo': 'adelanto',
            'titulo': f'Solicitud de adelanto {a.estado.lower()}',
            'descripcion': f'S/ {a.monto:.2f} solicitado por {nombre}',
            'fecha': a.fecha_gestion or a.fecha,
            'icono': 'piggy-bank',
        })

    solicitudes = SolicitudInsumo.query.options(db.joinedload(SolicitudInsumo.producto_rel), db.joinedload(SolicitudInsumo.usuario_solicitud)).filter(SolicitudInsumo.estado == 'Pendiente').order_by(SolicitudInsumo.fecha.desc()).limit(limite).all()
    for s in solicitudes:
        items.append({
            'tipo': 'solicitud_insumo',
            'titulo': 'Solicitud de insumo',
            'descripcion': f'{s.cantidad:g} × {s.producto} solicitado por {s.solicitante or "cocina"}',
            'fecha': s.fecha,
            'icono': 'box-open',
        })

    inversiones = Inversion.query.options(db.joinedload(Inversion.proveedor_rel)).order_by(Inversion.fecha.desc()).limit(limite).all()
    for i in inversiones:
        items.append({
            'tipo': 'inversion',
            'titulo': 'Inversión anulada' if i.estado == 'Anulada' else 'Inversión registrada',
            'descripcion': f'S/ {i.monto:.2f} — {i.descripcion}' + (f' ({i.proveedor})' if i.proveedor else ''),
            'fecha': i.fecha,
            'icono': 'chart-line',
        })

    items.sort(key=lambda x: utc(x['fecha']).timestamp() if x['fecha'] else 0, reverse=True)
    data = actividad_reciente_schema.dump(items[:limite])
    return jsonify({'success': True, 'data': data})


@admin_bp.route('/adelantos', methods=['GET'])
@admin_required
def listar_solicitudes():
    solicitudes = Adelanto.query.options(db.joinedload(Adelanto.usuario_adelanto)).order_by(Adelanto.fecha.desc()).all()
    return jsonify({'success': True, 'data': adelantos_admin_schema.dump(solicitudes)})


@admin_bp.route('/adelantos/<int:id_adelanto>', methods=['PUT'])
@admin_required
def gestionar_solicitud(id_adelanto):
    adelanto = Adelanto.query.filter_by(id_adelanto=id_adelanto).with_for_update().first()
    if not adelanto:
        return jsonify({'success': False, 'error': 'Solicitud no encontrada'}), 404
    if adelanto.estado != 'Pendiente':
        return jsonify(success=False, error='Esta solicitud ya fue resuelta o cancelada.'), 409

    data = _json_objeto()
    if data is None:
        return jsonify(success=False, error='El cuerpo debe ser un objeto JSON.'), 400
    accion_recibida = data.get('accion') or ''
    respuesta_recibida = data.get('respuesta') or ''
    if not isinstance(accion_recibida, str) or not isinstance(respuesta_recibida, str):
        return jsonify(success=False, error='La acción o la respuesta no es válida.'), 400
    accion = accion_recibida.strip().lower()
    respuesta = respuesta_recibida.strip()
    if len(respuesta) > 300:
        return jsonify(success=False, error='La respuesta admite hasta 300 caracteres.'), 400

    if accion == 'aprobar':
        adelanto.estado = 'Aprobado'
    elif accion == 'rechazar':
        adelanto.estado = 'Rechazado'
    else:
        return jsonify({'success': False, 'error': 'Acción no válida'}), 400

    adelanto.respuesta_admin = respuesta if respuesta else None
    adelanto.fecha_gestion = ahora()
    crear_notificacion(
        adelanto.id_usuario,
        f'Solicitud de adelanto {adelanto.estado}',
        f'Tu adelanto de S/ {adelanto.monto:.2f} fue {adelanto.estado.lower()}.'
        + (f' Respuesta: {respuesta}' if respuesta else '')
    )
    db.session.commit()

    try:
        admin_id = int(get_jwt_identity())
        accion_act = ActividadUsuario(id_usuario=admin_id, accion=f"{accion.capitalize()} adelanto #{id_adelanto}", fecha=ahora())
        db.session.add(accion_act)
        db.session.commit()
    except Exception:
        db.session.rollback()

    return jsonify({'success': True, 'message': f'Adelanto {adelanto.estado.lower()} correctamente'})

@admin_bp.route('/seguridad', methods=['GET'])
@admin_required
def get_seguridad():
    instante = ahora()
    dias = request.args.get('dias', 7, type=int)
    limite = instante - timedelta(days=max(1, min(dias, 90)))

    intentos = IntentoLogin.query.options(db.joinedload(IntentoLogin.usuario_rel)).filter(IntentoLogin.fecha >= limite).order_by(IntentoLogin.fecha.desc()).limit(200).all()
    intentos_data = intentos_login_schema.dump(intentos)

    bloqueos = BloqueoLogin.query.options(db.joinedload(BloqueoLogin.usuario_rel).joinedload(Usuario.rol)).filter(
        BloqueoLogin.bloqueado_hasta.isnot(None),
        BloqueoLogin.bloqueado_hasta > instante
    ).order_by(BloqueoLogin.intentos.desc()).all()
    bloqueos_data = [{**fila, 'activo': b.bloqueado_hasta is not None and utc(b.bloqueado_hasta) > instante}
                     for fila, b in zip(bloqueos_login_schema.dump(bloqueos), bloqueos)]

    resumen = {
        'exitos': IntentoLogin.query.filter(IntentoLogin.resultado == 'exito', IntentoLogin.fecha >= limite).count(),
        'fallos': IntentoLogin.query.filter(IntentoLogin.resultado == 'fallo', IntentoLogin.fecha >= limite).count(),
        'bloqueados': IntentoLogin.query.filter(IntentoLogin.resultado == 'bloqueado', IntentoLogin.fecha >= limite).count(),
        'bloqueos_activos': sum(
            1 for b in bloqueos
            if b.bloqueado_hasta is not None and utc(b.bloqueado_hasta) > instante
        ),
    }

    return jsonify({'success': True, 'data': {
        'resumen': resumen,
        'intentos': intentos_data,
        'bloqueos': bloqueos_data,
    }})

@admin_bp.route('/seguridad/desbloquear', methods=['POST'])
@admin_required
def desbloquear():
    data = _json_objeto()
    if data is None:
        return jsonify(success=False, error='El cuerpo debe ser un objeto JSON.'), 400
    usuario_recibido = data.get('usuario') or ''
    if not isinstance(usuario_recibido, str):
        return jsonify(success=False, error='Usuario no válido'), 400
    usuario = usuario_recibido.strip()
    if not usuario:
        return jsonify({'success': False, 'error': 'Usuario requerido'}), 400
    for b in BloqueoLogin.query.filter(BloqueoLogin.usuario == usuario).all():
        db.session.delete(b)
    db.session.commit()
    return jsonify({'success': True, 'message': f'Bloqueos de {usuario} eliminados'})
