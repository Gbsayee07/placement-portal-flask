from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from models import db, User, CompanyProfile, StudentProfile, PlacementDrive, Application

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_only():
    return current_user.is_authenticated and current_user.role == "admin"


@admin_bp.route("/dashboard")
@login_required
def dashboard():
    if not admin_only():
        return "Forbidden", 403

    total_students = StudentProfile.query.count()
    total_companies = CompanyProfile.query.count()
    total_drives = PlacementDrive.query.count()
    total_applications = Application.query.count()

    pending_companies = CompanyProfile.query.filter_by(approval_status="pending").all()

    return render_template(
        "admin/dashboard.html",
        total_students=total_students,
        total_companies=total_companies,
        total_drives=total_drives,
        total_applications=total_applications,
        pending_companies=pending_companies
    )


@admin_bp.route("/approve-company/<int:company_id>")
@login_required
def approve_company(company_id):
    if not admin_only():
        return "Forbidden", 403

    company = CompanyProfile.query.get_or_404(company_id)
    company.approval_status = "approved"

    db.session.commit()

    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/reject-company/<int:company_id>")
@login_required
def reject_company(company_id):
    if not admin_only():
        return "Forbidden", 403

    company = CompanyProfile.query.get_or_404(company_id)
    company.approval_status = "rejected"

    db.session.commit()

    return redirect(url_for("admin.dashboard"))

@admin_bp.route("/drives")
@login_required
def drives():
    if not admin_only():
        return "Forbidden", 403

    pending_drives = PlacementDrive.query.filter_by(status="pending").order_by(PlacementDrive.created_at.desc()).all()
    all_drives = PlacementDrive.query.order_by(PlacementDrive.created_at.desc()).all()

    return render_template("admin/drives.html", pending_drives=pending_drives, all_drives=all_drives)


@admin_bp.route("/approve-drive/<int:drive_id>")
@login_required
def approve_drive(drive_id):
    if not admin_only():
        return "Forbidden", 403

    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.status = "approved"
    db.session.commit()
    return redirect(url_for("admin.drives"))


@admin_bp.route("/reject-drive/<int:drive_id>")
@login_required
def reject_drive(drive_id):
    if not admin_only():
        return "Forbidden", 403

    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.status = "rejected"
    db.session.commit()
    return redirect(url_for("admin.drives"))