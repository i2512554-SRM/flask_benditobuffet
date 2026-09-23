import os

from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()


def init_db(app):

    user = os.getenv("DB_USER", "postgres.dotnogeffcylgiplpfyj")
    password = os.getenv("DB_PASSWORD", "BenditoBuffetAV_P183")
    host = os.getenv("DB_HOST", "aws-0-us-west-2.pooler.supabase.com")
    port = os.getenv("DB_PORT", "6543")
    database = os.getenv("DB_NAME", "postgres")

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"postgresql+psycopg://{user}:{password}@{host}:{port}/{database}?sslmode=require"
    )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True
    }

    db.init_app(app)