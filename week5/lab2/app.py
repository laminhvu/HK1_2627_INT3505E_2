import base64
import json

from flask import Blueprint, Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select, tuple_


db = SQLAlchemy()


class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    price_vnd = db.Column(db.Integer, nullable=False, index=True)
    category_id = db.Column(db.Integer, nullable=False, index=True)

    def to_dict(self):
        return {"id": self.id, "title": self.title,
                "price_vnd": self.price_vnd, "category_id": self.category_id}


bp = Blueprint("books", __name__, url_prefix="/api/v1/books")

SORT = {"id": Book.id, "price": Book.price_vnd}


def parse_sort(raw):
    desc = raw.startswith("-")
    key = raw.lstrip("-")
    if key not in SORT:
        return None, "bad_sort", 400
    p = SORT[key]
    cols = [
        p.desc() if desc else p.asc(),
        Book.id.desc() if desc else Book.id.asc(),
    ]
    return p, cols, desc


def _enc(s):
    return base64.urlsafe_b64encode(
        json.dumps(s).encode()
    ).decode().rstrip("=")


def apply_cursor(q, raw, sort, p, desc):
    if not raw:
        return q, None, 200
    pad = "=" * (-len(raw) % 4)
    c = json.loads(
        base64.urlsafe_b64decode(raw + pad))
    if c.get("s") != sort:
        return None, "sort_chg", 400
    v, i = c["v"], c["i"]
    op = "<" if desc else ">"
    condition = tuple_(p, Book.id).op(op)(
        tuple_(v, i))
    return q.filter(condition), None, 200



def build_response(items, lim, sort, p, more):
    nxt = None
    if items and more:
        last = items[-1]
        nxt = _enc({
            "s": sort,
            "v": getattr(last, p.key),
            "i": last.id,
        })
    return jsonify({
        "data": [b.to_dict() for b in items],
        "page": {"next": nxt, "more": more},
    })


@bp.get("")
def list_books():
    raw = request.args.get("cursor")
    lim = min(request.args.get(
        "limit", 20, type=int), 100)
    sort = request.args.get("sort", "-id")
    cat = request.args.get("category", type=int)
    p, cols, desc = parse_sort(sort)
    if p is None:
        return cols, 400
    q = select(Book).order_by(*cols)
    if cat:
        q = q.filter(Book.category_id == cat)
    q, err, code = apply_cursor(q, raw, sort, p, desc)
    if err:
        return {"e": err}, code
    rows = db.session.scalars(q.limit(lim + 1)).all()
    return build_response(
        rows[:lim], lim, sort, p, len(rows) > lim)


def create_app(db_uri="sqlite:///books.db"):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    db.init_app(app)
    app.register_blueprint(bp)
    return app


def seed():
    
    prices = [50000, 30000, 30000, 30000, 20000, 10000]
    for n in range(25):
        db.session.add(Book(title=f"Book {n + 1}",
                            price_vnd=prices[n % len(prices)],
                            category_id=(n % 3) + 1))
    db.session.commit()


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
        if not db.session.query(Book).first():
            seed()
    app.run(debug=True, port=5000)