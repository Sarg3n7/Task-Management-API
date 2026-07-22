from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token

from ..extensions import db
from ..models import User


class RegisterResource(Resource):
    """POST /api/register -> create a new user account."""

    def post(self):
        data = request.get_json(silent=True) or {}
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return {"message": "username and password are required"}, 400

        if User.query.filter_by(username=username).first():
            return {"message": "username already exists"}, 409

        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return {"message": "user registered successfully", "id": user.id}, 201


class LoginResource(Resource):
    """POST /api/login -> return a JWT access token on valid credentials."""

    def post(self):
        data = request.get_json(silent=True) or {}
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return {"message": "username and password are required"}, 400

        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            return {"message": "invalid credentials"}, 401

        # Identity must be a string in current Flask-JWT-Extended versions.
        access_token = create_access_token(identity=str(user.id))
        return {"access_token": access_token}, 200
