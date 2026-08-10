from bd import db


class Rol(db.Model):
    __tablename__ = 'roles'

    id_rol = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<Rol {self.id_rol} {self.nombre}>"


class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id_usuario = db.Column(db.Integer, primary_key=True)
    nombres = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100))
    dni = db.Column(db.String(15))
    correo = db.Column(db.String(150), unique=True)
    telefono = db.Column(db.String(15))
    usuario = db.Column(db.String(50), unique=True, nullable=False)
    clave = db.Column(db.String(255), nullable=False)
    id_rol = db.Column(db.Integer, db.ForeignKey('roles.id_rol'))
    estado = db.Column(db.Integer, default=1)
    turno = db.Column(db.String(50), nullable=True)

    rol = db.relationship('Rol', backref='usuarios')
    perfil = db.relationship('UsuarioPerfil', back_populates='usuario', uselist=False, cascade='all, delete-orphan')
    pagos_personal = db.relationship('PagoPersonal', back_populates='usuario', lazy='dynamic')
    pagos_empleados = db.relationship('PagoEmpleado', backref='usuario_empleado', lazy='dynamic')
    adelantos = db.relationship('Adelanto', backref='usuario_adelanto', lazy='dynamic')

    def __repr__(self):
        return f"<Usuario {self.id_usuario} {self.usuario}>"


class UsuarioPerfil(db.Model):
    __tablename__ = 'usuario_perfiles'

    id_perfil = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), unique=True)
    foto_perfil = db.Column(db.String(255))
    fecha_ingreso = db.Column(db.Date)
    horario = db.Column(db.String(100))
    salario = db.Column(db.Float)

    usuario = db.relationship('Usuario', back_populates='perfil')

    def __repr__(self):
        return f"<UsuarioPerfil {self.id_perfil} usuario={self.id_usuario}>"


class PagoEmpleado(db.Model):
    __tablename__ = 'pagos_empleados'
    __table_args__ = (
        db.Index('ix_pagos_empleados_usuario', 'id_usuario'),
        db.Index('ix_pagos_empleados_fecha', 'fecha_pago'),
    )

    id_pago = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'))
    monto = db.Column(db.Float, nullable=False)
    fecha_pago = db.Column(db.DateTime, nullable=False)
    estado = db.Column(db.String(80), nullable=False)
    descripcion = db.Column(db.String(255))

    def __repr__(self):
        return f"<PagoEmpleado {self.id_pago} usuario={self.id_usuario} monto={self.monto}>"


class PagoPersonal(db.Model):
    __tablename__ = 'pagos_personal'
    __table_args__ = (
        db.Index('ix_pagos_personal_usuario', 'id_usuario'),
        db.Index('ix_pagos_personal_fecha', 'fecha'),
    )

    id_pago = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'))
    monto = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    tipo = db.Column(db.String(100))

    usuario = db.relationship('Usuario', back_populates='pagos_personal')

    def __repr__(self):
        return f"<PagoPersonal {self.id_pago} usuario={self.id_usuario} monto={self.monto} tipo={self.tipo}>"


class Adelanto(db.Model):
    __tablename__ = 'adelantos'
    __table_args__ = (
        db.Index('ix_adelantos_usuario', 'id_usuario'),
        db.Index('ix_adelantos_fecha', 'fecha'),
        db.Index('ix_adelantos_estado', 'estado'),
    )

    id_adelanto = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'))
    motivo = db.Column(db.String(255), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.DateTime, nullable=False)
    estado = db.Column(db.String(80), nullable=False, default='Pendiente')
    respuesta_admin = db.Column(db.Text, nullable=True)
    fecha_gestion = db.Column(db.DateTime, nullable=True)
    notificacion_vista = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<Adelanto {self.id_adelanto} usuario={self.id_usuario} monto={self.monto}>"


class ActividadUsuario(db.Model):
    __tablename__ = 'actividad_usuario'
    __table_args__ = (
        db.Index('ix_actividad_usuario_usuario', 'id_usuario'),
        db.Index('ix_actividad_usuario_fecha', 'fecha'),
    )

    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'))
    accion = db.Column(db.String(255), nullable=False)
    fecha = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"<ActividadUsuario {self.id} usuario={self.id_usuario} accion={self.accion}>"


class IntentoLogin(db.Model):
    __tablename__ = 'intentos_login'
    __table_args__ = (
        db.Index('ix_intentos_login_fecha', 'fecha'),
    )

    id = db.Column(db.Integer, primary_key=True)
    identificador = db.Column(db.String(255), nullable=False, index=True)
    fecha = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"<IntentoLogin {self.id} {self.identificador} {self.fecha}>"


class TransaccionCaja(db.Model):
    __tablename__ = 'transacciones_caja'
    __table_args__ = (
        db.Index('ix_transacciones_caja_usuario', 'id_usuario'),
        db.Index('ix_transacciones_caja_fecha', 'fecha'),
    )

    id_transaccion = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'))
    tipo = db.Column(db.String(50), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    metodo_pago = db.Column(db.String(50), nullable=False)
    categoria = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text)
    fecha = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"<TransaccionCaja {self.id_transaccion} {self.tipo} {self.monto}>"


class CierreCaja(db.Model):
    __tablename__ = 'cierres_caja'
    __table_args__ = (
        db.Index('ix_cierres_caja_fecha', 'fecha'),
    )

    id_cierre = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'))
    total_ventas = db.Column(db.Float, nullable=False)
    total_gastos = db.Column(db.Float, nullable=False)
    neto = db.Column(db.Float, nullable=False)
    observaciones = db.Column(db.Text)
    fecha = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"<CierreCaja {self.id_cierre} {self.fecha}>"


class Producto(db.Model):
    __tablename__ = 'productos'
    __table_args__ = (
        db.Index('ix_productos_fecha_registro', 'fecha_registro'),
    )

    id_producto = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Float, nullable=False)
    categoria = db.Column(db.String(100), nullable=False)
    fecha_registro = db.Column(db.DateTime, nullable=False)
    fecha_edicion = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<Producto {self.id_producto} {self.nombre}>"


class Inversion(db.Model):
    __tablename__ = 'inversiones'
    __table_args__ = (
        db.Index('ix_inversiones_fecha', 'fecha'),
    )

    id_inversion = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.Text, nullable=False)
    proveedor = db.Column(db.String(150), nullable=False)
    notas = db.Column(db.Text, nullable=True)
    monto = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"<Inversion {self.id_inversion} {self.monto}>"


class Categoria(db.Model):
    __tablename__ = 'categorias'

    id_categoria = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    fecha_creacion = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"<Categoria {self.id_categoria} {self.nombre}>"


