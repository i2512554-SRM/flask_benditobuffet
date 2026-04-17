# Importamos la clase Flask desde el paquete flask
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
from functools import wraps
from bd import db, Usuario, Rol

# Creamos una instancia de la aplicación Flask
app = Flask(__name__)
app.secret_key = "clave_secreta_segura_bendito_buffet"
# Configuración de SQLAlchemy para conectar con MySQL usando mysqlconnector
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/bendito_buffet'
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
        correo = request.form["correo"]
        clave = request.form["clave"]

        usuario = Usuario.query.filter_by(correo=correo).first()

        if usuario and verify_password(usuario.clave, clave):
            if not is_hashed_password(usuario.clave):
                usuario.clave = bcrypt.generate_password_hash(clave).decode('utf-8')
                db.session.commit()

            session.clear()
            session["usuario_id"] = usuario.id_usuario
            session["rol"] = usuario.rol.nombre.lower() if usuario.rol else ""
            session["nombre"] = usuario.nombres
            return redirect(url_for("panel"))
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