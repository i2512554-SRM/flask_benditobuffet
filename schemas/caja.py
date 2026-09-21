from flask_marshmallow import Marshmallow
from flask_marshmallow.sqla import SQLAlchemyAutoSchema
from marshmallow import fields
from models import TransaccionCaja, CierreCaja
from api.fechas import iso_utc

ma = Marshmallow()

class TransaccionCajaSchema(SQLAlchemyAutoSchema):
    fecha = fields.Method('serializar_fecha')
    monto = fields.Float()

    def serializar_fecha(self, objeto):
        return iso_utc(objeto.fecha)

    class Meta:
        model = TransaccionCaja
        load_instance = False
        sqla_session = None
        
transaccion_schema = TransaccionCajaSchema()
transacciones_schema = TransaccionCajaSchema(many=True)

class CierreCajaSchema(SQLAlchemyAutoSchema):
    fecha = fields.Method('serializar_fecha')
    fecha_cierre = fields.Method('serializar_cierre')
    monto_inicial = fields.Float()
    total_ventas = fields.Float()
    total_gastos = fields.Float()
    neto = fields.Float(allow_none=True)

    def serializar_fecha(self, objeto):
        return iso_utc(objeto.fecha)

    def serializar_cierre(self, objeto):
        return iso_utc(objeto.fecha_cierre)

    class Meta:
        model = CierreCaja
        load_instance = False
        sqla_session = None
        
cierre_schema = CierreCajaSchema()
cierres_schema = CierreCajaSchema(many=True)
