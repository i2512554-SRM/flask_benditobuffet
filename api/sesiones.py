"""Sesiones revocables compartidas entre procesos y renovación limitada."""
import hashlib
import uuid
from datetime import timedelta
from flask import current_app, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token
from models import db, SesionUsuario, Usuario
from api.fechas import ahora, utc


def huella(usuario):
    return hashlib.sha256(str(usuario.clave).encode('utf-8')).hexdigest()


def crear_sesion(usuario):
    vigencia = current_app.config.get('JWT_REFRESH_TOKEN_EXPIRES', timedelta(days=30))
    if isinstance(vigencia, (int, float)):
        vigencia = timedelta(seconds=vigencia)
    s = SesionUsuario(id=str(uuid.uuid4()), id_usuario=usuario.id_usuario,
        huella_clave=huella(usuario), expira=ahora() + vigencia, revocada=False)
    db.session.add(s)
    db.session.commit()
    claims = {'sid': s.id}
    return (create_access_token(identity=str(usuario.id_usuario), additional_claims=claims),
            create_refresh_token(identity=str(usuario.id_usuario), additional_claims=claims))


def configurar_sesiones(jwt):
    @jwt.token_in_blocklist_loader
    def revocado(header, payload):
        sid = payload.get('sid')
        if not sid:
            return True  # Las sesiones antiguas deben volver a iniciar sesión.
        s = db.session.get(SesionUsuario, sid)
        u = db.session.get(Usuario, s.id_usuario) if s else None
        return (not s or s.revocada or utc(s.expira) <= ahora() or not u
                or not u.estado or not u.rol or not u.rol.estado
                or str(u.id_usuario) != payload.get('sub')
                or s.huella_clave != huella(u))

    @jwt.revoked_token_loader
    def rechazar(header, payload):
        return jsonify(success=False, error='La sesión terminó. Inicia sesión nuevamente.'), 401
