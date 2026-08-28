import logging
import requests
import re
import os
from datetime import datetime, date, timedelta

from flask import Flask, send_from_directory, request, jsonify
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

app = Flask(__name__, static_folder=None)
app.secret_key = os.getenv("SECRET_KEY", "clave_secreta_segura_bendito_buffet")
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024
app.config['WTF_CSRF_ENABLED'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads', 'perfiles')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173", "http://localhost:5174"]}})

init_db(app)

bcrypt = Bcrypt(app)
csrf = CSRFProtect(app)
jwt = JWTManager(app)
ma = Marshmallow(app)
logging.basicConfig(level=logging.INFO)

from models import (
    Usuario, Rol, DocumentoIdentidad, UsuarioPerfil, PagoEmpleado, PagoPersonal,
    Adelanto, ActividadUsuario, IntentoLogin, TransaccionCaja,
    CierreCaja, Producto, Inversion, Categoria, Proveedor
)

from api.auth import auth_bp
from api.admin import admin_bp
from api.caja import caja_bp
from api.personal import personal_bp
from api.inventario import inventario_bp
from api.perfil import perfil_bp
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(caja_bp, url_prefix='/api/caja')
app.register_blueprint(personal_bp, url_prefix='/api/personal')
app.register_blueprint(inventario_bp, url_prefix='/api/inventario')
app.register_blueprint(perfil_bp)

csrf.exempt(auth_bp)
csrf.exempt(admin_bp)
csrf.exempt(caja_bp)
csrf.exempt(personal_bp)
csrf.exempt(inventario_bp)
csrf.exempt(perfil_bp)

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
@app.route("/api/dni/<dni>")
def api_consultar_dni(dni):
    if not re.match(r'^\d{8}$', dni):
        return jsonify({"error": "DNI invalido"}), 400
    token = os.getenv("DNI_API_TOKEN", "").strip()
    if not token:
        return jsonify({"error": "Token de DNI no configurado"}), 500
    try:
        respuesta = requests.get(
            f"https://dniruc.apisperu.com/api/v1/dni/{dni}",
            params={"token": token},
            timeout=10,
        )
        return jsonify(respuesta.json()), respuesta.status_code
    except requests.RequestException:
        return jsonify({"error": "Error de conexion con la API de RENIEC"}), 502

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
    if path and os.path.exists(os.path.join(FRONTEND_DIST, path)):
        return send_from_directory(FRONTEND_DIST, path)
    return send_from_directory(FRONTEND_DIST, 'index.html')

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
