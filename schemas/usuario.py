from flask_marshmallow import Marshmallow
from flask_marshmallow.sqla import SQLAlchemyAutoSchema
from marshmallow import fields
from models import Usuario
from api.fechas import iso_utc

ma = Marshmallow()


def _nombre(usuario):
    return f"{usuario.nombres} {usuario.apellido}" if usuario else 'Empleado'


class UsuarioSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Usuario
        load_instance = False
        sqla_session = None
        include_fk = False
        exclude = ('clave',)

    dni = fields.String(attribute='dni')
    fecha_creacion = fields.Function(lambda u: iso_utc(u.fecha_creacion))


class PagoHistorialSchema(ma.Schema):
    id_pago = fields.Integer()
    id_usuario = fields.Integer(allow_none=True)
    empleado = fields.Function(lambda p: _nombre(p.usuario_empleado))
    monto = fields.Float()
    fecha = fields.Function(lambda p: iso_utc(p.fecha_pago))
    estado = fields.String()
    descripcion = fields.String(allow_none=True)
    tipo = fields.String(allow_none=True)
    semana = fields.Function(lambda p: p.semana.isoformat() if p.semana else None)


class AdelantoHistorialSchema(ma.Schema):
    id_pago = fields.Function(lambda a: f'adelanto-{a.id_adelanto}')
    id_usuario = fields.Integer(allow_none=True)
    empleado = fields.Function(lambda a: _nombre(a.usuario_adelanto))
    monto = fields.Float()
    fecha = fields.Function(lambda a: iso_utc(a.fecha_gestion or a.fecha))
    estado = fields.String()
    descripcion = fields.Function(lambda a: f'Adelanto: {a.motivo}')


class PagoDetalleSchema(ma.Schema):
    id_pago = fields.Integer()
    monto = fields.Float()
    fecha = fields.Function(lambda p: iso_utc(p.fecha_pago))
    estado = fields.String()
    descripcion = fields.String(allow_none=True)


class PagoPersonalSchema(ma.Schema):
    id_pago = fields.Integer()
    monto = fields.Float()
    fecha = fields.Function(lambda p: p.fecha.isoformat() if p.fecha else None)
    tipo = fields.String()
    descripcion = fields.String(allow_none=True)


class AdelantoDetalleSchema(ma.Schema):
    id_adelanto = fields.Integer()
    monto = fields.Float()
    motivo = fields.String()
    fecha = fields.Function(lambda a: iso_utc(a.fecha_gestion or a.fecha))
    estado = fields.String()
    respuesta = fields.String(attribute='respuesta_admin', allow_none=True)


class AdelantoListadoSchema(ma.Schema):
    id_adelanto = fields.Integer()
    id_usuario = fields.Integer(allow_none=True)
    monto = fields.Float()
    fecha = fields.Function(lambda a: iso_utc(a.fecha))
    estado = fields.String()
    motivo = fields.String()


usuario_schema = UsuarioSchema()
pagos_historial_schema = PagoHistorialSchema(many=True)
adelantos_historial_schema = AdelantoHistorialSchema(many=True)
pago_registrado_schema = PagoDetalleSchema(only=('id_pago', 'monto', 'fecha', 'estado'))
pagos_detalle_schema = PagoDetalleSchema(many=True)
pagos_personal_schema = PagoPersonalSchema(many=True)
adelantos_detalle_schema = AdelantoDetalleSchema(many=True)
adelantos_listado_schema = AdelantoListadoSchema(many=True)
