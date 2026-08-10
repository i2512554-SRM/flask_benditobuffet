import os

from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    load_dotenv()

    db_user = os.getenv('DB_USER', '')
    db_password = os.getenv('DB_PASSWORD', '')
    db_host = os.getenv('DB_HOST', '')
    db_name = os.getenv('DB_NAME', '')

    if not all([db_user, db_password, db_host, db_name]):
        raise RuntimeError(
            "Faltan variables de entorno de la base de datos (DB_USER, DB_PASSWORD, DB_HOST, DB_NAME). "
            "Revisa el archivo .env"
        )

    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}?ssl_disabled=false'
    )

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
