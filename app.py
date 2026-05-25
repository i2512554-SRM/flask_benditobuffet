# Importamos la clase Flask desde el paquete flask
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_bcrypt import Bcrypt
from functools import wraps
from datetime import datetime, date
import re
import os
import uuid
from calendar import monthrange
from werkzeug.utils import secure_filename
from bd import db, init_db
from models import (
    Usuario,
    Rol,
    UsuarioPerfil,
    PagoEmpleado,
    PagoPersonal,
    Adelanto,
    ActividadUsuario,
    TransaccionCaja,
    CierreCaja,
    Producto,
    Inversion,
)

# Creamos una instancia de la aplicación Flask
app = Flask(__name__)
app.secret_key = "clave_secreta_segura_bendito_buffet"
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads', 'perfiles')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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
    ventas_mes, egresos_mes, neto_mes = _calcular_resumen_mensual_cierres()
    if rol == "administrador":
        return render_template(
            "panel_admin.html",
            ventas_mes=ventas_mes,
            egresos_mes=egresos_mes,
            neto_mes=neto_mes,
        )
    elif rol in ("cajera", "cajero"):
        return render_template(
            "panel_cajero.html",
            ventas_mes=ventas_mes,
            egresos_mes=egresos_mes,
            neto_mes=neto_mes,
        )
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


def _calcular_resumen_mensual_cierres():
    hoy = date.today()
    primer_dia = date(hoy.year, hoy.month, 1)
    ventas_mes = db.session.query(db.func.coalesce(db.func.sum(CierreCaja.total_ventas), 0))
    ventas_mes = ventas_mes.filter(db.func.date(CierreCaja.fecha) >= primer_dia, db.func.date(CierreCaja.fecha) <= hoy).scalar() or 0
    egresos_mes = db.session.query(db.func.coalesce(db.func.sum(CierreCaja.total_gastos), 0))
    egresos_mes = egresos_mes.filter(db.func.date(CierreCaja.fecha) >= primer_dia, db.func.date(CierreCaja.fecha) <= hoy).scalar() or 0
    neto_mes = float(ventas_mes) - float(egresos_mes)
    return float(ventas_mes), float(egresos_mes), float(neto_mes)


def _validar_categoria(categoria):
    return bool(re.match(r'^[A-Za-záéíóúÁÉÍÓÚñÑ ]+$', categoria.strip()))


ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}

def _allowed_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


def _secure_profile_filename(usuario_id, filename):
    extension = filename.rsplit('.', 1)[1].lower()
    return secure_filename(f"perfil_{usuario_id}_{uuid.uuid4().hex}.{extension}")


def _log_actividad(usuario_id, accion):
    try:
        actividad = ActividadUsuario(id_usuario=usuario_id, accion=accion, fecha=datetime.now())
        db.session.add(actividad)
        db.session.commit()
    except Exception:
        db.session.rollback()


def _mes_actual():
    hoy = date.today()
    return date(hoy.year, hoy.month, 1), hoy


def _parse_filtro_mes():
    year = request.args.get('year', type=int)
    month = request.args.get('month')
    if month:
        try:
            if isinstance(month, str) and '-' in month:
                year_part, month_part = month.split('-', 1)
                year = int(year_part)
                month = int(month_part)
            else:
                month = int(month)
            if year and month:
                ultimo_dia = monthrange(year, month)[1]
                return date(year, month, 1), date(year, month, ultimo_dia)
        except (ValueError, TypeError):
            pass
    return _mes_actual()


def _obtener_totales_pagos(start_date, end_date, id_usuario=None):
    pagos_query = db.session.query(db.func.coalesce(db.func.sum(PagoEmpleado.monto), 0))
    pagos_query = pagos_query.filter(PagoEmpleado.estado == 'Pagado')
    pagos_query = pagos_query.filter(db.func.date(PagoEmpleado.fecha_pago) >= start_date, db.func.date(PagoEmpleado.fecha_pago) <= end_date)
    if id_usuario:
        pagos_query = pagos_query.filter(PagoEmpleado.id_usuario == id_usuario)
    total_pagos = pagos_query.scalar() or 0

    adelantos_query = db.session.query(db.func.coalesce(db.func.sum(Adelanto.monto), 0))
    adelantos_query = adelantos_query.filter(db.func.date(Adelanto.fecha) >= start_date, db.func.date(Adelanto.fecha) <= end_date)
    adelantos_query = adelantos_query.filter(Adelanto.estado != 'Cancelado')
    if id_usuario:
        adelantos_query = adelantos_query.filter(Adelanto.id_usuario == id_usuario)
    total_adelantos = adelantos_query.scalar() or 0

    return float(total_pagos), float(total_adelantos), float(total_pagos) - float(total_adelantos)


def _obtener_proximo_pago():
    pago_pendiente = PagoEmpleado.query.filter(PagoEmpleado.estado == 'Pendiente', db.func.date(PagoEmpleado.fecha_pago) >= date.today()).order_by(PagoEmpleado.fecha_pago.asc()).first()
    if pago_pendiente:
        delta = (pago_pendiente.fecha_pago.date() - date.today()).days
        return delta if delta >= 0 else 0
    return None


@app.route('/pagos-personal')
@login_required
@admin_required
def pagos_personal():
    inicio, fin = _parse_filtro_mes()
    total_pagado_mes, total_adelantos_mes, neto_mes = _obtener_totales_pagos(inicio, fin)
    empleados_activos = Usuario.query.filter_by(estado=1).count()
    proximo_pago_dias = _obtener_proximo_pago()

    empleados = Usuario.query.filter_by(estado=1).order_by(Usuario.nombres.asc()).all()
    resumen_empleados = []
    for empleado in empleados:
        pagos, adelantos, neto = _obtener_totales_pagos(inicio, fin, empleado.id_usuario)
        resumen_empleados.append({
            'empleado': empleado,
            'total_pagado': pagos,
            'total_adelantos': adelantos,
            'neto': neto,
        })

    pagos_historial = PagoEmpleado.query.filter(PagoEmpleado.estado == 'Pagado', db.func.date(PagoEmpleado.fecha_pago) >= inicio, db.func.date(PagoEmpleado.fecha_pago) <= fin).order_by(PagoEmpleado.fecha_pago.desc()).all()
    return render_template(
        'pagos_personal.html',
        inicio=inicio,
        fin=fin,
        total_pagado_mes=total_pagado_mes,
        total_adelantos_mes=total_adelantos_mes,
        neto_mes=neto_mes,
        empleados_activos=empleados_activos,
        proximo_pago_dias=proximo_pago_dias,
        resumen_empleados=resumen_empleados,
        pagos_historial=pagos_historial,
    )


@app.route('/pagos-personal/empleado/<int:id_usuario>')
@login_required
@admin_required
def pagos_personal_detalle(id_usuario):
    empleado = Usuario.query.get_or_404(id_usuario)
    inicio, fin = _parse_filtro_mes()
    total_pagado, total_adelantos, neto = _obtener_totales_pagos(inicio, fin, empleado.id_usuario)
    pagos = PagoEmpleado.query.filter(PagoEmpleado.id_usuario == empleado.id_usuario).order_by(PagoEmpleado.fecha_pago.desc()).all()
    pagos_personal = PagoPersonal.query.filter(PagoPersonal.id_usuario == empleado.id_usuario).order_by(PagoPersonal.fecha.desc()).all()
    adelantos = Adelanto.query.filter(Adelanto.id_usuario == empleado.id_usuario).order_by(Adelanto.fecha.desc()).all()
    return render_template(
        'pagos_personal_detalle.html',
        empleado=empleado,
        inicio=inicio,
        fin=fin,
        total_pagado=total_pagado,
        total_adelantos=total_adelantos,
        neto=neto,
        pagos=pagos,
        pagos_personal=pagos_personal,
        adelantos=adelantos,
    )


@app.route('/pagos-personal/pago', methods=['POST'])
@login_required
@admin_required
def registrar_pago_personal():
    id_usuario = request.form.get('id_usuario', type=int)
    tipo = request.form.get('tipo', '').strip()
    monto_text = request.form.get('monto', '').strip().replace(',', '.')
    fecha_text = request.form.get('fecha', '').strip()
    estado = request.form.get('estado', 'Pendiente').strip()
    descripcion = request.form.get('descripcion', '').strip()

    if not id_usuario or not Usuario.query.get(id_usuario):
        flash('Empleado no válido.', 'error')
        return redirect(url_for('pagos_personal'))

    try:
        monto = float(monto_text)
        if monto <= 0:
            raise ValueError
    except ValueError:
        flash('El monto debe ser un número mayor que cero.', 'error')
        return redirect(url_for('pagos_personal'))

    try:
        pago_fecha = datetime.strptime(fecha_text, '%Y-%m-%d').date() if fecha_text else date.today()
    except ValueError:
        flash('Fecha de pago inválida.', 'error')
        return redirect(url_for('pagos_personal'))

    existe_pago = PagoEmpleado.query.filter(
        PagoEmpleado.id_usuario == id_usuario,
        db.func.date(PagoEmpleado.fecha_pago) == pago_fecha,
        PagoEmpleado.monto == monto,
        PagoEmpleado.estado == estado
    ).first()
    if existe_pago:
        flash('Ya existe un pago similar para esa fecha.', 'error')
        return redirect(url_for('pagos_personal'))

    pago_personal = PagoPersonal(
        id_usuario=id_usuario,
        monto=monto,
        fecha=pago_fecha,
        tipo=tipo or 'Pago'
    )
    db.session.add(pago_personal)
    db.session.flush()
    pago_empleado = PagoEmpleado(
        id_usuario=id_usuario,
        monto=monto,
        fecha_pago=datetime.combine(pago_fecha, datetime.min.time()),
        estado=estado,
        descripcion=descripcion
    )
    db.session.add(pago_empleado)
    db.session.commit()
    _log_actividad(session.get('usuario_id'), f'Registró pago para empleado {id_usuario}')
    flash('Pago registrado correctamente.', 'success')
    return redirect(url_for('pagos_personal'))


@app.route('/pagos-personal/adelanto', methods=['POST'])
@login_required
@admin_required
def registrar_adelanto_personal():
    id_usuario = request.form.get('id_usuario', type=int)
    motivo = request.form.get('motivo', '').strip()
    monto_text = request.form.get('monto', '').strip().replace(',', '.')
    fecha_text = request.form.get('fecha', '').strip()
    estado = request.form.get('estado', 'Pendiente').strip()

    if not id_usuario or not Usuario.query.get(id_usuario):
        flash('Empleado no válido.', 'error')
        return redirect(url_for('pagos_personal'))
    if not motivo:
        flash('El motivo es obligatorio.', 'error')
        return redirect(url_for('pagos_personal'))

    try:
        monto = float(monto_text)
        if monto <= 0:
            raise ValueError
    except ValueError:
        flash('El monto debe ser un número mayor que cero.', 'error')
        return redirect(url_for('pagos_personal'))

    try:
        adelanto_fecha = datetime.strptime(fecha_text, '%Y-%m-%d') if fecha_text else datetime.now()
    except ValueError:
        flash('Fecha de adelanto inválida.', 'error')
        return redirect(url_for('pagos_personal'))

    existe_adelanto = Adelanto.query.filter(
        Adelanto.id_usuario == id_usuario,
        db.func.date(Adelanto.fecha) == adelanto_fecha.date(),
        Adelanto.monto == monto,
        Adelanto.motivo == motivo
    ).first()
    if existe_adelanto:
        flash('Ya existe un adelanto similar para esa fecha.', 'error')
        return redirect(url_for('pagos_personal'))

    nuevo_adelanto = Adelanto(
        id_usuario=id_usuario,
        motivo=motivo,
        monto=monto,
        fecha=adelanto_fecha,
        estado=estado,
    )
    db.session.add(nuevo_adelanto)
    db.session.commit()
    _log_actividad(session.get('usuario_id'), f'Registró adelanto para empleado {id_usuario}')
    flash('Adelanto registrado correctamente.', 'success')
    return redirect(url_for('pagos_personal'))


@app.route("/perfil")
@login_required
def perfil():
    usuario = Usuario.query.get_or_404(session["usuario_id"])
    perfil = usuario.perfil
    pagos = PagoEmpleado.query.filter_by(id_usuario=usuario.id_usuario).order_by(PagoEmpleado.fecha_pago.desc()).limit(6).all()
    adelantos = Adelanto.query.filter_by(id_usuario=usuario.id_usuario).order_by(Adelanto.fecha.desc()).limit(6).all()
    actividades = ActividadUsuario.query.filter_by(id_usuario=usuario.id_usuario).order_by(ActividadUsuario.fecha.desc()).limit(8).all()
    return render_template(
        "perfil.html",
        usuario=usuario,
        perfil=perfil,
        pagos=pagos,
        adelantos=adelantos,
        actividades=actividades,
    )


@app.route("/perfil/editar", methods=["POST"])
@login_required
def editar_perfil():
    usuario = Usuario.query.get_or_404(session["usuario_id"])
    telefono = request.form.get("telefono", "").strip()
    correo = request.form.get("correo", "").strip().lower()
    clave_nueva = request.form.get("clave", "").strip()
    foto = request.files.get("foto_perfil")

    if not correo or not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', correo):
        flash("Ingrese un correo válido", "error")
        return redirect(url_for("perfil"))

    correo_existente = Usuario.query.filter(Usuario.correo == correo, Usuario.id_usuario != usuario.id_usuario).first()
    if correo_existente:
        flash("El correo ya está registrado en otra cuenta", "error")
        return redirect(url_for("perfil"))

    usuario.correo = correo
    usuario.telefono = telefono

    if clave_nueva:
        usuario.clave = bcrypt.generate_password_hash(clave_nueva).decode('utf-8')

    perfil = usuario.perfil
    if not perfil:
        perfil = UsuarioPerfil(id_usuario=usuario.id_usuario)
        db.session.add(perfil)

    if foto and foto.filename:
        if not _allowed_image(foto.filename):
            flash("Formato de imagen no válido. Usa jpg, jpeg, png o webp", "error")
            return redirect(url_for("perfil"))
        nombre_archivo = _secure_profile_filename(usuario.id_usuario, foto.filename)
        ruta_archivo = os.path.join(app.config['UPLOAD_FOLDER'], nombre_archivo)
        foto.save(ruta_archivo)
        if perfil.foto_perfil:
            ruta_anterior = os.path.join(app.config['UPLOAD_FOLDER'], perfil.foto_perfil)
            if os.path.exists(ruta_anterior):
                try:
                    os.remove(ruta_anterior)
                except OSError:
                    pass
        perfil.foto_perfil = nombre_archivo

    try:
        db.session.commit()
        flash("Perfil actualizado correctamente", "success")
    except Exception:
        db.session.rollback()
        flash("No se pudo actualizar el perfil. Intente de nuevo.", "error")

    return redirect(url_for("perfil"))


@app.route("/perfil/adelanto", methods=["POST"])
@login_required
def solicitar_adelanto():
    usuario = Usuario.query.get_or_404(session["usuario_id"])
    motivo = request.form.get("motivo", "").strip()
    monto_text = request.form.get("monto", "").strip().replace(",", ".")

    if not motivo:
        flash("El motivo es obligatorio para solicitar un adelanto", "error")
        return redirect(url_for("perfil"))

    try:
        monto = float(monto_text)
        if monto <= 0:
            raise ValueError
    except ValueError:
        flash("Ingrese un monto válido. Debe ser mayor a cero.", "error")
        return redirect(url_for("perfil"))

    adelanto = Adelanto(
        id_usuario=usuario.id_usuario,
        motivo=motivo,
        monto=monto,
        fecha=datetime.now(),
        estado="Pendiente"
    )
    db.session.add(adelanto)
    db.session.commit()
    _log_actividad(usuario.id_usuario, "Solicitó adelanto")
    flash("Solicitud de adelanto enviada", "success")
    return redirect(url_for("perfil"))


@app.route("/perfil/solicitar/<int:id_adelanto>/cancelar")
@login_required
def cancelar_adelanto(id_adelanto):
    adelanto = Adelanto.query.filter_by(id_adelanto=id_adelanto, id_usuario=session.get("usuario_id")).first_or_404()
    adelanto.estado = "Cancelado"
    db.session.commit()
    flash("Solicitud de adelanto cancelada", "success")
    return redirect(url_for("perfil"))


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
    _log_actividad(session.get("usuario_id"), "Registró venta" if tipo == "Venta" else "Registró gasto")

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
    _log_actividad(session.get("usuario_id"), "Cerró caja")

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"success": True, "message": "Caja cerrada correctamente."})

    flash("Caja cerrada correctamente", "success")
    return redirect(url_for("caja"))




@app.route('/enviar_reporte', methods=['POST'])
@login_required
@role_required("administrador", "cajera", "cajero")
def enviar_reporte():

    import subprocess

    hoy = date.today()
    fecha = datetime.now().strftime("%Y-%m-%d")

    cajero = session.get("nombre")

    transacciones = TransaccionCaja.query.filter(
        db.func.date(TransaccionCaja.fecha) == hoy
    ).all()

    total = sum(
        t.monto if t.tipo == "Venta" else -t.monto
        for t in transacciones
    )

    efectivo = sum(
        t.monto if t.tipo == "Venta" else -t.monto
        for t in transacciones
        if t.metodo_pago == "Efectivo"
    )

    tarjeta = sum(
        t.monto if t.tipo == "Venta" else -t.monto
        for t in transacciones
        if t.metodo_pago == "Tarjeta"
    )

    transferencia = sum(
        t.monto if t.tipo == "Venta" else -t.monto
        for t in transacciones
        if t.metodo_pago == "Transferencia"
    )

    result = subprocess.run([
        "python",
        "automatizacion_caja/enviar_cierre.py",
        "--fecha", fecha,
        "--cajero", cajero,
        "--total", str(total),
        "--efectivo", str(efectivo),
        "--tarjeta", str(tarjeta),
        "--transferencia", str(transferencia),
        "--destinatario", "i2512554@continental.edu.pe"
    ],
    capture_output=True,
    text=True)

    if result.returncode == 0:
        flash("Reporte enviado correctamente", "success")
        _log_actividad(session.get("usuario_id"), "Envió reporte")
    else:
        flash(f"Error al enviar reporte: {result.stderr}", "error")

    return redirect(url_for("caja"))


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
    _log_actividad(session.get("usuario_id"), "Registró gasto de inventario")
    flash("Inversión registrada correctamente", "success")
    return redirect(url_for("inventario"))


@app.route("/inventario/compra/<int:id>")
@login_required
@admin_required
def inventario_compra_detalle(id):
    inversion = Inversion.query.get_or_404(id)
    return render_template("inventario_compra_detalle.html", inversion=inversion)

# -------------------------------
# AUTOMATIZACION DE CAJA 
# -------------------------------

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