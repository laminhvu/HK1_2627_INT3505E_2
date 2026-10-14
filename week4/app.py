
from flask import Flask, abort
from flask.views import MethodView
from flask_smorest import Api, Blueprint
from marshmallow import Schema, fields, validate

app = Flask(__name__)

app.config["API_TITLE"] = "Tasks API"
app.config["API_VERSION"] = "1.0.0"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_URL_PREFIX"] = "/"
app.config["OPENAPI_JSON_PATH"] = "openapi.json"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/docs"
app.config["OPENAPI_SWAGGER_UI_URL"] = (
    "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/"
)

api = Api(app)

tasks_blp = Blueprint(
    "Tasks",
    "tasks",
    url_prefix="/tasks",
    description="Quan ly cong viec"
)


class TaskSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    status = fields.Str(
        required=True,
        validate=validate.OneOf(["TODO", "IN_PROGRESS", "DONE"])
    )
    priority = fields.Str(
        required=True,
        validate=validate.OneOf(["LOW", "MEDIUM", "HIGH"])
    )
    dueDate = fields.Date(allow_none=True)
    assigneeId = fields.Int(allow_none=True)


class TaskCreateSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    status = fields.Str(
        load_default="TODO",
        validate=validate.OneOf(["TODO", "IN_PROGRESS", "DONE"])
    )
    priority = fields.Str(
        load_default="MEDIUM",
        validate=validate.OneOf(["LOW", "MEDIUM", "HIGH"])
    )
    dueDate = fields.Date(allow_none=True, load_default=None)
    assigneeId = fields.Int(allow_none=True, load_default=None)


class TaskUpdateSchema(Schema):
    title = fields.Str(validate=validate.Length(min=1, max=200))
    status = fields.Str(
        validate=validate.OneOf(["TODO", "IN_PROGRESS", "DONE"])
    )
    priority = fields.Str(
        validate=validate.OneOf(["LOW", "MEDIUM", "HIGH"])
    )
    dueDate = fields.Date(allow_none=True)
    assigneeId = fields.Int(allow_none=True)


class TaskQuerySchema(Schema):
    status = fields.Str(
        validate=validate.OneOf(["TODO", "IN_PROGRESS", "DONE"])
    )
    page = fields.Int(load_default=1, validate=validate.Range(min=1))
    limit = fields.Int(
        load_default=10,
        validate=validate.Range(min=1, max=100)
    )


tasks = {
    1: {
        "id": 1,
        "title": "Hoc OpenAPI",
        "status": "IN_PROGRESS",
        "priority": "HIGH",
        "dueDate": None,
        "assigneeId": 1
    },
    2: {
        "id": 2,
        "title": "Hoan thanh bai tap Flask",
        "status": "TODO",
        "priority": "MEDIUM",
        "dueDate": None,
        "assigneeId": 2
    }
}

next_id = 3


@tasks_blp.route("/")
class TasksList(MethodView):

    @tasks_blp.arguments(TaskQuerySchema, location="query")
    @tasks_blp.response(200)
    def get(self, query):
        """Lay danh sach task, co loc va phan trang."""
        filtered = list(tasks.values())

        if query.get("status"):
            filtered = [
                task for task in filtered
                if task["status"] == query["status"]
            ]

        page = query["page"]
        limit = query["limit"]
        total = len(filtered)
        start = (page - 1) * limit

        return {
            "items": filtered[start:start + limit],
            "page": page,
            "limit": limit,
            "total": total,
            "totalPages": (total + limit - 1) // limit
        }

    @tasks_blp.arguments(TaskCreateSchema)
    @tasks_blp.response(201, TaskSchema)
    def post(self, data):
        """Tao task moi."""
        global next_id

        task = {"id": next_id, **data}
        tasks[next_id] = task
        next_id += 1

        return task


@tasks_blp.route("/<int:task_id>")
class TaskDetail(MethodView):

    @tasks_blp.response(200, TaskSchema)
    def get(self, task_id):
        """Lay chi tiet task theo ID."""
        task = tasks.get(task_id)

        if task is None:
            abort(404, description="Khong tim thay task")

        return task

    @tasks_blp.arguments(TaskUpdateSchema)
    @tasks_blp.response(200, TaskSchema)
    def patch(self, data, task_id):
        """Cap nhat mot phan thong tin task."""
        task = tasks.get(task_id)

        if task is None:
            abort(404, description="Khong tim thay task")

        if not data:
            abort(400, description="Can co it nhat mot truong de cap nhat")

        task.update(data)
        return task

    @tasks_blp.response(204)
    def delete(self, task_id):
        """Xoa task theo ID."""
        if task_id not in tasks:
            abort(404, description="Khong tim thay task")

        del tasks[task_id]
        return ""


api.register_blueprint(tasks_blp)


if __name__ == "__main__":
    app.run(debug=True)
