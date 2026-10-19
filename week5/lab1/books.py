import json
from pathlib import Path

from flask import Blueprint, jsonify, request
from jsonschema import Draft202012Validator

from models import db, Book, Author, Category


books_bp = Blueprint("books", __name__, url_prefix="/api/v1/books")

bookSchema = json.loads(
    (Path(__file__).parent / "book.json").read_text()
)



def handleError(status, message, details=None):
    body = {"error": message}

    if details:
        body["details"] = details

    return jsonify(body), status


def validateData(data, partial=False):
    schema = dict(bookSchema)

    if partial:
        schema["required"] = []

    errors = Draft202012Validator(schema).iter_errors(data or {})
    errors = sorted(errors, key=lambda error: list(error.path))

    result = []
    for error in errors:
        field = "/".join(map(str, error.path)) or "body"
        result.append(f"{field}: {error.message}")

    return result


def getOrCreateAuthor(name):
    author = db.session.scalar(
        db.select(Author).where(Author.name == name)
    )

    if author is None:
        author = Author(name=name)
        db.session.add(author)

    return author


def getOrCreateCategory(name):
    slug = name.strip().lower().replace(" ", "-")

    category = db.session.scalar(
        db.select(Category).where(Category.slug == slug)
    )

    if category is None:
        category = Category(name=name, slug=slug)
        db.session.add(category)

    return category


def applyBookData(book, data):
    fields = ("title", "isbn", "price_vnd", "stock", "category_id")

    for field in fields:
        if field in data:
            setattr(book, field, data[field])

    if "category" in data:
        book.category = getOrCreateCategory(data["category"])

    if "authors" in data:
        book.authors = [
            getOrCreateAuthor(name) for name in data["authors"]
        ]
    elif "author_ids" in data:
        book.authors = db.session.scalars(
            db.select(Author).where(
                Author.id.in_(data["author_ids"])
            )
        ).all()


@books_bp.get("")
def listBooks():
    page = request.args.get("page", 1, type=int)
    perPage = min(request.args.get("per_page", 10, type=int), 100)

    stmt = db.select(Book).order_by(Book.id)

    category = request.args.get("category")
    if category:
        stmt = stmt.join(Category).where(Category.slug == category)

    result = db.paginate(
        stmt,
        page=page,
        per_page=perPage,
        error_out=False
    )

    return jsonify({
        "items": [book.toDict() for book in result.items],
        "page": result.page,
        "per_page": result.per_page,
        "total": result.total
    })


@books_bp.get("/<int:book_id>")
def getBook(book_id):
    book = db.session.get(Book, book_id)

    if book is None:
        return handleError(404, "Book not found")

    return jsonify(book.toDict())


@books_bp.post("")
def createBook():
    data = request.get_json(silent=True)
    errors = validateData(data)

    if errors:
        return handleError(400, "Validation failed", errors)

    book = Book()
    applyBookData(book, data)

    db.session.add(book)
    db.session.commit()

    return jsonify(book.toDict()), 201


@books_bp.put("/<int:book_id>")
def updateBook(book_id):
    book = db.session.get(Book, book_id)

    if book is None:
        return handleError(404, "Book not found")

    data = request.get_json(silent=True)
    errors = validateData(data, partial=True)

    if errors:
        return handleError(400, "Validation failed", errors)

    applyBookData(book, data)
    db.session.commit()

    return jsonify(book.toDict())


@books_bp.delete("/<int:book_id>")
def deleteBook(book_id):
    book = db.session.get(Book, book_id)

    if book is None:
        return handleError(404, "Book not found")

    db.session.delete(book)
    db.session.commit()

    return "", 204
