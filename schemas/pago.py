from flask_marshmallow import Marshmallow

ma = Marshmallow()

class PagoEmpleadoSchema(ma.Schema):
    class Meta:
        fields = ('id', 'empleado_id', 'monto', 'fecha', 'periodo', 'descripcion', 'estado')
        
pago_schema = PagoEmpleadoSchema()
pagos_schema = PagoEmpleadoSchema(many=True)

class PagoPersonalSchema(ma.Schema):
    class Meta:
        fields = ('id', 'empleado_id', 'monto', 'fecha', 'periodo', 'tipo', 'descripcion')
        
pago_personal_schema = PagoPersonalSchema()
pagos_personal_schema = PagoPersonalSchema(many=True)
