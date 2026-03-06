from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, StudentProfile, CompanyProfile

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash("Invalid email or password.", "danger")
            return render_template("auth/login.html")

        if not user.is_active or user.is_blacklisted:
            flash("Your account is inactive or blacklisted. Contact admin.", "danger")
            return render_template("auth/login.html")

        # Company can login only if approved
        if user.role == "company":
            if not user.company_profile or user.company_profile.approval_status != "approved":
                flash("Company account not approved by admin yet.", "warning")
                return render_template("auth/login.html")

        login_user(user)
        return redirect(url_for("main.dashboard"))

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for("auth.login"))


@auth_bp.route("/register/student", methods=["GET", "POST"])
def register_student():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        college_id = request.form.get("college_id", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not (full_name and college_id and email and password):
            flash("Please fill all required fields.", "danger")
            return render_template("auth/register_student.html")

        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
            return render_template("auth/register_student.html")

        if StudentProfile.query.filter_by(college_id=college_id).first():
            flash("College ID already registered.", "danger")
            return render_template("auth/register_student.html")

        user = User(email=email, role="student")
        user.set_password(password)

        student = StudentProfile(
            user=user,
            full_name=full_name,
            college_id=college_id,
            phone=phone
        )

        db.session.add(user)
        db.session.add(student)
        db.session.commit()

        flash("Student registered successfully. Please login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register_student.html")


@auth_bp.route("/register/company", methods=["GET", "POST"])
def register_company():
    if request.method == "POST":
        company_name = request.form.get("company_name", "").strip()
        hr_name = request.form.get("hr_name", "").strip()
        hr_email = request.form.get("hr_email", "").strip()
        phone = request.form.get("phone", "").strip()
        website = request.form.get("website", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not (company_name and email and password):
            flash("Please fill all required fields.", "danger")
            return render_template("auth/register_company.html")

        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
            return render_template("auth/register_company.html")

        user = User(email=email, role="company")
        user.set_password(password)

        company = CompanyProfile(
            user=user,
            company_name=company_name,
            hr_name=hr_name,
            hr_email=hr_email,
            phone=phone,
            website=website,
            approval_status="pending"
        )

        db.session.add(user)
        db.session.add(company)
        db.session.commit()

        flash("Company registered. Wait for admin approval before login.", "info")
        return redirect(url_for("auth.login"))

    return render_template("auth/register_company.html")