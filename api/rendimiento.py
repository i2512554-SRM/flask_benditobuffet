from flask import Blueprint, request, jsonify
from api.caja import puntos_reporte
from api.roles import ROLES_CAJA, requiere_roles
from schemas.rendimiento import puntos_rendimiento_schema

rendimiento_bp = Blueprint('rendimiento', __name__)

_permitido = requiere_roles(*ROLES_CAJA, mensaje='Acceso restringido a rendimiento')

@rendimiento_bp.route('/rendimiento', methods=['GET'])
@_permitido
def rendimiento():
    try:
        puntos = puntos_reporte(request.args.get('periodo', 'mes'), request.args.get('fecha'))
    except ValueError:
        return jsonify(success=False, error='Fecha o periodo no válido'), 400
    return jsonify(success=True, data=puntos_rendimiento_schema.dump(puntos))
