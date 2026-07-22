import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration used when running the app normally."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-secret-change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(basedir, os.pardir, "tasks.db"),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestConfig(Config):
    """Configuration used by the test suite (in-memory DB)."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
