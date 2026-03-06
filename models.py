from flask_login import UserMixin
from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# ---------- Core User Table ----------
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(20), nullable=False)  # admin / student / company

    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_blacklisted = db.Column(db.Boolean, default=False, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships (one-to-one)
    student_profile = db.relationship("StudentProfile", backref="user", uselist=False)
    company_profile = db.relationship("CompanyProfile", backref="user", uselist=False)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


# ---------- Student ----------
class StudentProfile(db.Model):
    __tablename__ = "student_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)

    full_name = db.Column(db.String(120), nullable=False)
    college_id = db.Column(db.String(50), unique=True, nullable=False, index=True)  # ✅ your choice
    phone = db.Column(db.String(20), nullable=True)

    department = db.Column(db.String(80), nullable=True)
    cgpa = db.Column(db.Float, nullable=True)
    batch_year = db.Column(db.Integer, nullable=True)

    resume_filename = db.Column(db.String(255), nullable=True)

    applications = db.relationship("Application", backref="student", cascade="all, delete-orphan")


# ---------- Company ----------
class CompanyProfile(db.Model):
    __tablename__ = "company_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)

    company_name = db.Column(db.String(150), nullable=False, index=True)
    hr_name = db.Column(db.String(120), nullable=True)
    hr_email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    website = db.Column(db.String(255), nullable=True)

    approval_status = db.Column(db.String(20), default="pending", nullable=False)  # pending/approved/rejected
    remarks = db.Column(db.String(255), nullable=True)

    drives = db.relationship("PlacementDrive", backref="company", cascade="all, delete-orphan")


# ---------- Placement Drive ----------
class PlacementDrive(db.Model):
    __tablename__ = "placement_drives"

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("company_profiles.id"), nullable=False)

    job_title = db.Column(db.String(150), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    eligibility_criteria = db.Column(db.Text, nullable=True)

    deadline = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default="pending", nullable=False)  # pending/approved/closed

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    applications = db.relationship("Application", backref="drive", cascade="all, delete-orphan")

    def is_open(self) -> bool:
        if self.status != "approved":
            return False
        return date.today() <= self.deadline


# ---------- Application ----------
class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    resume_filename = db.Column(db.String(255), nullable=False)

    student_id = db.Column(db.Integer, db.ForeignKey("student_profiles.id"), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey("placement_drives.id"), nullable=False)

    applied_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(20), default="applied", nullable=False)  # applied/shortlisted/selected/rejected

    # ✅ Prevent multiple applications by same student to same drive
    __table_args__ = (
        db.UniqueConstraint("student_id", "drive_id", name="uq_student_drive"),
    )