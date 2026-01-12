from app.database import db
from app.routers.auth import auth_route
from app.routers.users import user_route
from app.routers.device import device_route
from app.routers.control import control_route
from app.routers.video import video_route
from environs import Env
from flask import Flask, redirect, url_for
from flask_jwt_extended import JWTManager


def create_app():
    env = Env()
    env.read_env(override=True)

    app = Flask(__name__)
    jwt = JWTManager(app)

    app.config["SQLALCHEMY_DATABASE_URI"] = env.str("DATABASE_URI")
    app.config["JWT_SECRET_KEY"] = env.str("JWT_SECRET_KEY")
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False
    db.init_app(app)

    @jwt.invalid_token_loader
    def repath(*args):
        return redirect(url_for("auth.login"))

    with app.app_context():
        db.create_all()

    app.register_blueprint(user_route, url_prefix="/users")
    app.register_blueprint(auth_route, url_prefix="/auth")
    app.register_blueprint(device_route, url_prefix="/device")
    app.register_blueprint(control_route, url_prefix="/control")
    app.register_blueprint(video_route, url_prefix="/video")

    return app
