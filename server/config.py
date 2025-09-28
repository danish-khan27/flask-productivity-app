from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_restful import Api

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
api = Api()

def create_app(env: str = "dev") -> Flask:
    app = Flask(__name__)

    # Basic config
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Session cookie basics
    app.secret_key = "replace-me-with-a-long-random-string"
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    api.init_app(app)

    # Register routes *after* api.init_app, inside app context
    with app.app_context():
        from server.routes import register_routes
        register_routes(api)

    return app
