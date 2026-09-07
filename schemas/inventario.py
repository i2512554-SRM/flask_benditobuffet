from flask_marshmallow import Marshmallow
from flask_marshmallow.sqla import SQLAlchemyAutoSchema
from marshmallow import fields
from models import Producto, Inversion, CompraInventario, DetalleCompraInventario, InventarioMovimiento

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

class DetalleCompraInventarioSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = DetalleCompraInventario
        load_instance = False
        sqla_session = None

    producto = fields.String(attribute='producto')

detalle_compra_inventario_schema = DetalleCompraInventarioSchema()
detalles_compra_inventario_schema = DetalleCompraInventarioSchema(many=True)

class CompraInventarioSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = CompraInventario
        load_instance = False
        sqla_session = None

    proveedor = fields.String(attribute='proveedor')
    detalle = fields.List(fields.Nested(DetalleCompraInventarioSchema), attribute='detalle')

compra_inventario_schema = CompraInventarioSchema()
compras_inventario_schema = CompraInventarioSchema(many=True)

class InventarioMovimientoSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = InventarioMovimiento
        load_instance = False
        sqla_session = None

    producto = fields.String(attribute='producto')
    usuario = fields.String(attribute='usuario')

inventario_movimiento_schema = InventarioMovimientoSchema()
inventario_movimientos_schema = InventarioMovimientoSchema(many=True)
