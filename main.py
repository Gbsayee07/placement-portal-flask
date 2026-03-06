from flask import Blueprint, redirect, url_for, render_template
from flask_login import login_required, current_user

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def home():
    return render_template("home.html")

@main_bp.route("/dashboard")
@login_required
def dashboard():
    # Simple role-based routing (we’ll build real dashboards later)
    if current_user.role == "admin":
        return redirect(url_for("admin.dashboard"))
    if current_user.role == "company":
        return redirect(url_for("company.dashboard"))
    return redirect(url_for("student.dashboard"))