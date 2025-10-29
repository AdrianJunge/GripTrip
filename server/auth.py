from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
import flask_login

from . import db
from . import model

bp = Blueprint("auth", __name__)


@bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("auth/signup.html")
    elif request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")

        if password != request.form.get("password_repeat"):
            flash("Error, passwords are different!", "error")
            return redirect(url_for("auth.signup"))

        query = db.select(model.User).where(model.User.email == email)
        user = db.session.execute(query).scalar_one_or_none()

        if user:
            flash("Sorry, the email you provided is already registered!", "error")
            return redirect(url_for("auth.signup"))

        password_hash = generate_password_hash(password)
        new_user = model.User(email=email, name=username, password=password_hash)
        db.session.add(new_user)
        db.session.commit()
        flash("User created successfully! Please log in.", "success")
        return redirect(url_for("auth.login"))

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("auth/login.html")
    elif request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        query = db.select(model.User).where(model.User.email == email)
        user = db.session.execute(query).scalar_one_or_none()

        if user is None or not check_password_hash(user.password, password):
            flash("Invalid email or password!", "error")
            return redirect(url_for("auth.login"))

        flask_login.login_user(user)
        return redirect(url_for("main.index"))

@bp.route("/logout")
def logout():
    flask_login.logout_user()
    return redirect(url_for("auth.login"))
