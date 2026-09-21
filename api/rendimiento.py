from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Usuario
from api.caja import _puntos_reporte

rendimiento_bp = Blueprint('rendimiento', __name__)

ROLES_PERMITIDOS = (1, 2)
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

@rendimiento_bp.route('/rendimiento', methods=['GET'])
@_permitido
def rendimiento():
    try:
        puntos = _puntos_reporte(request.args.get('periodo', 'mes'), request.args.get('fecha'))
    except ValueError:
        return jsonify(success=False, error='Fecha o periodo no válido'), 400
    return jsonify(success=True, data=puntos)
