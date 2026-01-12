from flask import Blueprint, request, render_template, redirect, make_response, url_for
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    create_access_token,
    set_access_cookies, )

from app.database import db
from app.models.user import User

auth_route = Blueprint("auth", __name__)


@auth_route.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("auth/login.html")

    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        return render_template("auth/login.html", error="Invalid credentials")

    user: User = db.session.execute(
        db.select(User).filter_by(username=username)
    ).scalar_one_or_none()

    if not user or not user.check_password(password):
        return render_template("auth/login.html", error="Invalid credentials")

    if not user.is_active:
        return render_template("auth/activation.html")

    response = make_response(redirect("/"))
    token = create_access_token(username)
    set_access_cookies(response, token)

    return response


@auth_route.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "GET":
        return render_template("auth/register.html")

    username = request.form.get("username", None)
    password = request.form.get("password", None)
    confirm_password = request.form.get("confirm_password", None)

    if not username or not password or not confirm_password:
        return render_template(
            "auth/register.html", password_error="Passwords didn’t match. Try again.",
            username_error="Username cannot be empty"
        )

    if password != confirm_password:
        return render_template(
            "auth/register.html", password_error="Passwords didn’t match. Try again."
        )

    user = db.session.execute(
        db.select(User).filter_by(username=username)
    ).scalar_one_or_none()

    if user:
        return render_template(
            "auth/register.html", username_error="This username already exists"
        )

    user = User(
        username=request.form["username"],
    )
    user.set_password(request.form["password"])
    db.session.add(user)
    db.session.commit()

    return redirect(url_for("auth.login", created=True))


@auth_route.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    user = get_jwt_identity()
    return {"message": "Hello", "user": user}
