# Importamos la clase Flask desde el paquete flask
import os
from datetime import datetime, timedelta, timezone

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
from functools import wraps
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.middleware.proxy_fix import ProxyFix
from bd import db, Usuario, Rol, BloqueoLogin

# Creamos una instancia de la aplicación Flask
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "clave_secreta_segura_bendito_buffet")
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)

# Configuración de SQLAlchemy para conectar con MySQL usando mysqlconnector
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://bendito_sebas:sebas1819+@mysql-bendito.alwaysdata.net/bendito_buffet?charset=utf8mb4'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Inicializamos SQLAlchemy con la aplicación Flask
db.init_app(app)
bcrypt = Bcrypt(app)

# Helpers de contraseña

def is_hashed_password(password):
    return isinstance(password, str) and (password.startswith("$2a$") or password.startswith("$2b$") or password.startswith("$2y$"))


def verify_password(stored_password, provided_password):
    if not stored_password:
        return False
    if is_hashed_password(stored_password):
        return bcrypt.check_password_hash(stored_password, provided_password)
    return stored_password == provided_password

LOCK_THRESHOLDS = {
    "usuario": 5,
    "ip": 10,
}
LOCK_DURATION = timedelta(minutes=3)
DUMMY_HASH = bcrypt.generate_password_hash("dummy_password").decode("utf-8")


def current_time():
    return datetime.now()


def get_client_ip():
    return request.remote_addr or "0.0.0.0"


def normalize_expired_block(bloqueo):
    if bloqueo and bloqueo.bloqueado_hasta and bloqueo.bloqueado_hasta <= current_time():
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


def reset_block(bloqueo):
    if bloqueo:
        bloqueo.intentos = 0
        bloqueo.bloqueado_hasta = None


def increment_failure(bloqueo):
    if bloqueo is None:
        return
    bloqueo.intentos = (bloqueo.intentos or 0) + 1
    if bloqueo.intentos >= get_lock_threshold(bloqueo.tipo):
        bloqueo.bloqueado_hasta = current_time() + LOCK_DURATION


def is_digits(value):
    return isinstance(value, str) and value.isdigit()


def validate_dni(dni):
    return is_digits(dni) and 1 <= len(dni) <= 8


def validate_telefono(telefono):
    return is_digits(telefono) and 1 <= len(telefono) <= 9

# -------------------------------
# DECORADOR: LOGIN REQUERIDO
# -------------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# -------------------------------
# DECORADOR: ROLES PERMITIDOS
# -------------------------------
def role_required(*roles):
    allowed_roles = [r.lower() for r in roles]
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_role = str(session.get("rol", "")).lower()
            if user_role not in allowed_roles:
                flash("Acceso denegado", "error")
                return redirect(url_for("panel"))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Decorador para administradores
def admin_required(f):
    return role_required("administrador")(f)

# -------------------------------
# RUTAS
# -------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form["correo"].strip()
        clave = request.form["clave"]
        client_ip = get_client_ip()

        usuario = Usuario.query.filter_by(correo=correo).first()
        ip_block = get_login_block("ip", ip=client_ip)
        user_block = get_login_block("usuario", usuario=correo) if usuario else None

        if is_blocked(ip_block) or is_blocked(user_block):
            flash("Acceso bloqueado temporalmente. Intente más tarde.", "error")
            return render_template("login.html")

        if usuario:
            password_ok = verify_password(usuario.clave, clave)
        else:
            password_ok = bcrypt.check_password_hash(DUMMY_HASH, clave)

        if usuario and password_ok:
            if not is_hashed_password(usuario.clave):
                usuario.clave = bcrypt.generate_password_hash(clave).decode('utf-8')

            reset_block(ip_block)
            reset_block(user_block)

            session.clear()
            session["usuario_id"] = usuario.id_usuario
            session["rol"] = usuario.rol.nombre.lower() if usuario.rol else ""
            session["nombre"] = usuario.nombres

            try:
                db.session.commit()
            except SQLAlchemyError:
                db.session.rollback()
                flash("Error interno. Intente de nuevo más tarde.", "error")
                return render_template("login.html")

            return redirect(url_for("panel"))

        ip_block = get_or_create_login_block("ip", ip=client_ip)
        if usuario:
            user_block = get_or_create_login_block("usuario", usuario=correo)

        increment_failure(ip_block)
        increment_failure(user_block)

        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            flash("Error interno. Intente de nuevo más tarde.", "error")
            return render_template("login.html")

        flash("Credenciales incorrectas", "error")
    else:
        session.clear()

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
@login_required
def panel():
    rol = session.get("rol", "").lower()
    if rol == "administrador":
        return render_template("panel_admin.html")
    elif rol in ("cajera", "cajero"):
        return render_template("panel_cajero.html")
    else:
        flash("Rol no reconocido", "error")
        return redirect(url_for("login"))

# -------------------------------
# EMPLEADOS (solo admin)
# -------------------------------

@app.route("/empleados")
@login_required
@admin_required
def empleados():
    empleados_list = Usuario.query.all()
    roles = Rol.query.all()
    return render_template("empleados.html", empleados=empleados_list, roles=roles)

@app.route("/empleados/estado/<int:id>")
@login_required
@admin_required
def toggle_estado_empleado(id):
    empleado = Usuario.query.get_or_404(id)
    empleado.estado = 0 if empleado.estado == 1 else 1
    db.session.commit()
    flash(f"Empleado {'activado' if empleado.estado == 1 else 'desactivado'}", "success")
    return redirect(url_for("empleados"))

@app.route("/empleados/nuevo", methods=["GET", "POST"])
@login_required
@admin_required
def nuevo_empleado():
    roles = Rol.query.all()

    if request.method == "POST":
        nombres = request.form["nombres"].strip()
        apellido = request.form.get("apellido", "").strip()
        dni = request.form["dni"].strip()
        correo = request.form["correo"].strip()
        telefono = request.form.get("telefono", "").strip()
        try:
            rol_id = int(request.form["rol_id"])
        except (ValueError, TypeError):
            rol_id = None
        clave = request.form["clave"]

        if not nombres or not dni or not correo or not telefono or not rol_id or not clave:
            flash("Todos los campos obligatorios deben completarse", "error")
            return render_template("empleados_from.html", roles=roles)

        if not validate_dni(dni):
            flash("DNI debe contener solo números y hasta 8 dígitos", "error")
            return render_template("empleados_from.html", roles=roles)

        if not validate_telefono(telefono):
            flash("Teléfono debe contener solo números y hasta 9 dígitos", "error")
            return render_template("empleados_from.html", roles=roles)

        usuario_login = correo
        hashed_clave = bcrypt.generate_password_hash(clave).decode('utf-8')

        nuevo_usuario = Usuario(
            nombres=nombres,
            apellido=apellido,
            dni=dni,
            correo=correo,
            telefono=telefono,
            usuario=usuario_login,
            clave=hashed_clave,
            id_rol=rol_id,
            estado=1
        )
        db.session.add(nuevo_usuario)
        db.session.commit()

        flash("Empleado registrado exitosamente", "success")
        return redirect(url_for("empleados"))

    return render_template("empleados_from.html", roles=roles)

@app.route("/empleados/editar/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def editar_empleado(id):
    empleado = Usuario.query.get_or_404(id)
    roles = Rol.query.all()

    if request.method == "POST":
        nombres = request.form["nombres"].strip()
        apellido = request.form.get("apellido", "").strip()
        dni = request.form["dni"].strip()
        correo = request.form["correo"].strip()
        telefono = request.form.get("telefono", "").strip()
        try:
            rol_id = int(request.form["rol_id"])
        except (ValueError, TypeError):
            rol_id = None
        clave_nueva = request.form.get("clave")

        if not nombres or not dni or not correo or not telefono or not rol_id:
            flash("Todos los campos obligatorios deben completarse", "error")
            return render_template("empleados_from.html", empleado=empleado, roles=roles)

        if not validate_dni(dni):
            flash("DNI debe contener solo números y hasta 8 dígitos", "error")
            return render_template("empleados_from.html", empleado=empleado, roles=roles)

        if not validate_telefono(telefono):
            flash("Teléfono debe contener solo números y hasta 9 dígitos", "error")
            return render_template("empleados_from.html", empleado=empleado, roles=roles)

        empleado.nombres = nombres
        empleado.apellido = apellido
        empleado.dni = dni
        empleado.correo = correo
        empleado.telefono = telefono
        empleado.id_rol = rol_id
        empleado.usuario = request.form.get("usuario", empleado.correo)

        if clave_nueva:
            empleado.clave = bcrypt.generate_password_hash(clave_nueva).decode('utf-8')

        db.session.commit()
        flash("Empleado actualizado", "success")
        return redirect(url_for("empleados"))

    return render_template("empleados_from.html", empleado=empleado, roles=roles)

@app.route("/empleados/eliminar/<int:id>")
@login_required
@admin_required
def eliminar_empleado(id):
    empleado = Usuario.query.get_or_404(id)
    db.session.delete(empleado)
    db.session.commit()
    flash("Empleado eliminado", "success")
    return redirect(url_for("empleados"))

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
# -------------------------------
# INICIALIZACIÓN
# -------------------------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        if not Rol.query.filter_by(nombre="Administrador").first():
            roles = [
                Rol(nombre="Administrador"),
                Rol(nombre="Cajera"),
                Rol(nombre="Cocinero"),
                Rol(nombre="Trabajador")
            ]
            db.session.bulk_save_objects(roles)
            db.session.commit()

        if not Usuario.query.filter_by(correo="admin@bendito.com").first():
            hashed = bcrypt.generate_password_hash("admin123").decode('utf-8')
            admin_role = Rol.query.filter_by(nombre="Administrador").first()
            admin = Usuario(
                nombres="Administrador",
                apellido="",
                dni="",
                correo="admin@bendito.com",
                telefono="",
                usuario="admin@bendito.com",
                clave=hashed,
                id_rol=admin_role.id_rol if admin_role else 1,
                estado=1
            )
            db.session.add(admin)
            db.session.commit()
    app.run(debug=True)

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response