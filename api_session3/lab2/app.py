from flask import Flask, abort, jsonify, request
from uuid import uuid4
from werkzeug.exceptions import HTTPException


ERROR_BASE = "https://api.example.com/error"



class ProblemError(Exception):
    

    def __init__(self, status, title, type_path=None, detail=None, **extra):
        super().__init__(title)
        self.status = status
        self.title = title
        self.type = f"{ERROR_BASE}/{type_path}" if type_path else "about:blank"
        self.detail = detail
        self.extra = extra 



def problem(status, title, type="about:blank", detail=None, **extra):
    body = {
        "type": type,
        "title": title,
        "status": status,
        "instance": request.path,
    }
    if detail:
        body["detail"] = detail
    body.update(extra)

    resp = jsonify(body)
    resp.status_code = status
    resp.headers["Content-Type"] = "application/problem+json" 
    return resp


def error_handlers(app):
    
    @app.errorhandler(ProblemError)
    def handle_problem(err):
        return problem(
            err.status, err.title, err.type, err.detail, **err.extra
        )

   
    @app.errorhandler(HTTPException)
    def handle_http_exception(err):
        return problem(err.code, err.name, detail=err.description)

    
    @app.errorhandler(Exception)
    def handle_unexpected(err):
        app.logger.exception("unhandled exception")
        return problem(500,   "Internal Server Error")





app = Flask(__name__)
error_handlers(app)

USERS = {1: {"id": 1, "name": "username1"}}

@app.get("/users/<int:id>")
def get_resource(id):
        user = USERS.get(id)
        if user is None:
            raise ProblemError(
                status = 404,
                title="user not found", 
                type_path="user-not-found",
                userid=id,
            )
        return jsonify(user)
@app.get("/boom")
def boom():
    1 / 0






if __name__ == "__main__":
    app.run(debug=False)  