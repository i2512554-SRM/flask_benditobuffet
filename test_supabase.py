from app import app
from bd import db
from models import Rol

with app.app_context():
    roles = Rol.query.order_by(Rol.id_rol).all()

    print("\n===== ROLES EN SUPABASE =====")
    for rol in roles:
        print(f"ID: {rol.id_rol} | Nombre: {rol.nombre} | Estado: {rol.estado}")