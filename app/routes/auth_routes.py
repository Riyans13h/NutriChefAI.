"""
Authentication Routes
---------------------
Handles:
- User registration
- User login
- User logout
"""

from flask import Blueprint, render_template, request, redirect, url_for, session

from app.services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/", methods=["GET"])
def home():
    """
    Landing page redirects to login.
    """
    return redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    User registration route.
    """
    if request.method == "POST":
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        password = request.form.get("password")

        success, message = AuthService.register_user(
            full_name=full_name,
            email=email,
            password=password
        )

        if success:
            return redirect(url_for("auth.login"))

        return render_template(
            "register.html",
            error=message
        )

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    User login route.
    """
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = AuthService.authenticate_user(
            email=email,
            password=password
        )

        if user:
            session["user_id"] = user["user_id"]
            session["user_name"] = user["full_name"]
            return redirect(url_for("meal.dashboard"))

        return render_template(
            "login.html",
            error="Invalid email or password"
        )

    return render_template("login.html")


@auth_bp.route("/logout", methods=["GET"])
def logout():
    """
    User logout route.
    """
    session.clear()
    return redirect(url_for("auth.login"))
