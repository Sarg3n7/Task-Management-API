from flask import Flask
from flask_restful import Api

from .config import Config
from .extensions import db, jwt
from .resources.auth import RegisterResource, LoginResource
from .resources.tasks import TaskListResource, TaskResource


def create_app(config_class=Config):
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Bind extensions to this app instance.
    db.init_app(app)
    jwt.init_app(app)

    # Register REST endpoints.
    api = Api(app)
    api.add_resource(RegisterResource, "/api/register")
    api.add_resource(LoginResource, "/api/login")
    api.add_resource(TaskListResource, "/api/tasks")
    api.add_resource(TaskResource, "/api/tasks/<int:task_id>")

    # Create tables if they don't exist yet.
    with app.app_context():
        db.create_all()

    return app
