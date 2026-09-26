from flask_marshmallow import Marshmallow
from marshmallow import fields

ma = Marshmallow()


class ConsultaDniSchema(ma.Schema):
    success = fields.Boolean()
    dni = fields.String()
    nombres = fields.String()
    apellidoPaterno = fields.String()
    apellidoMaterno = fields.String()


consulta_dni_schema = ConsultaDniSchema()
