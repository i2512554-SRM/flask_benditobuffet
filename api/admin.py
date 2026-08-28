from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date
from calendar import monthrange
from bd import db
from models import Usuario, TransaccionCaja, CierreCaja, Adelanto, ActividadUsuario

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
        return jsonify({'success': False, 'error': 'Accion no valida'}), 400

    adelanto.respuesta_admin = respuesta if respuesta else None
    adelanto.fecha_gestion = datetime.now()
    adelanto.notificacion_vista = False
    db.session.commit()

    try:
        admin_id = int(get_jwt_identity())
        accion_act = ActividadUsuario(id_usuario=admin_id, accion=f"{accion.capitalize()} adelanto #{id_adelanto}", fecha=datetime.now())
        db.session.add(accion_act)
        db.session.commit()
    except Exception:
        db.session.rollback()

    return jsonify({'success': True, 'message': f'Adelanto {adelanto.estado.lower()} correctamente'})
