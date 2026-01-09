from flask import Blueprint, request, redirect, url_for, render_template
from flask import jsonify

from app.database import db
from app.models.user import User

user_route = Blueprint('users', __name__)


@user_route.route("/")
def user_list():
    users = (
        db.session
        .execute(db.select(User).order_by(User.username))
        .scalars()
        .all()
    )
    return jsonify([
        {
            "id": user.id,
            "username": user.username,
        }
        for user in users
    ])


@user_route.route("/create", methods=["GET", "POST"])
def user_create():
    if request.method == "POST":
        user = User(
            username=request.form["username"],
        )
        user.set_password(request.form['password'])
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("users.user_list"))

    return render_template("user/create.html")
