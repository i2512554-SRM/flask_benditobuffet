from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    db_user = 'bendito_sebas'
    db_password = 'sebas1819+'
    db_host = 'mysql-bendito.alwaysdata.net'
    db_name = 'bendito_buffet'

    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}?ssl_disabled=false'
        )

    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
