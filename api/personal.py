from api.validaciones import validar_personal, numero
from api.fechas import limites_dia, LIMA, ahora
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date, time, timedelta
from calendar import monthrange
from dateutil.relativedelta import relativedelta
from decimal import Decimal, InvalidOperation
from models import SueldoSemanal, DescuentoSemanal
import bcrypt
from models import db, Usuario, Rol, PagoPersonal, PagoEmpleado, Adelanto, ActividadUsuario, DocumentoIdentidad, crear_notificacion
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
    empleados = Usuario.query.options(db.joinedload(Usuario.rol), db.joinedload(Usuario.documento), db.joinedload(Usuario.perfil)).order_by(Usuario.nombres.asc()).all()
    data = []
    for emp in empleados:
        item = usuario_schema.dump(emp)
        item['rol_nombre'] = emp.rol.nombre if emp.rol else None
        item['id_rol'] = emp.id_rol
        data.append(item)
    return jsonify({'success': True, 'data': data})

@personal_bp.route('/<int:id>', methods=['GET'])
@admin_required
def get_empleado(id):
    empleado = Usuario.query.get_or_404(id)
    return jsonify({'success': True, 'data': usuario_schema.dump(empleado)})

@personal_bp.route('/', methods=['POST'])
@admin_required
def crear_empleado():
    data = request.get_json(silent=True) or {}
    error = validar_personal(data, crear=True)
    if error:
        return jsonify(success=False, message=error), 400
    from datetime import datetime
    from sqlalchemy.exc import IntegrityError

    dni = str(data.get('dni') or '').strip()
    if not dni or not data.get('nombres') or not data.get('apellido'):
        return jsonify({'success': False, 'message': 'Los campos DNI, nombres y apellidos son obligatorios'}), 400

    if DocumentoIdentidad.query.filter_by(numero=dni).first():
        return jsonify({'success': False, 'message': 'El DNI ya se encuentra registrado'}), 400

    id_rol = int(data.get('id_rol') or 2)
    rol = Rol.query.get(id_rol)
    if not rol or not rol.estado:
        return jsonify({'success': False, 'message': 'Rol no válido'}), 400

    try:
        documento = DocumentoIdentidad(
            tipo_documento='DNI',
            numero=dni
        )
        db.session.add(documento)
        db.session.flush()

        correo = (data.get('correo') or '').strip() or f"{dni}@empleado.benditobuffet.local"

        turno = data.get('turno') or ''
        if isinstance(turno, list):
            turno = ','.join(str(t) for t in turno if str(t).strip())
        elif isinstance(turno, str):
            turno = ','.join(t.strip() for t in turno.split(',') if t.strip())

        empleado = Usuario(
            nombres=data['nombres'],
            apellido=data['apellido'],
            correo=correo,
            telefono=data.get('telefono', ''),
            usuario=data.get('usuario') or dni,
            clave=bcrypt.hashpw(data['clave'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            id_documento=documento.id_documento,
            id_rol=rol.id_rol,
            estado=True,
            turno=turno or None,
            fecha_creacion=datetime.utcnow()
        )
        db.session.add(empleado)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'El DNI o correo ya se encuentra registrado'}), 400

    return jsonify({'success': True, 'data': usuario_schema.dump(empleado)})

@personal_bp.route('/<int:id>', methods=['PUT'])
@admin_required
def actualizar_empleado(id):
    empleado = Usuario.query.get_or_404(id)
    data = request.get_json(silent=True) or {}
    error = validar_personal(data, crear=False)
    if error:
        return jsonify(success=False, message=error), 400

    empleado.nombres = data.get('nombres', empleado.nombres)
    empleado.apellido = data.get('apellido', empleado.apellido)
    empleado.correo = data.get('correo', empleado.correo)
    empleado.telefono = data.get('telefono', empleado.telefono)

    if 'id_rol' in data:
        id_rol = int(data['id_rol'])
        rol = Rol.query.get(id_rol)
        if not rol or not rol.estado:
            return jsonify({'success': False, 'message': 'Rol no válido'}), 400
        empleado.id_rol = rol.id_rol

    if 'estado' in data:
        empleado.estado = bool(data['estado'])

    if 'turno' in data:
        turno = data['turno']
        if isinstance(turno, list):
            turno = ','.join(str(t) for t in turno if str(t).strip())
        elif isinstance(turno, str):
            turno = ','.join(t.strip() for t in turno.split(',') if t.strip())
        empleado.turno = turno or None

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
    now = ahora().astimezone(LIMA)
    anio = request.args.get('anio', type=int) or now.year
    mes = request.args.get('mes', type=int) or now.month
    ultimo_dia = monthrange(anio, mes)[1]
    inicio, _ = limites_dia(date(anio, mes, 1))
    _, fin = limites_dia(date(anio, mes, ultimo_dia))
    fin -= timedelta(microseconds=1)
    return inicio, fin, mes, anio

def _totales_pagos(start_date, end_date, id_usuario=None):
    inicio = start_date
    fin = end_date
    pagos_q = db.session.query(db.func.coalesce(db.func.sum(PagoEmpleado.monto), 0)).filter(
        PagoEmpleado.estado == 'Pagado', PagoEmpleado.fecha_pago >= inicio, PagoEmpleado.fecha_pago <= fin)
    adelantos_q = db.session.query(db.func.coalesce(db.func.sum(Adelanto.monto), 0)).filter(
        Adelanto.fecha >= inicio, Adelanto.fecha <= fin, Adelanto.estado == 'Aprobado')
    if id_usuario:
        pagos_q = pagos_q.filter(PagoEmpleado.id_usuario == id_usuario)
        adelantos_q = adelantos_q.filter(Adelanto.id_usuario == id_usuario)
    total_pagos = float(pagos_q.scalar() or 0)
    total_adelantos = float(adelantos_q.scalar() or 0)
    return total_pagos, total_adelantos, total_pagos + total_adelantos

def _totales_por_empleado(start_date, end_date):
    inicio = start_date
    fin = end_date
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
    ini, fin = limites_dia(fecha)
    fin -= timedelta(microseconds=1)
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
                'neto': p + a
            })

    historial = PagoEmpleado.query.options(
        db.joinedload(PagoEmpleado.usuario_empleado)
    ).filter(
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
            'historial': sorted([{
                'id_pago': h.id_pago,
                'id_usuario': h.id_usuario,
                'empleado': f"{h.usuario_empleado.nombres} {h.usuario_empleado.apellido}" if h.usuario_empleado else 'Empleado',
                'monto': h.monto,
                'fecha': h.fecha_pago.strftime('%Y-%m-%d') if h.fecha_pago else None,
                'estado': h.estado,
                'descripcion': h.descripcion,
            } for h in historial] + [{
                'id_pago': f'adelanto-{a.id_adelanto}', 'id_usuario': a.id_usuario,
                'empleado': f'{a.usuario_adelanto.nombres} {a.usuario_adelanto.apellido}' if a.usuario_adelanto else 'Empleado',
                'monto': a.monto, 'fecha': a.fecha.strftime('%Y-%m-%d'), 'estado': a.estado,
                'descripcion': f'Adelanto: {a.motivo}'
            } for a in Adelanto.query.options(db.joinedload(Adelanto.usuario_adelanto)).filter(
                Adelanto.fecha >= inicio, Adelanto.fecha <= fin).all()], key=lambda x: x['fecha'] or '', reverse=True)
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
        monto = numero(data['monto'], .01)
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
    if tipo and tipo != 'Pago' and tipo != 'Adelanto':
        descripcion = f'{tipo}: {descripcion}'.strip()

    if _duplicado_pago(fecha, id_usuario, monto, estado):
        return jsonify({'success': False, 'message': 'Ya existe un pago similar para esa fecha'}), 400

    pago_personal = PagoPersonal(
        id_usuario=id_usuario, monto=monto, fecha=fecha,
        tipo=tipo, estado=estado, descripcion=descripcion
    )
    db.session.add(pago_personal)
    db.session.flush()
    pago_empleado = PagoEmpleado(
        id_usuario=id_usuario, monto=monto,
        fecha_pago=limites_dia(fecha)[0],
        estado=estado, descripcion=descripcion
    )
    db.session.add(pago_empleado)
    db.session.add(ActividadUsuario(id_usuario=admin_id, accion=f'Registró pago para empleado {id_usuario}', fecha=datetime.now()))
    crear_notificacion(
        id_usuario,
        'Nuevo pago registrado',
        f'Se registró tu pago por S/ {monto:.2f} ({estado}).'
    )
    db.session.commit()
    return jsonify({'success': True, 'data': {'id_pago': pago_empleado.id_pago, 'monto': monto, 'fecha': fecha.isoformat(), 'estado': estado}})

@personal_bp.route('/pagos/adelanto', methods=['POST'])
@admin_required
def crear_pago_adelanto():
    data = request.get_json() or {}
    admin_id = int(get_jwt_identity())
    try:
        id_usuario = int(data.get('id_usuario'))
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Empleado no válido'}), 400
    empleado = db.session.get(Usuario, id_usuario)
    if not empleado or not empleado.estado or empleado.id_rol == 1:
        return jsonify({'success': False, 'message': 'Empleado no válido'}), 400
    motivo = str(data.get('motivo') or data.get('descripcion') or '').strip()
    if not motivo:
        return jsonify({'success': False, 'message': 'El motivo es obligatorio'}), 400
    try:
        monto = numero(data['monto'], .01)
        if monto <= 0:
            raise ValueError
    except (ValueError, KeyError, TypeError):
        return jsonify({'success': False, 'message': 'El monto debe ser un número mayor que cero'}), 400

    fecha_text = data.get('fecha')
    if fecha_text:
        try:
            adelanto_fecha = limites_dia(datetime.strptime(str(fecha_text)[:10], '%Y-%m-%d').date())[0]
        except ValueError:
            return jsonify({'success': False, 'message': 'Fecha de adelanto inválida'}), 400
    else:
        adelanto_fecha = ahora()

    estado = data.get('estado', 'Pendiente')
    if estado not in ('Pendiente', 'Aprobado'):
        estado = 'Pendiente'
    ini, fin = limites_dia(adelanto_fecha.astimezone(LIMA).date())
    existe = Adelanto.query.filter(
        Adelanto.id_usuario == id_usuario, Adelanto.fecha >= ini, Adelanto.fecha < fin,
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
    return crear_pago_adelanto()

@personal_bp.route('/salarios', methods=['GET'])
@admin_required
def get_salarios():
    try:
        fecha = date.fromisoformat(request.args.get('fecha') or ahora().astimezone(LIMA).date().isoformat())
    except ValueError:
        return jsonify(success=False, error='Fecha no válida'), 400
    lunes = fecha - timedelta(days=fecha.weekday())
    inicio, _ = limites_dia(lunes)
    fin = inicio + timedelta(days=7)
    pagos = dict(db.session.query(PagoEmpleado.id_usuario, db.func.sum(PagoEmpleado.monto)).filter(
        PagoEmpleado.estado == 'Pagado', PagoEmpleado.fecha_pago >= inicio, PagoEmpleado.fecha_pago < fin
    ).group_by(PagoEmpleado.id_usuario).all())
    adelantos = dict(db.session.query(Adelanto.id_usuario, db.func.sum(Adelanto.monto)).filter(
        Adelanto.estado == 'Aprobado', Adelanto.fecha >= inicio, Adelanto.fecha < fin
    ).group_by(Adelanto.id_usuario).all())
    empleados = Usuario.query.filter(Usuario.id_rol != 1).order_by(Usuario.nombres).all()
    tarifas = SueldoSemanal.query.filter(SueldoSemanal.desde <= lunes).order_by(SueldoSemanal.desde).all()
    bases = {t.id_usuario: t.monto for t in tarifas}
    descuentos = DescuentoSemanal.query.filter_by(semana=lunes, anulado=False).order_by(DescuentoSemanal.id).all()
    detalle = {}
    for d in descuentos:
        detalle.setdefault(d.id_usuario, []).append({'id': d.id, 'monto': float(d.monto), 'motivo': d.motivo})
    datos = [{'id_usuario': e.id_usuario, 'empleado': f'{e.nombres} {e.apellido}', 'usuario': e.usuario,
        'total_pagos': round(float(pagos.get(e.id_usuario) or 0), 2),
        'total_adelantos': round(float(adelantos.get(e.id_usuario) or 0), 2),
        'neto': round(float(pagos.get(e.id_usuario) or 0) + float(adelantos.get(e.id_usuario) or 0), 2)
    } for e in empleados if e.estado or e.id_usuario in pagos or e.id_usuario in adelantos]
    for fila in datos:
        uid = fila['id_usuario']
        base = bases.get(uid)
        deducciones = sum((Decimal(str(d['monto'])) for d in detalle.get(uid, [])), Decimal('0'))
        saldo = None if base is None else base - deducciones - Decimal(str(fila['neto']))
        fila.update(sueldo_base=None if base is None else float(base), descuentos=detalle.get(uid, []),
                    total_descuentos=float(deducciones), saldo=None if saldo is None else float(round(saldo, 2)))
    return jsonify(success=True, data=datos, inicio=lunes.isoformat(), fin=(lunes + timedelta(days=6)).isoformat())


def _datos_nomina(data):
    empleado = db.session.get(Usuario, int(data.get('id_usuario')))
    if not empleado or not empleado.estado or empleado.id_rol == 1:
        raise ValueError('Empleado no válido')
    dia = date.fromisoformat(data.get('fecha', ''))
    return empleado, dia - timedelta(days=dia.weekday())


@personal_bp.route('/salarios/sueldo', methods=['POST'])
@admin_required
def guardar_sueldo_semanal():
    data = request.get_json() or {}
    try:
        empleado, lunes = _datos_nomina(data)
        monto = Decimal(str(numero(data.get('monto'), 0)))
        if monto > Decimal('9999999999.99') or monto != monto.quantize(Decimal('.01')):
            raise ValueError('Use como máximo dos decimales')
    except (TypeError, ValueError, InvalidOperation):
        return jsonify(success=False, message='Empleado, fecha o sueldo no válido; use hasta dos decimales'), 400
    if db.engine.dialect.name == 'postgresql':
        db.session.execute(db.text('SELECT pg_advisory_xact_lock(:clave)'), {'clave': 72500000 + empleado.id_usuario})
    tarifa = SueldoSemanal.query.filter_by(id_usuario=empleado.id_usuario, desde=lunes).first()
    if tarifa is None:
        tarifa = SueldoSemanal(id_usuario=empleado.id_usuario, desde=lunes)
        db.session.add(tarifa)
    tarifa.monto = monto
    tarifa.registrado_por = int(get_jwt_identity())
    tarifa.fecha = ahora()
    db.session.add(ActividadUsuario(id_usuario=tarifa.registrado_por,
        accion=f'Sueldo semanal de empleado {empleado.id_usuario}: {monto}, desde {lunes}', fecha=ahora()))
    db.session.commit()
    return jsonify(success=True)


@personal_bp.route('/salarios/descuentos', methods=['POST'])
@admin_required
def registrar_descuento_semanal():
    data = request.get_json() or {}
    try:
        empleado, lunes = _datos_nomina(data)
        monto = Decimal(str(numero(data.get('monto'), .01)))
        motivo = str(data.get('motivo') or '').strip()
        if not motivo or len(motivo) > 255 or monto > Decimal('9999999999.99') or monto != monto.quantize(Decimal('.01')):
            raise ValueError()
    except (TypeError, ValueError, InvalidOperation):
        return jsonify(success=False, message='Indique empleado, fecha, motivo y monto positivo con hasta dos decimales'), 400
    uid = int(get_jwt_identity())
    db.session.add(DescuentoSemanal(id_usuario=empleado.id_usuario, semana=lunes, monto=monto,
        motivo=motivo, registrado_por=uid, fecha=ahora()))
    db.session.add(ActividadUsuario(id_usuario=uid,
        accion=f'Descuento de {monto} al empleado {empleado.id_usuario} para {lunes}: {motivo}'[:255], fecha=ahora()))
    db.session.commit()
    return jsonify(success=True)


@personal_bp.route('/salarios/descuentos/<int:descuento_id>/anular', methods=['POST'])
@admin_required
def anular_descuento_semanal(descuento_id):
    descuento = db.session.get(DescuentoSemanal, descuento_id)
    if not descuento:
        return jsonify(success=False, message='Descuento no encontrado'), 404
    descuento.anulado = True
    db.session.add(ActividadUsuario(id_usuario=int(get_jwt_identity()),
        accion=f'Anuló descuento {descuento_id} del empleado {descuento.id_usuario}', fecha=ahora()))
    db.session.commit()
    return jsonify(success=True)
