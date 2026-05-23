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

    rol = db.relationship('Rol', backref='usuarios')

    def __repr__(self):
        return f"<Usuario {self.id_usuario} {self.usuario}>"


class TransaccionCaja(db.Model):
    __tablename__ = 'transacciones_caja'

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

    id_producto = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Float, nullable=False)
    categoria = db.Column(db.String(100), nullable=False)
    fecha_registro = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"<Producto {self.id_producto} {self.nombre}>"


class Inversion(db.Model):
    __tablename__ = 'inversiones'

    id_inversion = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.Text, nullable=False)
    proveedor = db.Column(db.String(150), nullable=False)
    notas = db.Column(db.Text, nullable=True)
    monto = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"<Inversion {self.id_inversion} {self.monto}>"
