# Importamos la clase Flask desde el paquete flask
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_bcrypt import Bcrypt
from functools import wraps
from datetime import datetime, date
import re
from bd import db, init_db
from models import Usuario, Rol, TransaccionCaja, CierreCaja, Producto, Inversion

# Creamos una instancia de la aplicación Flask
app = Flask(__name__)
app.secret_key = "clave_secreta_segura_bendito_buffet"

# Inicializamos SQLAlchemy con la aplicación Flask
init_db(app)
with app.app_context():
    db.create_all()
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
# GESTIÓN DE CAJA
# -------------------------------

def _calcular_resumen_caja():
    hoy = date.today()
    ventas = db.session.query(db.func.coalesce(db.func.sum(TransaccionCaja.monto), 0))
    ventas = ventas.filter(TransaccionCaja.tipo == "Venta", db.func.date(TransaccionCaja.fecha) == hoy).scalar() or 0
    gastos = db.session.query(db.func.coalesce(db.func.sum(TransaccionCaja.monto), 0))
    gastos = gastos.filter(TransaccionCaja.tipo == "Gasto", db.func.date(TransaccionCaja.fecha) == hoy).scalar() or 0
    neto = float(ventas) - float(gastos)
    return float(ventas), float(gastos), float(neto)


def _validar_categoria(categoria):
    return bool(re.match(r'^[A-Za-záéíóúÁÉÍÓÚñÑ ]+$', categoria.strip()))


@app.route("/caja")
@login_required
@role_required("administrador", "cajera", "cajero")
def caja():
    ventas_dia, gastos_dia, neto_dia = _calcular_resumen_caja()
    transacciones = TransaccionCaja.query.order_by(TransaccionCaja.fecha.desc()).all()
    cierres = CierreCaja.query.order_by(CierreCaja.fecha.desc()).all()
    return render_template(
        "caja.html",
        ventas_dia=ventas_dia,
        gastos_dia=gastos_dia,
        neto_dia=neto_dia,
        transacciones=transacciones,
        cierres=cierres
    )


@app.route("/caja/registrar", methods=["POST"])
@login_required
@role_required("administrador", "cajera", "cajero")
def caja_registrar():
    tipo = request.form.get("tipo", "").strip()
    monto_text = request.form.get("monto", "").strip().replace(',', '.')
    metodo_pago = request.form.get("metodo_pago", "").strip()
    categoria = request.form.get("categoria", "").strip()
    descripcion = request.form.get("descripcion", "").strip()

    errores = []
    if tipo not in ["Venta", "Gasto"]:
        errores.append("El tipo de transacción es inválido.")
    try:
        monto = float(monto_text)
        if monto <= 0:
            errores.append("El monto debe ser un número positivo.")
    except ValueError:
        errores.append("El monto debe ser un valor numérico válido.")
    if metodo_pago not in ["Efectivo", "Tarjeta", "Transferencia"]:
        errores.append("El método de pago es inválido.")
    if not categoria or not _validar_categoria(categoria):
        errores.append("La categoría es obligatoria y no puede contener números.")

    if errores:
        mensaje = errores[0]
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"success": False, "message": mensaje}), 400
        flash(mensaje, "error")
        return redirect(url_for("caja"))

    nueva_transaccion = TransaccionCaja(
        id_usuario=session.get("usuario_id"),
        tipo=tipo,
        monto=monto,
        metodo_pago=metodo_pago,
        categoria=categoria,
        descripcion=descripcion,
        fecha=datetime.now()
    )
    db.session.add(nueva_transaccion)
    db.session.commit()

    ventas_dia, gastos_dia, neto_dia = _calcular_resumen_caja()
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({
            "success": True,
            "message": "Transacción registrada correctamente.",
            "ventas_dia": ventas_dia,
            "gastos_dia": gastos_dia,
            "neto_dia": neto_dia
        })

    flash("Transacción registrada correctamente", "success")
    return redirect(url_for("caja"))


@app.route("/caja/cerrar", methods=["POST"])
@login_required
@role_required("administrador", "cajera", "cajero")
def caja_cerrar():
    observaciones = request.form.get("observaciones", "").strip()
    if not observaciones:
        observaciones = "Sin anotaciones"

    ventas_dia, gastos_dia, neto_dia = _calcular_resumen_caja()

    cierre = CierreCaja(
        id_usuario=session.get("usuario_id"),
        total_ventas=ventas_dia,
        total_gastos=gastos_dia,
        neto=neto_dia,
        observaciones=observaciones,
        fecha=datetime.now()
    )
    db.session.add(cierre)
    db.session.commit()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"success": True, "message": "Caja cerrada correctamente."})

    flash("Caja cerrada correctamente", "success")
    return redirect(url_for("caja"))

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
        nombres = request.form["nombres"]
        apellido = request.form.get("apellido", "")
        dni = request.form["dni"]
        correo = request.form["correo"]
        telefono = request.form.get("telefono", "")
        rol_id = int(request.form["rol_id"])
        clave = request.form["clave"]

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

    return render_template("empleados_form.html", roles=roles)

@app.route("/empleados/editar/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def editar_empleado(id):
    empleado = Usuario.query.get_or_404(id)
    roles = Rol.query.all()

    if request.method == "POST":
        empleado.nombres = request.form["nombres"]
        empleado.apellido = request.form.get("apellido", "")
        empleado.dni = request.form["dni"]
        empleado.correo = request.form["correo"]
        empleado.telefono = request.form.get("telefono", "")
        empleado.id_rol = int(request.form["rol_id"])
        empleado.usuario = request.form.get("usuario", empleado.correo)

        clave_nueva = request.form.get("clave")
        if clave_nueva:
            empleado.clave = bcrypt.generate_password_hash(clave_nueva).decode('utf-8')

        db.session.commit()
        flash("Empleado actualizado", "success")
        return redirect(url_for("empleados"))

    return render_template("empleados_form.html", empleado=empleado, roles=roles)

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
# INVENTARIO E INVERSIÓN
# -------------------------------

def _calcular_resumen_inventario():
    total_inventario = db.session.query(
        db.func.coalesce(db.func.sum(Producto.precio * Producto.stock), 0)
    ).scalar() or 0
    total_equipamiento = db.session.query(
        db.func.coalesce(db.func.sum(Producto.precio * Producto.stock), 0)
    ).filter(
        db.func.lower(Producto.categoria).like('%equipamiento%')
    ).scalar() or 0
    return float(total_inventario), float(total_equipamiento)


def _inversiones_del_mes():
    hoy = date.today()
    primer_dia = date(hoy.year, hoy.month, 1)
    return db.session.query(
        db.func.coalesce(db.func.sum(Inversion.monto), 0)
    ).filter(
        db.func.date(Inversion.fecha) >= primer_dia,
        db.func.date(Inversion.fecha) <= hoy
    ).scalar() or 0


def _productos_registrados_mes():
    hoy = date.today()
    primer_dia = date(hoy.year, hoy.month, 1)
    return Producto.query.filter(
        db.func.date(Producto.fecha_registro) >= primer_dia,
        db.func.date(Producto.fecha_registro) <= hoy
    ).count()


@app.route("/inventario")
@login_required
@admin_required
def inventario():
    valor_total_inventario, equipamiento_valor = _calcular_resumen_inventario()
    inversiones_mes = _inversiones_del_mes()
    articulos_registrados = Producto.query.count()
    productos_mes = _productos_registrados_mes()
    productos = Producto.query.order_by(Producto.fecha_registro.desc()).all()
    inversiones = Inversion.query.order_by(Inversion.fecha.desc()).all()
    return render_template(
        "inventario.html",
        valor_total_inventario=valor_total_inventario,
        inversiones_mes=inversiones_mes,
        articulos_registrados=articulos_registrados,
        productos_mes=productos_mes,
        equipamiento_valor=equipamiento_valor,
        productos=productos,
        inversiones=inversiones
    )


@app.route("/inventario/articulo/nuevo", methods=["POST"])
@login_required
@admin_required
def inventario_articulo_nuevo():
    nombre = request.form.get("nombre", "").strip()
    categoria = request.form.get("categoria", "").strip()
    precio_text = request.form.get("precio", "").strip().replace(',', '.')
    stock_text = request.form.get("stock", "").strip().replace(',', '.')

    errores = []
    if not nombre:
        errores.append("El nombre del artículo es obligatorio.")
    if not categoria:
        errores.append("La categoría es obligatoria.")
    try:
        precio = float(precio_text)
        if precio < 0:
            errores.append("El precio debe ser un número válido.")
    except ValueError:
        errores.append("El precio debe ser un número válido.")
    try:
        stock = float(stock_text)
        if stock < 0:
            errores.append("El stock debe ser un número válido.")
    except ValueError:
        errores.append("El stock debe ser un número válido.")

    if errores:
        flash(errores[0], "error")
        return redirect(url_for("inventario"))

    producto = Producto(
        nombre=nombre,
        categoria=categoria,
        precio=precio,
        stock=stock,
        fecha_registro=datetime.now()
    )
    db.session.add(producto)
    db.session.commit()
    flash("Artículo agregado al inventario", "success")
    return redirect(url_for("inventario"))


@app.route("/inventario/compra/nuevo", methods=["POST"])
@login_required
@admin_required
def inventario_compra_nuevo():
    descripcion = request.form.get("descripcion", "").strip()
    proveedor = request.form.get("proveedor", "").strip()
    notas = request.form.get("notas", "").strip()
    monto_text = request.form.get("monto", "").strip().replace(',', '.')

    errores = []
    if not descripcion:
        errores.append("La descripción de la inversión es obligatoria.")
    if not proveedor:
        errores.append("El proveedor es obligatorio.")
    try:
        monto = float(monto_text)
        if monto <= 0:
            errores.append("El monto debe ser mayor a cero.")
    except ValueError:
        errores.append("El monto debe ser un valor numérico válido.")

    if errores:
        flash(errores[0], "error")
        return redirect(url_for("inventario"))

    inversion = Inversion(
        descripcion=descripcion,
        proveedor=proveedor,
        notas=notas,
        monto=monto,
        fecha=datetime.now()
    )
    db.session.add(inversion)
    db.session.commit()
    flash("Inversión registrada correctamente", "success")
    return redirect(url_for("inventario"))


@app.route("/inventario/compra/<int:id>")
@login_required
@admin_required
def inventario_compra_detalle(id):
    inversion = Inversion.query.get_or_404(id)
    return render_template("inventario_compra_detalle.html", inversion=inversion)


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