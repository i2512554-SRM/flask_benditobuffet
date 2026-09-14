import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine import URL
from dotenv import load_dotenv

load_dotenv()
db = SQLAlchemy()


def init_db(app):
    requeridas = ('DB_USER', 'DB_PASSWORD', 'DB_HOST')
    if any(not os.getenv(nombre) for nombre in requeridas):
        raise RuntimeError('Configure DB_USER, DB_PASSWORD y DB_HOST en el entorno del servidor.')
    app.config['SQLALCHEMY_DATABASE_URI'] = URL.create(
        'postgresql+psycopg', username=os.environ['DB_USER'], password=os.environ['DB_PASSWORD'],
        host=os.environ['DB_HOST'], port=int(os.getenv('DB_PORT', '6543')),
        database=os.getenv('DB_NAME', 'postgres'), query={'sslmode': 'require'})
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_pre_ping': True}
    db.init_app(app)
