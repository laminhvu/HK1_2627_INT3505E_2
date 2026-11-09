from flask import Flask

from .errors import register_error_handlers
from .extensions import db


def create_app(config=None):
    app = Flask(__name__)
    app.config.update(
        SQLALCHEMY_DATABASE_URI="sqlite:///products.db",
    )
    if config:
        app.config.update(config)

    db.init_app(app)

    from .api.products import products_bp
    app.register_blueprint(products_bp)
    register_error_handlers(app)

    with app.app_context():
        from . import models  # noqa: F401
        db.create_all()

    return app
