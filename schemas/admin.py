from flask_marshmallow import Marshmallow
from marshmallow import fields

from api.fechas import iso_utc

ma = Marshmallow()


def _nombre(usuario, defecto):
    return f"{usuario.nombres} {usuario.apellido}" if usuario else defecto


class RolSchema(ma.Schema):
    id_rol = fields.Integer()
    nombre = fields.String()
    estado = fields.Boolean()
    fecha_creacion = fields.Function(lambda r: iso_utc(r.fecha_creacion))


class ActividadSchema(ma.Schema):
    id_actividad = fields.Integer()
    id_usuario = fields.Integer(allow_none=True)
    accion = fields.String()
    fecha = fields.Function(lambda a: iso_utc(a.fecha))


class AdelantoAdminSchema(ma.Schema):
    id_adelanto = fields.Integer()
    id_usuario = fields.Integer(allow_none=True)
    empleado = fields.Function(lambda a: _nombre(a.usuario_adelanto, 'Desconocido'))
    motivo = fields.String()
    monto = fields.Float()
    fecha = fields.Function(lambda a: iso_utc(a.fecha))
    fecha_gestion = fields.Function(lambda a: iso_utc(a.fecha_gestion))
    estado = fields.String()
    respuesta_admin = fields.String(allow_none=True)


class IntentoLoginSchema(ma.Schema):
    id = fields.Integer()
    identificador = fields.String()
    usuario_nombre = fields.String(allow_none=True)
    ip = fields.Function(lambda i: i.ip or '-')
    resultado = fields.String()
    fecha = fields.Function(lambda i: iso_utc(i.fecha))


class BloqueoLoginSchema(ma.Schema):
    id = fields.Integer()
    usuario = fields.String()
    usuario_nombre = fields.String(allow_none=True)
    usuario_rol = fields.Integer(allow_none=True)
    ip = fields.Function(lambda b: b.ip or '-')
    intentos = fields.Integer()
    bloqueado_hasta = fields.Function(lambda b: iso_utc(b.bloqueado_hasta))
    fecha = fields.Function(lambda b: iso_utc(b.fecha))


class ActividadRecienteSchema(ma.Schema):
    tipo = fields.String()
    titulo = fields.String()
    descripcion = fields.String()
    icono = fields.String()
    fecha = fields.Function(lambda item: iso_utc(item['fecha']))


roles_schema = RolSchema(many=True)
actividades_schema = ActividadSchema(many=True)
adelantos_admin_schema = AdelantoAdminSchema(many=True)
intentos_login_schema = IntentoLoginSchema(many=True)
bloqueos_login_schema = BloqueoLoginSchema(many=True)
actividad_reciente_schema = ActividadRecienteSchema(many=True)
