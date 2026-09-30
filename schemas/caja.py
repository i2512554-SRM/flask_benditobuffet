from flask_marshmallow import Marshmallow
from flask_marshmallow.sqla import SQLAlchemyAutoSchema
from marshmallow import fields
from models import db, TransaccionCaja, CierreCaja, Usuario
from api.fechas import iso_utc

ma = Marshmallow()

def _nombre_usuario(id_usuario):
    if not id_usuario:
        return None
    usuario = db.session.get(Usuario, int(id_usuario))
    if not usuario:
        return None
    return f'{usuario.nombres} {usuario.apellido}'.strip() or None

def _turno_usuario(id_usuario):
    if not id_usuario:
        return None
    usuario = db.session.get(Usuario, int(id_usuario))
    return usuario.turno or None if usuario else None

class TransaccionCajaSchema(SQLAlchemyAutoSchema):
    fecha = fields.Method('serializar_fecha')
    monto = fields.Float()
    responsable = fields.Method('serializar_responsable')

    def serializar_fecha(self, objeto):
        return iso_utc(objeto.fecha)

    def serializar_responsable(self, objeto):
        return _nombre_usuario(objeto.id_usuario)

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
    efectivo_contado = fields.Float(allow_none=True)
    responsable = fields.Method('serializar_responsable')
    turno = fields.Method('serializar_turno')

    def serializar_fecha(self, objeto):
        return iso_utc(objeto.fecha)

    def serializar_cierre(self, objeto):
        return iso_utc(objeto.fecha_cierre)

    def serializar_responsable(self, objeto):
        return _nombre_usuario(objeto.id_usuario)

    def serializar_turno(self, objeto):
        return _turno_usuario(objeto.id_usuario)

    class Meta:
        model = CierreCaja
        load_instance = False
        sqla_session = None
        
cierre_schema = CierreCajaSchema()
cierres_schema = CierreCajaSchema(many=True)
