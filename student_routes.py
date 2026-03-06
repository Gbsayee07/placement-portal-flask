import os
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, StudentProfile, PlacementDrive, Application
from werkzeug.utils import secure_filename
from flask import current_app, request
from datetime import datetime

student_bp = Blueprint("student", __name__, url_prefix="/student")


def student_only():
    return current_user.is_authenticated and current_user.role == "student"


def get_student_profile():
    return StudentProfile.query.filter_by(user_id=current_user.id).first()

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_RESUME_EXTENSIONS"]

@student_bp.route("/dashboard")
@login_required
def dashboard():
    if not student_only():
        return "Forbidden", 403

    student = get_student_profile()

    # Show only approved drives
    drives = PlacementDrive.query.filter_by(status="approved").all()

    applications = {
        app.drive_id: app
        for app in Application.query.filter_by(student_id=student.id).all()
    }

    return render_template(
        "student/dashboard.html",
        student=student,
        drives=drives,
        applications=applications
    )



def allowed_resume(filename: str) -> bool:
    allowed = {"pdf", "doc", "docx"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed



@student_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if not student_only():
        return "Forbidden", 403

    student = get_student_profile()

    if request.method == "POST":
        student.full_name = request.form.get("full_name", "").strip()
        student.phone = request.form.get("phone", "").strip()
        student.department = request.form.get("department", "").strip()

        cgpa_val = request.form.get("cgpa", "").strip()
        student.cgpa = float(cgpa_val) if cgpa_val else None

        batch_val = request.form.get("batch_year", "").strip()
        student.batch_year = int(batch_val) if batch_val else None

        # Resume upload
        resume = request.files.get("resume")
        if resume and resume.filename:
            if not allowed_file(resume.filename):
                flash("Resume must be PDF/DOC/DOCX.", "danger")
                return render_template("student/profile.html", student=student)

            filename = secure_filename(resume.filename)
            unique_name = f"{student.college_id}_{filename}"

            save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], unique_name)
            resume.save(save_path)

            student.resume_filename = unique_name

        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("student.profile"))

    return render_template("student/profile.html", student=student)



@student_bp.route("/apply/<int:drive_id>", methods=["GET", "POST"])
@login_required
def apply(drive_id):
    if not student_only():
        return "Forbidden", 403

    student = get_student_profile()
    drive = PlacementDrive.query.get_or_404(drive_id)

    # Only allow applying to approved drives
    if drive.status != "approved":
        flash("This drive is not open for applications.", "danger")
        return redirect(url_for("student.dashboard"))

    # Prevent duplicate
    existing = Application.query.filter_by(student_id=student.id, drive_id=drive.id).first()
    if existing:
        flash("You already applied to this drive.", "warning")
        return redirect(url_for("student.dashboard"))

    if request.method == "POST":
        resume = request.files.get("resume")
        if not resume or not resume.filename:
            flash("Resume is required for each application.", "danger")
            return render_template("student/apply.html", student=student, drive=drive)

        if not allowed_resume(resume.filename):
            flash("Resume must be PDF/DOC/DOCX.", "danger")
            return render_template("student/apply.html", student=student, drive=drive)

        filename = secure_filename(resume.filename)
        unique_name = f"{student.college_id}_drive{drive.id}_{int(datetime.utcnow().timestamp())}_{filename}"
        save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], unique_name)
        resume.save(save_path)

        application = Application(
            student_id=student.id,
            drive_id=drive.id,
            status="applied",
            resume_filename=unique_name
        )

        db.session.add(application)
        db.session.commit()

        flash("Application submitted successfully!", "success")
        return redirect(url_for("student.dashboard"))

    # GET → show upload form
    return render_template("student/apply.html", student=student, drive=drive)