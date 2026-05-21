from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    db_user = 'bendito'
    db_password = 'rosamelano602'
    db_host = 'mysql-bendito.alwaysdata.net'
    db_name = 'db_usuarios'

    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
