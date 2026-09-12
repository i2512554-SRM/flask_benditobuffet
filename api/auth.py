from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta, timezone
from sqlalchemy import or_
from bd import db
from models import Usuario, DocumentoIdentidad, BloqueoLogin, ActividadUsuario, IntentoLogin
import bcrypt

MAX_INTENTOS_FALLIDOS = 5
DURACION_BLOQUEO_MIN = 15

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def _ahora():
    return datetime.now(timezone.utc)


def _obtener_ip():
    fwd = request.headers.get('X-Forwarded-For', '')
    if fwd and fwd.strip():
        return fwd.split(',')[0].strip()
    return request.remote_addr or 'desconocida'


def _bloqueo_activo(identificador):
    limite = _ahora()
    return BloqueoLogin.query.filter(
        BloqueoLogin.usuario == identificador,
        BloqueoLogin.bloqueado_hasta.isnot(None),
        BloqueoLogin.bloqueado_hasta > limite
    ).order_by(BloqueoLogin.bloqueado_hasta.desc()).first()


def _registrar_intento(identificador, ip, resultado):
    db.session.add(IntentoLogin(
        identificador=identificador,
        ip=ip,
        resultado=resultado,
        fecha=_ahora()
    ))
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()


def _registrar_intento_fallido(identificador, ip):
    bloqueo = BloqueoLogin.query.filter_by(usuario=identificador, ip=ip).order_by(BloqueoLogin.id.desc()).first()
    if not bloqueo:
        bloqueo = BloqueoLogin(usuario=identificador, ip=ip, intentos=1, tipo='usuario', fecha=_ahora())
        db.session.add(bloqueo)
    else:
        bloqueo.intentos = (bloqueo.intentos or 0) + 1
        bloqueo.fecha = _ahora()

    if bloqueo.intentos >= MAX_INTENTOS_FALLIDOS:
        bloqueo.bloqueado_hasta = _ahora() + timedelta(minutes=DURACION_BLOQUEO_MIN)
    db.session.commit()


def _limpiar_bloqueos(identificador, ip):
    for b in BloqueoLogin.query.filter(BloqueoLogin.usuario == identificador).all():
        db.session.delete(b)
    db.session.commit()


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or 'usuario' not in data or 'clave' not in data:
        return jsonify({'success': False, 'error': 'Usuario y contraseña requeridos'}), 400

    identificador = data['usuario']
    ip = _obtener_ip()

    bloqueo = _bloqueo_activo(identificador)
    if bloqueo:
        _registrar_intento(identificador, ip, 'bloqueado')
        restante_min = max(1, int((bloqueo.bloqueado_hasta - _ahora()).total_seconds() // 60) + 1)
        return jsonify({
            'success': False,
            'error': f'Demasiados intentos fallidos. Cuenta bloqueada, reintenta en {restante_min} min.'
        }), 429

    usuario = Usuario.query.outerjoin(
        DocumentoIdentidad,
        DocumentoIdentidad.id_documento == Usuario.id_documento
    ).filter(
        or_(
            Usuario.usuario == identificador,
            DocumentoIdentidad.numero == identificador
        )
    ).first()

    if not usuario:
        _registrar_intento_fallido(identificador, ip)
        _registrar_intento(identificador, ip, 'fallo')
        return jsonify({'success': False, 'error': 'Credenciales inválidas'}), 401

    if not usuario.estado or not usuario.rol or not usuario.rol.estado:
        return jsonify(success=False, error='Cuenta inactiva'), 401
    clave = data['clave']
    stored = usuario.clave if isinstance(usuario.clave, str) else ''
    valida = False

    if stored.startswith('$2'):
        try:
            valida = bcrypt.checkpw(clave.encode('utf-8'), stored.encode('utf-8'))
        except (ValueError, TypeError):
            valida = False
    else:
        valida = (stored == clave)

    if not valida:
        _registrar_intento_fallido(identificador, ip)
        _registrar_intento(identificador, ip, 'fallo')
        return jsonify({'success': False, 'error': 'Credenciales inválidas'}), 401

    if not stored.startswith('$2'):
        usuario.clave = bcrypt.hashpw(clave.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        db.session.commit()

    _limpiar_bloqueos(identificador, ip)
    _registrar_intento(identificador, ip, 'exito')

    try:
        db.session.add(ActividadUsuario(id_usuario=usuario.id_usuario, accion='Inició sesión', fecha=_ahora()))
        db.session.commit()
    except Exception:
        db.session.rollback()

    access_token = create_access_token(identity=str(usuario.id_usuario))
    refresh_token = create_refresh_token(identity=str(usuario.id_usuario))

    return jsonify({
        'success': True,
        'data': {
            'token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': usuario.id_usuario,
                'nombre': usuario.nombres,
                'rol': usuario.rol.id_rol if usuario.rol else None
            }
        }
    })

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    # JWT es stateless, simplemente retornamos exito
    return jsonify({'success': True, 'message': 'Sesión cerrada correctamente'})

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    usuario = db.session.get(Usuario, int(current_user))
    if not usuario or not usuario.estado:
        return jsonify(success=False, error='Cuenta inactiva'), 401
    access_token = create_access_token(identity=current_user)
    return jsonify({'success': True, 'data': {'token': access_token}})

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    uid = int(get_jwt_identity())
    u = Usuario.query.get(uid)
    if not u or not u.estado:
        return jsonify({'success': False, 'error': 'Sesión no válida'}), 401
    return jsonify({
        'success': True,
        'data': {
            'id': u.id_usuario,
            'usuario': u.usuario,
            'nombre': u.nombres,
            'rol': u.rol.id_rol if u.rol else None,
        }
    })