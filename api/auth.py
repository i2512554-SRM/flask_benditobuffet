import hashlib
import ipaddress

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, decode_token, jwt_required, get_jwt_identity, get_jwt
from api.sesiones import crear_sesion
from schemas.auth import usuario_login_schema, usuario_sesion_schema
from api.fechas import utc
from models import SesionUsuario
from datetime import datetime, timedelta, timezone
from sqlalchemy import and_, or_, text
from bd import db
from models import Usuario, DocumentoIdentidad, BloqueoLogin, IntentoLogin
import bcrypt

MAX_INTENTOS_FALLIDOS = 5
MAX_INTENTOS_IP = 20
DURACION_BLOQUEO_MIN = 15
VENTANA_INTENTOS_MIN = 15
_HASH_FICTICIO = bcrypt.hashpw(b'usuario-inexistente', bcrypt.gensalt())

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def _ahora():
    return datetime.now(timezone.utc)


def _obtener_ip():
    def normalizar(valor):
        try:
            return ipaddress.ip_address((valor or '').strip())
        except ValueError:
            return None

    configuradas = current_app.config.get('TRUSTED_PROXY_IPS', ())
    if isinstance(configuradas, str):
        configuradas = configuradas.split(',')
    redes = []
    for valor in configuradas:
        try:
            redes.append(ipaddress.ip_network(str(valor).strip(), strict=False))
        except ValueError:
            continue

    remota = normalizar(request.remote_addr)
    if remota is None:
        return 'desconocida'
    if not any(remota in red for red in redes):
        return str(remota)

    encabezado = request.headers.get('X-Forwarded-For', '')
    cadena = [normalizar(valor) for valor in encabezado.split(',') if valor.strip()]
    if not cadena or any(valor is None for valor in cadena):
        return str(remota)
    for candidata in reversed(cadena):
        if not any(candidata in red for red in redes):
            return str(candidata)
    return str(cadena[0])


def _usuario_bucket_ip(ip):
    return f'@ip:{ip}'


def _bloqueo_activo(identificador, ip):
    limite = _ahora()
    return BloqueoLogin.query.filter(
        or_(
            and_(
                BloqueoLogin.tipo == 'usuario',
                BloqueoLogin.usuario == identificador,
                BloqueoLogin.ip == ip
            ),
            and_(
                BloqueoLogin.tipo == 'ip',
                BloqueoLogin.usuario == _usuario_bucket_ip(ip),
                BloqueoLogin.ip == ip
            )
        ),
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


def _clave_advisory(tipo, usuario, ip):
    resumen = hashlib.sha256(f'{tipo}\0{usuario}\0{ip}'.encode('utf-8')).digest()
    return int.from_bytes(resumen[:8], byteorder='big', signed=True)


def _registrar_intento_fallido(identificador, ip, registrar_usuario):
    buckets = [(_usuario_bucket_ip(ip), ip, 'ip', MAX_INTENTOS_IP)]
    if registrar_usuario:
        buckets.append((identificador, ip, 'usuario', MAX_INTENTOS_FALLIDOS))

    if db.session.get_bind().dialect.name == 'postgresql':
        for llave in sorted({_clave_advisory(tipo, usuario, origen) for usuario, origen, tipo, _ in buckets}):
            db.session.execute(
                text('SELECT pg_advisory_xact_lock(CAST(:llave AS BIGINT))'),
                {'llave': llave}
            )

    ahora = _ahora()
    registros = []
    for usuario, origen, tipo, maximo in buckets:
        bloqueo = BloqueoLogin.query.filter_by(
            usuario=usuario,
            ip=origen,
            tipo=tipo
        ).order_by(BloqueoLogin.id.desc()).first()
        registros.append((bloqueo, usuario, origen, tipo, maximo))

    if any(
        bloqueo and bloqueo.bloqueado_hasta and utc(bloqueo.bloqueado_hasta) > ahora
        for bloqueo, _, _, _, _ in registros
    ):
        db.session.commit()
        return True

    bloqueado = False
    for bloqueo, usuario, origen, tipo, maximo in registros:
        if not bloqueo:
            bloqueo = BloqueoLogin(
                usuario=usuario,
                ip=origen,
                intentos=0,
                tipo=tipo,
                fecha=ahora
            )
            db.session.add(bloqueo)
        elif (
            utc(bloqueo.fecha) <= ahora - timedelta(minutes=VENTANA_INTENTOS_MIN)
            or bloqueo.bloqueado_hasta is not None
        ):
            bloqueo.intentos = 0
            bloqueo.bloqueado_hasta = None
        bloqueo.intentos = (bloqueo.intentos or 0) + 1
        bloqueo.fecha = ahora
        if bloqueo.intentos >= maximo:
            bloqueo.bloqueado_hasta = ahora + timedelta(minutes=DURACION_BLOQUEO_MIN)
            bloqueado = True
    db.session.commit()
    return bloqueado


def _limpiar_bloqueos(identificador, ip):
    if db.session.get_bind().dialect.name == 'postgresql':
        db.session.execute(
            text('SELECT pg_advisory_xact_lock(CAST(:llave AS BIGINT))'),
            {'llave': _clave_advisory('usuario', identificador, ip)}
        )
    for b in BloqueoLogin.query.filter_by(usuario=identificador, ip=ip, tipo='usuario').all():
        db.session.delete(b)
    db.session.commit()


def verificar_clave(usuario, clave):
    guardada = usuario.clave if isinstance(usuario.clave, str) else ''
    if not guardada.startswith('$2'):
        bcrypt.checkpw(clave.encode('utf-8'), _HASH_FICTICIO)
        return False
    try:
        return bcrypt.checkpw(clave.encode('utf-8'), guardada.encode('utf-8'))
    except (ValueError, TypeError):
        return False


def _respuesta_bloqueado(restante_min=DURACION_BLOQUEO_MIN):
    return jsonify({
        'success': False,
        'error': f'Demasiados intentos fallidos. Reintenta en {restante_min} min.'
    }), 429


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True)

    if (
        not isinstance(data, dict)
        or not isinstance(data.get('usuario'), str)
        or not isinstance(data.get('clave'), str)
    ):
        return jsonify({'success': False, 'error': 'Usuario y contraseña requeridos'}), 400

    identificador = data['usuario'].strip()
    clave = data['clave']
    if not identificador or not clave:
        return jsonify({'success': False, 'error': 'Usuario y contraseña requeridos'}), 400
    if len(identificador) > 255 or len(clave) > 1024:
        return jsonify({'success': False, 'error': 'Formato de credenciales inválido'}), 400
    ip = _obtener_ip()

    bloqueo = _bloqueo_activo(identificador, ip)
    if bloqueo:
        restante_min = max(1, int((utc(bloqueo.bloqueado_hasta) - _ahora()).total_seconds() // 60) + 1)
        return _respuesta_bloqueado(restante_min)

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
        bcrypt.checkpw(clave.encode('utf-8'), _HASH_FICTICIO)
        bloqueado = _registrar_intento_fallido(identificador, ip, registrar_usuario=False)
        _registrar_intento(identificador, ip, 'bloqueado' if bloqueado else 'fallo')
        if bloqueado:
            return _respuesta_bloqueado()
        return jsonify({'success': False, 'error': 'Credenciales inválidas'}), 401

    valida = verificar_clave(usuario, clave)

    if not valida:
        bloqueado = _registrar_intento_fallido(identificador, ip, registrar_usuario=True)
        _registrar_intento(identificador, ip, 'bloqueado' if bloqueado else 'fallo')
        if bloqueado:
            return _respuesta_bloqueado()
        return jsonify({'success': False, 'error': 'Credenciales inválidas'}), 401

    if not usuario.estado or not usuario.rol or not usuario.rol.estado:
        return jsonify(success=False, error='Cuenta inactiva'), 401

    _limpiar_bloqueos(identificador, ip)
    _registrar_intento(identificador, ip, 'exito')

    access_token, refresh_token = crear_sesion(usuario)

    return jsonify({
        'success': True,
        'data': {
            'token': access_token,
            'refresh_token': refresh_token,
            'user': usuario_login_schema.dump(usuario)
        }
    })

@auth_bp.route('/logout', methods=['POST'])
def logout():
    autorizacion = request.headers.get('Authorization', '')
    partes = autorizacion.split(None, 1)
    if len(partes) != 2 or partes[0].lower() != 'bearer' or not partes[1].strip():
        return jsonify({'success': False, 'error': 'Token requerido'}), 401
    try:
        payload = decode_token(partes[1].strip(), allow_expired=True)
    except Exception:
        return jsonify({'success': False, 'error': 'Token inválido'}), 401
    sid = payload.get('sid')
    identidad = payload.get('sub')
    if not sid or identidad is None:
        return jsonify({'success': False, 'error': 'Token inválido'}), 401
    sesion = db.session.get(SesionUsuario, sid)
    if sesion and str(sesion.id_usuario) == str(identidad) and not sesion.revocada:
        sesion.revocada = True
        db.session.commit()
    return jsonify({'success': True, 'message': 'Sesión cerrada correctamente'})

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    usuario = db.session.get(Usuario, int(current_user))
    if not usuario or not usuario.estado or not usuario.rol or not usuario.rol.estado:
        return jsonify(success=False, error='Cuenta inactiva'), 401
    access_token = create_access_token(identity=current_user, additional_claims={'sid': get_jwt()['sid']})
    return jsonify({'success': True, 'data': {'token': access_token}})

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    uid = int(get_jwt_identity())
    u = db.session.get(Usuario, uid)
    if not u or not u.estado:
        return jsonify({'success': False, 'error': 'Sesión no válida'}), 401
    return jsonify({'success': True, 'data': usuario_sesion_schema.dump(u)})
