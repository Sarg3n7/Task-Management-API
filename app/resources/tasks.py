from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..extensions import db
from ..models import Task


class TaskListResource(Resource):
    """Collection endpoint: list all tasks / create a task."""

    @jwt_required()
    def get(self):
        user_id = int(get_jwt_identity())
        tasks = Task.query.filter_by(user_id=user_id).all()
        return {"tasks": [t.to_dict() for t in tasks]}, 200

    @jwt_required()
    def post(self):
        user_id = int(get_jwt_identity())
        data = request.get_json(silent=True) or {}

        title = data.get("title")
        if not title:
            return {"message": "title is required"}, 400

        task = Task(
            title=title,
            description=data.get("description", ""),
            completed=bool(data.get("completed", False)),
            user_id=user_id,
        )
        db.session.add(task)
        db.session.commit()
        return task.to_dict(), 201


class TaskResource(Resource):
    """Item endpoint: read / update / delete a single task."""

    def _get_owned_task(self, task_id, user_id):
        return Task.query.filter_by(id=task_id, user_id=user_id).first()

    @jwt_required()
    def get(self, task_id):
        user_id = int(get_jwt_identity())
        task = self._get_owned_task(task_id, user_id)
        if not task:
            return {"message": "task not found"}, 404
        return task.to_dict(), 200

    @jwt_required()
    def put(self, task_id):
        user_id = int(get_jwt_identity())
        task = self._get_owned_task(task_id, user_id)
        if not task:
            return {"message": "task not found"}, 404

        data = request.get_json(silent=True) or {}
        task.title = data.get("title", task.title)
        task.description = data.get("description", task.description)
        if "completed" in data:
            task.completed = bool(data["completed"])
        db.session.commit()
        return task.to_dict(), 200

    @jwt_required()
    def delete(self, task_id):
        user_id = int(get_jwt_identity())
        task = self._get_owned_task(task_id, user_id)
        if not task:
            return {"message": "task not found"}, 404

        db.session.delete(task)
        db.session.commit()
        return {"message": "task deleted"}, 200
