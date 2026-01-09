from app.database import db
from app.models.user import User
from flask import Blueprint, request, render_template, redirect, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, set_access_cookies

auth_route = Blueprint("auth", __name__)


@auth_route.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("auth/login.html")

    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        return render_template("auth/login.html", error="Invalid credentials")

    user = db.session.execute(db.select(User).filter_by(username=username)).scalar_one_or_none()

    if not user or not user.check_password(password):
        return render_template("auth/login.html", error="Invalid credentials")

    response = make_response(redirect("/"))
    token = create_access_token(username)
    set_access_cookies(response, token)

    return response


@auth_route.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    user = get_jwt_identity()
    return {"message": "Hello", "user": user}
