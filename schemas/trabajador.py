from flask_marshmallow import Marshmallow
from marshmallow import fields

from api.fechas import iso_utc

ma = Marshmallow()


class NotificacionSchema(ma.Schema):
    id_notificacion = fields.Integer()
    titulo = fields.String()
    mensaje = fields.String(allow_none=True)
    leida = fields.Boolean()
    fecha = fields.Function(lambda n: iso_utc(n.fecha))


class PagoTrabajadorSchema(ma.Schema):
    id_pago = fields.Integer()
    monto = fields.Float()
    fecha = fields.Function(lambda p: iso_utc(p.fecha_pago))
    estado = fields.String()
    descripcion = fields.Function(lambda p: p.descripcion or 'Pago registrado')


class AdelantoTrabajadorSchema(ma.Schema):
    id_adelanto = fields.Integer()
    monto = fields.Float()
    motivo = fields.String()
    fecha = fields.Function(lambda a: iso_utc(a.fecha))
    estado = fields.String()
    respuesta = fields.String(attribute='respuesta_admin', allow_none=True)


class InfoTrabajadorSchema(ma.Schema):
    nombres = fields.String()
    apellido = fields.String()
    dni = fields.String(allow_none=True)
    correo = fields.String()
    telefono = fields.String(allow_none=True)
    cargo = fields.Function(lambda u: u.rol.nombre if u.rol else None)
    turnos = fields.Function(lambda u: [t.strip() for t in (u.turno or '').split(',') if t.strip()])
    estado_laboral = fields.Function(lambda u: 'Activo' if u.estado else 'Inactivo')
    fecha_ingreso = fields.Function(lambda u: u.perfil.fecha_ingreso.isoformat() if (u.perfil and u.perfil.fecha_ingreso) else None)
    horario = fields.Function(lambda u: u.perfil.horario if u.perfil else None)


notificaciones_schema = NotificacionSchema(many=True)
pagos_trabajador_schema = PagoTrabajadorSchema(many=True)
adelantos_trabajador_schema = AdelantoTrabajadorSchema(many=True)
info_trabajador_schema = InfoTrabajadorSchema()
