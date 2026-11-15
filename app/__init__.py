import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

DEFAULT_DATABASE_URL = (
    "postgresql+psycopg2://postgres:postgres@localhost:5432/cestasolidaria"
)


def create_app(config: dict | None = None) -> Flask:
    """Application factory.

    A conexao com o banco e definida pela variavel de ambiente DATABASE_URL.
    Sem ela, usa o PostgreSQL local padrao definido em DEFAULT_DATABASE_URL.
    """
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", DEFAULT_DATABASE_URL
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    if config:
        app.config.update(config)

    db.init_app(app)

    from . import models  # noqa: F401  (registra os modelos no metadata)
    from .routes import bp

    app.register_blueprint(bp)

    with app.app_context():
        db.create_all()

    return app
