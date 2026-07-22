from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

# Instantiated here (no app yet) so they can be imported anywhere
# without causing circular imports, then bound to the app in create_app().
db = SQLAlchemy()
jwt = JWTManager()
