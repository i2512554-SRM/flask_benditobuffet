from flask import Blueprint, jsonify
from datetime import datetime, timezone, timedelta

from bd import db
from api.fechas import iso_utc, LIMA
from api.roles import ROLES_TRABAJADOR, requiere_roles
from schemas.trabajador import (notificaciones_schema, pagos_trabajador_schema,
                                adelantos_trabajador_schema, info_trabajador_schema)
from models import (
    PagoEmpleado, Adelanto, Notificacion
)

trabajador_bp = Blueprint('trabajador', __name__, url_prefix='/api/trabajador')



def _ahora():
    return datetime.now(timezone.utc)


_trabajador = requiere_roles(*ROLES_TRABAJADOR, mensaje='Acceso restringido a trabajadores', pasar_usuario=True)


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
    hoy = _ahora().astimezone(LIMA)

    DIAS_SEMANA = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    semana = []
    inicio = hoy.date() - timedelta(days=hoy.weekday())
    for i in range(7):
        fecha = inicio + timedelta(days=i)
        activo = i < 6 and len(turnos) > 0
        semana.append({
            'dia': DIAS_SEMANA[i],
            'fecha': fecha.isoformat(),
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
            'fecha': iso_utc(_ahora()),
            'turnos': _turnos(trabajador),
            'resumen': {
                'total_pagado': float(total_pagado),
                'pagos': len(pagos),
                'adelantos_pendientes': pendientes_admin,
                'notificaciones_no_leidas': no_leidas,
            },
            'notificaciones': notificaciones_schema.dump(ultimas_notif),
        }
    })


@trabajador_bp.route('/mi-info', methods=['GET'])
@_trabajador
def mi_info(trabajador):
    return jsonify({'success': True, 'data': info_trabajador_schema.dump(trabajador)})


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
            'pagos': pagos_trabajador_schema.dump(pagos),
            'adelantos': adelantos_trabajador_schema.dump(adelantos),
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
        'data': notificaciones_schema.dump(notifs)
    })


@trabajador_bp.route('/notificaciones/leer', methods=['POST'])
@_trabajador
def marcar_notificaciones(trabajador):
    Notificacion.query.filter_by(id_usuario=trabajador.id_usuario, leida=False).update({'leida': True})
    db.session.commit()
    return jsonify({'success': True, 'message': 'Notificaciones marcadas como leídas'})
