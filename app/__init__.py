from environs import Env
from flask import Flask

from app.database import db
from app.routers.users import user_route


def create_app():
    env = Env()
    env.read_env(override=True)

    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = env.str("DATABASE_URI")

    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(user_route, url_prefix="/users")

    return app
