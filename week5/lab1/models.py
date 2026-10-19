from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Table, Column, Integer, String, Text
from sqlalchemy.orm import mapped_column, relationship


db = SQLAlchemy()

book_author = Table(
    "book_author",
    db.metadata,
    Column("book_id", Integer, ForeignKey("book.id"), primary_key=True),
    Column("author_id", Integer, ForeignKey("author.id"), primary_key=True)
)


class Category(db.Model):
    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(100), nullable=False)
    slug = mapped_column(String(100), unique=True, nullable=False)

    books = relationship("Book", back_populates="category")

    def toDict(self):
        return {
            "id": f"category_{self.id}",
            "name": self.name,
            "slug": self.slug
        }


class Author(db.Model):
    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(150), nullable=False)
    bio = mapped_column(Text)

    books = relationship(
        "Book",
        secondary=book_author,
        back_populates="authors"
    )

    def toDict(self):
        return {
            "id": f"author_{self.id}",
            "name": self.name,
            "bio": self.bio
        }


class Book(db.Model):
    id = mapped_column(Integer, primary_key=True)
    title = mapped_column(String(200), nullable=False)
    isbn = mapped_column(String(20), unique=True)
    price_vnd = mapped_column(Integer, nullable=False, default=0)
    stock = mapped_column(Integer, nullable=False, default=0)
    category_id = mapped_column(ForeignKey("category.id"))

    category = relationship("Category", back_populates="books")
    authors = relationship(
        "Author",
        secondary=book_author,
        back_populates="books"
    )
    reviews = relationship(
        "Review",
        back_populates="book",
        cascade="all, delete-orphan"
    )

    def toDict(self):
        return {
            "id": f"book_{self.id}",
            "title": self.title,
            "isbn": self.isbn,
            "price_vnd": self.price_vnd,
            "stock": self.stock,
            "category": self.category.toDict() if self.category else None,
            "authors": [author.toDict() for author in self.authors]
        }


class User(db.Model):
    id = mapped_column(Integer, primary_key=True)
    email = mapped_column(String(255), unique=True, nullable=False)
    display_name = mapped_column(String(100), nullable=False)

    reviews = relationship("Review", back_populates="user")

    def toDict(self):
        return {
            "id": f"user_{self.id}",
            "email": self.email,
            "display_name": self.display_name
        }


class Review(db.Model):
    id = mapped_column(Integer, primary_key=True)
    rating = mapped_column(Integer, nullable=False)
    book_id = mapped_column(ForeignKey("book.id"), nullable=False)
    user_id = mapped_column(ForeignKey("user.id"), nullable=False)

    book = relationship("Book", back_populates="reviews")
    user = relationship("User", back_populates="reviews")

    def toDict(self):
        return {
            "id": f"review_{self.id}",
            "rating": self.rating,
            "book_id": f"book_{self.book_id}",
            "user_id": f"user_{self.user_id}"
        }
