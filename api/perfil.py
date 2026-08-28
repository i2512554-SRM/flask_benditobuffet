import os
import re
import uuid
from datetime import datetime

import bcrypt
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from models import db, Usuario, UsuarioPerfil, PagoEmpleado, Adelanto, ActividadUsuario
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


def _serializar_usuario(usuario):
    perfil = usuario.perfil
    turnos = [t.strip() for t in (usuario.turno or '').split(',') if t.strip()]
    return {
        'id_usuario': usuario.id_usuario,
        'nombres': usuario.nombres,
        'apellido': usuario.apellido,
        'correo': usuario.correo,
        'telefono': usuario.telefono,
        'usuario': usuario.usuario,
        'dni': usuario.dni,
        'rol': usuario.rol.nombre if usuario.rol else None,
        'id_rol': usuario.id_rol,
        'turno': usuario.turno,
        'turnos': turnos,
        'fecha_creacion': usuario.fecha_creacion.isoformat() if usuario.fecha_creacion else None,
        'perfil': {
            'foto_perfil': f"/uploads/perfiles/{perfil.foto_perfil}" if (perfil and perfil.foto_perfil) else None,
            'fecha_ingreso': perfil.fecha_ingreso.strftime('%d/%m/%Y') if (perfil and perfil.fecha_ingreso) else None,
            'horario': perfil.horario if perfil else None,
            'salario': perfil.salario if perfil else None,
        }
    }


@perfil_bp.route('', methods=['GET'])
@jwt_required()
def get_perfil():
    usuario_id = int(get_jwt_identity())
    usuario = Usuario.query.filter_by(id_usuario=usuario_id).first()
    if not usuario:
        return jsonify({'success': False, 'error': 'Usuario no encontrado'}), 404

    pagos = PagoEmpleado.query.filter_by(id_usuario=usuario_id).order_by(PagoEmpleado.fecha_pago.desc()).limit(6).all()
    adelantos = Adelanto.query.filter_by(id_usuario=usuario_id).order_by(Adelanto.fecha.desc()).limit(6).all()
    actividades = ActividadUsuario.query.filter_by(id_usuario=usuario_id).order_by(ActividadUsuario.fecha.desc()).limit(8).all()

    notificaciones_frescas = Adelanto.query.filter_by(
        id_usuario=usuario_id, notificacion_vista=False
    ).filter(Adelanto.respuesta_admin.isnot(None)).all()

    notif_data = []
    if notificaciones_frescas:
        for n in notificaciones_frescas:
            notif_data.append({
                'id_adelanto': n.id_adelanto,
                'monto': n.monto,
                'estado': n.estado,
                'respuesta_admin': n.respuesta_admin,
            })
            n.notificacion_vista = True
        db.session.commit()

    return jsonify({
        'success': True,
        'data': {
            'usuario': _serializar_usuario(usuario),
            'pagos': [{
                'id_pago': p.id_pago,
                'monto': p.monto,
                'fecha_pago': p.fecha_pago.strftime('%d/%m/%Y') if p.fecha_pago else None,
                'descripcion': p.descripcion or 'Pago registrado',
                'estado': p.estado,
            } for p in pagos],
            'adelantos': [{
                'id_adelanto': a.id_adelanto,
                'motivo': a.motivo,
                'monto': a.monto,
                'fecha': a.fecha.strftime('%d/%m/%Y') if a.fecha else None,
                'estado': a.estado,
                'respuesta_admin': a.respuesta_admin,
            } for a in adelantos],
            'actividades': [{
                'id_actividad': a.id_actividad,
                'accion': a.accion,
                'fecha': a.fecha.strftime('%d/%m/%Y %H:%M') if a.fecha else None,
            } for a in actividades],
            'notificaciones': notif_data,
            'resumen': {
                'pagos': len(pagos),
                'adelantos': len(adelantos),
            }
        }
    })


@perfil_bp.route('', methods=['PUT'])
@jwt_required()
def editar_perfil():
    usuario_id = int(get_jwt_identity())
    usuario = Usuario.query.filter_by(id_usuario=usuario_id).first()
    if not usuario:
        return jsonify({'success': False, 'error': 'Usuario no encontrado'}), 404

    contenido_tipo = request.content_type or ''
    if 'multipart/form-data' in contenido_tipo:
        telefono = (request.form.get('telefono') or '').strip()
        correo = (request.form.get('correo') or '').strip().lower()
        clave_nueva = (request.form.get('clave') or '').strip()
        foto = request.files.get('foto_perfil')
    else:
        data = request.get_json(silent=True) or {}
        telefono = (data.get('telefono') or '').strip()
        correo = (data.get('correo') or '').strip().lower()
        clave_nueva = (data.get('clave') or '').strip()
        foto = None

    if not correo or not _validar_correo(correo):
        return jsonify({'success': False, 'error': 'Ingrese un correo valido'}), 400

    correo_existente = Usuario.query.filter(
        Usuario.correo == correo, Usuario.id_usuario != usuario_id
    ).first()
    if correo_existente:
        return jsonify({'success': False, 'error': 'El correo ya esta registrado en otra cuenta'}), 400

    usuario.correo = correo
    usuario.telefono = telefono

    if clave_nueva:
        usuario.clave = bcrypt.hashpw(clave_nueva.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    perfil = usuario.perfil
    if not perfil:
        perfil = UsuarioPerfil(id_usuario=usuario_id)
        db.session.add(perfil)

    if foto and foto.filename:
        ext = foto.filename.rsplit('.', 1)[1].lower() if '.' in foto.filename else ''
        if ext not in ALLOWED_IMAGE_EXTENSIONS:
            return jsonify({'success': False, 'error': 'Formato de imagen no valido. Usa jpg, jpeg, png o webp'}), 400
        if not _validar_imagen_por_contenido(foto):
            return jsonify({'success': False, 'error': 'El archivo seleccionado no es una imagen valida'}), 400

        nombre_archivo = secure_filename(f"perfil_{usuario_id}_{uuid.uuid4().hex}.{ext}")
        ruta_archivo = os.path.join(current_app.config['UPLOAD_FOLDER'], nombre_archivo)
        foto.save(ruta_archivo)

        if perfil.foto_perfil:
            ruta_anterior = os.path.join(current_app.config['UPLOAD_FOLDER'], perfil.foto_perfil)
            if os.path.exists(ruta_anterior):
                try:
                    os.remove(ruta_anterior)
                except OSError:
                    pass

        perfil.foto_perfil = nombre_archivo

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'Perfil actualizado correctamente', 'data': _serializar_usuario(usuario)})
    except Exception:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'No se pudo actualizar el perfil. Intente de nuevo.'}), 500


@perfil_bp.route('/contrasena', methods=['PUT'])
@jwt_required()
def cambiar_contrasena():
    usuario_id = int(get_jwt_identity())
    usuario = Usuario.query.filter_by(id_usuario=usuario_id).first()
    if not usuario:
        return jsonify({'success': False, 'error': 'Usuario no encontrado'}), 404

    data = request.get_json(silent=True) or {}
    actual = (data.get('contrasena_actual') or '')
    nueva = (data.get('contrasena_nueva') or '')
    verificar = (data.get('contrasena_verificar') or '')

    if not actual or not nueva or not verificar:
        return jsonify({'success': False, 'error': 'Todos los campos son obligatorios'}), 400

    stored = usuario.clave.encode('utf-8') if isinstance(usuario.clave, str) else usuario.clave
    valida_actual = False
    try:
        valida_actual = bcrypt.checkpw(actual.encode('utf-8'), stored)
    except (ValueError, TypeError):
        valida_actual = (usuario.clave == actual)

    if not valida_actual:
        return jsonify({'success': False, 'error': 'La contrasena actual no es correcta'}), 400

    if nueva != verificar:
        return jsonify({'success': False, 'error': 'Las contrasenas nuevas no coinciden'}), 400

    if nueva == actual:
        return jsonify({'success': False, 'error': 'La nueva contrasena no puede ser igual a la actual'}), 400

    try:
        usuario.clave = bcrypt.hashpw(nueva.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        db.session.commit()
        return jsonify({'success': True, 'message': 'Contrasena actualizada correctamente'})
    except Exception:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'No se pudo cambiar la contrasena. Intente de nuevo.'}), 500


@perfil_bp.route('/adelantos', methods=['POST'])
@jwt_required()
def solicitar_adelanto():
    usuario_id = int(get_jwt_identity())
    usuario = Usuario.query.filter_by(id_usuario=usuario_id).first()
    if not usuario:
        return jsonify({'success': False, 'error': 'Usuario no encontrado'}), 404

    data = request.get_json(silent=True) or {}
    motivo = str(data.get('motivo') or '').strip()
    monto_text = str(data.get('monto') or '').strip().replace(',', '.')

    if not motivo:
        return jsonify({'success': False, 'error': 'El motivo es obligatorio para solicitar un adelanto'}), 400

    try:
        monto = float(monto_text)
        if monto <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Ingrese un monto valido. Debe ser mayor a cero.'}), 400

    adelanto = Adelanto(
        id_usuario=usuario_id,
        motivo=motivo,
        monto=monto,
        fecha=datetime.now(),
        estado='Pendiente'
    )
    db.session.add(adelanto)
    db.session.commit()

    try:
        rer_accion = ActividadUsuario(id_usuario=usuario_id, accion='Solicito adelanto', fecha=datetime.now())
        db.session.add(rer_accion)
        db.session.commit()
    except Exception:
        db.session.rollback()

    return jsonify({'success': True, 'message': 'Solicitud de adelanto enviada', 'data': {
        'id_adelanto': adelanto.id_adelanto,
        'motivo': adelanto.motivo,
        'monto': adelanto.monto,
        'fecha': adelanto.fecha.strftime('%d/%m/%Y') if adelanto.fecha else None,
        'estado': adelanto.estado,
    }})


@perfil_bp.route('/adelantos/<int:id_adelanto>', methods=['DELETE'])
@jwt_required()
def cancelar_adelanto(id_adelanto):
    usuario_id = int(get_jwt_identity())
    adelanto = Adelanto.query.filter_by(
        id_adelanto=id_adelanto, id_usuario=usuario_id
    ).first()
    if not adelanto:
        return jsonify({'success': False, 'error': 'Solicitud no encontrada'}), 404

    adelanto.estado = 'Cancelado'
    db.session.commit()
    return jsonify({'success': True, 'message': 'Solicitud de adelanto cancelada'})


@perfil_bp.route('/notificaciones/leer', methods=['POST'])
@jwt_required()
def leer_notificaciones():
    usuario_id = int(get_jwt_identity())
    Adelanto.query.filter_by(
        id_usuario=usuario_id, notificacion_vista=False
    ).update({'notificacion_vista': True})
    db.session.commit()
    return ('', 204)
