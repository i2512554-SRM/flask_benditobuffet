from flask_marshmallow import Marshmallow
from marshmallow import fields

ma = Marshmallow()


def _foto(usuario):
    return f"/uploads/perfiles/{usuario.perfil.foto_perfil}" if (usuario.perfil and usuario.perfil.foto_perfil) else None


class UsuarioSesionSchema(ma.Schema):
    id = fields.Integer(attribute='id_usuario')
    usuario = fields.String()
    nombre = fields.String(attribute='nombres')
    rol = fields.Function(lambda u: u.rol.id_rol if u.rol else None)
    foto_perfil = fields.Function(_foto)


usuario_login_schema = UsuarioSesionSchema(only=('id', 'nombre', 'rol', 'foto_perfil'))
usuario_sesion_schema = UsuarioSesionSchema()
