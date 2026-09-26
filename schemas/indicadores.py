from flask_marshmallow import Marshmallow
from marshmallow import fields

ma = Marshmallow()


class KpiSchema(ma.Schema):
    codigo = fields.String()
    nombre = fields.String()
    descripcion = fields.String(allow_none=True)
    valor = fields.Float(allow_none=True)
    unidad = fields.String()
    alerta = fields.String(allow_none=True)
    nota = fields.String(allow_none=True)
    estimado = fields.Boolean()
    variacion = fields.Float(allow_none=True)
    tendencia = fields.String(allow_none=True)
    comparacion = fields.Dict(allow_none=True)
    serie = fields.List(fields.Dict(allow_none=True))
    detalle = fields.Dict(allow_none=True)


kpis_schema = KpiSchema(many=True)