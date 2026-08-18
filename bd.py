import os

from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()


def init_db(app):

    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "benditobeffet2026")
    host = os.getenv("DB_HOST", "db.dotnogeffcylgiplpfyj.supabase.co")
    port = os.getenv("DB_PORT", "5432")
    database = os.getenv("DB_NAME", "postgres")

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"postgresql+psycopg://{user}:{password}@{host}:{port}/{database}?sslmode=require"
    )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True
    }

    db.init_app(app)