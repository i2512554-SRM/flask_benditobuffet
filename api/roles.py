from functools import wraps

from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from bd import db
from models import Usuario

ADMIN = 1
CAJERA = 2
COCINA = 3
TRABAJADOR = 4

ROLES_CAJA = (ADMIN, CAJERA)
ROLES_INVENTARIO = (ADMIN, COCINA)
ROLES_TRABAJADOR = (CAJERA, COCINA, TRABAJADOR)


def requiere_roles(*roles, mensaje='Acceso denegado', pasar_usuario=False):
    def decorador(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            usuario = db.session.get(Usuario, int(get_jwt_identity()))
            if not usuario or not usuario.estado or usuario.id_rol not in roles:
                return jsonify(success=False, error=mensaje), 403
            if pasar_usuario:
                return fn(usuario, *args, **kwargs)
            return fn(*args, **kwargs)
        return wrapper
    return decorador


admin_required = requiere_roles(ADMIN, mensaje='Acceso restringido a administradores')
