from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta, timezone
from models import db, TransaccionCaja, Usuario

rendimiento_bp = Blueprint('rendimiento', __name__)

ROLES_PERMITIDOS = (1, 2)
PERIODOS = ('dia', 'semana', 'mes', 'anio')
DIAS = ['dom', 'lun', 'mar', 'mié', 'jue', 'vie', 'sáb']
MESES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']


def _permitido(fn):
    from functools import wraps

    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        uid = int(get_jwt_identity())
        u = Usuario.query.get(uid)
        if not u or u.id_rol not in ROLES_PERMITIDOS or not u.estado:
            return jsonify({'success': False, 'error': 'Acceso restringido a rendimiento'}), 403
        return fn(*args, **kwargs)

    return wrapper


def _buckets(periodo, now):
    if periodo == 'dia':
        inicio = now.replace(hour=0, minute=0, second=0, microsecond=0)
        return [
            (f"{h:02d}:00", inicio + timedelta(hours=h), inicio + timedelta(hours=h + 1))
            for h in range(24)
        ]

    if periodo == 'semana':
        inicio = (now - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
        buckets = []
        for i in range(7):
            d = inicio + timedelta(days=i)
            buckets.append((f"{DIAS[d.weekday()]} {d.day:02d}", d, d + timedelta(days=1)))
        return buckets

    if periodo == 'mes':
        inicio = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        buckets = []
        for d in range(1, now.day + 1):
            bstart = inicio + timedelta(days=d - 1)
            buckets.append((f"{d:02d}", bstart, bstart + timedelta(days=1)))
        return buckets

    buckets = []
    for i in range(11, -1, -1):
        m = now.month - i
        y = now.year
        if m <= 0:
            m += 12
            y -= 1
        bstart = datetime(y, m, 1, tzinfo=timezone.utc)
        if m == 12:
            bend = datetime(y + 1, 1, 1, tzinfo=timezone.utc)
        else:
            bend = datetime(y, m + 1, 1, tzinfo=timezone.utc)
        buckets.append((MESES[m - 1], bstart, bend))
    return buckets


@rendimiento_bp.route('/rendimiento', methods=['GET'])
@_permitido
def rendimiento():
    from api.caja import reportes
    respuesta = reportes.__wrapped__()
    if isinstance(respuesta, tuple):
        return respuesta
    return jsonify(success=True, data=respuesta.get_json()['data']['puntos'])
