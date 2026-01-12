from app.database import db
from app.models.user import User
from flask import Blueprint, request, redirect, url_for, render_template
from flask import jsonify

user_route = Blueprint("users", __name__)