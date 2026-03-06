from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, CompanyProfile, PlacementDrive, Application, StudentProfile

company_bp = Blueprint("company", __name__, url_prefix="/company")


def company_only():
    return current_user.is_authenticated and current_user.role == "company"


def get_company_profile():
    return CompanyProfile.query.filter_by(user_id=current_user.id).first()


@company_bp.route("/dashboard")
@login_required
def dashboard():
    if not company_only():
        return "Forbidden", 403

    company = get_company_profile()
    if not company or company.approval_status != "approved":
        return "Company not approved", 403

    drives = PlacementDrive.query.filter_by(company_id=company.id).order_by(PlacementDrive.created_at.desc()).all()
    return render_template("company/dashboard.html", company=company, drives=drives)


@company_bp.route("/drives/create", methods=["GET", "POST"])
@login_required
def create_drive():
    if not company_only():
        return "Forbidden", 403

    company = get_company_profile()
    if not company or company.approval_status != "approved":
        return "Company not approved", 403

    if request.method == "POST":
        job_title = request.form.get("job_title", "").strip()
        job_description = request.form.get("job_description", "").strip()
        eligibility_criteria = request.form.get("eligibility_criteria", "").strip()
        deadline_str = request.form.get("deadline", "").strip()

        if not (job_title and job_description and deadline_str):
            flash("Please fill all required fields.", "danger")
            return render_template("company/create_drive.html")

        try:
            deadline = datetime.strptime(deadline_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid deadline date.", "danger")
            return render_template("company/create_drive.html")

        drive = PlacementDrive(
            company_id=company.id,
            job_title=job_title,
            job_description=job_description,
            eligibility_criteria=eligibility_criteria,
            deadline=deadline,
            status="pending"
        )

        db.session.add(drive)
        db.session.commit()

        flash("Drive created and sent for admin approval.", "success")
        return redirect(url_for("company.dashboard"))

    return render_template("company/create_drive.html")


@company_bp.route("/drives/<int:drive_id>/edit", methods=["GET", "POST"])
@login_required
def edit_drive(drive_id):
    if not company_only():
        return "Forbidden", 403

    company = get_company_profile()
    if not company or company.approval_status != "approved":
        return "Company not approved", 403

    drive = PlacementDrive.query.get_or_404(drive_id)
    if drive.company_id != company.id:
        return "Forbidden", 403

    if request.method == "POST":
        drive.job_title = request.form.get("job_title", "").strip()
        drive.job_description = request.form.get("job_description", "").strip()
        drive.eligibility_criteria = request.form.get("eligibility_criteria", "").strip()

        deadline_str = request.form.get("deadline", "").strip()
        try:
            drive.deadline = datetime.strptime(deadline_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid deadline date.", "danger")
            return render_template("company/edit_drive.html", drive=drive)

        # If editing an already-approved drive, we keep it approved.
        # If you want edits to require re-approval, set drive.status = "pending" here.

        db.session.commit()
        flash("Drive updated successfully.", "success")
        return redirect(url_for("company.dashboard"))

    return render_template("company/edit_drive.html", drive=drive)


@company_bp.route("/drives/<int:drive_id>/applicants")
@login_required
def view_applicants(drive_id):
    if not company_only():
        return "Forbidden", 403

    company = get_company_profile()
    drive = PlacementDrive.query.get_or_404(drive_id)

    if not company or drive.company_id != company.id:
        return "Forbidden", 403

    applications = Application.query.filter_by(drive_id=drive.id).all()
    return render_template("company/applicants.html", drive=drive, applications=applications)



@company_bp.route("/applications/<int:application_id>/status/<string:new_status>")
@login_required
def update_application_status(application_id, new_status):
    if not company_only():
        return "Forbidden", 403

    allowed = {"shortlisted", "selected", "rejected"}
    if new_status not in allowed:
        return "Invalid status", 400

    company = get_company_profile()
    app_obj = Application.query.get_or_404(application_id)

    # Ensure this application belongs to a drive owned by this company
    if app_obj.drive.company_id != company.id:
        return "Forbidden", 403

    app_obj.status = new_status
    db.session.commit()

    flash(f"Application updated to {new_status}.", "success")
    return redirect(url_for("company.view_applicants", drive_id=app_obj.drive_id))


@company_bp.route("/drives/<int:drive_id>/close")
@login_required
def close_drive(drive_id):
    if not company_only():
        return "Forbidden", 403

    company = get_company_profile()
    drive = PlacementDrive.query.get_or_404(drive_id)
    if not company or drive.company_id != company.id:
        return "Forbidden", 403

    drive.status = "closed"
    db.session.commit()
    flash("Drive closed.", "warning")
    return redirect(url_for("company.dashboard"))


@company_bp.route("/drives/<int:drive_id>/delete")
@login_required
def delete_drive(drive_id):
    if not company_only():
        return "Forbidden", 403

    company = get_company_profile()
    drive = PlacementDrive.query.get_or_404(drive_id)
    if not company or drive.company_id != company.id:
        return "Forbidden", 403

    db.session.delete(drive)
    db.session.commit()
    flash("Drive deleted.", "danger")
    return redirect(url_for("company.dashboard"))