from flask_marshmallow import Marshmallow
from marshmallow import fields

from models import db, Usuario
from api.fechas import iso_utc

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
    limites = fields.Dict(allow_none=True)


kpis_schema = KpiSchema(many=True)


class MetaIndicadorSchema(ma.Schema):
    codigo = fields.String()
    atencion = fields.Float(attribute='limite_atencion')
    revisar = fields.Float(attribute='limite_revisar')
    actualizado_en = fields.Method('serializar_fecha')
    actualizado_por = fields.Method('serializar_responsable')

    def serializar_fecha(self, objeto):
        return iso_utc(objeto.actualizado_en)

    def serializar_responsable(self, objeto):
        if not objeto.id_usuario:
            return None
        usuario = db.session.get(Usuario, int(objeto.id_usuario))
        return f'{usuario.nombres} {usuario.apellido}'.strip() or None if usuario else None


meta_indicador_schema = MetaIndicadorSchema()
