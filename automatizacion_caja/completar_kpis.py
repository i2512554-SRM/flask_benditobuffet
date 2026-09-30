"""Completa el costo de productos base de ejemplo (Arroz, Azúcar) para que los indicadores tengan dato.

Solo para bases de demostración. Los sueldos de ejemplo los genera sembrar_historicos.py.
Aplicar: --confirmo-datos-de-ejemplo
"""
import os
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))
os.chdir(_PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv(_PROJECT_ROOT / '.env')

import psycopg
from flask import Flask
from bd import init_db, db
from models import Producto, Usuario

COSTO_ARROZ = 4.40
COSTO_AZUCAR = 4.00


def limpiar_prepared_statements():
    conexion = psycopg.connect(
        host=os.environ['DB_HOST'], port=int(os.getenv('DB_PORT', '6543')),
        user=os.environ['DB_USER'], password=os.environ['DB_PASSWORD'],
        dbname=os.getenv('DB_NAME', 'postgres'), sslmode='require', autocommit=True)
    conexion.execute('DEALLOCATE ALL')
    conexion.close()


def main():
    if '--confirmo-datos-de-ejemplo' not in sys.argv:
        print('Este script modifica datos de ejemplo. Ejecútalo con --confirmo-datos-de-ejemplo.')
        return
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


if __name__ == '__main__':
    main()
