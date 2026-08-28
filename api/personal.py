from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date, time, timedelta
from calendar import monthrange
from dateutil.relativedelta import relativedelta
import bcrypt
from models import db, Usuario, PagoPersonal, PagoEmpleado, Adelanto, ActividadUsuario, DocumentoIdentidad
from schemas.usuario import usuario_schema, usuarios_schema, pago_schema, pagos_schema

personal_bp = Blueprint('personal', __name__)

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

@personal_bp.route('/', methods=['GET'])
@admin_required
def get_empleados():
    empleados = Usuario.query.filter_by(estado=True).all()
    return jsonify({'success': True, 'data': usuarios_schema.dump(empleados)})

@personal_bp.route('/<int:id>', methods=['GET'])
@admin_required
def get_empleado(id):
    empleado = Usuario.query.get_or_404(id)
    return jsonify({'success': True, 'data': usuario_schema.dump(empleado)})

@personal_bp.route('/', methods=['POST'])
@admin_required
def crear_empleado():
    data = request.get_json(silent=True) or {}
    from datetime import datetime
    from sqlalchemy.exc import IntegrityError

    dni = str(data.get('dni') or '').strip()
    if not dni or not data.get('nombres') or not data.get('apellido'):
        return jsonify({'success': False, 'message': 'Los campos DNI, nombres y apellidos son obligatorios'}), 400

    if DocumentoIdentidad.query.filter_by(numero=dni).first():
        return jsonify({'success': False, 'message': 'El DNI ya se encuentra registrado'}), 400

    try:
        documento = DocumentoIdentidad(
            tipo_documento='DNI',
            numero=dni
        )
        db.session.add(documento)
        db.session.flush()

        empleado = Usuario(
            nombres=data['nombres'],
            apellido=data['apellido'],
            correo=data.get('correo', ''),
            telefono=data.get('telefono', ''),
            usuario=data.get('usuario') or dni,
            clave=bcrypt.hashpw((data.get('clave') or dni).encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            id_documento=documento.id_documento,
            id_rol=2,
            estado=True,
            turno=data.get('turno', 'Manana'),
            fecha_creacion=datetime.utcnow()
        )
        db.session.add(empleado)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'El DNI ya se encuentra registrado'}), 400

    return jsonify({'success': True, 'data': usuario_schema.dump(empleado)})

@personal_bp.route('/<int:id>', methods=['PUT'])
@admin_required
def actualizar_empleado(id):
    empleado = Usuario.query.get_or_404(id)
    data = request.get_json()
    
    empleado.nombres = data.get('nombres', empleado.nombres)
    empleado.apellido = data.get('apellido', empleado.apellido)
    empleado.correo = data.get('correo', empleado.correo)
    empleado.telefono = data.get('telefono', empleado.telefono)
    empleado.turno = data.get('turno', empleado.turno)

    nueva_clave = data.get('clave')
    if nueva_clave:
        empleado.clave = bcrypt.hashpw(str(nueva_clave).encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    if 'dni' in data and empleado.documento:
        empleado.documento.numero = data['dni']
    
    db.session.commit()
    return jsonify({'success': True, 'data': usuario_schema.dump(empleado)})

@personal_bp.route('/<int:id>', methods=['DELETE'])
@admin_required
def eliminar_empleado(id):
    empleado = Usuario.query.get_or_404(id)
    empleado.estado = False
    db.session.commit()
    return jsonify({'success': True, 'message': 'Empleado desactivado'})

def _filtro_mes():
    now = datetime.now()
    anio = request.args.get('anio', type=int) or now.year
    mes = request.args.get('mes', type=int) or now.month
    ultimo_dia = monthrange(anio, mes)[1]
    inicio = datetime(anio, mes, 1)
    fin = datetime(anio, mes, ultimo_dia, 23, 59, 59)
    return inicio, fin, mes, anio

def _totales_pagos(start_date, end_date, id_usuario=None):
    inicio = datetime.combine(start_date.date(), time.min)
    fin = datetime.combine(end_date.date(), time.max)
    pagos_q = db.session.query(db.func.coalesce(db.func.sum(PagoEmpleado.monto), 0)).filter(
        PagoEmpleado.estado == 'Pagado', PagoEmpleado.fecha_pago >= inicio, PagoEmpleado.fecha_pago <= fin)
    adelantos_q = db.session.query(db.func.coalesce(db.func.sum(Adelanto.monto), 0)).filter(
        Adelanto.fecha >= inicio, Adelanto.fecha <= fin, Adelanto.estado == 'Aprobado')
    if id_usuario:
        pagos_q = pagos_q.filter(PagoEmpleado.id_usuario == id_usuario)
        adelantos_q = adelantos_q.filter(Adelanto.id_usuario == id_usuario)
    total_pagos = float(pagos_q.scalar() or 0)
    total_adelantos = float(adelantos_q.scalar() or 0)
    return total_pagos, total_adelantos, total_pagos - total_adelantos

def _totales_por_empleado(start_date, end_date):
    inicio = datetime.combine(start_date.date(), time.min)
    fin = datetime.combine(end_date.date(), time.max)
    pagos = dict(db.session.query(
        PagoEmpleado.id_usuario, db.func.coalesce(db.func.sum(PagoEmpleado.monto), 0)
    ).filter(PagoEmpleado.estado == 'Pagado', PagoEmpleado.fecha_pago >= inicio, PagoEmpleado.fecha_pago <= fin)
        .group_by(PagoEmpleado.id_usuario).all())
    adelantos = dict(db.session.query(
        Adelanto.id_usuario, db.func.coalesce(db.func.sum(Adelanto.monto), 0)
    ).filter(Adelanto.fecha >= inicio, Adelanto.fecha <= fin, Adelanto.estado == 'Aprobado')
        .group_by(Adelanto.id_usuario).all())
    return pagos, adelantos

def _proximo_pago():
    hoy = date.today()
    pendiente = PagoEmpleado.query.filter(
        PagoEmpleado.estado == 'Pendiente', db.func.date(PagoEmpleado.fecha_pago) >= hoy
    ).order_by(PagoEmpleado.fecha_pago.asc()).first()
    if pendiente:
        delta = (pendiente.fecha_pago.date() - hoy).days
        return delta if delta >= 0 else 0
    return None

def _duplicado_pago(fecha, id_usuario, monto, estado):
    ini = datetime.combine(fecha, time.min)
    fin = datetime.combine(fecha, time.max)
    return PagoEmpleado.query.filter(
        PagoEmpleado.id_usuario == id_usuario,
        PagoEmpleado.fecha_pago >= ini,
        PagoEmpleado.fecha_pago <= fin,
        PagoEmpleado.monto == monto,
        PagoEmpleado.estado == estado
    ).first()

@personal_bp.route('/pagos', methods=['GET'])
@admin_required
def get_pagos():
    inicio, fin, mes, anio = _filtro_mes()
    total_pagado, total_adelantos, neto = _totales_pagos(inicio, fin)
    empleados_activos = Usuario.query.filter_by(estado=True).count()
    proximo_pago = _proximo_pago()

    empleados = Usuario.query.filter_by(estado=True).order_by(Usuario.nombres.asc()).all()
    pagos_map, adelantos_map = _totales_por_empleado(inicio, fin)
    resumen_empleados = []
    for emp in empleados:
        p = float(pagos_map.get(emp.id_usuario, 0))
        a = float(adelantos_map.get(emp.id_usuario, 0))
        if p or a:
            resumen_empleados.append({
                'id_usuario': emp.id_usuario,
                'nombres': emp.nombres,
                'apellido': emp.apellido,
                'total_pagado': p,
                'total_adelantos': a,
                'neto': p - a
            })

    historial = PagoEmpleado.query.options(
        db.joinedload(PagoEmpleado.usuario_empleado)
    ).filter(
        PagoEmpleado.estado == 'Pagado',
        PagoEmpleado.fecha_pago >= inicio,
        PagoEmpleado.fecha_pago <= fin
    ).order_by(PagoEmpleado.fecha_pago.desc()).all()

    return jsonify({
        'success': True,
        'data': {
            'mes': mes,
            'anio': anio,
            'totales': {'pagado': total_pagado, 'adelantos': total_adelantos, 'neto': neto},
            'empleados_activos': empleados_activos,
            'proximo_pago': proximo_pago,
            'resumen': resumen_empleados,
            'historial': [{
                'id_pago': h.id_pago,
                'id_usuario': h.id_usuario,
                'empleado': f"{h.usuario_empleado.nombres} {h.usuario_empleado.apellido}" if h.usuario_empleado else 'Empleado',
                'monto': h.monto,
                'fecha': h.fecha_pago.strftime('%Y-%m-%d') if h.fecha_pago else None,
                'estado': h.estado,
                'descripcion': h.descripcion,
            } for h in historial]
        }
    })

@personal_bp.route('/pagos/empleado/<int:id_usuario>', methods=['GET'])
@admin_required
def get_pago_detalle(id_usuario):
    empleado = Usuario.query.get_or_404(id_usuario)
    inicio, fin, mes, anio = _filtro_mes()
    total_pagado, total_adelantos, neto = _totales_pagos(inicio, fin, id_usuario)

    pagos = PagoEmpleado.query.filter(PagoEmpleado.id_usuario == id_usuario).order_by(PagoEmpleado.fecha_pago.desc()).all()
    pagos_personal = PagoPersonal.query.filter(PagoPersonal.id_usuario == id_usuario).order_by(PagoPersonal.fecha.desc()).all()
    adelantos = Adelanto.query.filter(Adelanto.id_usuario == id_usuario).order_by(Adelanto.fecha.desc()).all()

    return jsonify({
        'success': True,
        'data': {
            'empleado': usuario_schema.dump(empleado),
            'mes': mes,
            'anio': anio,
            'totales': {'pagado': total_pagado, 'adelantos': total_adelantos, 'neto': neto},
            'pagos': [{
                'id_pago': p.id_pago, 'monto': p.monto,
                'fecha': p.fecha_pago.strftime('%Y-%m-%d') if p.fecha_pago else None,
                'estado': p.estado, 'descripcion': p.descripcion
            } for p in pagos],
            'pagos_personal': [{
                'id_pago': p.id_pago, 'monto': p.monto,
                'fecha': p.fecha.strftime('%Y-%m-%d') if p.fecha else None,
                'tipo': p.tipo, 'descripcion': p.descripcion
            } for p in pagos_personal],
            'adelantos': [{
                'id_adelanto': a.id_adelanto, 'monto': a.monto, 'motivo': a.motivo,
                'fecha': a.fecha.strftime('%Y-%m-%d') if a.fecha else None,
                'estado': a.estado, 'respuesta': a.respuesta_admin
            } for a in adelantos],
        }
    })

@personal_bp.route('/pagos', methods=['POST'])
@admin_required
def crear_pago():
    data = request.get_json()
    admin_id = int(get_jwt_identity())
    try:
        id_usuario = int(data.get('id_usuario'))
    except (TypeError, ValueError):
        return jsonify({'success': False, 'message': 'Empleado no válido'}), 400
    if not Usuario.query.get(id_usuario):
        return jsonify({'success': False, 'message': 'Empleado no válido'}), 400
    try:
        monto = float(data['monto'])
        if monto <= 0:
            raise ValueError
    except (ValueError, KeyError, TypeError):
        return jsonify({'success': False, 'message': 'El monto debe ser un número mayor que cero'}), 400

    fecha_text = data.get('fecha')
    if fecha_text:
        try:
            fecha = datetime.strptime(str(fecha_text)[:10], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'success': False, 'message': 'Fecha de pago inválida'}), 400
    else:
        fecha = date.today()

    estado = data.get('estado', 'Pagado')
    if estado not in ('Pagado', 'Pendiente'):
        estado = 'Pagado'
    descripcion = data.get('descripcion', '')
    tipo = data.get('tipo', 'Pago')
    if descripcion and tipo and tipo != 'Pago' and tipo != 'Adelanto':
        descripcion = f'{tipo}: {descripcion}'.strip()

    if _duplicado_pago(fecha, id_usuario, monto, estado):
        return jsonify({'success': False, 'message': 'Ya existe un pago similar para esa fecha'}), 400

    pago_personal = PagoPersonal(
        id_usuario=id_usuario, monto=monto, fecha=fecha,
        tipo='Pago', estado=estado, descripcion=descripcion
    )
    db.session.add(pago_personal)
    db.session.flush()
    pago_empleado = PagoEmpleado(
        id_usuario=id_usuario, monto=monto,
        fecha_pago=datetime.combine(fecha, time.min),
        estado=estado, descripcion=descripcion
    )
    db.session.add(pago_empleado)
    db.session.add(ActividadUsuario(id_usuario=admin_id, accion=f'Registró pago para empleado {id_usuario}', fecha=datetime.now()))
    db.session.commit()
    return jsonify({'success': True, 'data': {'id_pago': pago_empleado.id_pago, 'monto': monto, 'fecha': fecha.isoformat(), 'estado': estado}})

@personal_bp.route('/pagos/adelanto', methods=['POST'])
@admin_required
def crear_pago_adelanto():
    data = request.get_json()
    admin_id = int(get_jwt_identity())
    id_usuario = int(data.get('id_usuario'))
    if not id_usuario or not Usuario.query.get(id_usuario):
        return jsonify({'success': False, 'message': 'Empleado no válido'}), 400
    motivo = (data.get('motivo') or '').strip()
    if not motivo:
        return jsonify({'success': False, 'message': 'El motivo es obligatorio'}), 400
    try:
        monto = float(data['monto'])
        if monto <= 0:
            raise ValueError
    except (ValueError, KeyError, TypeError):
        return jsonify({'success': False, 'message': 'El monto debe ser un número mayor que cero'}), 400

    fecha_text = data.get('fecha')
    if fecha_text:
        try:
            adelanto_fecha = datetime.strptime(str(fecha_text)[:10], '%Y-%m-%d')
        except ValueError:
            return jsonify({'success': False, 'message': 'Fecha de adelanto inválida'}), 400
    else:
        adelanto_fecha = datetime.now()

    estado = data.get('estado', 'Pendiente')
    if estado not in ('Pendiente', 'Aprobado'):
        estado = 'Pendiente'
    ini = datetime.combine(adelanto_fecha.date(), time.min)
    fin = datetime.combine(adelanto_fecha.date(), time.max)
    existe = Adelanto.query.filter(
        Adelanto.id_usuario == id_usuario, Adelanto.fecha >= ini, Adelanto.fecha <= fin,
        Adelanto.monto == monto, Adelanto.motivo == motivo
    ).first()
    if existe:
        return jsonify({'success': False, 'message': 'Ya existe un adelanto similar para esa fecha'}), 400

    nuevo = Adelanto(id_usuario=id_usuario, motivo=motivo, monto=monto, fecha=adelanto_fecha, estado=estado)
    db.session.add(nuevo)
    db.session.add(ActividadUsuario(id_usuario=admin_id, accion=f'Registró adelanto para empleado {id_usuario}', fecha=datetime.now()))
    db.session.commit()
    return jsonify({'success': True, 'data': {'id_adelanto': nuevo.id_adelanto, 'monto': monto, 'estado': estado}})

@personal_bp.route('/adelantos', methods=['GET'])
@admin_required
def get_adelantos():
    adelantos = Adelanto.query.order_by(Adelanto.fecha.desc()).all()
    return jsonify({'success': True, 'data': [{'id_adelanto': a.id_adelanto, 'id_usuario': a.id_usuario, 'monto': a.monto, 'fecha': a.fecha, 'estado': a.estado, 'motivo': a.motivo} for a in adelantos]})

@personal_bp.route('/adelantos', methods=['POST'])
@admin_required
def crear_adelanto():
    data = request.get_json()
    from datetime import datetime
    adelanto = Adelanto(
        id_usuario=data['id_usuario'],
        monto=data['monto'],
        motivo=data.get('motivo', data.get('descripcion', '')),
        fecha=datetime.utcnow().date(),
        estado='Pendiente'
    )
    db.session.add(adelanto)
    db.session.commit()
    return jsonify({'success': True, 'data': {'id_adelanto': adelanto.id_adelanto, 'id_usuario': adelanto.id_usuario, 'monto': adelanto.monto, 'fecha': adelanto.fecha, 'estado': adelanto.estado}})

@personal_bp.route('/salarios', methods=['GET'])
@admin_required
def get_salarios():
    from datetime import datetime
    from flask import request as req
    from dateutil.relativedelta import relativedelta

    now = datetime.now()
    mes = req.args.get('mes', type=int) or now.month
    anio = req.args.get('anio', type=int) or now.year

    inicio = datetime(anio, mes, 1)
    fin = inicio + relativedelta(months=1)

    empleados = Usuario.query.filter_by(estado=True).all()
    salarios = []

    for emp in empleados:
        pagos = PagoPersonal.query.filter(
            PagoPersonal.id_usuario == emp.id_usuario,
            PagoPersonal.fecha >= inicio,
            PagoPersonal.fecha < fin
        ).all()

        adelantos = Adelanto.query.filter(
            Adelanto.id_usuario == emp.id_usuario,
            Adelanto.estado == 'Aprobado',
            Adelanto.fecha >= inicio,
            Adelanto.fecha < fin
        ).all()

        total_pagos = sum(p.monto for p in pagos)
        total_adelantos = sum(a.monto for a in adelantos)

        salarios.append({
            'id_usuario': emp.id_usuario,
            'nombres': emp.nombres,
            'apellido': emp.apellido,
            'sueldo_base': 0,
            'total_pagos': total_pagos,
            'total_adelantos': total_adelantos,
            'neto': total_pagos - total_adelantos
        })

    return jsonify({'success': True, 'data': salarios})
