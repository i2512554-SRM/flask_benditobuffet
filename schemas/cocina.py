from flask_marshmallow import Marshmallow
from marshmallow import fields

from api.fechas import iso_utc

ma = Marshmallow()


class ProductoCocinaSchema(ma.Schema):
    id_producto = fields.Integer()
    nombre = fields.String()
    categoria = fields.Function(lambda p: p.categoria or None)
    stock = fields.Function(lambda p: float(p.stock or 0))
    unidad = fields.Function(lambda p: p.unidad_medida or 'Un')
    unidad_medida = fields.Function(lambda p: p.unidad_medida or 'Un')
    activo = fields.Boolean(attribute='estado')


class SolicitudInsumoSchema(ma.Schema):
    id_solicitud = fields.Integer()
    id_producto = fields.Integer()
    producto = fields.String()
    cantidad = fields.Float()
    observacion = fields.String(allow_none=True)
    estado = fields.String()
    respuesta = fields.String(allow_none=True)
    fecha = fields.Function(lambda s: iso_utc(s.fecha))


producto_cocina_schema = ProductoCocinaSchema()
solicitud_schema = SolicitudInsumoSchema()
solicitudes_schema = SolicitudInsumoSchema(many=True)
