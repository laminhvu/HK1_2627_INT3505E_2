from flask import Flask, jsonify, request
app = Flask(__name__)
_next = 1
BOOKS = [{"id": 1, "title" : "clean code", "author" : "lmv" , "year" : 2006}]
def find(bid):
    return next((b for b in BOOKS if b["id"] == bid), None)
#get
def sort_title(books):
    for i in range(len(books)):
        for j in range(i + 1, len(books)):
            if books[i]["title"].lower() > books[j]["title"].lower():
                temp = books[i]
                books[i] = books[j]
                books[j] = temp
@app.route("/books", methods = ["GET"])
def list_book():
    n = int(request.args.get("limit",100))
    q = request.args.get("q")
    sort = request.args.get("sort")
    year = int(request.args.get("year"))

    if q:
        result = []
        for book in BOOKS:
            if q in book["title"]:
                result.append(book)
        if sort == "title":
            sort_title(result)
        return jsonify(result[:n]), 200   

    if sort == "title":
        books = BOOKS
        sort_title(books)
        return jsonify(books[:n]), 200

    if year:
        result = []
        for book in BOOKS:
            if book["year"] >= year:
                result.append(book)
        return jsonify(result[:n]), 200



    
    return jsonify(BOOKS[:n]), 200
#get detail
@app.route("/books/<int:bid>", methods= ["GET"])
def get_book(bid):
    book = find(bid)
    if not book:
        return {"error" : "not found"} , 404
    return jsonify(book) , 200
#get book theo q
@app.route("/books/")

#create
@app.route("/books", methods = ["POST"])
def create_book():
    global _next
    body = request.get_json(silent= True) or {}
    t, a = body.get("title"), body.get("author")
    if not t or not a:
        return {"error" : "need title and author"}, 400
    _next +=1
    book = {"id" : _next, "title" : t , "author" : a}
    BOOKS.append(book)
    return jsonify(book), 201, {"location" : f"/books/{book['id']}"}

#update
@app.route("/books/<int:bid>" , methods = ["PUT", "DELETE"])
def modify_book(bid):
    book = find(bid)
    if not book:
        return {"error" : "not found"} , 404
    if request.method == "PUT":
        book.update(request.get_json(silent= True) or {})
        return jsonify(book), 200
    BOOKS.remove(book)
    
    return jsonify(BOOKS), 200
if __name__ == "__main__":

    app.run(host= "127.0.0.1", port = 5000, debug = True) 


