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
from flask_login import login_required
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

LOCK_THRESHOLDS = {
    "usuario": 3,
    "ip": 5,
}
LOCK_DURATION_USER = timedelta(minutes=10)
LOCK_DURATION_IP_TEMP = timedelta(hours=24)
PERMANENT_IP_LOCK = timedelta(days=365 * 100)
DUMMY_HASH = bcrypt.generate_password_hash("dummy_password").decode("utf-8")


def current_time():
    return datetime.now()


def get_client_ip():
    return request.remote_addr or "0.0.0.0"


def normalize_expired_block(bloqueo):
    if bloqueo and bloqueo.bloqueado_hasta and bloqueo.bloqueado_hasta <= current_time():
        if bloqueo.tipo == "ip" and bloqueo.intentos >= get_lock_threshold("ip"):
            bloqueo.bloqueado_hasta = None
        else:
            bloqueo.intentos = 0
            bloqueo.bloqueado_hasta = None
    return bloqueo


def get_login_block(tipo, usuario=None, ip=None):
    query = BloqueoLogin.query.filter_by(tipo=tipo)
    if usuario is not None:
        query = query.filter_by(usuario=usuario)
    else:
        query = query.filter(BloqueoLogin.usuario.is_(None))
    if ip is not None:
        query = query.filter_by(ip=ip)
    else:
        query = query.filter(BloqueoLogin.ip.is_(None))
    bloqueo = query.first()
    return normalize_expired_block(bloqueo)


def get_or_create_login_block(tipo, usuario=None, ip=None):
    bloqueo = get_login_block(tipo, usuario=usuario, ip=ip)
    if bloqueo is None:
        bloqueo = BloqueoLogin(tipo=tipo, usuario=usuario, ip=ip, intentos=0)
        db.session.add(bloqueo)
    return bloqueo


def is_blocked(bloqueo):
    return bloqueo and bloqueo.bloqueado_hasta and bloqueo.bloqueado_hasta > current_time()


def get_lock_threshold(tipo):
    return LOCK_THRESHOLDS.get(tipo, 5)


def is_permanent_ip_block(bloqueo):
    if bloqueo is None or bloqueo.tipo != "ip" or bloqueo.bloqueado_hasta is None:
        return False
    return bloqueo.bloqueado_hasta - current_time() >= timedelta(days=365 * 10)


def get_remaining_block_seconds(bloqueo):
    if bloqueo is None or bloqueo.bloqueado_hasta is None:
        return 0
    remaining = bloqueo.bloqueado_hasta - current_time()
    return max(int(remaining.total_seconds()), 0)


def format_remaining_time(seconds):
    minutes, secs = divmod(seconds, 60)
    return f"{minutes}m {secs:02d}s" if minutes else f"{secs}s"


def render_temporal_block_message(label, seconds):
    formatted = format_remaining_time(seconds)
    return Markup(
        f"{label} bloqueado temporalmente. Vuelve a intentarlo en "
        f'<span class="blocked-countdown" data-seconds="{seconds}">{formatted}</span>.'
    )


def render_permanent_ip_message():
    return "IP baneada permanentemente. Contacta al administrador."


def get_block_message(bloqueo):
    if bloqueo.tipo == "usuario":
        return render_temporal_block_message("Usuario", get_remaining_block_seconds(bloqueo))
    if bloqueo.tipo == "ip":
        if is_permanent_ip_block(bloqueo):
            return render_permanent_ip_message()
        return render_temporal_block_message("IP", get_remaining_block_seconds(bloqueo))
    return "Acceso bloqueado temporalmente. Intente más tarde."


def reset_block(bloqueo):
    if bloqueo:
        bloqueo.intentos = 0
        bloqueo.bloqueado_hasta = None


def increment_failure(bloqueo):
    if bloqueo is None:
        return
    bloqueo.intentos = (bloqueo.intentos or 0) + 1
    threshold = get_lock_threshold(bloqueo.tipo)
    if bloqueo.bloqueado_hasta is None and bloqueo.intentos >= threshold:
        if bloqueo.tipo == "ip" and bloqueo.intentos > threshold:
            bloqueo.bloqueado_hasta = current_time() + PERMANENT_IP_LOCK
        elif bloqueo.tipo == "ip":
            bloqueo.bloqueado_hasta = current_time() + LOCK_DURATION_IP_TEMP
        else:
            bloqueo.bloqueado_hasta = current_time() + LOCK_DURATION_USER


def is_digits(value):
    return isinstance(value, str) and value.isdigit()


def validate_dni(dni):
    return is_digits(dni) and 1 <= len(dni) <= 8


def validate_telefono(telefono):
    return is_digits(telefono) and 1 <= len(telefono) <= 9

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

@app.route("/perfil/<int:id>")
@login_required
def perfil(id):
    empleado = Usuario.query.get_or_404(id)
    return render_template("perfil.html", empleado=empleado)

@app.route("/consulta_dni")
@login_required
def consulta_dni():
    return render_template("consulta_dni.html")

@app.route('/api/dni/<dni>')
@login_required
def consultar_dni(dni):
    import requests

    token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6ImkyNTEyNTU0QGNvbnRpbmVudGFsLmVkdS5wZSJ9.atmlR91JznkCYGLaL5wQg7BW1vYo6aMC5YIkHg40-Zo"  

    url = f"https://dniruc.apisperu.com/api/v1/dni/{dni}?token={token}"

    try:
        response = requests.get(url, timeout=5)
        data = response.json()

        # Validar respuesta
        if not data or data.get("success") is False:
            return {"error": "No se encontró el DNI"}

        nombres = data.get("nombres", "")
        apellidos = f"{data.get('apellidoPaterno', '')} {data.get('apellidoMaterno', '')}"

        return {
            "nombres": nombres,
            "apellidos": apellidos
        }

    except Exception as e:
        print("Error API:", e)
        return {"error": "Error consultando DNI"}
    
@app.route("/test-db")
def test_db():
    try:
        from bd import Usuario
        usuarios = Usuario.query.all()
        return f"✅ Conectado. Usuarios encontrados: {len(usuarios)}"
    except Exception as e:
        return f"💥 Error: {str(e)}"

@app.route("/panel")
@login_required
def panel_redirect():
    return redirect(url_for("panel"))

@app.route("/editar_perfil", methods=["GET", "POST"])
@login_required
def editar_perfil():
    empleado = Usuario.query.get_or_404(session["usuario_id"])
    if request.method == "POST":
        empleado.nombres = request.form.get("nombres", empleado.nombres).strip()
        empleado.apellido = request.form.get("apellido", empleado.apellido).strip()
        empleado.telefono = request.form.get("telefono", empleado.telefono).strip()
        try:
            db.session.commit()
            flash("Perfil actualizado correctamente", "success")
        except SQLAlchemyError:
            db.session.rollback()
            flash("Error al actualizar perfil", "error")
        return redirect(url_for("perfil", id=empleado.id_usuario))
    return redirect(url_for("perfil", id=empleado.id_usuario))

@app.route("/caja")
@login_required
def caja():
    flash("Módulo de Caja en desarrollo", "error")
    return redirect(url_for("panel"))

@app.route("/inventario")
@login_required
def inventario():
    flash("Módulo de Inventario en desarrollo", "error")
    return redirect(url_for("panel"))

@app.errorhandler(404)
def pagina_no_encontrada(e):
    return render_template("404.html"), 404

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
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() in ("1", "true", "yes"), host="0.0.0.0", port=5000)
