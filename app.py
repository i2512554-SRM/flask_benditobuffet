import logging
import secrets
import os
from datetime import timedelta

from flask import Flask, send_from_directory, request, jsonify, abort
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path)
load_dotenv()

from bd import db, init_db


def _resolver_secret_key():
    debug = os.getenv("FLASK_DEBUG", "false").lower() in ("1", "true", "yes")
    entorno = (os.getenv("APP_ENV") or os.getenv("FLASK_ENV") or "").strip().lower()
    secret = os.getenv("SECRET_KEY", "").strip()
    if secret:
        return secret
    entorno_no_productivo = entorno in ("development", "dev", "testing", "test")
    if not (entorno_no_productivo or (not entorno and debug)):
        raise RuntimeError(
            "SECRET_KEY es obligatoria fuera de los entornos de desarrollo y pruebas."
        )
    logging.getLogger(__name__).warning(
        "SECRET_KEY no definida: se generó una clave temporal para desarrollo o pruebas."
    )
    return secrets.token_hex(32)


app = Flask(__name__, static_folder=None)
_debug_activo = os.getenv("FLASK_DEBUG", "false").lower() in ("1", "true", "yes")
_secret_key = _resolver_secret_key()
app.secret_key = _secret_key
app.config['SECRET_KEY'] = _secret_key
app.config['JWT_SECRET_KEY'] = _secret_key
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=30)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024
app.config['WTF_CSRF_ENABLED'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['TRUSTED_PROXY_IPS'] = tuple(
    valor.strip()
    for valor in os.getenv('TRUSTED_PROXY_IPS', '').split(',')
    if valor.strip()
)
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads', 'perfiles')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173", "http://localhost:5174", "http://localhost:5000", "http://127.0.0.1:5000"]}})

init_db(app)

bcrypt = Bcrypt(app)
csrf = CSRFProtect(app)
jwt = JWTManager(app)
from api.sesiones import configurar_sesiones
configurar_sesiones(jwt)
from api.errores_bd import configurar_errores_bd
configurar_errores_bd(app)
ma = Marshmallow(app)
logging.basicConfig(level=logging.INFO)

from models import (
    Usuario, Rol, DocumentoIdentidad, UsuarioPerfil, PagoEmpleado, PagoPersonal,
    Adelanto, ActividadUsuario, IntentoLogin, TransaccionCaja,
    CierreCaja, Producto, Inversion, Categoria, Proveedor,
    CompraInventario, DetalleCompraInventario, InventarioMovimiento, BloqueoLogin
)

from api.auth import auth_bp
from api.admin import admin_bp
from api.caja import caja_bp
from api.personal import personal_bp
from api.inventario import inventario_bp
from api.perfil import perfil_bp
from api.cocina import cocina_bp
from api.trabajador import trabajador_bp
from api.rendimiento import rendimiento_bp
from api.indicadores import indicadores_bp
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(caja_bp, url_prefix='/api/caja')
app.register_blueprint(personal_bp, url_prefix='/api/personal')
app.register_blueprint(inventario_bp, url_prefix='/api/inventario')
app.register_blueprint(perfil_bp)
app.register_blueprint(cocina_bp)
app.register_blueprint(trabajador_bp)
app.register_blueprint(rendimiento_bp, url_prefix='/api')
app.register_blueprint(indicadores_bp, url_prefix='/api')

csrf.exempt(auth_bp)
csrf.exempt(admin_bp)
csrf.exempt(caja_bp)
csrf.exempt(personal_bp)
csrf.exempt(inventario_bp)
csrf.exempt(perfil_bp)
csrf.exempt(cocina_bp)
csrf.exempt(trabajador_bp)
csrf.exempt(rendimiento_bp)
csrf.exempt(indicadores_bp)

# -------------------------------
# ERROR HANDLERS (API)
# -------------------------------
@app.errorhandler(400)
def bad_request(error):
    return jsonify({'success': False, 'error': 'Solicitud invalida'}), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'success': False, 'error': 'No autorizado'}), 401

@app.errorhandler(403)
def forbidden(error):
    return jsonify({'success': False, 'error': 'Acceso denegado'}), 403

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Recurso no encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500

# -------------------------------
# API: DNI LOOKUP
# -------------------------------
from api.dni import consultar_dni
app.add_url_rule('/api/dni/<dni>', view_func=consultar_dni)

# -------------------------------
# SERVIR VUE SPA
# -------------------------------
FRONTEND_DIST = os.path.join(os.path.dirname(__file__), 'frontend', 'dist')

@app.route('/uploads/perfiles/<path:filename>')
def uploads_perfiles(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_vue(path):
    if path == 'api' or path.startswith('api/'):
        abort(404)
    if path and os.path.exists(os.path.join(FRONTEND_DIST, path)):
        return send_from_directory(FRONTEND_DIST, path)
    return send_from_directory(FRONTEND_DIST, 'index.html')

@app.after_request
def add_header(response):
    if request.path.startswith('/assets/') and response.status_code == 200:
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        return response
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

if __name__ == "__main__":
    host = os.getenv("FLASK_HOST", "").strip() or ("127.0.0.1" if _debug_activo else "0.0.0.0")
    app.run(debug=_debug_activo, host=host, port=5000)
