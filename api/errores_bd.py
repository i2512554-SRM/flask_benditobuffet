from flask import jsonify
from sqlalchemy.exc import ProgrammingError, OperationalError, DataError, IntegrityError
from models import db


def configurar_errores_bd(app):
    @app.errorhandler(DataError)
    def error_datos(error):
        db.session.rollback()
        app.logger.warning('Dato rechazado por la base de datos: %s', getattr(error.orig, 'sqlstate', None))
        return jsonify(success=False, error='Algún dato excede el tamaño o formato permitido.'), 400

    @app.errorhandler(IntegrityError)
    def error_integridad(error):
        db.session.rollback()
        app.logger.warning('Operación rechazada por integridad: %s', getattr(error.orig, 'sqlstate', None))
        return jsonify(success=False, error='La operación entra en conflicto con registros existentes.'), 409

    @app.errorhandler(ProgrammingError)
    @app.errorhandler(OperationalError)
    def error_base(error):
        db.session.rollback()
        codigo = getattr(error.orig, 'sqlstate', None)
        texto = str(error.orig).lower()
        if codigo in ('42P01', '42703') or ('no such' in texto and any(t in texto for t in (
            'sesiones_usuario', 'sueldos_semanales', 'descuentos_semanales', 'atenciones_insumos', 'pagos_empleados'))):
            app.logger.error('Falta aplicar la actualización de esquema del sistema.')
            return jsonify(success=False, error='Hay una actualización pendiente del sistema. Contacta al administrador.'), 503
        app.logger.error('No se pudo completar una operación de base de datos.')
        return jsonify(success=False, error='No se pudo completar la operación. Intenta nuevamente.'), 500
