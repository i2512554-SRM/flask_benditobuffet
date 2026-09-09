from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timezone, timedelta

from bd import db
from models import (
    Usuario, PagoEmpleado, Adelanto, Notificacion, UsuarioPerfil
)

trabajador_bp = Blueprint('trabajador', __name__, url_prefix='/api/trabajador')

ROLES_PERMITIDOS = (2, 3, 4)


def _ahora():
    return datetime.now(timezone.utc)


def _trabajador(fn):
    from functools import wraps

    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        uid = int(get_jwt_identity())
        u = Usuario.query.get(uid)
        if not u or u.id_rol not in ROLES_PERMITIDOS or not u.estado:
            return jsonify({'success': False, 'error': 'Acceso restringido a trabajadores'}), 403
        return fn(u, *args, **kwargs)

    return wrapper


def _turnos(usuario):
    return [t.strip() for t in (usuario.turno or '').split(',') if t.strip()]


HORARIOS_TURNO = {
    'Mañana': ('08:00', '14:00'),
    'Tarde': ('14:00', '22:00'),
    'Noche': ('22:00', '06:00'),
}


def _horario(usuario):
    perfil = usuario.perfil
    return perfil.horario if (perfil and perfil.horario) else None


def _horas_de(turno, horario):
    if not horario:
        return HORARIOS_TURNO.get(turno, ('--:--', '--:--'))
    rango = horario
    for sep in (' a ', '-', '–', '—'):
        if sep in rango:
            partes = [p.strip() for p in rango.split(sep)]
            if len(partes) >= 2 and ':' in partes[-2] and ':' in partes[-1]:
                return (partes[-2], partes[-1])
    return HORARIOS_TURNO.get(turno, ('--:--', '--:--'))


@trabajador_bp.route('/turnos', methods=['GET'])
@_trabajador
def mis_turnos(trabajador):
    turnos = _turnos(trabajador)
    horario = _horario(trabajador)
    hoy = datetime.now(timezone.utc)

    DIAS_SEMANA = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    semana = []
    inicio = hoy.date() - timedelta(days=hoy.weekday())
    for i in range(7):
        fecha = inicio + timedelta(days=i)
        activo = i < 6 and len(turnos) > 0
        semana.append({
            'dia': DIAS_SEMANA[i],
            'fecha': fecha.strftime('%d/%m/%Y'),
            'laboral': activo,
            'estado': 'Activo' if activo else 'Descanso',
            'turnos': [
                {
                    'nombre': t,
                    'hora_entrada': _horas_de(t, horario)[0],
                    'hora_salida': _horas_de(t, horario)[1],
                }
                for t in turnos
            ] if activo else [],
        })

    return jsonify({
        'success': True,
        'data': {
            'turnos': turnos,
            'horario': horario,
            'estado_laboral': 'Activo' if trabajador.estado else 'Inactivo',
            'semana': semana,
        }
    })


@trabajador_bp.route('/dashboard', methods=['GET'])
@_trabajador
def dashboard(trabajador):
    pagos = PagoEmpleado.query.filter_by(id_usuario=trabajador.id_usuario).order_by(
        PagoEmpleado.fecha_pago.desc()
    ).all()
    total_pagado = sum(p.monto for p in pagos if p.estado == 'Pagado')
    pendientes_admin = Adelanto.query.filter_by(
        id_usuario=trabajador.id_usuario, estado='Pendiente'
    ).count()
    no_leidas = Notificacion.query.filter_by(id_usuario=trabajador.id_usuario, leida=False).count()
    ultimas_notif = Notificacion.query.filter_by(id_usuario=trabajador.id_usuario).order_by(
        Notificacion.fecha.desc()
    ).limit(4).all()

    return jsonify({
        'success': True,
        'data': {
            'usuario': {
                'nombres': trabajador.nombres,
                'apellido': trabajador.apellido,
                'rol': trabajador.rol.nombre if trabajador.rol else None,
            },
            'fecha': _ahora().strftime('%A, %d de %B del %Y'),
            'turnos': _turnos(trabajador),
            'resumen': {
                'total_pagado': float(total_pagado),
                'pagos': len(pagos),
                'adelantos_pendientes': pendientes_admin,
                'notificaciones_no_leidas': no_leidas,
            },
            'notificaciones': [{
                'id_notificacion': n.id_notificacion,
                'titulo': n.titulo,
                'mensaje': n.mensaje,
                'leida': n.leida,
                'fecha': n.fecha.strftime('%d/%m/%Y %H:%M') if n.fecha else None,
            } for n in ultimas_notif],
        }
    })


@trabajador_bp.route('/mi-info', methods=['GET'])
@_trabajador
def mi_info(trabajador):
    perfil = trabajador.perfil
    return jsonify({
        'success': True,
        'data': {
            'nombres': trabajador.nombres,
            'apellido': trabajador.apellido,
            'dni': trabajador.dni,
            'correo': trabajador.correo,
            'telefono': trabajador.telefono,
            'cargo': trabajador.rol.nombre if trabajador.rol else None,
            'turnos': _turnos(trabajador),
            'estado_laboral': 'Activo' if trabajador.estado else 'Inactivo',
            'fecha_ingreso': perfil.fecha_ingreso.strftime('%d/%m/%Y') if (perfil and perfil.fecha_ingreso) else None,
            'horario': perfil.horario if perfil else None,
        }
    })


@trabajador_bp.route('/pagos', methods=['GET'])
@_trabajador
def mis_pagos(trabajador):
    pagos = PagoEmpleado.query.filter_by(id_usuario=trabajador.id_usuario).order_by(
        PagoEmpleado.fecha_pago.desc()
    ).all()
    adelantos = Adelanto.query.filter_by(id_usuario=trabajador.id_usuario).order_by(
        Adelanto.fecha.desc()
    ).all()

    return jsonify({
        'success': True,
        'data': {
            'pagos': [{
                'id_pago': p.id_pago,
                'monto': p.monto,
                'fecha': p.fecha_pago.strftime('%d/%m/%Y') if p.fecha_pago else None,
                'estado': p.estado,
                'descripcion': p.descripcion or 'Pago registrado',
            } for p in pagos],
            'adelantos': [{
                'id_adelanto': a.id_adelanto,
                'monto': a.monto,
                'motivo': a.motivo,
                'fecha': a.fecha.strftime('%d/%m/%Y') if a.fecha else None,
                'estado': a.estado,
                'respuesta': a.respuesta_admin,
            } for a in adelantos],
        }
    })


@trabajador_bp.route('/notificaciones', methods=['GET'])
@_trabajador
def notificaciones(trabajador):
    notifs = Notificacion.query.filter_by(id_usuario=trabajador.id_usuario).order_by(
        Notificacion.fecha.desc()
    ).all()
    return jsonify({
        'success': True,
        'data': [{
            'id_notificacion': n.id_notificacion,
            'titulo': n.titulo,
            'mensaje': n.mensaje,
            'leida': n.leida,
            'fecha': n.fecha.strftime('%d/%m/%Y %H:%M') if n.fecha else None,
        } for n in notifs]
    })


@trabajador_bp.route('/notificaciones/leer', methods=['POST'])
@_trabajador
def marcar_notificaciones(trabajador):
    Notificacion.query.filter_by(id_usuario=trabajador.id_usuario, leida=False).update({'leida': True})
    db.session.commit()
    return jsonify({'success': True, 'message': 'Notificaciones marcadas como leídas'})