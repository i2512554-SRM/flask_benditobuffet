from bd import db


class Rol(db.Model):
    __tablename__ = 'roles'

    id_rol = db.Column(db.BigInteger, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True)
    estado = db.Column(db.Boolean, nullable=False, default=True)
    fecha_creacion = db.Column(db.DateTime(timezone=True), nullable=False)

    usuarios = db.relationship('Usuario', back_populates='rol')


class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id_usuario = db.Column(db.BigInteger, primary_key=True)
    nombres = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)

    id_documento = db.Column(
        db.BigInteger,
        db.ForeignKey('documentos_identidad.id_documento'),
        nullable=False
    )

    correo = db.Column(db.String(150), nullable=False, unique=True)
    telefono = db.Column(db.String(20))
    usuario = db.Column(db.String(50), nullable=False, unique=True)
    clave = db.Column(db.String(255), nullable=False)

    id_rol = db.Column(
        db.BigInteger,
        db.ForeignKey('roles.id_rol'),
        nullable=False
    )

    estado = db.Column(db.Boolean, nullable=False, default=True)
    turno = db.Column(db.String(50))
    fecha_creacion = db.Column(db.DateTime(timezone=True), nullable=False)

    rol = db.relationship('Rol', back_populates='usuarios')
    documento = db.relationship('DocumentoIdentidad', back_populates='usuario', uselist=False)
    perfil = db.relationship('UsuarioPerfil', back_populates='usuario', uselist=False)
    pagos_personal = db.relationship('PagoPersonal', back_populates='usuario')

    @property
    def dni(self):
        return self.documento.numero if self.documento else None

    @dni.setter
    def dni(self, value):
        if self.documento:
            self.documento.numero = value


class DocumentoIdentidad(db.Model):
    __tablename__ = 'documentos_identidad'

    id_documento = db.Column(db.BigInteger, primary_key=True)
    tipo_documento = db.Column(db.String(30), nullable=False, default='DNI')
    numero = db.Column(db.String(20), nullable=False, unique=True)
    estado = db.Column(db.Boolean, nullable=False, default=True)

    usuario = db.relationship('Usuario', back_populates='documento', uselist=False)


class UsuarioPerfil(db.Model):
    __tablename__ = 'usuario_perfiles'

    id_perfil = db.Column(db.BigInteger, primary_key=True)
    id_usuario = db.Column(db.BigInteger, db.ForeignKey('usuarios.id_usuario'), unique=True, nullable=False)
    foto_perfil = db.Column(db.String(255))
    fecha_ingreso = db.Column(db.Date)
    horario = db.Column(db.String(100))
    salario = db.Column(db.Float)
    fecha_creacion = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    usuario = db.relationship('Usuario', back_populates='perfil')

    def __repr__(self):
        return f"<UsuarioPerfil {self.id_perfil} usuario={self.id_usuario}>"


class Proveedor(db.Model):
    __tablename__ = 'proveedores'

    id_proveedor = db.Column(db.BigInteger, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    ruc = db.Column(db.String(20))
    telefono = db.Column(db.String(20))
    correo = db.Column(db.String(150))
    direccion = db.Column(db.String(255))
    estado = db.Column(db.Boolean, nullable=False, default=True)
    fecha_creacion = db.Column(db.DateTime(timezone=True))

    def __repr__(self):
        return f"<Proveedor {self.id_proveedor} {self.nombre}>"


class PagoEmpleado(db.Model):
    __tablename__ = 'pagos_empleados'
    __table_args__ = (
        db.Index('ix_pagos_empleados_usuario', 'id_usuario'),
        db.Index('ix_pagos_empleados_fecha', 'fecha_pago'),
    )

    id_pago = db.Column(db.BigInteger, primary_key=True)
    id_usuario = db.Column(db.BigInteger, db.ForeignKey('usuarios.id_usuario'))
    monto = db.Column(db.Float, nullable=False)
    fecha_pago = db.Column(db.DateTime(timezone=True), nullable=False)
    estado = db.Column(db.String(80), nullable=False)
    descripcion = db.Column(db.String(255))

    usuario_empleado = db.relationship('Usuario', foreign_keys=[id_usuario])

    def __repr__(self):
        return f"<PagoEmpleado {self.id_pago} usuario={self.id_usuario} monto={self.monto}>"


class PagoPersonal(db.Model):
    __tablename__ = 'pagos_personal'
    __table_args__ = (
        db.Index('ix_pagos_personal_usuario', 'id_usuario'),
        db.Index('ix_pagos_personal_fecha', 'fecha'),
    )

    id_pago = db.Column(db.BigInteger, primary_key=True)
    id_usuario = db.Column(db.BigInteger, db.ForeignKey('usuarios.id_usuario'))
    monto = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    tipo = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(80), nullable=False, server_default='Completado')
    descripcion = db.Column(db.String(255))

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

    id_adelanto = db.Column(db.BigInteger, primary_key=True)
    id_usuario = db.Column(db.BigInteger, db.ForeignKey('usuarios.id_usuario'))
    motivo = db.Column(db.String(255), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.DateTime(timezone=True), nullable=False)
    estado = db.Column(db.String(80), nullable=False, default='Pendiente')
    respuesta_admin = db.Column(db.Text, nullable=True)
    fecha_gestion = db.Column(db.DateTime(timezone=True), nullable=True)
    notificacion_vista = db.Column(db.Boolean, default=False)

    usuario_adelanto = db.relationship('Usuario', foreign_keys=[id_usuario])

    def __repr__(self):
        return f"<Adelanto {self.id_adelanto} usuario={self.id_usuario} monto={self.monto}>"


class ActividadUsuario(db.Model):
    __tablename__ = 'actividad_usuario'
    __table_args__ = (
        db.Index('ix_actividad_usuario_usuario', 'id_usuario'),
        db.Index('ix_actividad_usuario_fecha', 'fecha'),
    )

    id_actividad = db.Column(db.BigInteger, primary_key=True)
    id_usuario = db.Column(db.BigInteger, db.ForeignKey('usuarios.id_usuario'))
    accion = db.Column(db.String(255), nullable=False)
    fecha = db.Column(db.DateTime(timezone=True), nullable=False)

    def __repr__(self):
        return f"<ActividadUsuario {self.id_actividad} usuario={self.id_usuario} accion={self.accion}>"


class IntentoLogin(db.Model):
    __tablename__ = 'intentos_login'
    __table_args__ = (
        db.Index('ix_intentos_login_fecha', 'fecha'),
    )

    id = db.Column(db.BigInteger, primary_key=True)
    identificador = db.Column(db.String(255), nullable=False, index=True)
    fecha = db.Column(db.DateTime(timezone=True), nullable=False)

    def __repr__(self):
        return f"<IntentoLogin {self.id} {self.identificador} {self.fecha}>"


class TransaccionCaja(db.Model):
    __tablename__ = 'transacciones_caja'
    __table_args__ = (
        db.Index('ix_transacciones_caja_usuario', 'id_usuario'),
        db.Index('ix_transacciones_caja_fecha', 'fecha'),
    )

    id_transaccion = db.Column(db.BigInteger, primary_key=True)
    id_usuario = db.Column(db.BigInteger, db.ForeignKey('usuarios.id_usuario'))
    tipo = db.Column(db.String(50))
    monto = db.Column(db.Float, nullable=False)
    metodo_pago = db.Column(db.String(50))
    categoria = db.Column(db.String(150))
    descripcion = db.Column(db.Text)
    fecha = db.Column(db.DateTime(timezone=True), nullable=False)

    def __repr__(self):
        return f"<TransaccionCaja {self.id_transaccion} {self.tipo} {self.monto}>"


class CierreCaja(db.Model):
    __tablename__ = 'cierres_caja'
    __table_args__ = (
        db.Index('ix_cierres_caja_fecha', 'fecha'),
    )

    id_cierre = db.Column(db.BigInteger, primary_key=True)
    id_usuario = db.Column(db.BigInteger, db.ForeignKey('usuarios.id_usuario'))
    total_ventas = db.Column(db.Float, nullable=False)
    total_gastos = db.Column(db.Float, nullable=False)
    neto = db.Column(db.Float, db.Computed('(total_ventas - total_gastos)'))
    observaciones = db.Column(db.Text)
    estado = db.Column(db.String(20), nullable=False, default='cerrada')
    fecha_cierre = db.Column(db.DateTime(timezone=True), nullable=True)
    fecha = db.Column(db.DateTime(timezone=True), nullable=False)

    def __repr__(self):
        return f"<CierreCaja {self.id_cierre} {self.fecha}>"


class Producto(db.Model):
    __tablename__ = 'productos'
    __table_args__ = (
        db.Index('ix_productos_fecha_registro', 'fecha_registro'),
    )

    id_producto = db.Column(db.BigInteger, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Float, nullable=False)
    id_categoria = db.Column(db.BigInteger, db.ForeignKey('categorias.id_categoria'), nullable=False)
    fecha_registro = db.Column(db.DateTime(timezone=True), nullable=False)
    fecha_edicion = db.Column(db.DateTime(timezone=True), nullable=False)

    categoria_rel = db.relationship('Categoria', foreign_keys=[id_categoria])

    @property
    def categoria(self):
        return self.categoria_rel.nombre if self.categoria_rel else None

    def __repr__(self):
        return f"<Producto {self.id_producto} {self.nombre}>"


class Inversion(db.Model):
    __tablename__ = 'inversiones'
    __table_args__ = (
        db.Index('ix_inversiones_fecha', 'fecha'),
    )

    id_inversion = db.Column(db.BigInteger, primary_key=True)
    descripcion = db.Column(db.String(255), nullable=False)
    id_proveedor = db.Column(db.BigInteger, db.ForeignKey('proveedores.id_proveedor'), nullable=True)
    notas = db.Column(db.Text, nullable=True)
    monto = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.DateTime(timezone=True), nullable=False)

    proveedor_rel = db.relationship('Proveedor', foreign_keys=[id_proveedor])

    @property
    def proveedor(self):
        return self.proveedor_rel.nombre if self.proveedor_rel else None

    @proveedor.setter
    def proveedor(self, value):
        if value:
            prov = Proveedor.query.filter_by(nombre=value).first()
            if not prov:
                prov = Proveedor(nombre=value)
                db.session.add(prov)
                db.session.flush()
            self.id_proveedor = prov.id_proveedor

    def __repr__(self):
        return f"<Inversion {self.id_inversion} {self.monto}>"


class Categoria(db.Model):
    __tablename__ = 'categorias'

    id_categoria = db.Column(db.BigInteger, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    fecha_creacion = db.Column(db.DateTime(timezone=True), nullable=False)

    def __repr__(self):
        return f"<Categoria {self.id_categoria} {self.nombre}>"
