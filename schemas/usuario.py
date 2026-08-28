from flask_marshmallow import Marshmallow
from flask_marshmallow.sqla import SQLAlchemyAutoSchema
from models import Usuario, PagoPersonal

ma = Marshmallow()

class UsuarioSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Usuario
        load_instance = False
        sqla_session = None
        include_fk = False
        exclude = ('clave',)
        
usuario_schema = UsuarioSchema()
usuarios_schema = UsuarioSchema(many=True)

class PagoPersonalSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = PagoPersonal
        load_instance = False
        sqla_session = None
        
pago_schema = PagoPersonalSchema()
pagos_schema = PagoPersonalSchema(many=True)
