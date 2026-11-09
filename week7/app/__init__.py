from flask import Flask

from .errors import register_error_handlers
from .extensions import db
from .api.products import products_bp
from .api.orders import orders_bp


def create_app(config=None):
    app = Flask(__name__)
    app.config.update(
        SQLALCHEMY_DATABASE_URI="sqlite:///products.db",
    )
    if config:
        app.config.update(config)

    db.init_app(app)

    app.register_blueprint(products_bp)
    app.register_blueprint(orders_bp)
    register_error_handlers(app)

    with app.app_context():
        from . import models  # noqa: F401
        db.create_all()

    return app