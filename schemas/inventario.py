from flask_marshmallow import Marshmallow
from flask_marshmallow.sqla import SQLAlchemyAutoSchema
from marshmallow import fields
from models import Producto, Inversion

ma = Marshmallow()

class ProductoSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Producto
        load_instance = False
        sqla_session = None

    categoria = fields.String(attribute='categoria')
        
producto_schema = ProductoSchema()
productos_schema = ProductoSchema(many=True)

class InversionSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Inversion
        load_instance = False
        sqla_session = None

    proveedor = fields.String(attribute='proveedor')
        
inversion_schema = InversionSchema()
inversiones_schema = InversionSchema(many=True)
