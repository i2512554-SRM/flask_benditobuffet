from api.fechas import ahora, LIMA
from api.validaciones import validar_personal
from api.sesiones import crear_sesion
from api.auth import verificar_clave
from api.roles import ADMIN
from schemas.perfil import (usuario_perfil_schema, pagos_perfil_schema, adelantos_perfil_schema,
                            adelanto_creado_schema, actividades_perfil_schema, notificaciones_perfil_schema)
from models import SueldoSemanal
import os
import re
import uuid
from decimal import Decimal, InvalidOperation

import bcrypt
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from models import db, Usuario, UsuarioPerfil, PagoEmpleado, Adelanto, ActividadUsuario, Notificacion
from werkzeug.utils import secure_filename


perfil_bp = Blueprint('perfil', __name__, url_prefix='/api/perfil')

ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}

_MAGIC_BYTES = {
    b'\xff\xd8\xff': 'jpg',
    b'\x89PNG\r\n\x1a\n': 'png',
    b'RIFF': 'webp',
}


def _validar_imagen_por_contenido(foto):
    source = foto.stream if hasattr(foto, 'stream') else foto
    header = source.read(12)
    source.seek(0)
    for magic in _MAGIC_BYTES:
        if header[:len(magic)] == magic:
            return True
    return False


def _validar_correo(correo):
    return bool(re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', correo))


def _json_objeto():
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else None


def _serializar_usuario(usuario):
    data = usuario_perfil_schema.dump(usuario)
    tarifa = SueldoSemanal.query.filter(SueldoSemanal.id_usuario == usuario.id_usuario,
        SueldoSemanal.desde <= ahora().astimezone(LIMA).date()).order_by(SueldoSemanal.desde.desc()).first()
    data['perfil']['sueldo_semanal'] = float(tarifa.monto) if tarifa else None
    return data


@perfil_bp.route('', methods=['GET'])
@jwt_required()
def get_perfil():
    usuario_id = int(get_jwt_identity())
    usuario = Usuario.query.filter_by(id_usuario=usuario_id).first()
    if not usuario or not usuario.estado:
        return jsonify({'success': False, 'error': 'Usuario no encontrado'}), 404

    pagos = PagoEmpleado.query.filter_by(id_usuario=usuario_id).order_by(PagoEmpleado.fecha_pago.desc()).limit(6).all()
    adelantos = Adelanto.query.filter_by(id_usuario=usuario_id).order_by(Adelanto.fecha.desc()).limit(6).all()
    actividades = ActividadUsuario.query.filter_by(id_usuario=usuario_id).order_by(ActividadUsuario.fecha.desc()).limit(8).all()

    notificaciones = Notificacion.query.filter_by(id_usuario=usuario_id, leida=False).order_by(
        Notificacion.fecha.desc()).limit(10).all()

    return jsonify({
        'success': True,
        'data': {
            'usuario': _serializar_usuario(usuario),
            'pagos': pagos_perfil_schema.dump(pagos),
            'adelantos': adelantos_perfil_schema.dump(adelantos),
            'actividades': actividades_perfil_schema.dump(actividades),
            'notificaciones': notificaciones_perfil_schema.dump(notificaciones),
            'resumen': {
                'pagos': PagoEmpleado.query.filter_by(id_usuario=usuario_id).count(),
                'adelantos': Adelanto.query.filter_by(id_usuario=usuario_id).count(),
            }
        }
    })


@perfil_bp.route('', methods=['PUT'])
@jwt_required()
def editar_perfil():
    usuario_id = int(get_jwt_identity())
    usuario = Usuario.query.filter_by(id_usuario=usuario_id).first()
    if not usuario or not usuario.estado:
        return jsonify({'success': False, 'error': 'Usuario no encontrado'}), 404

    contenido_tipo = request.content_type or ''
    if 'multipart/form-data' in contenido_tipo:
        origen = request.form
        foto = request.files.get('foto_perfil')
    else:
        origen = _json_objeto()
        if origen is None:
            return jsonify(success=False, error='El cuerpo debe ser un objeto JSON.'), 400
        foto = None
    telefono_recibido = origen.get('telefono')
    correo_recibido = origen.get('correo')
    clave_recibida = origen.get('clave') or ''
    if not all(isinstance(valor, str) for valor in (telefono_recibido or '', correo_recibido or '', clave_recibida)):
        return jsonify(success=False, error='Los datos del perfil no son válidos.'), 400
    telefono = telefono_recibido.strip() if telefono_recibido is not None else usuario.telefono
    correo = correo_recibido.strip().lower() if correo_recibido is not None else usuario.correo
    clave_nueva = clave_recibida.strip()

    if not correo or len(correo) > 150 or not _validar_correo(correo):
        return jsonify({'success': False, 'error': 'Ingrese un correo válido'}), 400

    correo_existente = Usuario.query.filter(
        Usuario.correo == correo, Usuario.id_usuario != usuario_id
    ).first()
    if correo_existente:
        return jsonify({'success': False, 'error': 'El correo ya está registrado en otra cuenta'}), 400

    if telefono_recibido is not None and telefono and not re.fullmatch(r'[0-9]{9}', telefono):
        return jsonify(success=False, error='El teléfono debe contener 9 números.'), 400

    usuario.correo = correo
    usuario.telefono = telefono

    if clave_nueva:
        return jsonify(success=False, error='Utiliza Cambiar contraseña con tu contraseña actual.'), 400

    perfil = usuario.perfil
    nombre_nuevo = None
    ruta_nueva = None
    nombre_anterior = perfil.foto_perfil if perfil else None
    if foto and foto.filename:
        ext = foto.filename.rsplit('.', 1)[1].lower() if '.' in foto.filename else ''
        if ext not in ALLOWED_IMAGE_EXTENSIONS:
            return jsonify({'success': False, 'error': 'Formato de imagen no válido. Usa jpg, jpeg, png o webp'}), 400
        if not _validar_imagen_por_contenido(foto):
            return jsonify({'success': False, 'error': 'El archivo seleccionado no es una imagen válida'}), 400

        nombre_nuevo = secure_filename(f"perfil_{usuario_id}_{uuid.uuid4().hex}.{ext}")
        ruta_nueva = os.path.join(current_app.config['UPLOAD_FOLDER'], nombre_nuevo)

    try:
        if not perfil:
            perfil = UsuarioPerfil(id_usuario=usuario_id)
            db.session.add(perfil)
        if ruta_nueva:
            foto.save(ruta_nueva)
            perfil.foto_perfil = nombre_nuevo
        db.session.commit()
    except Exception:
        db.session.rollback()
        if ruta_nueva and os.path.exists(ruta_nueva):
            try:
                os.remove(ruta_nueva)
            except OSError:
                pass
        return jsonify({'success': False, 'error': 'No se pudo actualizar el perfil. Intente de nuevo.'}), 500

    if nombre_nuevo and nombre_anterior and nombre_anterior != nombre_nuevo:
        ruta_anterior = os.path.join(current_app.config['UPLOAD_FOLDER'], nombre_anterior)
        if os.path.exists(ruta_anterior):
            try:
                os.remove(ruta_anterior)
            except OSError:
                pass

    return jsonify({'success': True, 'message': 'Perfil actualizado correctamente', 'data': _serializar_usuario(usuario)})


@perfil_bp.route('/contrasena', methods=['PUT'])
@jwt_required()
def cambiar_contrasena():
    usuario_id = int(get_jwt_identity())
    usuario = Usuario.query.filter_by(id_usuario=usuario_id).first()
    if not usuario or not usuario.estado:
        return jsonify({'success': False, 'error': 'Usuario no encontrado'}), 404

    data = _json_objeto()
    if data is None:
        return jsonify(success=False, error='El cuerpo debe ser un objeto JSON.'), 400
    actual = (data.get('contrasena_actual') or '')
    nueva = (data.get('contrasena_nueva') or '')
    verificar = (data.get('contrasena_verificar') or '')

    if not all(isinstance(valor, str) for valor in (actual, nueva, verificar)):
        return jsonify(success=False, error='Las contraseñas deben ser texto.'), 400

    if not actual or not nueva or not verificar:
        return jsonify({'success': False, 'error': 'Todos los campos son obligatorios'}), 400

    if not verificar_clave(usuario, actual):
        return jsonify({'success': False, 'error': 'La contraseña actual no es correcta'}), 400

    if nueva != verificar:
        return jsonify({'success': False, 'error': 'Las contraseñas nuevas no coinciden'}), 400
    error = validar_personal({'clave': nueva})
    if error:
        return jsonify(success=False, error=error), 400

    if nueva == actual:
        return jsonify({'success': False, 'error': 'La nueva contraseña no puede ser igual a la actual'}), 400

    try:
        usuario.clave = bcrypt.hashpw(nueva.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'No se pudo cambiar la contraseña. Intente de nuevo.'}), 500
    token, refresh_token = crear_sesion(usuario)
    return jsonify({'success': True, 'message': 'Contraseña actualizada. Las demás sesiones abiertas se cerraron.',
                    'data': {'token': token, 'refresh_token': refresh_token}})


@perfil_bp.route('/adelantos', methods=['POST'])
@jwt_required()
def solicitar_adelanto():
    usuario_id = int(get_jwt_identity())
    usuario = Usuario.query.filter_by(id_usuario=usuario_id).first()
    if not usuario or not usuario.estado:
        return jsonify({'success': False, 'error': 'Usuario no encontrado'}), 404

    if usuario.id_rol == ADMIN:
        return jsonify(success=False, error='Los administradores no solicitan adelantos.'), 403
    data = _json_objeto()
    if data is None:
        return jsonify(success=False, error='El cuerpo debe ser un objeto JSON.'), 400
    motivo_recibido = data.get('motivo') or ''
    if not isinstance(motivo_recibido, str):
        return jsonify(success=False, error='El motivo no es válido.'), 400
    motivo = motivo_recibido.strip()
    monto_text = str(data.get('monto') or '').strip().replace(',', '.')

    if not motivo or len(motivo) > 255:
        return jsonify({'success': False, 'error': 'El motivo es obligatorio y admite hasta 255 caracteres'}), 400

    try:
        monto = Decimal(monto_text)
        if (
            not monto.is_finite()
            or monto <= 0
            or monto > Decimal('9999999999.99')
            or monto.quantize(Decimal('.01')) != monto
        ):
            raise ValueError()
    except (InvalidOperation, ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Ingrese un monto positivo con hasta dos decimales.'}), 400

    adelanto = Adelanto(
        id_usuario=usuario_id,
        motivo=motivo,
        monto=monto,
        fecha=ahora(),
        estado='Pendiente'
    )
    db.session.add(adelanto)
    db.session.commit()

    try:
        rer_accion = ActividadUsuario(id_usuario=usuario_id, accion='Solicito adelanto', fecha=ahora())
        db.session.add(rer_accion)
        db.session.commit()
    except Exception:
        db.session.rollback()

    return jsonify({'success': True, 'message': 'Solicitud de adelanto enviada',
                    'data': adelanto_creado_schema.dump(adelanto)})


@perfil_bp.route('/adelantos/<int:id_adelanto>', methods=['DELETE'])
@jwt_required()
def cancelar_adelanto(id_adelanto):
    usuario_id = int(get_jwt_identity())
    adelanto = Adelanto.query.filter_by(
        id_adelanto=id_adelanto, id_usuario=usuario_id
    ).with_for_update().first()
    if not adelanto:
        return jsonify({'success': False, 'error': 'Solicitud no encontrada'}), 404

    if adelanto.estado != 'Pendiente':
        return jsonify(success=False, error='Solo puedes cancelar solicitudes pendientes.'), 409
    adelanto.estado = 'Cancelado'
    db.session.commit()
    return jsonify({'success': True, 'message': 'Solicitud de adelanto cancelada'})


@perfil_bp.route('/notificaciones/leer', methods=['POST'])
@jwt_required()
def leer_notificaciones():
    usuario_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    consulta = Notificacion.query.filter_by(id_usuario=usuario_id, leida=False)
    if isinstance(data, dict) and data.get('id_notificacion') is not None:
        try:
            consulta = consulta.filter(Notificacion.id_notificacion == int(data['id_notificacion']))
        except (TypeError, ValueError):
            return jsonify(success=False, error='Notificación no válida.'), 400
    consulta.update({'leida': True}, synchronize_session=False)
    db.session.commit()
    return ('', 204)
