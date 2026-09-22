from flask import Flask, jsonify, request, make_response
import sqlite3 
import hashlib
import json

app = Flask(__name__)
DB = "api_session2/books.db"
def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()

    conn.execute(
        "CREATE TABLE IF NOT EXISTS books (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, author TEXT NOT NULL, isbn TEXT, price REAL)"
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer TEXT NOT NULL,
            status TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()

BOOKS = []
_next_id = 1
#GET
# @app.get("/books")
# def list_book():
#     return jsonify({
#         "data" : BOOKS,
#         "total" : len(BOOKS)
#     }), 200
#POST
@app.post("/books")
def create_book():
    # global _next_id
    if not request.is_json:
        return jsonify(error = "expected JSON"), 415
    
    p = request.get_json(silent = True) or {}
    t = (p.get("title") or "").strip()
    a = (p.get("author") or "").strip()

    if not t or not a:
        return jsonify(error="title and author required"), 422

    conn = get_db()

    point = conn.execute(
        "INSERT INTO books (title, author) VALUES(?,?)", (t,a) 
    )


    conn.commit()

    book_id = point.lastrowid 
    book = conn.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    

    conn.close()

    # book = {"id" : _next_id, "title": t, "author": a}
    # BOOKS.append(book)
    # _next_id +=1

    resp = make_response(jsonify(dict(book)), 201)
    resp.headers["Location"] = f"books/{book['id']}"
    return resp


# get /books/<id>
@app.get("/books/<int:bid>")
def fetch(bid):
    # i = next((k for k, b in enumerate(BOOKS) if b["id"] == bid), None)

    conn = get_db()

    book = conn.execute("SELECT * FROM books WHERE id = ?", (bid,)).fetchone()

    conn.close()
    data = dict(book)

    content = json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":")
    )

    etag = hashlib.sha256(content.encode()).hexdigest()

    client_etag = request.headers.get("If-None-Match")

    if client_etag == etag:
        resp = make_response("", 304)
        resp.headers["ETag"] = etag
        return resp


    if book is None : return jsonify(error = "not found"), 404
    resp = make_response(jsonify(dict(book)), 200)
    resp.headers["ETag"] = etag
    resp.headers["Cache-Control"] = "max-age=60" 
    return resp

# PUT 
@app.put("/books/<int:bid>")
def put(bid):
    # i = next((k for k , b in enumerate(BOOKS) if b["id"] == bid), None)
    conn = get_db()
    book = conn.execute("SELECT * FROM books WHERE id = ?",(bid,)).fetchone()

    if book is None :
        return jsonify(error = "not found"), 404
    
    p = request.get_json(silent= True) or {}
    t,a = p.get("title"), p.get("author")

    if not t or not a:
        return jsonify(error = "need title + author") , 422
    
    # BOOKS[i] = {"id" : bid , "title" : t.strip(), "author" : a.strip(), "isbn" : p.get("isbn"), "price" : p.get("price")}
    conn.execute("""
        UPDATE books 
        SET title = ?, author = ?, isbn = ?, price = ?
        WHERE id = ?
        """,(t,a,p.get("isbn"), p.get("price"), bid ))

    conn.commit()

    book = conn.execute("SELECT * FROM books WHERE id = ?",(bid,)).fetchone()
    conn.close()

    return jsonify(dict(book)), 200


#PATCH
@app.patch("/books/<int:bid>")
def patch(bid):
    # i = next((k for k, b in enumerate(BOOKS) if b["id"] == bid), None)
    conn = get_db()
    book = conn.execute("SELECT * FROM books WHERE id = ?", (bid,)).fetchone()


    if book is None:
        return jsonify(error = "not found"), 404


    p = request.get_json(silent = True) or {}


    if p.get("price", 0 ) < 0 :
        return jsonify(error ="price must be positive"), 422
    
    for k in "title author isbn price".split():
        if k in p:
            conn.execute(f"UPDATE books SET {k} = ? WHERE id = ?",(p[k], bid))
            # BOOKS[i][k] = p[k]
    
    conn.commit()
    book = conn.execute("SELECT * FROM books WHERE id = ?", (bid,)).fetchone()
    conn.close()
    return jsonify(dict(book)), 200

#DELETE
@app.delete("/books/<int:bid>")
def delete(bid):
    # i = next((k for k, b in enumerate(BOOKS) if b["id"] == bid), None)
    conn = get_db()
    book = conn.execute("SELECT * FROM books WHERE id = ?", (bid,)).fetchone()

    if book is None:
        return jsonify(error = "not found"), 404

    
    # BOOKS.pop(i)

    conn.execute("DELETE FROM books WHERE id = ?",(bid,))
    conn.commit()
    conn.close()

    return "", 204


DEFAULT_SIZE, MAX_SIZE = 20, 100
# list, filter, paginate, links
@app.get("/books")
def list_book():
    #filter
    try:
        page = int(request.args.get("page", 1))
        size = int(request.args.get("size", DEFAULT_SIZE))
    except ValueError:
        return jsonify(error = "page and size must be int"), 400
    
    page = max(page,1)
    size = max(min(size, MAX_SIZE), 1)

    # flt = BOOKS
    conn = get_db()
    conditions = []
    params = []

    
    a = request.args.get("author")
    if a:
        conditions.append("LOWER(author) = LOWER(?)")
        params.append(a)
    q = (request.args.get("q") or "").strip()
    if q:
        conditions.append("LOWER(title) LIKE LOWER(?)")
        params.append(f"%{q}%")

    sql = "SELECT * FROM books"

    count_sql = "SELECT COUNT(*) FROM books"

    if conditions:
        count_sql += " WHERE " + " AND ".join(conditions)




    total = conn.execute(count_sql, params).fetchone()[0]


    start = (page - 1) * size

    sql += " LIMIT ? OFFSET ?"

    rows = conn.execute(sql, params + [size, start]).fetchall()

    conn.close()

    items = [dict(row) for row in rows]
    last = (total +size-1)// size


    
    



    # a = request.args.get("author")
    # if a:
    #     flt = [b for b in flt if b["author"].lower() == a.lower()]
    # q = (request.args.get("q") or "").lower()
    # if q:
    #     flt = [b for b in flt if b["title"].lower() == q.lower()]


    # #paginate
    # total = len(flt)
    # start = (page-1)* size
    # end = start + size
    # items = flt[start:end]
    # last = (total+size-1)//size


    # #hateoas links
    def u(p):
        return f"/books?page={p}&size={size}"
    links = {"self" : {"href":u(page)},
             "first" : {"href" :u(1)},
             "last" : {"href" : u(max(last,1))}}

    
    if page > 1 :
        links["prev"] = {"href":u(page -1)}
    if last < total:
        links["next"] = {"href" : u(page+1)}


    body = {"data" : items,
            "pagination" : {"page" : page,
                            "size" : size,
                            "total" : total,
                            "totalpages" : last},
            "_links" : links}

    
    resp = make_response(jsonify(body), 200)
    resp.headers["Cache-Control"] = "public, max-age=30"
    return resp
    
@app.get("/orders/<int:oid>")
def get_order(oid):
    conn = get_db()

    order = conn.execute("SELECT * FROM orders WHERE id = ?",(oid,)).fetchone()

    conn.close()


    if order is None:
        return jsonify(error="not found"), 404

    return jsonify(dict(order)), 200
    

if __name__ == "__main__":
    init_db()
    app.run(debug = True)

    