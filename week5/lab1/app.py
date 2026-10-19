from flask import Flask, jsonify

from models import db
from books import books_bp


def createApp():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bookstore.db"

    db.init_app(app)
    app.register_blueprint(books_bp)

    @app.errorhandler(404)
    def notFound(error):
        return jsonify({"error": "Not found"}), 404

    with app.app_context():
        db.create_all()

    return app


app = createApp()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
