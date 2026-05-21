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
