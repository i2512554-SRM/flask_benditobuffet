from flask_marshmallow import Marshmallow
from marshmallow import fields

from api.fechas import iso_utc

ma = Marshmallow()


class DatosPerfilSchema(ma.Schema):
    foto_perfil = fields.Function(lambda p: f"/uploads/perfiles/{p.foto_perfil}" if p.foto_perfil else None)
    fecha_ingreso = fields.Function(lambda p: p.fecha_ingreso.isoformat() if p.fecha_ingreso else None)
    horario = fields.String(allow_none=True)
    salario = fields.Float(allow_none=True)


class UsuarioPerfilSchema(ma.Schema):
    id_usuario = fields.Integer()
    nombres = fields.String()
    apellido = fields.String()
    correo = fields.String()
    telefono = fields.String(allow_none=True)
    usuario = fields.String()
    dni = fields.String(allow_none=True)
    rol = fields.Function(lambda u: u.rol.nombre if u.rol else None)
    id_rol = fields.Integer()
    turno = fields.String(allow_none=True)
    turnos = fields.Function(lambda u: [t.strip() for t in (u.turno or '').split(',') if t.strip()])
    fecha_creacion = fields.Function(lambda u: iso_utc(u.fecha_creacion))
    perfil = fields.Method('serializar_perfil')

    def serializar_perfil(self, usuario):
        if usuario.perfil:
            return DatosPerfilSchema().dump(usuario.perfil)
        return {'foto_perfil': None, 'fecha_ingreso': None, 'horario': None, 'salario': None}


class PagoPerfilSchema(ma.Schema):
    id_pago = fields.Integer()
    monto = fields.Float()
    fecha_pago = fields.Function(lambda p: iso_utc(p.fecha_pago))
    descripcion = fields.Function(lambda p: p.descripcion or 'Pago registrado')
    estado = fields.String()


class AdelantoPerfilSchema(ma.Schema):
    id_adelanto = fields.Integer()
    motivo = fields.String()
    monto = fields.Float()
    fecha = fields.Function(lambda a: iso_utc(a.fecha))
    estado = fields.String()
    respuesta_admin = fields.String(allow_none=True)


class ActividadPerfilSchema(ma.Schema):
    id_actividad = fields.Integer()
    accion = fields.String()
    fecha = fields.Function(lambda a: iso_utc(a.fecha))


class NotificacionPerfilSchema(ma.Schema):
    id_notificacion = fields.Integer()
    titulo = fields.String()
    mensaje = fields.String(allow_none=True)
    fecha = fields.Function(lambda n: iso_utc(n.fecha))


usuario_perfil_schema = UsuarioPerfilSchema()
pagos_perfil_schema = PagoPerfilSchema(many=True)
adelantos_perfil_schema = AdelantoPerfilSchema(many=True)
adelanto_creado_schema = AdelantoPerfilSchema(only=('id_adelanto', 'motivo', 'monto', 'fecha', 'estado'))
actividades_perfil_schema = ActividadPerfilSchema(many=True)
notificaciones_perfil_schema = NotificacionPerfilSchema(many=True)
