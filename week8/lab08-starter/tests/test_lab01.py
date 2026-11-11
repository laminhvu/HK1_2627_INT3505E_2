"""LAB 1 — add your five tests here. Do not delete the smoke tests.

A. GET /books, empty database -> HTTP 200 and []
B. GET /books/9999 -> HTTP 404, JSON code == NOT_FOUND
C. POST /books with only author -> HTTP 400, errors contains title
D. POST valid book, DELETE it, GET same id -> HTTP 404
BONUS. Validate a Book response using JSON Schema; add an unknown
       field to a *copy* of the response and assert ValidationError.

Useful imports:
    from jsonschema import validate, ValidationError
    import pytest
    from tools import get_book_schema

Do not depend on test execution order. Fixtures: client, app, sample_book.
"""


import pytest


 
# A trả về [] thay vì null nếu db rỗng
def test_list_books_empty_returns_empty_array(client):
    r = client.get("/books")
    assert r.status_code == 200
    assert r.content_type == "application/json"
    assert r.get_json() == []
 
 
# B id không tồn tại - 4040
def test_get_unknown_book(client):
    r = client.get("/books/9999")
    assert r.status_code == 404
    assert r.get_json()["code"] == "NOT_FOUND"
 
 
# C  thiếu title 400 
def test_create_book_without_title(client):
    r = client.post("/books", json={"author": "X"})
    assert r.status_code == 400

    body = r.get_json()
    errors = body["errors"]

   
    fields = []
    for error in errors:
        fields.append(error["field"])

    assert "title" in fields
 
 
# D xoá rồi get lại cùng id404
def test_deleted_same_book(client, sample_book):
    assert client.delete(f"/books/{sample_book}").status_code == 204
    assert client.get(f"/books/{sample_book}").status_code == 404
 

