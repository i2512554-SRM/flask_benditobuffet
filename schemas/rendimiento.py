from flask_marshmallow import Marshmallow
from marshmallow import fields

ma = Marshmallow()


class PuntoRendimientoSchema(ma.Schema):
    etiqueta = fields.String()
    ingresos = fields.Float()
    egresos = fields.Float()
    ganancia = fields.Float()


puntos_rendimiento_schema = PuntoRendimientoSchema(many=True)
