from flask import Flask, request, jsonify

app = Flask(__name__)

POSTS = {}        
_next_id = 1



# POST 
@app.post("/posts")
def create_post():


    global _next_id


    body = request.get_json(silent=True) or{}

    if not body.get("title") or not body.get("content"):
        return jsonify(error =  "title và  content là bắt buộc") ,404


    post = {
        "id": _next_id,
        "title": body["title"],
        "content": body["content"],
        "tags": body.get("tags", []),
    }


    POSTS[_next_id] = post
    _next_id += 1

    resp = jsonify(post)
    resp.status_code = 201                             
    resp.headers["Location"] = f"/v1/posts/{post['id']}"  
    return resp


if __name__ == "__main__":
    app.run(debug=True)