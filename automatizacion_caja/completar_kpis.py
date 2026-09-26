"""Completa campos que dejan los KPIs sin dato: costo de productos y sueldos semanales."""
import os
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))
os.chdir(_PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv(_PROJECT_ROOT / '.env')

from datetime import date
import psycopg
from flask import Flask
from bd import init_db, db
from models import Producto, Usuario, SueldoSemanal

COSTO_ARROZ = 4.40
COSTO_AZUCAR = 4.00
SUELDO_SEMANAL = 300.00
DESDE_SUELDO = date(2024, 12, 30)


def limpiar_prepared_statements():
    conexion = psycopg.connect(
        host=os.environ['DB_HOST'], port=int(os.getenv('DB_PORT', '6543')),
        user=os.environ['DB_USER'], password=os.environ['DB_PASSWORD'],
        dbname=os.getenv('DB_NAME', 'postgres'), sslmode='require', autocommit=True)
    conexion.execute('DEALLOCATE ALL')
    conexion.close()


def main():
    limpiar_prepared_statements()
    app = Flask(__name__)
    init_db(app)
    with app.app_context():
        admin = Usuario.query.filter(Usuario.id_rol == 1, Usuario.estado.is_(True)).order_by(Usuario.id_usuario).first()
        if not admin:
            print('No hay usuario administrador activo. Nada que hacer.')
            return

        productos = Producto.query.all()
        costos_objetivo = {
            'Arroz': COSTO_ARROZ,
            'Azucar': COSTO_AZUCAR,
            'Azúcar': COSTO_AZUCAR,
        }
        for p in productos:
            if p.nombre.strip() in costos_objetivo:
                p.costo = costos_objetivo[p.nombre.strip()]
        db.session.commit()
        print('Costos actualizados:')
        for p in Producto.query.order_by(Producto.id_producto).all():
            print('  ', p.nombre, '->', float(p.costo) if p.costo is not None else None)

        empleados = Usuario.query.filter(Usuario.estado.is_(True), Usuario.id_rol != 1).order_by(Usuario.id_usuario).all()
        insertados, existentes = 0, 0
        for e in empleados:
            previo = SueldoSemanal.query.filter_by(id_usuario=e.id_usuario).first()
            if previo:
                existentes += 1
                continue
            db.session.add(SueldoSemanal(
                id_usuario=e.id_usuario,
                desde=DESDE_SUELDO,
                monto=SUELDO_SEMANAL,
                registrado_por=admin.id_usuario,
                fecha=db.func.now(),
            ))
            insertados += 1
        db.session.commit()
        print(f'Sueldos semanales: {insertados} insertados, {existentes} ya existentes.')


if __name__ == '__main__':
    main()