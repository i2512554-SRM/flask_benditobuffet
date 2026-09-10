from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date, timedelta, timezone
from calendar import monthrange
from bd import db
from models import Rol, Usuario, TransaccionCaja, CierreCaja, Adelanto, ActividadUsuario, IntentoLogin, BloqueoLogin, Producto, SolicitudInsumo, PagoEmpleado, Inversion, crear_notificacion

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

def admin_required(fn):
    from functools import wraps
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        uid = int(get_jwt_identity())
        u = Usuario.query.get(uid)
        if not u or u.id_rol != 1 or not u.estado:
            return jsonify({'success': False, 'message': 'Acceso restringido a administradores'}), 403
        return fn(*args, **kwargs)
    return wrapper

@admin_bp.route('/panel-stats', methods=['GET'])
@admin_required
def get_panel_stats():
    try:
        # Obtener mes y año actual
        now = datetime.now()
        year = now.year
        month = now.month
        
        # Calcular primer y ultimo dia del mes
        first_day = date(year, month, 1)
        last_day = date(year, month, monthrange(year, month)[1])
        
        # Obtener transacciones del mes
        transacciones = TransaccionCaja.query.filter(
            TransaccionCaja.fecha >= first_day,
            TransaccionCaja.fecha <= last_day
        ).all()
        
        # Calcular totales
        ventas_mes = sum(t.monto for t in transacciones if t.tipo == 'Venta')
        egresos_mes = sum(t.monto for t in transacciones if t.tipo == 'Gasto')
        neto_mes = ventas_mes - egresos_mes
        
        return jsonify({
            'success': True,
            'data': {
                'ventas_mes': float(ventas_mes),
                'egresos_mes': float(egresos_mes),
                'neto_mes': float(neto_mes)
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/roles', methods=['GET'])
@admin_required
def listar_roles():
    roles = Rol.query.order_by(Rol.id_rol).all()
    data = []
    for r in roles:
        data.append({
            'id_rol': r.id_rol,
            'nombre': r.nombre,
            'estado': r.estado,
            'total_usuarios': Usuario.query.filter(Usuario.id_rol == r.id_rol).count(),
            'fecha_creacion': r.fecha_creacion.strftime('%d/%m/%Y') if r.fecha_creacion else None,
        })
    return jsonify({'success': True, 'data': data})


@admin_bp.route('/actividad', methods=['GET'])
@admin_required
def listar_actividad():
    limite = request.args.get('limit', 100, type=int)
    registros = ActividadUsuario.query.order_by(ActividadUsuario.fecha.desc()).limit(min(limite, 500)).all()
    data = []
    for a in registros:
        emp = Usuario.query.get(a.id_usuario)
        data.append({
            'id_actividad': a.id_actividad,
            'id_usuario': a.id_usuario,
            'usuario': f"{emp.nombres} {emp.apellido}" if emp else 'Desconocido',
            'correo': emp.correo if emp else '-',
            'accion': a.accion,
            'fecha': a.fecha.strftime('%d/%m/%Y %H:%M') if a.fecha else None,
        })
    return jsonify({'success': True, 'data': data})


@admin_bp.route('/alertas-resumen', methods=['GET'])
@admin_required
def alertas_resumen():
    umbral = 10
    productos = Producto.query.all()
    stock_bajo = sum(1 for p in productos if 0 < float(p.stock or 0) < umbral)
    agotados = sum(1 for p in productos if float(p.stock or 0) <= 0)
    adelantos_pendientes = Adelanto.query.filter(Adelanto.estado == 'Pendiente').count()
    solicitudes_pendientes = SolicitudInsumo.query.filter(SolicitudInsumo.estado == 'Pendiente').count()
    pagos_pendientes = PagoEmpleado.query.filter(PagoEmpleado.estado != 'Pagado').count()
    ahora = datetime.now(timezone.utc)
    bloqueos_activos = BloqueoLogin.query.filter(
        BloqueoLogin.bloqueado_hasta.isnot(None),
        BloqueoLogin.bloqueado_hasta > ahora
    ).count()
    hoy = datetime.utcnow().date()
    inicio = datetime.combine(hoy, datetime.min.time())
    movimientos_hoy = TransaccionCaja.query.filter(TransaccionCaja.fecha >= inicio).count()
    return jsonify({'success': True, 'data': {
        'stock_bajo': stock_bajo,
        'agotados': agotados,
        'adelantos_pendientes': adelantos_pendientes,
        'solicitudes_pendientes': solicitudes_pendientes,
        'pagos_pendientes': pagos_pendientes,
        'bloqueos_activos': bloqueos_activos,
        'movimientos_hoy': movimientos_hoy,
    }})


@admin_bp.route('/actividad-reciente', methods=['GET'])
@admin_required
def actividad_reciente():
    limite = request.args.get('limit', 10, type=int)
    limite = min(limite, 50)
    items = []

    pagos = PagoEmpleado.query.order_by(PagoEmpleado.fecha_pago.desc()).limit(limite).all()
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
    for c in cierres:
        emp = Usuario.query.get(c.id_usuario)
        nombre = f"{emp.nombres} {emp.apellido}".strip() if emp else 'Cajera'
        items.append({
            'tipo': 'cierre_caja',
            'titulo': 'Cierre de caja',
            'descripcion': f'Ventas S/ {float(c.total_ventas or 0):.2f} · Saldo S/ {float(c.neto or 0):.2f} por {nombre}',
            'fecha': c.fecha_cierre or c.fecha,
            'icono': 'cash-register',
        })

    adelantos = Adelanto.query.order_by(Adelanto.fecha.desc()).limit(limite).all()
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

    solicitudes = SolicitudInsumo.query.filter(SolicitudInsumo.estado == 'Pendiente').order_by(SolicitudInsumo.fecha.desc()).limit(limite).all()
    for s in solicitudes:
        items.append({
            'tipo': 'solicitud_insumo',
            'titulo': 'Solicitud de insumo',
            'descripcion': f'{s.cantidad:g} × {s.producto} solicitado por {s.solicitante or "cocina"}',
            'fecha': s.fecha,
            'icono': 'box-open',
        })

    inversiones = Inversion.query.order_by(Inversion.fecha.desc()).limit(limite).all()
    for i in inversiones:
        items.append({
            'tipo': 'inversion',
            'titulo': 'Inversión registrada',
            'descripcion': f'S/ {i.monto:.2f} — {i.descripcion}' + (f' ({i.proveedor})' if i.proveedor else ''),
            'fecha': i.fecha,
            'icono': 'chart-line',
        })

    items.sort(key=lambda x: x['fecha'] or datetime.min, reverse=True)
    data = [{
        'tipo': it['tipo'],
        'titulo': it['titulo'],
        'descripcion': it['descripcion'],
        'icono': it['icono'],
        'fecha': it['fecha'].strftime('%d/%m/%Y %H:%M') if it['fecha'] else None,
    } for it in items[:limite]]
    return jsonify({'success': True, 'data': data})


@admin_bp.route('/adelantos', methods=['GET'])
@admin_required
def listar_solicitudes():
    solicitudes = Adelanto.query.order_by(Adelanto.fecha.desc()).all()
    data = []
    for s in solicitudes:
        emp = s.usuario_adelanto
        data.append({
            'id_adelanto': s.id_adelanto,
            'id_usuario': s.id_usuario,
            'empleado': f"{emp.nombres} {emp.apellido}" if emp else 'Desconocido',
            'motivo': s.motivo,
            'monto': s.monto,
            'fecha': s.fecha.strftime('%d/%m/%Y') if s.fecha else None,
            'fecha_gestion': s.fecha_gestion.strftime('%d/%m/%Y %H:%M') if s.fecha_gestion else None,
            'estado': s.estado,
            'respuesta_admin': s.respuesta_admin,
        })
    return jsonify({'success': True, 'data': data})


@admin_bp.route('/adelantos/<int:id_adelanto>', methods=['PUT'])
@admin_required
def gestionar_solicitud(id_adelanto):
    adelanto = Adelanto.query.get(id_adelanto)
    if not adelanto:
        return jsonify({'success': False, 'error': 'Solicitud no encontrada'}), 404

    data = request.get_json(silent=True) or {}
    accion = (data.get('accion') or '').strip().lower()
    respuesta = (data.get('respuesta') or '').strip()

    if accion == 'aprobar':
        adelanto.estado = 'Aprobado'
    elif accion == 'rechazar':
        adelanto.estado = 'Rechazado'
    else:
        return jsonify({'success': False, 'error': 'Acción no válida'}), 400

    adelanto.respuesta_admin = respuesta if respuesta else None
    adelanto.fecha_gestion = datetime.now()
    adelanto.notificacion_vista = False
    crear_notificacion(
        adelanto.id_usuario,
        f'Solicitud de adelanto {adelanto.estado}',
        f'Tu adelanto de S/ {adelanto.monto:.2f} fue {adelanto.estado.lower()}.'
        + (f' Respuesta: {respuesta}' if respuesta else '')
    )
    db.session.commit()

    try:
        admin_id = int(get_jwt_identity())
        accion_act = ActividadUsuario(id_usuario=admin_id, accion=f"{accion.capitalize()} adelanto #{id_adelanto}", fecha=datetime.now())
        db.session.add(accion_act)
        db.session.commit()
    except Exception:
        db.session.rollback()

    return jsonify({'success': True, 'message': f'Adelanto {adelanto.estado.lower()} correctamente'})

@admin_bp.route('/seguridad', methods=['GET'])
@admin_required
def get_seguridad():
    ahora = datetime.now(timezone.utc)
    dias = request.args.get('dias', 7, type=int)
    limite = ahora - timedelta(days=min(dias, 90))

    intentos = IntentoLogin.query.filter(IntentoLogin.fecha >= limite).order_by(IntentoLogin.fecha.desc()).limit(200).all()
    intentos_data = []
    for i in intentos:
        intentos_data.append({
            'id': i.id,
            'identificador': i.identificador,
            'usuario_nombre': i.usuario_nombre,
            'ip': i.ip or '-',
            'resultado': i.resultado,
            'fecha': i.fecha.strftime('%d/%m/%Y %H:%M') if i.fecha else None,
        })

    bloqueos = BloqueoLogin.query.filter(
        BloqueoLogin.bloqueado_hasta.isnot(None),
        BloqueoLogin.bloqueado_hasta > ahora
    ).order_by(BloqueoLogin.intentos.desc()).all()
    bloqueos_data = []
    for b in bloqueos:
        activo = b.bloqueado_hasta is not None and b.bloqueado_hasta > ahora
        bloqueos_data.append({
            'id': b.id,
            'usuario': b.usuario,
            'usuario_nombre': b.usuario_nombre,
            'usuario_rol': b.usuario_rol,
            'ip': b.ip or '-',
            'intentos': b.intentos,
            'bloqueado_hasta': b.bloqueado_hasta.strftime('%d/%m/%Y %H:%M') if b.bloqueado_hasta else None,
            'activo': activo,
            'fecha': b.fecha.strftime('%d/%m/%Y %H:%M') if b.fecha else None,
        })

    resumen = {
        'exitos': IntentoLogin.query.filter(IntentoLogin.resultado == 'exito', IntentoLogin.fecha >= limite).count(),
        'fallos': IntentoLogin.query.filter(IntentoLogin.resultado == 'fallo', IntentoLogin.fecha >= limite).count(),
        'bloqueados': IntentoLogin.query.filter(IntentoLogin.resultado == 'bloqueado', IntentoLogin.fecha >= limite).count(),
        'bloqueos_activos': sum(1 for b in bloqueos if b.bloqueado_hasta is not None and b.bloqueado_hasta > ahora),
    }

    return jsonify({'success': True, 'data': {
        'resumen': resumen,
        'intentos': intentos_data,
        'bloqueos': bloqueos_data,
    }})

@admin_bp.route('/seguridad/desbloquear', methods=['POST'])
@admin_required
def desbloquear():
    data = request.get_json(silent=True) or {}
    usuario = (data.get('usuario') or '').strip()
    if not usuario:
        return jsonify({'success': False, 'error': 'Usuario requerido'}), 400
    for b in BloqueoLogin.query.filter(BloqueoLogin.usuario == usuario).all():
        db.session.delete(b)
    db.session.commit()
    return jsonify({'success': True, 'message': f'Bloqueos de {usuario} eliminados'})
