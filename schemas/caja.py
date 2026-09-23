from flask_marshmallow import Marshmallow
from flask_marshmallow.sqla import SQLAlchemyAutoSchema
from models import TransaccionCaja, CierreCaja

ma = Marshmallow()

class TransaccionCajaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = TransaccionCaja
        load_instance = False
        sqla_session = None
        
transaccion_schema = TransaccionCajaSchema()
transacciones_schema = TransaccionCajaSchema(many=True)

class CierreCajaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = CierreCaja
        load_instance = False
        sqla_session = None
        
cierre_schema = CierreCajaSchema()
cierres_schema = CierreCajaSchema(many=True)
